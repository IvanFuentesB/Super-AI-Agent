#!/usr/bin/env python3
"""Local-only safe computer-use observation harness.

This script reads a repo-local fixture, summarizes what is visible in that
fixture, and proposes a human-approved plan. It never opens a browser, never
uses the network, and never clicks or types.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TOP_LEVEL = {
    "scenario_id": str,
    "scenario_goal": str,
    "observation_source": str,
    "local_fixture_only": bool,
    "products": list,
}

REQUIRED_PRODUCT_KEYS = {
    "name": str,
    "category": str,
    "price_placeholder": str,
    "performance_notes": str,
    "display_notes": str,
    "ports_notes": str,
    "storage_notes": str,
}

FORBIDDEN_ACTIONS = [
    "browser_launch",
    "open_chrome",
    "visit_live_site",
    "click",
    "type",
    "login",
    "account_action",
    "cart",
    "purchase",
    "payment",
    "captcha_bypass",
    "cookie_bypass",
    "live_scraping",
    "network_request",
]

ALLOWED_ACTIONS_NOW = [
    "summarize_fixture",
    "propose_plan",
]


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError as exc:
        raise ValueError(f"fixture not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"fixture is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("fixture root must be an object")
    return data


def validate_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected_type in REQUIRED_TOP_LEVEL.items():
        value = data.get(key)
        if not isinstance(value, expected_type):
            errors.append(f"{key} must be {expected_type.__name__}")
    if data.get("local_fixture_only") is not True:
        errors.append("local_fixture_only must be true")

    products = data.get("products")
    if isinstance(products, list):
        if not products:
            errors.append("products must not be empty")
        for index, product in enumerate(products):
            if not isinstance(product, dict):
                errors.append(f"products[{index}] must be an object")
                continue
            for key, expected_type in REQUIRED_PRODUCT_KEYS.items():
                if not isinstance(product.get(key), expected_type):
                    errors.append(f"products[{index}].{key} must be {expected_type.__name__}")

    optional_lists = ["comparison_axes", "human_questions"]
    for key in optional_lists:
        if key in data and not all(isinstance(item, str) for item in data.get(key, [])):
            errors.append(f"{key} must be a list of strings")
    return errors


def build_observation(data: dict[str, Any], fixture_path: Path) -> dict[str, Any]:
    products = data["products"]
    product_names = [product["name"] for product in products]
    categories = sorted({product["category"] for product in products})
    comparison_axes = data.get(
        "comparison_axes",
        ["performance", "portability", "ports", "storage", "price_placeholder"],
    )
    human_questions = data.get(
        "human_questions",
        [
            "Which workload matters most?",
            "Is portability more important than desktop value?",
            "What budget range should constrain the final recommendation?",
        ],
    )

    proposed_next_steps = [
        "Review the local fixture summary.",
        "Choose the comparison axes that matter for the human decision.",
        "Approve or reject any future live-browser observation separately.",
        "If approved in a later milestone, collect visible page facts without login, cart, purchase, or bypass behavior.",
    ]

    return {
        "ok": True,
        "scenario_id": data["scenario_id"],
        "fixture_path": repo_relative(fixture_path),
        "observation_summary": (
            f"Local fixture compares {', '.join(product_names)} for "
            f"{data['scenario_goal']}. No live site was opened."
        ),
        "detected_entities": {
            "products": product_names,
            "categories": categories,
            "comparison_axes": comparison_axes,
            "human_questions": human_questions,
        },
        "proposed_next_steps": proposed_next_steps,
        "required_human_approval": True,
        "requires_human_approval": True,
        "allowed_actions_now": ALLOWED_ACTIONS_NOW,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "safety_verdict": "OBSERVATION_ONLY_REQUIRES_HUMAN_APPROVAL",
        "safety_flags": {
            "local_only": True,
            "observation_only": True,
            "browser_opened": False,
            "live_browser_executed": False,
            "chrome_opened": False,
            "live_site_visited": False,
            "clicked_or_typed": False,
            "click_enabled": False,
            "type_enabled": False,
            "account_action_enabled": False,
            "login_enabled": False,
            "cart_enabled": False,
            "purchase_enabled": False,
            "captcha_bypass_enabled": False,
            "cookie_bypass_enabled": False,
            "live_network_used": False,
            "live_api_used": False,
            "third_party_tools_executed": False,
            "external_telemetry_enabled": False,
        },
        "future_run_note": (
            "Any real browser/computer-use run must be a separately audited, "
            "human-approved milestone."
        ),
    }


def run(fixture_path: Path) -> dict[str, Any]:
    data = load_fixture(fixture_path)
    errors = validate_fixture(data)
    if errors:
        raise ValueError("; ".join(errors))
    return build_observation(data, fixture_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Path to a repo-local observation fixture JSON file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = run(Path(args.fixture))
    except ValueError as exc:
        error = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(error, indent=2, sort_keys=True))
        else:
            print(error["error"], file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["observation_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
