#!/usr/bin/env python3
"""Sandbox-only computer-use action runner (N+6.13A).

Default mode is a **dry run**: it reports the action plan it would perform against
the local sandbox target and performs nothing (action_performed == False). No real
click, no real typing, no hotkeys, no desktop control, no live browser, no network,
no installs, no third-party code execution.

The optional --allow-sandbox-action mode does NOT control the real operating
system. With the standard library alone, real mouse/keyboard input cannot be
strictly confined to the generated local sandbox target (OS input would reach
whatever window is focused). So this mode keeps the action a pure in-memory
**simulation** against a model parsed from the local sandbox HTML, reports
action_performed == False with
sandbox_action_not_performed_reason == "strict confinement not yet guaranteed",
and records a clear next step for N+6.13B.

This runner never imports or calls pyautogui, pynput, selenium, playwright, a live
CDP browser, or a shell. It only reads local files and builds local JSON.

Usage:
    python 03_scripts/computer_use_sandbox/sandbox_action_runner.py \
        --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json
    python 03_scripts/computer_use_sandbox/sandbox_action_runner.py \
        --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json \
        --allow-sandbox-action --json
"""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import sandbox_action_planner as planner  # noqa: E402  (local sibling module)

MILESTONE = "N+6.13A"
TOOL = "sandbox_action_runner"
TARGET_HTML = planner.SANDBOX_DIR / "sandbox_target.html"
CONFINEMENT_REASON = "strict confinement not yet guaranteed"
NEXT_STEP_N6_13B = (
    "N+6.13B: introduce a strictly confined sandbox executor (for example a local "
    "renderer the harness fully owns) before any real sandbox-only action is "
    "performed; until then the harness stays dry-run and simulation only."
)


class _IdCollector(HTMLParser):
    """Collect element ids from the local sandbox HTML. Parses text; runs nothing."""

    def __init__(self):
        super().__init__()
        self.elements = {}

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if "id" in attr:
            self.elements[attr["id"]] = {"tag": tag, "value": "", "text": ""}


def parse_target_ids(html_path):
    collector = _IdCollector()
    try:
        collector.feed(Path(html_path).read_text(encoding="utf-8"))
    except OSError:
        return {}
    return collector.elements


def simulate(actions, expected_outcome, model):
    """Apply the plan to an in-memory model of the local sandbox target only.

    Touches no real window, pointer, or keyboard. It mirrors the sandbox target's
    declared wiring: a click on the button copies the note value into the status
    output element.
    """
    derived_from = expected_outcome.get("derived_from")
    output_id = expected_outcome.get("element_id")
    for act in actions:
        target = act.get("target_id")
        if act.get("action") == "type_text" and target in model:
            model[target]["value"] = act.get("value", "")
        elif act.get("action") == "click":
            if output_id in model and derived_from in model:
                model[output_id]["text"] = model[derived_from]["value"]
    final_state = {
        eid: {"value": data["value"], "text": data["text"]}
        for eid, data in model.items()
    }
    expected_text = expected_outcome.get("expected_text", "")
    satisfied = output_id in model and model[output_id]["text"] == expected_text
    return final_state, bool(satisfied)


def run(fixture, allow_sandbox_action=False):
    flags = planner.load_feature_flags()
    plan = planner.plan_payload(fixture, flags=flags)
    actions = plan["actions"]
    expected_outcome = plan["expected_outcome"]

    payload = {
        "ok": True,
        "milestone": MILESTONE,
        "tool": TOOL,
        "target": "sandbox_only",
        "requested_goal": plan["requested_goal"],
        "requires_human_approval": True,
        "dry_run": not allow_sandbox_action,
        "mode": "allow_sandbox_action" if allow_sandbox_action else "dry_run",
        "action_performed": False,
        "real_click_performed": False,
        "real_type_performed": False,
        "os_input_used": False,
        "would_perform": actions,
        "expected_outcome": expected_outcome,
        "blocked_actions": plan["blocked_actions"],
        "feature_flags": flags,
        "global_kill_switch_engaged": plan["global_kill_switch_engaged"],
        "attribution": plan["attribution"],
        "safety": plan["safety"],
    }

    if not allow_sandbox_action:
        payload["simulated_action_performed"] = False
        return payload

    # --allow-sandbox-action: real OS control cannot be strictly confined with the
    # standard library, so the action stays a pure in-memory simulation.
    model = parse_target_ids(TARGET_HTML)
    final_state, satisfied = simulate(actions, expected_outcome, model)
    payload["simulated_action_performed"] = True
    payload["sandbox_action_not_performed_reason"] = CONFINEMENT_REASON
    payload["strict_sandbox_confinement_guaranteed"] = bool(
        flags.get("strict_sandbox_confinement_guaranteed", False))
    payload["simulation"] = {
        "elements_parsed_from_target": sorted(model.keys()),
        "final_state": final_state,
        "goal_satisfied_in_simulation": satisfied,
    }
    payload["next_step_n6_13b"] = NEXT_STEP_N6_13B
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sandbox-only computer-use action runner (dry-run by default).")
    parser.add_argument("--fixture", default=str(planner.DEFAULT_FIXTURE),
                        help="path to a local sandbox observation fixture JSON")
    parser.add_argument("--allow-sandbox-action", action="store_true",
                        help="run the plan as an in-memory sandbox simulation only")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        fixture = planner.load_json(Path(args.fixture))
    except (OSError, ValueError) as exc:
        message = {"ok": False, "tool": TOOL, "error": str(exc), "fixture": args.fixture}
        print(json.dumps(message, indent=2) if args.json else f"error: {exc}")
        return 1

    payload = run(fixture, allow_sandbox_action=args.allow_sandbox_action)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
