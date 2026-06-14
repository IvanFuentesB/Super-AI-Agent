#!/usr/bin/env python3
"""Suggestion-only local worker trial gated by the Rust Agent OS guard."""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RUST_MANIFEST = REPO_ROOT / "rust" / "Cargo.toml"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "14_context" / "agent_os"
TEST_OUTPUT_ROOT = Path(tempfile.gettempdir()) / "ghoti_agent_os_tests"
WORKFLOWS = {
    "automation-plan": "Draft a local automation checklist without executing commands.",
    "business-research-plan": "Draft a source-first business research checklist.",
    "coding-task-plan": "Draft an implementation and verification checklist.",
    "content-video-plan": "Draft a content and video production checklist.",
    "email-draft-plan": "Draft an email outline for human review; never send it.",
}
EXECUTED_MODES = {"simulation", "suggestion"}
BLOCKED_CAPABILITIES = [
    "account",
    "browser",
    "computer_use",
    "external_write",
    "mass_message",
    "mcp",
    "money",
    "payment",
    "posting",
    "purchase",
    "secrets",
]
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def _declared_paths(workflow: str) -> dict[str, str]:
    return {
        "plan": f"14_context/agent_os/trials/{workflow}.md",
        "run": f"14_context/agent_os/runs/{workflow}_run.json",
        "handoff": f"14_context/agent_os/handoffs/{workflow}_handoff.md",
    }


def _guard_request(workflow: str, mode: str, approval_token: str | None) -> dict[str, Any]:
    paths = _declared_paths(workflow)
    return {
        "schema_version": "1.0",
        "action_id": workflow,
        "mode": mode,
        "requested_capabilities": [
            "repo_read",
            "plan_render",
            "repo_write_trial",
            "run_record_write",
            "handoff_write",
        ],
        "input_paths": ["14_context/compact_memory/current_working_summary.md"],
        "output_paths": list(paths.values()),
        "locked_paths": [],
        "max_runtime_seconds": 30,
        "approval_token": approval_token,
    }


def _output_root_allowed(output_root: Path) -> bool:
    resolved = output_root.resolve()
    if resolved == DEFAULT_OUTPUT_ROOT.resolve():
        return True
    try:
        resolved.relative_to(TEST_OUTPUT_ROOT.resolve())
    except ValueError:
        return False
    return True


def _safe_write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path), encoded],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise OSError(f"safe data-only write failed for {path.name}: {result.stderr.strip()}")


def _invoke_guard(request: dict[str, Any]) -> dict[str, Any]:
    cargo = shutil.which("cargo")
    if not cargo:
        return {
            "allow": False,
            "decision": "denied",
            "reason": "cargo_unavailable",
            "reasons": ["cargo_unavailable"],
        }
    with tempfile.TemporaryDirectory(prefix="ghoti_agent_os_guard_") as temp_dir:
        request_path = Path(temp_dir) / "request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        env = os.environ.copy()
        env.setdefault(
            "CARGO_TARGET_DIR",
            str(Path(tempfile.gettempdir()) / "ghoti_agent_os_guard_target"),
        )
        result = subprocess.run(
            [
                cargo,
                "run",
                "--quiet",
                "--manifest-path",
                str(RUST_MANIFEST),
                "--bin",
                "agent_os_guard",
                "--",
                "--request",
                str(request_path),
                "--json",
            ],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    if result.returncode != 0:
        return {
            "allow": False,
            "decision": "denied",
            "reason": "guard_invocation_failed",
            "reasons": ["guard_invocation_failed"],
            "stderr": result.stderr.strip(),
        }
    return json.loads(result.stdout)


def _plan_markdown(workflow: str, mode: str) -> str:
    return "\n".join(
        [
            f"# {workflow}",
            "",
            f"Mode: `{mode}`",
            "Status: suggestion-only; no live action was performed.",
            "",
            "## Purpose",
            WORKFLOWS[workflow],
            "",
            "## Suggested Steps",
            "1. Review the goal and source material.",
            "2. Confirm scope, evidence, and human approval boundaries.",
            "3. Produce a local draft or checklist.",
            "4. Validate the draft before any separately approved future action.",
            "",
            "## Blocked",
            "Browser control, computer-use, accounts, sending, posting, purchases, and command execution.",
            "",
        ]
    )


def _handoff_markdown(workflow: str, mode: str, paths: dict[str, str]) -> str:
    return "\n".join(
        [
            f"# Handoff: {workflow}",
            "",
            f"- Mode: `{mode}`",
            "- Worker executed: suggestion renderer only",
            "- Live execution: false",
            f"- Plan: `{paths['plan']}`",
            f"- Run record: `{paths['run']}`",
            "- Next action: human reviews the local plan.",
            "",
        ]
    )


def run_check() -> dict[str, Any]:
    decision = _invoke_guard(_guard_request("coding-task-plan", "simulation", None))
    return {
        "ok": bool(decision.get("allow")),
        "guard_ready": bool(decision.get("allow")),
        "workflows": sorted(WORKFLOWS),
        "modes_executed": sorted(EXECUTED_MODES),
        "approved_local_execution_enabled": False,
        "live_execution": False,
        "browser_enabled": False,
        "computer_use_enabled": False,
        "account_actions_enabled": False,
        "model_output_as_command": False,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "guard_decision": decision,
    }


def run_workflow(
    workflow: str,
    mode: str,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    approval_token: str | None = None,
    request_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if workflow not in WORKFLOWS:
        return {
            "ok": False,
            "worker_executed": False,
            "reasons": ["unknown_workflow"],
            "live_execution": False,
        }
    if mode not in {"simulation", "suggestion", "approved_local"}:
        return {
            "ok": False,
            "worker_executed": False,
            "reasons": ["unknown_mode"],
            "live_execution": False,
        }
    if not _output_root_allowed(output_root):
        return {
            "ok": False,
            "worker_executed": False,
            "suggestion_only": True,
            "live_execution": False,
            "reasons": ["output_root_not_allowed"],
        }

    guard_request = _guard_request(workflow, mode, approval_token)
    if request_overrides:
        guard_request.update(request_overrides)
    guard_decision = _invoke_guard(guard_request)
    if mode == "approved_local":
        return {
            "ok": False,
            "worker_executed": False,
            "suggestion_only": True,
            "live_execution": False,
            "reasons": ["approved_local_not_executed"],
            "guard_decision": guard_decision,
        }
    if not guard_decision.get("allow"):
        run_path = output_root / "runs" / f"{workflow}_run.json"
        run_path.parent.mkdir(parents=True, exist_ok=True)
        run_record = {
            "schema_version": "1.0",
            "workflow": workflow,
            "mode": mode,
            "status": "denied",
            "worker_executed": False,
            "suggestion_only": True,
            "live_execution": False,
            "model_output_as_command": False,
            "guard_decision": guard_decision,
            "artifacts": {"run": _declared_paths(workflow)["run"]},
        }
        _safe_write_text(
            run_path,
            json.dumps(run_record, indent=2, sort_keys=True) + "\n",
        )
        return {
            "ok": True,
            "status": "denied",
            "worker_executed": False,
            "suggestion_only": True,
            "live_execution": False,
            "reasons": list(guard_decision.get("reasons", ["guard_denied"])),
            "guard_decision": guard_decision,
        }

    paths = _declared_paths(workflow)
    local_paths = {
        "plan": output_root / "trials" / f"{workflow}.md",
        "run": output_root / "runs" / f"{workflow}_run.json",
        "handoff": output_root / "handoffs" / f"{workflow}_handoff.md",
    }
    for path in local_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    run_record = {
        "schema_version": "1.0",
        "workflow": workflow,
        "mode": mode,
        "worker_executed": True,
        "suggestion_only": True,
        "live_execution": False,
        "model_output_as_command": False,
        "guard_decision": guard_decision,
        "artifacts": paths,
    }
    _safe_write_text(local_paths["plan"], _plan_markdown(workflow, mode))
    _safe_write_text(
        local_paths["run"],
        json.dumps(run_record, indent=2, sort_keys=True) + "\n",
    )
    _safe_write_text(
        local_paths["handoff"],
        _handoff_markdown(workflow, mode, paths),
    )
    return {
        "ok": True,
        "worker_executed": True,
        "suggestion_only": True,
        "live_execution": False,
        "guard_decision": guard_decision,
        "artifacts": paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--workflow", choices=sorted(WORKFLOWS))
    parser.add_argument(
        "--mode",
        choices=["simulation", "suggestion", "approved_local"],
        default="suggestion",
    )
    parser.add_argument("--approval-token")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = (
        run_check()
        if args.check
        else run_workflow(
            args.workflow,
            args.mode,
            approval_token=args.approval_token,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
