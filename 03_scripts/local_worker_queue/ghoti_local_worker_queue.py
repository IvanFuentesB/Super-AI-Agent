#!/usr/bin/env python3
"""Ghoti Local Worker Queue (N+6.15A).

Process a single local queue task described by a JSON file. The queue only ever
performs safe, local, read-only work and refuses everything else by default.

Supported task types (local, read-only):
  * status_summary             - build the local status packet (status brain)
  * computer_use_sandbox_status - report confined-sandbox readiness (dry-run only)
  * repo_intake_summary        - summarize statically inspected candidate repos

Blocked task types (default-deny; the queue never performs these):
  launch_claude, launch_codex, browser_live, computer_use_live, telegram_send,
  email_send, whatsapp_send, mcp_write, shell_exec, install_repo, docker_run.

Anything not explicitly supported is blocked. There is no live autonomy here: no
agent launch, no live browser, no OS-level input, no Telegram/MCP/email/WhatsApp,
no install, no Docker, no external API, and never a shell string (argument lists
only). The status brain it calls is local and offline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ghoti_status_brain.py lives next to this script; make it importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghoti_status_brain  # noqa: E402

MILESTONE = "N+6.15A"

SUPPORTED_TASK_TYPES = (
    "status_summary",
    "computer_use_sandbox_status",
    "repo_intake_summary",
)

BLOCKED_TASK_TYPES = (
    "launch_claude",
    "launch_codex",
    "browser_live",
    "computer_use_live",
    "telegram_send",
    "email_send",
    "whatsapp_send",
    "mcp_write",
    "shell_exec",
    "install_repo",
    "docker_run",
)

DEFAULT_INTAKE_CANDIDATES = list(ghoti_status_brain.INTAKE_CANDIDATES.keys())

SAFETY = {
    "live_browser_used": False,
    "os_input_used": False,
    "external_api_used": False,
    "telegram_control_used": False,
    "mcp_used": False,
    "auto_send_used": False,
    "agent_launch_used": False,
    "install_used": False,
    "docker_used": False,
    "shell_true_used": False,
    "local_only": True,
}


def _base_result(task_type, task_path):
    return {
        "ok": True,
        "milestone": MILESTONE,
        "task_type": task_type,
        "task_path": task_path,
        "supported": False,
        "blocked": False,
        "reason": None,
        "result": None,
        "safety": dict(SAFETY),
    }


def _handle_status_summary(task):
    packet = ghoti_status_brain.build_status_packet(
        include_computer_use_sandbox=bool(task.get("include_computer_use_sandbox", False)),
        use_gemma_if_available=bool(task.get("use_gemma_if_available", False)),
        write_handoff=bool(task.get("write_handoff", False)),
    )
    return packet


def _handle_computer_use_sandbox_status(task):
    # Dry-run only, always. The status brain never passes any allow flag.
    packet = ghoti_status_brain.build_status_packet(include_computer_use_sandbox=True)
    return {
        "dry_run_only": True,
        "never_allow_live": True,
        "computer_use_sandbox_status": packet["computer_use_sandbox_status"],
    }


def _handle_repo_intake_summary(task):
    candidates = task.get("include_candidates") or DEFAULT_INTAKE_CANDIDATES
    return {
        "candidates": ghoti_status_brain.repo_intake_candidate_status(candidates),
        "tool_intake_summary": ghoti_status_brain._tool_intake_summary(),
    }


_DISPATCH = {
    "status_summary": _handle_status_summary,
    "computer_use_sandbox_status": _handle_computer_use_sandbox_status,
    "repo_intake_summary": _handle_repo_intake_summary,
}


def process_task(task_path):
    """Process one queue task file and return the result dict."""
    path = Path(task_path)
    result = _base_result(None, str(task_path))

    if not path.is_file():
        result["ok"] = False
        result["reason"] = f"task file not found: {task_path}"
        return result

    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        result["ok"] = False
        result["reason"] = f"invalid task JSON: {exc}"
        return result

    if not isinstance(task, dict):
        result["ok"] = False
        result["reason"] = "task file must contain a JSON object"
        return result

    task_type = task.get("task_type")
    result["task_type"] = task_type

    if task_type in BLOCKED_TASK_TYPES:
        result["blocked"] = True
        result["reason"] = (
            f"task_type {task_type!r} is blocked by local worker queue policy "
            "(default-deny: no live autonomy, no launch, no send, no install, "
            "no docker, no shell exec)"
        )
        return result

    handler = _DISPATCH.get(task_type)
    if handler is None:
        result["blocked"] = True
        result["reason"] = (
            f"task_type {task_type!r} is not supported; blocked by default-deny"
        )
        return result

    result["supported"] = True
    result["result"] = handler(task)
    return result


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Local Worker Queue (N+6.15A) - process one local task."
    )
    parser.add_argument("--task", required=True,
                        help="Path to a queue task JSON file.")
    parser.add_argument("--json", action="store_true",
                        help="Emit the task result as JSON.")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    result = process_task(args.task)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        state = "blocked" if result["blocked"] else ("ok" if result["ok"] else "error")
        print(f"[{state}] task_type={result['task_type']} - {result['reason'] or 'done'}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
