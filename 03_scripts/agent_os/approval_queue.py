"""Inspectible approval queue backed by JSON files and the Rust Agent OS guard."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from approved_executor import execute_approved_request


SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
RUST_MANIFEST = SOURCE_REPO_ROOT / "rust" / "Cargo.toml"
DEFAULT_QUEUE_ROOT = SOURCE_REPO_ROOT / "14_context" / "agent_os" / "approval_queue"
STATES = ("pending", "approved", "rejected", "executed", "failed")
ACTION_BY_WORKFLOW = {
    "coding-task": "write_workflow_plan",
    "content-video": "write_workflow_plan",
    "business-research": "write_workflow_plan",
    "repo-audit": "write_evidence_note",
    "email-draft": "write_handoff_file",
    "automation-n8n": "write_workflow_plan",
    "computer-use-prep": "write_evidence_note",
}
_ID_RE = re.compile(r"^req-[a-z0-9][a-z0-9-]{7,63}$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _request_id(seed: dict) -> str:
    return "req-" + hashlib.sha256(_canonical(seed).encode("utf-8")).hexdigest()[:20]


def build_action_request(
    *,
    workflow_id: str,
    action_id: str | None = None,
    artifact_path: str | None = None,
    content: str | None = None,
    created_at: str | None = None,
    created_by: str = "agent-os-worker",
) -> dict:
    """Build one deterministic, pending, suggestion-mode action request."""
    action = action_id or ACTION_BY_WORKFLOW.get(workflow_id, "write_workflow_plan")
    created = created_at or _now()
    seed = {
        "workflow_id": workflow_id,
        "action_id": action,
        "artifact_path": artifact_path,
        "content": content,
        "created_at": created,
        "created_by": created_by,
    }
    request_id = _request_id(seed)
    artifact = artifact_path or (
        f"14_context/agent_os/workflows/approved_{workflow_id}_{request_id}.md"
    )
    run_record = f"14_context/agent_os/runs/approved_{request_id}.json"
    evidence = f"14_context/agent_os/evidence/approved_{request_id}.md"
    handoff = f"14_context/memory/agent_handoffs/agent-os/{request_id}.md"
    outputs = [artifact, run_record, evidence, handoff]
    return {
        "schema": "ghoti_action_request/1",
        "request_id": request_id,
        "created_at": created,
        "created_by": created_by,
        "workflow_id": workflow_id,
        "action_id": action,
        "mode": "suggestion",
        "approval_state": "pending",
        "requested_capabilities": [
            "agent_os.read_memory",
            "agent_os.write_repo_local",
        ],
        "input_paths": ["14_context/compact_memory/current_working_summary.md"],
        "output_paths": outputs,
        "owned_files": outputs,
        "locked_paths": [],
        "max_runtime_seconds": 30,
        "approval_token_hash": None,
        "summary": f"Write one approved local artifact for {workflow_id}.",
        "risk_note": "Text/JSON artifact only; no shell, network, browser, or account action.",
        "payload": {
            "kind": "write_text_artifact",
            "artifact_path": artifact,
            "run_record_path": run_record,
            "evidence_path": evidence,
            "handoff_path": handoff,
            "title": f"Approved {workflow_id} artifact",
            "content": content
            or (
                f"# Approved {workflow_id} artifact\n\n"
                "This bounded repo-local artifact was proposed by the Agent OS worker.\n"
            ),
        },
    }


class ApprovalQueue:
    def __init__(
        self,
        *,
        repo_root: Path = SOURCE_REPO_ROOT,
        queue_root: Path = DEFAULT_QUEUE_ROOT,
        guard_binary: Path | None = None,
    ):
        self.repo_root = repo_root.resolve()
        self.queue_root = queue_root.resolve()
        self.guard_binary = guard_binary
        self.queue_root.relative_to(self.repo_root)
        for state in STATES:
            (self.queue_root / state).mkdir(parents=True, exist_ok=True)

    def _path(self, state: str, request_id: str) -> Path:
        if state not in STATES or not _ID_RE.match(request_id):
            raise ValueError("invalid queue state or request id")
        return self.queue_root / state / f"{request_id}.json"

    def _write(self, path: Path, record: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp.replace(path)

    def _read(self, state: str, request_id: str) -> dict:
        return json.loads(self._path(state, request_id).read_text(encoding="utf-8"))

    def _find(self, request_id: str) -> tuple[str, dict]:
        for state in STATES:
            path = self._path(state, request_id)
            if path.is_file():
                return state, json.loads(path.read_text(encoding="utf-8"))
        raise FileNotFoundError(request_id)

    def _guard_command(self, request_path: Path) -> list[str] | None:
        if self.guard_binary and self.guard_binary.is_file():
            return [
                str(self.guard_binary),
                "validate",
                "--request",
                str(request_path),
                "--repo-root",
                str(self.repo_root),
                "--json",
            ]
        configured = os.environ.get("GHOTI_AGENT_OS_GUARD_BINARY")
        candidates = [
            Path(configured) if configured else None,
            SOURCE_REPO_ROOT / "rust" / "target" / "release" / "agent_os_guard.exe",
            SOURCE_REPO_ROOT / "rust" / "target" / "release" / "agent_os_guard",
            SOURCE_REPO_ROOT / "rust" / "target" / "debug" / "agent_os_guard.exe",
            SOURCE_REPO_ROOT / "rust" / "target" / "debug" / "agent_os_guard",
        ]
        binary = next((candidate for candidate in candidates if candidate and candidate.is_file()), None)
        if binary:
            return [
                str(binary),
                "validate",
                "--request",
                str(request_path),
                "--repo-root",
                str(self.repo_root),
                "--json",
            ]
        cargo = shutil.which("cargo")
        if not cargo:
            return None
        return [
            cargo,
            "run",
            "--quiet",
            "--manifest-path",
            str(RUST_MANIFEST),
            "--bin",
            "agent_os_guard",
            "--",
            "validate",
            "--request",
            str(request_path),
            "--repo-root",
            str(self.repo_root),
            "--json",
        ]

    def validate(self, request: dict) -> dict:
        with tempfile.TemporaryDirectory(prefix="ghoti_approval_guard_") as temp_dir:
            request_path = Path(temp_dir) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            command = self._guard_command(request_path)
            if command is None:
                return {
                    "allow": False,
                    "decision": "denied",
                    "reason": "rust_guard_unavailable",
                    "reasons": ["rust_guard_unavailable"],
                }
            env = os.environ.copy()
            env.setdefault(
                "CARGO_TARGET_DIR",
                str(Path(tempfile.gettempdir()) / "ghoti_agent_os_approval_guard"),
            )
            result = subprocess.run(
                command,
                cwd=SOURCE_REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
                shell=False,
                check=False,
            )
        if result.returncode != 0:
            return {
                "allow": False,
                "decision": "denied",
                "reason": "rust_guard_invocation_failed",
                "reasons": ["rust_guard_invocation_failed"],
                "error": result.stderr.strip(),
            }
        return json.loads(result.stdout)

    def propose(self, request: dict) -> dict:
        request = json.loads(json.dumps(request))
        request["mode"] = "suggestion"
        request["approval_state"] = "pending"
        request["approval_token_hash"] = None
        decision = self.validate(request)
        if not decision.get("allow"):
            return {
                "ok": False,
                "action": "propose-action",
                "approval_state": "denied",
                "guard_decision": decision,
            }
        record = {
            "request": request,
            "guard_decision": decision,
            "transitions": [{"state": "pending", "at": _now(), "actor": "agent-os-worker"}],
        }
        self._write(self._path("pending", request["request_id"]), record)
        return {
            "ok": True,
            "action": "propose-action",
            "request_id": request["request_id"],
            "approval_state": "pending",
            "request_path": self._path("pending", request["request_id"])
            .relative_to(self.repo_root)
            .as_posix(),
            "guard_decision": decision,
        }

    def list(self, state: str | None = None) -> dict:
        states = (state,) if state else STATES
        items = []
        for current in states:
            if current not in STATES:
                raise ValueError("invalid queue state")
            for path in sorted((self.queue_root / current).glob("*.json")):
                record = json.loads(path.read_text(encoding="utf-8"))
                request = record["request"]
                items.append(
                    {
                        "request_id": request["request_id"],
                        "workflow_id": request.get("workflow_id"),
                        "action_id": request["action_id"],
                        "approval_state": current,
                        "summary": request.get("summary"),
                        "path": path.relative_to(self.repo_root).as_posix(),
                    }
                )
        return {"ok": True, "action": "list-approvals", "count": len(items), "items": items}

    def approve(self, request_id: str) -> dict:
        record = self._read("pending", request_id)
        request = record["request"]
        seed = f"explicit-local-approval:{request_id}:{record['guard_decision']['request_fingerprint']}"
        request["mode"] = "approved_local"
        request["approval_state"] = "approved"
        request["approval_token_hash"] = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        decision = self.validate(request)
        if not decision.get("allow"):
            return {
                "ok": False,
                "action": "approve-action",
                "request_id": request_id,
                "approval_state": "denied",
                "guard_decision": decision,
            }
        record["guard_decision"] = decision
        record["transitions"].append({"state": "approved", "at": _now(), "actor": "human-cli"})
        target = self._path("approved", request_id)
        self._write(target, record)
        self._path("pending", request_id).unlink()
        return {
            "ok": True,
            "action": "approve-action",
            "request_id": request_id,
            "approval_state": "approved",
            "request_path": target.relative_to(self.repo_root).as_posix(),
            "guard_decision": decision,
        }

    def reject(self, request_id: str, *, reason: str = "human rejected") -> dict:
        state, record = self._find(request_id)
        if state not in {"pending", "approved"}:
            return {"ok": False, "action": "reject-action", "reason": "request_not_rejectable"}
        record["request"]["approval_state"] = "rejected"
        record["request"]["mode"] = "suggestion"
        record["request"]["approval_token_hash"] = None
        record["transitions"].append(
            {"state": "rejected", "at": _now(), "actor": "human-cli", "reason": reason}
        )
        target = self._path("rejected", request_id)
        self._write(target, record)
        self._path(state, request_id).unlink()
        return {
            "ok": True,
            "action": "reject-action",
            "request_id": request_id,
            "approval_state": "rejected",
            "reason": reason,
        }

    def execute(self, request_id: str) -> dict:
        record = self._read("approved", request_id)
        request = record["request"]
        decision = self.validate(request)
        if not decision.get("allow"):
            return {
                "ok": False,
                "action": "execute-approved",
                "request_id": request_id,
                "approval_state": "denied",
                "guard_decision": decision,
            }
        result = execute_approved_request(request, self.repo_root)
        target_state = "executed" if result.get("ok") else "failed"
        request["approval_state"] = target_state
        record["guard_decision"] = decision
        record["execution_result"] = result
        record["transitions"].append(
            {"state": target_state, "at": _now(), "actor": "approved-executor"}
        )
        target = self._path(target_state, request_id)
        self._write(target, record)
        self._path("approved", request_id).unlink()
        result.update(
            {
                "action": "execute-approved",
                "request_id": request_id,
                "approval_state": target_state,
                "guard_decision": decision,
            }
        )
        return result

    def status(self) -> dict:
        counts = {
            state: len(list((self.queue_root / state).glob("*.json"))) for state in STATES
        }
        pending = self.list("pending")["items"]
        return {
            "ok": True,
            "action": "approval-status",
            "counts": counts,
            "pending_count": counts["pending"],
            "latest_pending": pending[-1] if pending else None,
            "queue_root": self.queue_root.relative_to(self.repo_root).as_posix(),
            "approved_local_execution_enabled": True,
            "allowed_actions": sorted(set(ACTION_BY_WORKFLOW.values())),
            "live_external_execution_enabled": False,
            "human_approval_required": True,
        }
