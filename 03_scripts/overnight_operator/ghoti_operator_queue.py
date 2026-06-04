#!/usr/bin/env python3
"""Ghoti Operator Queue (N+6.19A).

Dispatch local overnight-operator tasks. This is the conductor of the first useful
automation layer: it turns a task JSON into one of a small set of safe local actions,
and it refuses every unsafe task type by name.

Supported task types:
  * build_prompt_packet     - render a copy/paste prompt packet (preview; --execute
                              writes it to the outbox).
  * hermes_status_prompt    - render a status-only Hermes prompt packet.
  * summarize_inbox_output  - summarize pasted outputs collected in the inbox into a
                              handoff/status summary (--execute writes the summary).
  * repo_execution_sandbox  - PREVIEW the allowlisted repo-sandbox plan (the actual
                              clone/scan/run is the explicit sandbox CLI, never here).

Blocked task types are refused by name (no app paste, no auto-submit, no agent
launch, no live browser, no account login, no telegram/email/whatsapp send, no MCP
write, no unbounded shell, no docker, no push/merge to main).

Safety posture: standard library only, no network, no shell, no secrets. It writes
only inside the local overnight-operator folders, and only when --execute is passed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

MILESTONE = "N+6.19A"

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
OP_DIR = REPO_ROOT / "14_context" / "overnight_operator"
OUTBOX_DIR = OP_DIR / "outbox"
INBOX_DIR = OP_DIR / "inbox"
ARCHIVE_DIR = OP_DIR / "archive"
ALLOWED_REPOS = OP_DIR / "allowlists" / "allowed_repos_n6_19a.json"

SUPPORTED_TASK_TYPES = {
    "build_prompt_packet",
    "hermes_status_prompt",
    "summarize_inbox_output",
    "repo_execution_sandbox",
}

BLOCKED_TASK_TYPES = {
    "live_app_paste",
    "auto_submit",
    "launch_claude",
    "launch_codex",
    "live_browser",
    "account_login",
    "telegram_send",
    "email_send",
    "whatsapp_send",
    "mcp_write",
    "shell_exec_unbounded",
    "docker_run",
    "git_push_main",
    "git_merge_main",
}

SAFETY = {
    "local_only": True,
    "network_used": False,
    "shell_used": False,
    "reads_secret_values": False,
    "clipboard_paste": False,
    "auto_submit": False,
    "app_window_control": False,
    "os_click_type": False,
    "live_agent_launch": False,
    "writes_only_inside_operator_folders": True,
}


def _load_builder():
    path = SCRIPT_DIR / "ghoti_prompt_packet_builder.py"
    spec = importlib.util.spec_from_file_location("ghoti_prompt_packet_builder", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _inbox_items():
    if not INBOX_DIR.is_dir():
        return []
    items = []
    for path in sorted(INBOX_DIR.glob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        first = next((line.strip() for line in text.splitlines() if line.strip()), "")
        items.append({"file": path.name, "chars": len(text), "first_line": first[:160]})
    return items


def _render_inbox_summary(items):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines = [
        "# Overnight operator - inbox summary",
        "",
        "Generated: {0}".format(stamp),
        "Inbox items: {0}".format(len(items)),
        "",
    ]
    if not items:
        lines.append("_The inbox is empty. Paste agent outputs as files into "
                     "14_context/overnight_operator/inbox/ to summarize them._")
    else:
        for item in items:
            lines.append("- `{0}` ({1} chars): {2}".format(
                item["file"], item["chars"], item["first_line"] or "(no first line)"))
    lines.append("")
    return "\n".join(lines)


def _summarize_inbox(execute):
    items = _inbox_items()
    summary_md = _render_inbox_summary(items)
    written = None
    if execute and items:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        path = ARCHIVE_DIR / "inbox_summary_{0}.md".format(stamp)
        path.write_text(summary_md, encoding="utf-8")
        written = path.relative_to(REPO_ROOT).as_posix()
    return {
        "inbox_count": len(items),
        "items": items,
        "summary_markdown": summary_md,
        "written": bool(written),
        "summary_path": written,
    }


def _repo_execution_plan(task):
    allow = _read_json(ALLOWED_REPOS) or {}
    repos = allow.get("repos", [])
    name = task.get("repo")
    entry = next((r for r in repos if r.get("name") == name or r.get("slug") == name), None)
    if not entry:
        return {"ok": False, "reason": "repo not allowlisted: {0}".format(name)}
    allowed = entry.get("allowed_actions", [])
    requested = task.get("actions", [])
    return {
        "ok": True,
        "repo": entry.get("name"),
        "slug": entry.get("slug"),
        "source_url": entry.get("source_url"),
        "source_url_required": bool(entry.get("source_url_required")),
        "allowed_actions": allowed,
        "requested_actions": requested,
        "rejected_actions": [a for a in requested if a not in allowed and a != "run_allowlisted"],
        "sandbox_clone_path": entry.get("sandbox_clone_path"),
        "runtime_execution_allowed": bool(entry.get("runtime_execution_allowed")),
        "run_with": "03_scripts/overnight_operator/ghoti_repo_execution_sandbox.py",
        "note": "Preview only. Run the sandbox CLI explicitly to clone/static-scan/"
                "run-allowlisted; the queue never clones or executes a repo itself.",
    }


def dispatch(task, execute=False):
    if not isinstance(task, dict):
        return {"ok": False, "milestone": MILESTONE, "error": "task is not a JSON object",
                "safety": dict(SAFETY)}
    task_type = task.get("task_type")
    base = {"ok": True, "milestone": MILESTONE, "tool": "ghoti_operator_queue",
            "task_type": task_type, "executed_writes": bool(execute),
            "safety": dict(SAFETY)}

    if task_type in BLOCKED_TASK_TYPES:
        base.update({
            "ok": False, "blocked": True,
            "reason": "task type '{0}' is blocked in this milestone".format(task_type),
            "next_milestone": "N+6.20A approved-window copy/paste harness",
        })
        return base

    if task_type not in SUPPORTED_TASK_TYPES:
        base.update({"ok": False, "blocked": True,
                     "reason": "unsupported task type: {0}".format(task_type)})
        return base

    if task_type in ("build_prompt_packet", "hermes_status_prompt"):
        builder = _load_builder()
        result = builder.build_result(task, write_outbox=execute)
        base.update({"dispatched": "prompt_packet", "result": result,
                     "ok": result["ok"]})
        return base

    if task_type == "summarize_inbox_output":
        base.update({"dispatched": "inbox_summary", "result": _summarize_inbox(execute)})
        return base

    # repo_execution_sandbox
    plan = _repo_execution_plan(task)
    base.update({"dispatched": "repo_execution_preview", "result": plan, "ok": plan["ok"]})
    return base


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Operator Queue (N+6.19A) - dispatch safe local tasks."
    )
    parser.add_argument("--task", help="Path to a local task JSON file.")
    parser.add_argument("--scan-inbox", action="store_true",
                        help="List and summarize the local inbox (read-only).")
    parser.add_argument("--execute", action="store_true",
                        help="Allow side-effecting writes inside the operator folders "
                             "(outbox packet / inbox summary). Off by default.")
    parser.add_argument("--json", action="store_true", help="Emit JSON (default).")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.scan_inbox:
        print(json.dumps({
            "ok": True, "milestone": MILESTONE, "tool": "ghoti_operator_queue",
            "action": "scan_inbox", "result": _summarize_inbox(execute=False),
            "safety": dict(SAFETY),
        }, indent=2))
        return 0
    if not args.task:
        print(json.dumps({"ok": False, "milestone": MILESTONE,
                          "error": "provide --task <path> or --scan-inbox",
                          "supported_task_types": sorted(SUPPORTED_TASK_TYPES),
                          "blocked_task_types": sorted(BLOCKED_TASK_TYPES),
                          "safety": dict(SAFETY)}, indent=2))
        return 1
    task = _read_json(args.task)
    if task is None:
        print(json.dumps({"ok": False, "milestone": MILESTONE,
                          "error": "could not read task JSON", "safety": dict(SAFETY)}, indent=2))
        return 1
    result = dispatch(task, execute=args.execute)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
