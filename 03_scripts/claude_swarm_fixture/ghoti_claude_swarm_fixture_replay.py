"""
ghoti_claude_swarm_fixture_replay.py — N+6.38A provider-free claude-swarm fixture replay.

Loads a static fixture shaped like claude-swarm output, validates its schema,
detects file-ownership overlaps, surfaces roles/tasks/dependencies/approval gates,
and emits Agent-Arena-shaped status.

Does NOT execute claude-swarm. Does NOT require claude-swarm installed.
Does NOT call any provider API. Does NOT use API keys.

N+6.37A finding: claude-swarm --dry-run requires ANTHROPIC_API_KEY and calls the
model decomposition path before the dry-run skip. This wrapper avoids that entirely
by replaying a pre-authored static fixture.

CLI flags:
  --replay [<path>]    Load and replay fixture (default: built-in sample)
  --check              Safety status check
  --validate <path>    Validate a fixture file against the schema
  --json               Machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

MILESTONE = "N+6.38A"
FIXTURE_RELATIVE = "14_context/claude_swarm_fixture/sample_claude_swarm_plan.json"
SCHEMA_RELATIVE  = "14_context/claude_swarm_fixture/claude_swarm_fixture_schema.json"

# API key env vars that must not be set
_API_KEY_ENV_VARS = ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "OPENAI_API_KEY"]

# Paths that are never valid as fixture input
_BLOCKED_PATH_PATTERNS = [
    "/etc/", "/proc/", "/sys/", "/root/",
    "C:\\Windows\\", "C:\\Program Files\\",
    ".env", "credentials", "secrets",
]

# Safety block present on every result
_SAFETY_BLOCK: dict[str, Any] = {
    "live_execution": False,
    "live_computer_use_enabled": False,
    "hooks_enabled": False,
    "docker_enabled": False,
    "mcp_enabled": False,
    "auto_submit": False,
    "simulation": True,
    "live_agent_launch": False,
    "api_key_used": False,
    "network_attempted": False,
    "provider_called": False,
    "external_cli_executed": False,
    "third_party_code_executed": False,
    "secrets_committed": False,
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_fixture_path() -> Path:
    return _repo_root() / FIXTURE_RELATIVE


def _default_schema_path() -> Path:
    return _repo_root() / SCHEMA_RELATIVE


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def _check_api_keys() -> list[str]:
    return [k for k in _API_KEY_ENV_VARS if os.environ.get(k)]


def _validate_fixture_path(path: Path) -> list[str]:
    blocked = []
    path_str = str(path)
    for pattern in _BLOCKED_PATH_PATTERNS:
        if pattern.lower() in path_str.lower():
            blocked.append(f"blocked_path_pattern: {pattern!r} in {path_str!r}")
    if not path_str.endswith(".json"):
        blocked.append("fixture_must_be_json")
    return blocked


def _validate_fixture_schema(data: dict) -> list[str]:
    errors = []
    # source must be static_fixture
    if data.get("source") != "static_fixture":
        errors.append(f"source must be 'static_fixture', got {data.get('source')!r}")
    # swarm safety flags
    swarm = data.get("swarm", {})
    if swarm.get("live_execution") is not False:
        errors.append("swarm.live_execution must be false")
    if swarm.get("simulation") is not True:
        errors.append("swarm.simulation must be true")
    if swarm.get("dry_run") is not True:
        errors.append("swarm.dry_run must be true")
    # safety block
    safety = data.get("safety", {})
    if safety.get("live_execution") is not False:
        errors.append("safety.live_execution must be false")
    if safety.get("simulation") is not True:
        errors.append("safety.simulation must be true")
    if safety.get("live_agent_launch") is not False:
        errors.append("safety.live_agent_launch must be false")
    # tasks must be a list
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
        return errors
    # each task must have id, description, agent_type, dependencies, files_to_modify
    seen_ids: set[str] = set()
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"tasks[{i}] must be a dict")
            continue
        for field in ("id", "description", "agent_type", "dependencies", "files_to_modify"):
            if field not in task:
                errors.append(f"tasks[{i}] missing field: {field!r}")
        task_id = task.get("id", f"<index:{i}>")
        if task_id in seen_ids:
            errors.append(f"duplicate task id: {task_id!r}")
        seen_ids.add(task_id)
        deps = task.get("dependencies", [])
        for dep in deps:
            if dep not in seen_ids and dep not in {t.get("id") for t in tasks}:
                errors.append(f"task {task_id!r} depends on unknown id: {dep!r}")
    return errors


def _detect_file_overlaps(tasks: list[dict]) -> list[dict]:
    file_owners: dict[str, list[str]] = {}
    for task in tasks:
        tid = task.get("id", "?")
        for f in task.get("files_to_modify", []):
            file_owners.setdefault(f, []).append(tid)
    return [
        {"file": f, "claimed_by": owners}
        for f, owners in file_owners.items()
        if len(owners) > 1
    ]


def _build_parallel_groups(tasks: list[dict]) -> list[list[str]]:
    remaining = {t["id"]: set(t.get("dependencies", [])) for t in tasks}
    groups = []
    while remaining:
        ready = [tid for tid, deps in remaining.items() if not deps]
        if not ready:
            break
        groups.append(sorted(ready))
        for tid in ready:
            del remaining[tid]
        for deps in remaining.values():
            deps -= set(ready)
    return groups


def _format_plan_summary(data: dict) -> dict:
    swarm = data.get("swarm", {})
    tasks = data.get("tasks", [])
    overlaps = _detect_file_overlaps(tasks)
    groups = _build_parallel_groups(tasks)

    by_agent: dict[str, list[str]] = {}
    for task in tasks:
        at = task.get("agent_type", "unknown")
        by_agent.setdefault(at, []).append(task["id"])

    return {
        "swarm_name": swarm.get("name"),
        "task_count": len(tasks),
        "agent_types": by_agent,
        "parallel_groups": groups,
        "file_overlaps": overlaps,
        "overlap_count": len(overlaps),
        "requires_human_approval": data.get("safety", {}).get("requires_human_approval", True),
        "total_budget_usd": sum(t.get("cost_usd", 0.0) for t in tasks),
    }


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def _run_check() -> dict:
    api_keys = _check_api_keys()
    fixture_path = _default_fixture_path()
    schema_path = _default_schema_path()
    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "check",
        "fixture_path": str(fixture_path),
        "fixture_exists": fixture_path.exists(),
        "schema_path": str(schema_path),
        "schema_exists": schema_path.exists(),
        "api_keys_in_env": api_keys,
        "api_keys_blocked": len(api_keys) > 0,
        "external_cli_execution": "BLOCKED — this wrapper never executes claude-swarm",
        "provider_api_calls": "BLOCKED — no API keys accepted",
        "start_conditions": {
            "n6_35b_on_main": True,
            "n6_36b_on_main": False,
            "n6_37b_on_main": False,
            "note": "N+6.35B merged. N+6.36B and N+6.37B PRs (#11, #12) are drafts.",
        },
        "safety_block": _SAFETY_BLOCK,
    }


def _run_validate(fixture_path: Path) -> dict:
    path_errors = _validate_fixture_path(fixture_path)
    if path_errors:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "validate",
            "fixture_path": str(fixture_path),
            "errors": path_errors,
            "safety_block": _SAFETY_BLOCK,
        }
    if not fixture_path.exists():
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "validate",
            "fixture_path": str(fixture_path),
            "errors": ["fixture_file_not_found"],
            "safety_block": _SAFETY_BLOCK,
        }
    try:
        data = json.loads(fixture_path.read_text())
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "validate",
            "errors": [f"json_parse_error: {exc}"],
            "safety_block": _SAFETY_BLOCK,
        }
    errors = _validate_fixture_schema(data)
    return {
        "ok": len(errors) == 0,
        "milestone": MILESTONE,
        "mode": "validate",
        "fixture_path": str(fixture_path),
        "errors": errors,
        "task_count": len(data.get("tasks", [])),
        "safety_block": _SAFETY_BLOCK,
    }


def _run_replay(fixture_path: Path | None = None) -> dict:
    api_keys = _check_api_keys()
    if api_keys:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "replay",
            "error": "api_keys_present",
            "blocked_keys": api_keys,
            "safety_block": _SAFETY_BLOCK,
        }

    if fixture_path is None:
        fixture_path = _default_fixture_path()

    path_errors = _validate_fixture_path(fixture_path)
    if path_errors:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "replay",
            "error": "blocked_path",
            "errors": path_errors,
            "safety_block": _SAFETY_BLOCK,
        }

    if not fixture_path.exists():
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "replay",
            "error": "fixture_not_found",
            "fixture_path": str(fixture_path),
            "safety_block": _SAFETY_BLOCK,
        }

    try:
        data = json.loads(fixture_path.read_text())
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "replay",
            "error": f"json_parse_error: {exc}",
            "safety_block": _SAFETY_BLOCK,
        }

    schema_errors = _validate_fixture_schema(data)
    if schema_errors:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "replay",
            "error": "schema_validation_failed",
            "schema_errors": schema_errors,
            "safety_block": _SAFETY_BLOCK,
        }

    tasks = data.get("tasks", [])
    overlaps = _detect_file_overlaps(tasks)
    summary = _format_plan_summary(data)

    # Overlaps are reported but do not block replay of a static fixture
    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "replay",
        "fixture_id": data.get("fixture_id"),
        "fixture_path": str(fixture_path),
        "simulation": True,
        "live_execution": False,
        "accepted": True,
        "plan_summary": summary,
        "overlaps": overlaps,
        "overlap_warning": len(overlaps) > 0,
        "external_cli_executed": False,
        "provider_called": False,
        "api_key_used": False,
        "network_attempted": False,
        "agents_launched": False,
        "safety_block": _SAFETY_BLOCK,
        "next_step": (
            "N+6.38A fixture replay complete. "
            "Next: run claude-swarm --demo --no-ui in isolated scratch "
            "(N+6.39A, requires N+6.36B + N+6.37B merged + human approval)."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=f"Ghoti {MILESTONE} claude-swarm fixture replay"
    )
    parser.add_argument("--replay", nargs="?", const="__default__", metavar="PATH",
                        help="Replay fixture (default: built-in sample)")
    parser.add_argument("--validate", metavar="PATH", help="Validate a fixture file")
    parser.add_argument("--check", action="store_true", help="Safety status check")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.validate:
        result = _run_validate(Path(args.validate))
    elif args.replay is not None:
        fp = None if args.replay == "__default__" else Path(args.replay)
        result = _run_replay(fp)
    else:
        result = _run_check()

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] ok={ok} mode={result.get('mode')}")
        sb = result.get("safety_block", {})
        print(f"  simulation={sb.get('simulation')} live_execution={sb.get('live_execution')}")
        if "plan_summary" in result:
            ps = result["plan_summary"]
            print(f"  tasks={ps['task_count']} overlaps={ps['overlap_count']} "
                  f"groups={len(ps['parallel_groups'])}")
        if result.get("overlap_warning"):
            print(f"  WARNING: {len(result['overlaps'])} file overlap(s) detected")
        if not ok:
            print(f"  error={result.get('error')}")


if __name__ == "__main__":
    _main()
