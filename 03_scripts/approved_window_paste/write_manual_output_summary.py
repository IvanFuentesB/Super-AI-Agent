#!/usr/bin/env python3
"""Summarize manually dropped agent outputs (N+6.20A).

After you copy a prompt packet to an agent and it answers, save its reply into
14_context/approved_window_paste/manual_output_drop/. This tool reads those dropped
files read-only and produces a Markdown summary (a lightweight handoff). With --write
it saves the summary into the (git-ignored) drop folder.

Standard library only. No network, no subprocess, no shell, no secrets. It runs no
commands and reads no secret values.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

MILESTONE = "N+6.20A"

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUAL_DROP = REPO_ROOT / "14_context" / "approved_window_paste" / "manual_output_drop"

SAFETY = {
    "local_only": True,
    "read_only_inputs": True,
    "runs_commands": False,
    "reads_secret_values": False,
    "sends_anything": False,
}


def _items():
    items = []
    if MANUAL_DROP.is_dir():
        for path in sorted(MANUAL_DROP.glob("*")):
            if not path.is_file() or path.name == "README.md" or path.name.startswith("_summary_"):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            first = next((line.strip() for line in text.splitlines() if line.strip()), "")
            items.append({"file": path.name, "chars": len(text), "first_line": first[:160]})
    return items


def _render(items):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines = [
        "# Manual output summary ({0})".format(MILESTONE),
        "",
        "Generated: {0}".format(stamp),
        "Dropped outputs: {0}".format(len(items)),
        "",
    ]
    if not items:
        lines.append("_No dropped outputs. Save agent replies into "
                     "14_context/approved_window_paste/manual_output_drop/._")
    else:
        for item in items:
            lines.append("- `{0}` ({1} chars): {2}".format(
                item["file"], item["chars"], item["first_line"] or "(no first line)"))
    lines.append("")
    return "\n".join(lines)


def build_result(write=False):
    items = _items()
    summary = _render(items)
    written = None
    if write and items:
        try:
            MANUAL_DROP.mkdir(parents=True, exist_ok=True)
            stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            path = MANUAL_DROP / "_summary_{0}.md".format(stamp)
            path.write_text(summary, encoding="utf-8")
            written = path.relative_to(REPO_ROOT).as_posix()
        except OSError:
            written = None
    return {
        "ok": True,
        "milestone": MILESTONE,
        "tool": "write_manual_output_summary",
        "dropped_count": len(items),
        "items": items,
        "summary_markdown": summary,
        "written": bool(written),
        "summary_path": written,
        "safety": dict(SAFETY),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarize manually dropped agent outputs (N+6.20A)."
    )
    parser.add_argument("--write", action="store_true",
                        help="Write the summary into the git-ignored manual_output_drop folder.")
    parser.add_argument("--json", action="store_true", help="Emit JSON (default).")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    print(json.dumps(build_result(write=args.write), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
