#!/usr/bin/env python3
"""Ghoti Prompt Packet Builder (N+6.19A).

Turn a local task JSON into a copy/paste-ready prompt packet for Claude, Codex, or
WSL Hermes. This is the first half of the overnight operator loop: generate a clear,
self-contained packet the operator can copy to the clipboard and paste into the
target agent themselves.

Safety posture (all enforced by construction):

  * Python standard library only. No third-party packages, no installs.
  * No network. No subprocess. No shell. No secrets are read or written.
  * It only reads a local task JSON and writes a Markdown packet to the local outbox
    when --write-outbox is passed; otherwise it writes nothing.
  * The packet always carries the no-AI-attribution rule and the feature-branch-only
    rule, so any downstream agent keeps the repo's commit policy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

MILESTONE = "N+6.19A"

# 03_scripts/overnight_operator/ghoti_prompt_packet_builder.py -> repo root is two up.
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTBOX_DIR = REPO_ROOT / "14_context" / "overnight_operator" / "outbox"

VALID_TARGETS = {"claude", "codex", "hermes", "ghoti_local"}

SAFETY = {
    "local_only": True,
    "network_used": False,
    "subprocess_used": False,
    "reads_secret_values": False,
    "auto_submit": False,
    "clipboard_paste": False,
}


def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return slug or "task"


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def build_packet_markdown(task):
    """Render the task dict as a copy/paste-ready prompt packet (Markdown)."""
    target = str(task.get("target_agent", "claude"))
    title = task.get("title") or task.get("milestone") or "task"
    lines = [
        "# Ghoti prompt packet - {0}".format(title),
        "",
        "- Target agent: **{0}**".format(target),
        "- Milestone: {0}".format(task.get("milestone", "(unspecified)")),
        "- Branch: `{0}`".format(task.get("branch", "(none)")),
        "- Worktree: `{0}`".format(task.get("worktree", "(none)")),
        "",
        "## Mission",
        "",
        str(task.get("mission", "(no mission provided)")),
        "",
        "## Files allowed",
        "",
    ]
    lines += ["- `{0}`".format(item) for item in _as_list(task.get("files_allowed"))] or ["- (none specified)"]
    lines += [
        "",
        "## Files forbidden",
        "",
    ]
    lines += ["- {0}".format(item) for item in _as_list(task.get("files_forbidden"))] or ["- (none specified)"]
    lines += [
        "",
        "## Safety rules",
        "",
    ]
    lines += ["- {0}".format(item) for item in _as_list(task.get("safety_rules"))] or ["- (none specified)"]
    lines += [
        "",
        "## Expected output",
        "",
        str(task.get("expected_output", "(unspecified)")),
        "",
        "## Commit and attribution rule",
        "",
        "- Commits must contain no AI attribution of any kind: no AI co-author "
        "trailer, and no mention of AI assistants or AI tools in the commit message.",
        "- Keep the human operator identity that is already configured for git.",
        "- Push the feature branch only; never push or merge main.",
        "",
        "_Generated locally by ghoti_prompt_packet_builder.py ({0}). No network, no "
        "secrets, no auto-submit. Copy/paste is manual and operator-approved._".format(MILESTONE),
        "",
    ]
    return "\n".join(lines)


def _validate_task(task):
    problems = []
    if not isinstance(task, dict):
        return ["task is not a JSON object"]
    target = task.get("target_agent")
    if target is not None and str(target) not in VALID_TARGETS:
        problems.append("unknown target_agent: {0}".format(target))
    if not task.get("mission"):
        problems.append("missing mission")
    return problems


def _write_outbox(task, markdown):
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    target = _slugify(task.get("target_agent", "agent"))
    title = _slugify(task.get("title") or task.get("milestone") or "task")
    name = "packet_{0}_{1}_{2}.md".format(target, title, stamp)
    path = OUTBOX_DIR / name
    path.write_text(markdown, encoding="utf-8")
    latest = OUTBOX_DIR / "latest_prompt_packet.md"
    latest.write_text(markdown, encoding="utf-8")
    return path.relative_to(REPO_ROOT).as_posix()


def build_result(task, write_outbox=False):
    """Build the JSON result for a task dict. Writes to the outbox only if asked."""
    problems = _validate_task(task)
    markdown = build_packet_markdown(task) if not problems else ""
    outbox_path = None
    if write_outbox and not problems:
        outbox_path = _write_outbox(task, markdown)
    return {
        "ok": not problems,
        "milestone": MILESTONE,
        "tool": "ghoti_prompt_packet_builder",
        "task_type": task.get("task_type") if isinstance(task, dict) else None,
        "target_agent": task.get("target_agent") if isinstance(task, dict) else None,
        "problems": problems,
        "packet_markdown": markdown,
        "packet_chars": len(markdown),
        "written": bool(outbox_path),
        "outbox_path": outbox_path,
        "safety": dict(SAFETY),
    }


def load_task(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Prompt Packet Builder (N+6.19A) - local, no network."
    )
    parser.add_argument("--task", required=True, help="Path to a local task JSON file.")
    parser.add_argument("--write-outbox", action="store_true",
                        help="Also write the packet Markdown into the local outbox.")
    parser.add_argument("--json", action="store_true",
                        help="Emit the result as JSON (default).")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    try:
        task = load_task(args.task)
    except (OSError, ValueError) as exc:
        print(json.dumps({
            "ok": False,
            "milestone": MILESTONE,
            "tool": "ghoti_prompt_packet_builder",
            "error": "could not read task JSON: {0}".format(exc.__class__.__name__),
            "safety": dict(SAFETY),
        }, indent=2))
        return 1
    result = build_result(task, write_outbox=args.write_outbox)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
