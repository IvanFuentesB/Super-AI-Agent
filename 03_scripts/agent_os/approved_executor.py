"""Bounded executor for explicitly approved repo-local text artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import data_only_writer


ALLOWED_ACTIONS = {
    "write_handoff_file",
    "write_workflow_plan",
    "write_evidence_note",
    "update_latest_state_note",
}
ALLOWED_ROOTS = (
    "14_context/agent_os/",
    "14_context/memory/agent_handoffs/",
    "14_context/operator_reports/generated/",
)
SECRET_MARKERS = (
    "api_key=",
    "apikey=",
    "authorization: bearer",
    "password=",
    "private_key",
    "secret=",
    "sk-ant-",
    "ghp_",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_repo_relative(raw: str) -> str:
    normalized = str(raw).strip().replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or ":" in normalized
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError("path must be a normalized repo-relative path")
    result = path.as_posix()
    if not any(result.startswith(root) for root in ALLOWED_ROOTS):
        raise ValueError("path is outside approved Agent OS output roots")
    return result


def _destination(repo_root: Path, raw: str) -> tuple[Path, str]:
    relative = _normalize_repo_relative(raw)
    destination = (repo_root / relative).resolve()
    destination.relative_to(repo_root.resolve())
    return destination, relative


def _write_text(repo_root: Path, raw_path: str, content: str) -> str:
    destination, relative = _destination(repo_root, raw_path)
    data_only_writer.write_text(destination, content)
    return relative


def _public_safe_text(content: str) -> bool:
    lowered = content.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        return False
    return "c:\\users\\" not in lowered and "c:/users/" not in lowered


def execute_approved_request(request: dict, repo_root: Path) -> dict:
    """Execute one allowlisted local artifact write and its evidence trail."""
    if request.get("schema") != "ghoti_action_request/1":
        return {"ok": False, "reason": "unsupported_schema"}
    if request.get("mode") != "approved_local" or request.get("approval_state") != "approved":
        return {"ok": False, "reason": "request_not_approved"}
    if request.get("action_id") not in ALLOWED_ACTIONS:
        return {"ok": False, "reason": "action_not_allowlisted"}
    if not request.get("approval_token_hash"):
        return {"ok": False, "reason": "approval_hash_missing"}

    payload = request.get("payload") or {}
    if payload.get("kind") != "write_text_artifact":
        return {"ok": False, "reason": "unsupported_payload_kind"}
    content = str(payload.get("content", ""))
    if not content or not _public_safe_text(content):
        return {"ok": False, "reason": "artifact_content_refused"}

    declared = set(request.get("output_paths") or [])
    required = {
        payload.get("artifact_path"),
        payload.get("run_record_path"),
        payload.get("evidence_path"),
        payload.get("handoff_path"),
    }
    if None in required or not required.issubset(declared):
        return {"ok": False, "reason": "execution_paths_not_declared"}

    try:
        artifact_path = _write_text(repo_root, payload["artifact_path"], content)
        executed_at = _now()
        run_record = {
            "schema": "ghoti_approved_run/1",
            "request_id": request["request_id"],
            "action_id": request["action_id"],
            "workflow_id": request.get("workflow_id"),
            "approval_state": "executed",
            "approved_local_execution": True,
            "artifact_path": artifact_path,
            "executed_at": executed_at,
            "live_execution": False,
            "network_used": False,
            "browser_used": False,
            "account_action": False,
            "shell_command_executed": False,
        }
        run_record_path = _write_text(
            repo_root,
            payload["run_record_path"],
            json.dumps(run_record, indent=2, sort_keys=True) + "\n",
        )
        evidence = "\n".join(
            [
                "# Approved Local Artifact Evidence",
                "",
                f"- Request: `{request['request_id']}`",
                f"- Action: `{request['action_id']}`",
                f"- Artifact: `{artifact_path}`",
                f"- Run record: `{run_record_path}`",
                "- Human approval: recorded",
                "- Live execution: false",
                "- Shell/network/browser/account actions: none",
                "",
            ]
        )
        evidence_path = _write_text(repo_root, payload["evidence_path"], evidence)
        handoff = "\n".join(
            [
                "# Agent OS Approved Action Handoff",
                "",
                f"- Request: `{request['request_id']}`",
                f"- Workflow: `{request.get('workflow_id', 'unknown')}`",
                f"- Artifact: `{artifact_path}`",
                f"- Evidence: `{evidence_path}`",
                "- Next action: review the local artifact.",
                "",
            ]
        )
        handoff_path = _write_text(repo_root, payload["handoff_path"], handoff)
    except (OSError, ValueError, KeyError) as error:
        return {"ok": False, "reason": "bounded_write_failed", "error": str(error)}

    return {
        "ok": True,
        "request_id": request["request_id"],
        "approval_state": "executed",
        "artifact_path": artifact_path,
        "run_record_path": run_record_path,
        "evidence_path": evidence_path,
        "handoff_path": handoff_path,
        "approved_local_execution": True,
        "live_execution": False,
        "executed_at": executed_at,
    }
