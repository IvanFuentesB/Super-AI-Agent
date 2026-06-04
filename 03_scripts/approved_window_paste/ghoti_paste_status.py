#!/usr/bin/env python3
"""Ghoti Approved-Window Paste status (N+6.20A).

A local, read-only status for the approved-window paste harness: which tools and
allowlists exist, whether the risky feature flags are all off, and the safe posture.
Standard library only. No network, no subprocess, no shell, no secrets, no writes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MILESTONE = "N+6.20A"

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PASTE_DIR = REPO_ROOT / "14_context" / "approved_window_paste"

DETECTOR = SCRIPT_DIR / "ghoti_approved_window_detector.ps1"
PASTE = SCRIPT_DIR / "ghoti_approved_clipboard_paste.ps1"
CHECK = SCRIPT_DIR / "check_approved_window_paste.ps1"
STATUS_TOOL = SCRIPT_DIR / "ghoti_paste_status.py"
SUMMARY_TOOL = SCRIPT_DIR / "write_manual_output_summary.py"
ALLOWLIST = PASTE_DIR / "approved_windows.example.json"
OUTBOX = REPO_ROOT / "14_context" / "overnight_operator" / "outbox"
MANUAL_DROP = PASTE_DIR / "manual_output_drop"
FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

RISKY_FLAGS = [
    "approved_window_paste_enabled",
    "clipboard_paste_enabled",
    "auto_submit_enabled",
    "approved_window_detection_enabled",
    "manual_output_drop_enabled",
    "unattended_live_agent_loop_enabled",
]

SAFETY = {
    "local_only": True,
    "clipboard_copy_on_explicit_command_only": True,
    "live_paste_execution_enabled": False,
    "presses_enter": False,
    "submits": False,
    "clicks_coordinates": False,
    "controls_chat_or_browser_apps": False,
    "auto_submit": False,
    "reads_secret_values": False,
    "rejects_secret_patterns_in_input": True,
    "input_must_be_under_outbox": True,
}


def _flags():
    try:
        return json.loads(FLAGS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def build_status():
    flags = _flags()
    enabled = sorted(key for key, value in flags.items() if value is True)
    risky = {name: bool(flags.get(name, False)) for name in RISKY_FLAGS}
    return {
        "ok": True,
        "milestone": MILESTONE,
        "tool": "ghoti_paste_status",
        "detector_exists": DETECTOR.is_file(),
        "paste_wrapper_exists": PASTE.is_file(),
        "check_exists": CHECK.is_file(),
        "status_tool_exists": STATUS_TOOL.is_file(),
        "manual_output_summary_exists": SUMMARY_TOOL.is_file(),
        "approved_windows_allowlist_present": ALLOWLIST.is_file(),
        "outbox_present": OUTBOX.is_dir(),
        "manual_output_drop_present": MANUAL_DROP.is_dir(),
        "approved_window_paste_enabled": bool(flags.get("approved_window_paste_enabled", False)),
        "clipboard_paste_enabled": bool(flags.get("clipboard_paste_enabled", False)),
        "auto_submit_enabled": bool(flags.get("auto_submit_enabled", False)),
        "unattended_live_agent_loop_enabled": bool(flags.get("unattended_live_agent_loop_enabled", False)),
        "risky_flags": risky,
        "risky_flags_default_false": not any(risky.values()),
        "only_status_commands_flag_enabled": enabled == ["telegram_status_commands_enabled"],
        "no_secrets": True,
        "safety": dict(SAFETY),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ghoti Approved-Window Paste status (N+6.20A) - local, read-only."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON (default).")
    parser.parse_args(argv if argv is not None else sys.argv[1:])
    print(json.dumps(build_status(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
