#!/usr/bin/env python3
"""Manage Ghoti agent lane lock and status JSONL files.

N+3.43 safety constraints:
- stdlib only
- repo-local only
- no network, model calls, installs, live actions, deletion, or git mutation
- dry-run is the default for new writes unless --apply is passed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
LANE_DIR = REPO_ROOT / "14_context" / "agent_lanes"
REGISTRY_PATH = LANE_DIR / "agent_lane_registry.json"
ACTIVE_LOCKS_PATH = LANE_DIR / "active_locks.jsonl"
LANE_STATUS_PATH = LANE_DIR / "lane_status.jsonl"

REQUIRED_FILES = [
    LANE_DIR / "README.md",
    LANE_DIR / "lane_template.md",
    LANE_DIR / "lock_template.md",
    LANE_DIR / "status_template.md",
    LANE_DIR / "merge_checklist.md",
    LANE_DIR / "shared_file_lock_policy.md",
    REGISTRY_PATH,
    ACTIVE_LOCKS_PATH,
    LANE_STATUS_PATH,
]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def id_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def short_hash(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]


def make_id(prefix: str, seed: str) -> str:
    stamp = id_timestamp()
    return f"{prefix}_{stamp}_{short_hash(prefix + stamp + seed)}"


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def validate_repo_path(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("path cannot be empty")

    raw = value.strip()
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        raise ValueError(f"URL paths are not repo-local: {raw}")
    if raw.startswith("\\\\"):
        raise ValueError(f"UNC paths are not repo-local: {raw}")

    candidate = Path(raw)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        posix = PurePosixPath(raw.replace("\\", "/"))
        if any(part == ".." for part in posix.parts):
            raise ValueError(f"parent traversal is not allowed: {raw}")
        resolved = (REPO_ROOT / candidate).resolve()

    try:
        return repo_relative(resolved)
    except ValueError as exc:
        raise ValueError(f"path is outside repo: {raw}") from exc


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        errors.append(f"missing JSONL file: {repo_relative(path)}")
        return records, errors

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{repo_relative(path)}:{line_number}: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{repo_relative(path)}:{line_number}: expected JSON object")
            continue
        records.append(value)
    return records, errors


def load_registry() -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"missing registry: {repo_relative(REGISTRY_PATH)}"
    except json.JSONDecodeError as exc:
        return None, f"registry JSON error: {exc}"
    if not isinstance(value, dict):
        return None, "registry must be a JSON object"
    return value, None


def command_check() -> int:
    failures: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            failures.append(f"missing required file: {repo_relative(path)}")

    registry, registry_error = load_registry()
    if registry_error:
        failures.append(registry_error)
    elif registry is not None:
        lanes = registry.get("lanes")
        if not isinstance(lanes, dict) or not lanes:
            failures.append("registry must include a non-empty lanes object")

    for path in [ACTIVE_LOCKS_PATH, LANE_STATUS_PATH]:
        _records, errors = parse_jsonl(path)
        failures.extend(errors)

    if failures:
        print("FAIL agent lane check")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS agent lane check")
    print(f"- required_files: {len(REQUIRED_FILES)}")
    print(f"- registry: {repo_relative(REGISTRY_PATH)}")
    print(f"- active_locks: {repo_relative(ACTIVE_LOCKS_PATH)}")
    print(f"- lane_status: {repo_relative(LANE_STATUS_PATH)}")
    return 0


def command_list() -> int:
    locks, lock_errors = parse_jsonl(ACTIVE_LOCKS_PATH)
    statuses, status_errors = parse_jsonl(LANE_STATUS_PATH)
    errors = lock_errors + status_errors
    if errors:
        print("FAIL cannot list lanes")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Active locks: {len(locks)}")
    if locks:
        for record in locks[-20:]:
            print(
                f"- {record.get('lock_id', 'unknown')} | "
                f"{record.get('agent_id', 'unknown')} | "
                f"{record.get('task_slug', 'unknown')} | "
                f"{record.get('status', 'unknown')}"
            )
    else:
        print("- none")

    print(f"Lane status records: {len(statuses)}")
    if statuses:
        for record in statuses[-20:]:
            print(
                f"- {record.get('status_id', 'unknown')} | "
                f"{record.get('agent_id', 'unknown')} | "
                f"{record.get('task_slug', 'unknown')} | "
                f"{record.get('current_state', 'unknown')}"
            )
    else:
        print("- none")
    return 0


def require_text(name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{name} is required and cannot be empty")
    return value.strip()


def normalized_paths(values: list[str] | None) -> list[str]:
    return [validate_repo_path(value) for value in (values or [])]


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def print_record(record: dict[str, Any], target: Path, apply: bool) -> None:
    print(json.dumps(record, indent=2, sort_keys=True))
    if apply:
        append_jsonl(target, record)
        print(f"Appended to {repo_relative(target)}")
    else:
        print("Dry-run only. No files written. Pass --apply to append.")


def command_new_lock(args: argparse.Namespace) -> int:
    try:
        agent_id = require_text("--agent-id", args.agent_id)
        lane_type = require_text("--lane-type", args.lane_type)
        task_slug = require_text("--task-slug", args.task_slug)
        branch = require_text("--branch", args.branch)
        locked_files = normalized_paths(args.locked_file)
        allowed_paths = normalized_paths(args.allowed_path)
        forbidden_paths = normalized_paths(args.forbidden_path)
    except ValueError as exc:
        print(f"FAIL new-lock: {exc}", file=sys.stderr)
        return 2

    now = utc_timestamp()
    seed = "|".join([agent_id, lane_type, task_slug, branch, now])
    record = {
        "lock_id": make_id("lock", seed),
        "created_at": now,
        "agent_id": agent_id,
        "lane_type": lane_type,
        "model_or_tool": args.model_or_tool or "",
        "branch": branch,
        "task_slug": task_slug,
        "locked_files": locked_files,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "expected_outputs": args.expected_output or [],
        "safe_to_interrupt": True,
        "status": "dry_run" if not args.apply else "active",
        "human_approval_required_for_merge": True,
        "local_only": True,
        "no_live_actions": True,
        "notes": args.note or [],
    }
    print_record(record, ACTIVE_LOCKS_PATH, args.apply)
    return 0


def command_new_status(args: argparse.Namespace) -> int:
    try:
        agent_id = require_text("--agent-id", args.agent_id)
        lane_type = require_text("--lane-type", args.lane_type)
        task_slug = require_text("--task-slug", args.task_slug)
        branch = require_text("--branch", args.branch)
        current_state = require_text("--current-state", args.current_state)
    except ValueError as exc:
        print(f"FAIL new-status: {exc}", file=sys.stderr)
        return 2

    now = utc_timestamp()
    seed = "|".join([agent_id, lane_type, task_slug, branch, current_state, now])
    record = {
        "status_id": make_id("status", seed),
        "created_at": now,
        "agent_id": agent_id,
        "lane_type": lane_type,
        "branch": branch,
        "task_slug": task_slug,
        "current_state": current_state,
        "last_heartbeat": now,
        "latest_commit": "",
        "pushed": False,
        "validation_status": "unknown",
        "blockers": [],
        "next_action": "",
        "expected_outputs": args.expected_output or [],
        "notes": args.note or [],
        "local_only": True,
        "no_live_actions": True,
    }
    print_record(record, LANE_STATUS_PATH, args.apply)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check and append Ghoti agent lane lock/status records.",
    )
    parser.add_argument("--list", action="store_true", help="List active locks and status records.")
    parser.add_argument("--check", action="store_true", help="Validate lane scaffolding and JSONL files.")
    parser.add_argument("--new-lock", action="store_true", help="Build a new lock record.")
    parser.add_argument("--new-status", action="store_true", help="Build a new status record.")
    parser.add_argument("--apply", action="store_true", help="Append a new record. Without this, writes are dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run. This is the default for new records.")
    parser.add_argument("--agent-id")
    parser.add_argument("--lane-type")
    parser.add_argument("--task-slug")
    parser.add_argument("--branch")
    parser.add_argument("--current-state")
    parser.add_argument("--model-or-tool", default="")
    parser.add_argument("--locked-file", action="append", default=[])
    parser.add_argument("--allowed-path", action="append", default=[])
    parser.add_argument("--forbidden-path", action="append", default=[])
    parser.add_argument("--expected-output", action="append", default=[])
    parser.add_argument("--note", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    actions = [args.list, args.check, args.new_lock, args.new_status]
    if sum(1 for item in actions if item) != 1:
        parser.error("choose exactly one action: --list, --check, --new-lock, or --new-status")
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run cannot be combined")

    if args.list:
        return command_list()
    if args.check:
        return command_check()
    if args.new_lock:
        return command_new_lock(args)
    if args.new_status:
        return command_new_status(args)
    parser.error("unreachable action state")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
