#!/usr/bin/env python3
"""Agent Lane Status helper.

stdlib only, repo-local, no external APIs, append-only JSONL.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
AGENT_LANES_DIR = REPO_ROOT / "14_context" / "agent_lanes"
REGISTRY_FILE = AGENT_LANES_DIR / "agent_lane_registry.json"
ACTIVE_LOCKS_FILE = AGENT_LANES_DIR / "active_locks.jsonl"
LANE_STATUS_FILE = AGENT_LANES_DIR / "lane_status.jsonl"

REQUIRED_LANE_FILES = [
    AGENT_LANES_DIR / "README.md",
    AGENT_LANES_DIR / "lane_template.md",
    AGENT_LANES_DIR / "lock_template.md",
    AGENT_LANES_DIR / "status_template.md",
    AGENT_LANES_DIR / "merge_checklist.md",
    AGENT_LANES_DIR / "shared_file_lock_policy.md",
    REGISTRY_FILE,
    ACTIVE_LOCKS_FILE,
    LANE_STATUS_FILE,
]


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _short_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:8]


def _make_lock_id(agent_id, task_slug):
    ts = _utc_now()
    h = _short_hash(f"{agent_id}:{task_slug}:{ts}")
    return f"lock_{ts}_{h}"


def _make_status_id(agent_id, task_slug):
    ts = _utc_now()
    h = _short_hash(f"{agent_id}:{task_slug}:{ts}")
    return f"status_{ts}_{h}"


def _validate_repo_relative_path(p):
    if not p or not p.strip():
        raise ValueError("Empty path not allowed")
    resolved = (REPO_ROOT / p).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(f"Path escapes repo root: {p}")
    return p


def _parse_jsonl(file_path):
    records = []
    errors = []
    if not file_path.exists() or file_path.stat().st_size == 0:
        return records, errors
    with open(file_path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append((lineno, str(exc)))
    return records, errors


def cmd_check(args):
    failures = []

    for req in REQUIRED_LANE_FILES:
        rel = req.relative_to(REPO_ROOT)
        if not req.exists():
            failures.append(f"MISSING: {rel}")
        else:
            print(f"  OK file: {rel}")

    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, encoding="utf-8") as fh:
                json.load(fh)
            print("  OK JSON: agent_lane_registry.json")
        except json.JSONDecodeError as exc:
            failures.append(f"INVALID JSON registry: {exc}")

    for jf in [ACTIVE_LOCKS_FILE, LANE_STATUS_FILE]:
        if jf.exists():
            records, errors = _parse_jsonl(jf)
            if errors:
                for lineno, err in errors:
                    failures.append(f"MALFORMED JSONL {jf.name} line {lineno}: {err}")
            else:
                print(f"  OK JSONL: {jf.name} ({len(records)} records)")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    else:
        print("\nPASS: all lane files and data valid")


def cmd_list(args):
    print("=== Active Locks ===")
    locks, lock_errors = _parse_jsonl(ACTIVE_LOCKS_FILE)
    for lineno, err in lock_errors:
        print(f"  WARNING malformed line {lineno}: {err}")
    if not locks:
        print("  (no active locks)")
    for r in locks:
        print(
            f"  [{r.get('lock_id', '?')}] agent={r.get('agent_id', '?')}"
            f" branch={r.get('branch', '?')} task={r.get('task_slug', '?')}"
        )
        locked = r.get("locked_files", [])
        if locked:
            print(f"    locked_files: {', '.join(locked)}")

    print("\n=== Latest Statuses ===")
    statuses, status_errors = _parse_jsonl(LANE_STATUS_FILE)
    for lineno, err in status_errors:
        print(f"  WARNING malformed line {lineno}: {err}")
    if not statuses:
        print("  (no statuses)")
    seen = {}
    for r in statuses:
        seen[r.get("agent_id", "?")] = r
    for agent_id, r in seen.items():
        print(
            f"  [{r.get('status_id', '?')}] agent={agent_id}"
            f" state={r.get('current_state', '?')} branch={r.get('branch', '?')}"
        )


def cmd_new_lock(args):
    if not args.agent_id:
        print("ERROR: --agent-id required")
        sys.exit(1)
    if not args.task_slug:
        print("ERROR: --task-slug required")
        sys.exit(1)

    locked_files = []
    for p in args.locked_file or []:
        try:
            locked_files.append(_validate_repo_relative_path(p))
        except ValueError as exc:
            print(f"ERROR: {exc}")
            sys.exit(1)

    record = {
        "lock_id": _make_lock_id(args.agent_id, args.task_slug),
        "agent_id": args.agent_id,
        "lane_type": args.lane_type or "",
        "model_or_tool": args.model_or_tool or "",
        "branch": args.branch or "",
        "task_slug": args.task_slug,
        "locked_files": locked_files,
        "allowed_paths": list(args.allowed_path or []),
        "forbidden_paths": list(args.forbidden_path or []),
        "expected_outputs": list(args.expected_output or []),
        "notes": list(args.note or []),
        "timestamp_utc": _utc_now(),
    }

    print(json.dumps(record, indent=2))

    if args.apply:
        with open(ACTIVE_LOCKS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        print(f"\nAppended to {ACTIVE_LOCKS_FILE.relative_to(REPO_ROOT)}")
    else:
        print("\n[DRY RUN] Pass --apply to write.")


def cmd_new_status(args):
    if not args.agent_id:
        print("ERROR: --agent-id required")
        sys.exit(1)
    if not args.task_slug:
        print("ERROR: --task-slug required")
        sys.exit(1)

    record = {
        "status_id": _make_status_id(args.agent_id, args.task_slug),
        "agent_id": args.agent_id,
        "lane_type": args.lane_type or "",
        "model_or_tool": args.model_or_tool or "",
        "branch": args.branch or "",
        "task_slug": args.task_slug,
        "current_state": args.current_state or "unknown",
        "notes": list(args.note or []),
        "timestamp_utc": _utc_now(),
    }

    print(json.dumps(record, indent=2))

    if args.apply:
        with open(LANE_STATUS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        print(f"\nAppended to {LANE_STATUS_FILE.relative_to(REPO_ROOT)}")
    else:
        print("\n[DRY RUN] Pass --apply to write.")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Lane Status — stdlib only, repo-local, append-only JSONL"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true",
                       help="Verify all required lane files exist and are valid")
    group.add_argument("--list", action="store_true",
                       help="Print active locks and latest statuses")
    group.add_argument("--new-lock", action="store_true",
                       help="Build a new lock record")
    group.add_argument("--new-status", action="store_true",
                       help="Build a new status record")

    parser.add_argument("--agent-id")
    parser.add_argument("--lane-type")
    parser.add_argument("--task-slug")
    parser.add_argument("--branch")
    parser.add_argument("--model-or-tool")
    parser.add_argument("--locked-file", action="append")
    parser.add_argument("--allowed-path", action="append")
    parser.add_argument("--forbidden-path", action="append")
    parser.add_argument("--expected-output", action="append")
    parser.add_argument("--note", action="append")
    parser.add_argument("--current-state")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Dry run (default; no writes)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually append record to JSONL file")

    args = parser.parse_args()

    if args.check:
        cmd_check(args)
    elif args.list:
        cmd_list(args)
    elif args.new_lock:
        cmd_new_lock(args)
    elif args.new_status:
        cmd_new_status(args)


if __name__ == "__main__":
    main()
