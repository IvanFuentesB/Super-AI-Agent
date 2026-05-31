#!/usr/bin/env python3
"""N+6.7A - Tool/Repo Intake Static Registry (read-only planning CLI).

Loads a static JSON registry of *candidate* external tools and reports their
intake classification. It is planning/intake bookkeeping only: it never adds,
downloads, fetches, or runs any external tool, and it makes no outbound network
calls. Every candidate stays at status 'candidate_only' or 'blocked' until a
separate, approved milestone wires it in after tests and a Codex audit.

Usage:
  python 03_scripts/tool_intake_static_registry.py --json
  python 03_scripts/tool_intake_static_registry.py --list
  python 03_scripts/tool_intake_static_registry.py --candidate "MarkItDown" --json
  python 03_scripts/tool_intake_static_registry.py --registry <path> --json

Stdlib only. Exits non-zero on an invalid registry or a missing candidate.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = REPO_ROOT / "14_context" / "tool_intake" / "tool_candidate_registry.json"

REQUIRED_CANDIDATE_FIELDS = [
    "name",
    "category",
    "priority",
    "status",
    "installed",
    "runtime_wired",
    "intended_value",
    "risk_level",
    "safe_intake_method",
    "first_safe_test",
    "integration_target",
    "stop_conditions",
    "allowed_now",
    "forbidden_now",
]

VALID_PRIORITIES = {"high", "medium", "blocked"}
VALID_STATUSES = {"candidate_only", "blocked"}
VALID_RISK = {"low", "medium", "high", "blocked"}

LIST_FIELDS = ("stop_conditions", "allowed_now", "forbidden_now")
STR_FIELDS = (
    "name",
    "category",
    "intended_value",
    "safe_intake_method",
    "first_safe_test",
    "integration_target",
)


def _emit_error(payload, code=2):
    """Print a JSON error object and return the process exit code."""
    print(json.dumps(payload, indent=2))
    return code


def load_registry(path):
    """Read and parse the registry JSON. Raises on malformed JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry(reg):
    """Return a list of error strings; an empty list means the registry is valid."""
    errors = []
    if not isinstance(reg, dict):
        return ["registry root is not a JSON object"]

    candidates = reg.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ["registry has no non-empty 'candidates' list"]

    seen = set()
    for index, cand in enumerate(candidates):
        if not isinstance(cand, dict):
            errors.append(f"candidate[{index}] is not an object")
            continue
        name = cand.get("name", f"<index {index}>")

        for field in REQUIRED_CANDIDATE_FIELDS:
            if field not in cand:
                errors.append(f"{name}: missing field '{field}'")

        if name in seen:
            errors.append(f"duplicate candidate name '{name}'")
        seen.add(name)

        if cand.get("priority") not in VALID_PRIORITIES:
            errors.append(f"{name}: invalid priority {cand.get('priority')!r}")
        if cand.get("status") not in VALID_STATUSES:
            errors.append(f"{name}: invalid status {cand.get('status')!r}")
        if cand.get("risk_level") not in VALID_RISK:
            errors.append(f"{name}: invalid risk_level {cand.get('risk_level')!r}")

        for field in STR_FIELDS:
            value = cand.get(field)
            if field in cand and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{name}: field '{field}' must be a non-empty string")

        for field in LIST_FIELDS:
            value = cand.get(field)
            if field in cand and (not isinstance(value, list) or not value):
                errors.append(f"{name}: field '{field}' must be a non-empty list")

        # Safety invariants: this registry never installs or wires anything.
        if cand.get("installed") is not False:
            errors.append(f"{name}: 'installed' must be false")
        if cand.get("runtime_wired") is not False:
            errors.append(f"{name}: 'runtime_wired' must be false")

        # A blocked-priority candidate must also carry blocked status.
        if cand.get("priority") == "blocked" and cand.get("status") != "blocked":
            errors.append(f"{name}: blocked priority requires status 'blocked'")

    return errors


def _count_by(candidates, key):
    counts = {}
    for cand in candidates:
        counts[cand[key]] = counts.get(cand[key], 0) + 1
    return dict(sorted(counts.items()))


def summarize(reg):
    """Build the JSON summary with counts by priority / risk / status."""
    candidates = reg["candidates"]
    return {
        "ok": True,
        "milestone": reg.get("milestone"),
        "status": reg.get("status"),
        "candidate_count": len(candidates),
        "by_priority": _count_by(candidates, "priority"),
        "by_risk": _count_by(candidates, "risk_level"),
        "by_status": _count_by(candidates, "status"),
        "any_installed": any(c.get("installed") for c in candidates),
        "any_runtime_wired": any(c.get("runtime_wired") for c in candidates),
        "global_safety": reg.get("global_safety", {}),
        "candidates": [c["name"] for c in candidates],
    }


def find_candidate(reg, name):
    target = name.strip().lower()
    for cand in reg["candidates"]:
        if cand["name"].strip().lower() == target:
            return cand
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Static tool/repo intake registry (read-only, planning only).",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="path to the registry JSON (defaults to the bundled registry)",
    )
    parser.add_argument("--json", action="store_true", help="emit the JSON summary")
    parser.add_argument("--list", action="store_true", help="list candidate names by tier")
    parser.add_argument("--candidate", help="show one candidate by name (JSON)")
    args = parser.parse_args(argv)

    path = Path(args.registry)
    if not path.is_file():
        return _emit_error({"ok": False, "error": f"registry not found: {path}"})

    try:
        reg = load_registry(path)
    except (json.JSONDecodeError, ValueError) as exc:
        return _emit_error({"ok": False, "error": f"registry is not valid JSON: {exc}"})

    errors = validate_registry(reg)
    if errors:
        return _emit_error({"ok": False, "errors": errors})

    if args.candidate:
        match = find_candidate(reg, args.candidate)
        if match is None:
            return _emit_error({"ok": False, "error": f"candidate not found: {args.candidate}"})
        print(json.dumps(match, indent=2))
        return 0

    if args.list:
        for cand in reg["candidates"]:
            print(f"{cand['priority']:7} {cand['status']:14} {cand['name']}")
        return 0

    # Default action (also covers --json): print the JSON summary.
    print(json.dumps(summarize(reg), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
