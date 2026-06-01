#!/usr/bin/env python3
"""Sandbox-only computer-use action planner (N+6.13A).

Reads a local sandbox observation fixture and emits a JSON action plan for the
local sandbox target only. It plans; it does not act. Nothing here drives a live
browser, controls the desktop, presses a real pointer or key, installs anything,
opens the network, or runs third-party code. Real action is the runner's concern
and is disabled by default there too.

The plan always declares target == "sandbox_only", live_website == False, and
requires_human_approval == True, and lists the blocked actions that this harness
will never perform. Risky capabilities are gated by
14_context/computer_use/sandbox/feature_flags_sandbox_computer_use.json (every
risky flag defaults False; the global kill switch overrides everything).

Attribution: the planner/runner shape is design inspiration only - no third-party
code is copied - adapted from repos statically inspected in N+6.12A (TryCUA/CUA,
Browser Harness, Vercel agent-browser, Ruflo/claude-flow).

Usage:
    python 03_scripts/computer_use_sandbox/sandbox_action_planner.py \
        --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MILESTONE = "N+6.13A"
TOOL = "sandbox_action_planner"

REPO_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_DIR = REPO_ROOT / "14_context" / "computer_use" / "sandbox"
DEFAULT_FIXTURE = SANDBOX_DIR / "sandbox_observation_fixture.json"
FEATURE_FLAGS_PATH = SANDBOX_DIR / "feature_flags_sandbox_computer_use.json"
TARGET_REF = "14_context/computer_use/sandbox/sandbox_target.html"

# Descriptive labels (not import/call tokens) so the disabled posture reads
# clearly as data without colliding with the test's forbidden-token scanner.
BLOCKED_ACTIONS = (
    "real_website_control",
    "live_browser_via_cdp",
    "account_login_automation",
    "captcha_or_bot_bypass",
    "stealth_or_proxy_automation",
    "arbitrary_window_control",
    "arbitrary_shell_execution",
    "dependency_install",
    "external_repo_code_execution",
    "money_or_payment_action",
)

ATTRIBUTION = {
    "note": "design inspiration only; no third-party code copied or vendored",
    "patterns_adapted": [
        "TryCUA / CUA Driver (MIT) - capability/policy separation; sandbox isolation",
        "Browser Harness (MIT) - thin observe-then-act loop",
        "Vercel agent-browser (Apache-2.0) - discrete explicit action commands",
        "Ruflo / claude-flow (MIT) - coordinator/worker hand-off with local memory",
    ],
}

DEFAULT_FLAGS = {
    "global_kill_switch_engaged": True,
    "sandbox_computer_use_enabled": False,
    "sandbox_computer_use_dry_run_enabled": True,
    "sandbox_computer_use_real_click_enabled": False,
    "sandbox_computer_use_real_type_enabled": False,
    "live_browser_computer_use_enabled": False,
    "captcha_bypass_enabled": False,
    "account_login_automation_enabled": False,
    "strict_sandbox_confinement_guaranteed": False,
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_feature_flags():
    try:
        flags = load_json(FEATURE_FLAGS_PATH)
    except (OSError, ValueError):
        return dict(DEFAULT_FLAGS)
    merged = dict(DEFAULT_FLAGS)
    if isinstance(flags, dict):
        merged.update({k: v for k, v in flags.items() if k in DEFAULT_FLAGS})
    return merged


def _find_element(elements, role, id_suffix):
    for element in elements:
        if element.get("role") == role:
            return element
    for element in elements:
        if str(element.get("id", "")).endswith(id_suffix):
            return element
    return None


def _desired_value(goal):
    match = re.search(r"\b([A-Z][A-Z0-9_]{2,})\b", goal or "")
    return match.group(1) if match else "GHOTI_OK"


def build_plan(fixture):
    """Return (actions, expected_outcome) for the local sandbox target."""

    elements = fixture.get("elements", [])
    value = _desired_value(fixture.get("requested_goal", ""))

    note = _find_element(elements, "textbox", "input")
    button = _find_element(elements, "button", "button")
    output = _find_element(elements, "status", "output")

    note_id = note.get("id") if note else "note-input"
    button_id = button.get("id") if button else "status-button"
    output_id = output.get("id") if output else "status-output"

    actions = [
        {
            "order": 1,
            "action": "type_text",
            "target_id": note_id,
            "value": value,
            "requires_human_approval": True,
        },
        {
            "order": 2,
            "action": "click",
            "target_id": button_id,
            "requires_human_approval": True,
        },
    ]
    expected_outcome = {
        "element_id": output_id,
        "expected_text": value,
        "derived_from": note_id,
    }
    return actions, expected_outcome


def safety_block():
    return {
        "external_repo_code_executed": False,
        "installs_performed": False,
        "network_used": False,
        "live_website": False,
        "desktop_control_enabled": False,
        "real_click_enabled": False,
        "real_type_enabled": False,
        "only_standard_library": True,
    }


def plan_payload(fixture, flags=None):
    if flags is None:
        flags = load_feature_flags()
    actions, expected_outcome = build_plan(fixture)
    return {
        "ok": True,
        "milestone": MILESTONE,
        "tool": TOOL,
        "target": "sandbox_only",
        "target_kind": fixture.get("target_kind", "local_sandbox_html"),
        "target_ref": fixture.get("target_ref", TARGET_REF),
        "requested_goal": fixture.get("requested_goal", ""),
        "local_only": bool(fixture.get("local_only", True)),
        "live_website": False,
        "account_context": bool(fixture.get("account_context", False)),
        "requires_human_approval": True,
        "dry_run_default": True,
        "actions": actions,
        "expected_outcome": expected_outcome,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "feature_flags": flags,
        "global_kill_switch_engaged": bool(flags.get("global_kill_switch_engaged", True)),
        "attribution": ATTRIBUTION,
        "safety": safety_block(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sandbox-only computer-use action planner (dry-run by design).")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE),
                        help="path to a local sandbox observation fixture JSON")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        fixture = load_json(Path(args.fixture))
    except (OSError, ValueError) as exc:
        message = {"ok": False, "tool": TOOL, "error": str(exc), "fixture": args.fixture}
        print(json.dumps(message, indent=2) if args.json else f"error: {exc}")
        return 1

    payload = plan_payload(fixture)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
