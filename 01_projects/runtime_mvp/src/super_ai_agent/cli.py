from __future__ import annotations

import argparse
import subprocess
import sys

from .handoff import build_handoff_snapshot
from .queue import approve_task, enqueue_task, get_status_summary, list_tasks, reject_task
from .storage import APPROVALS_PATH, TASKS_PATH, ensure_runtime_files, get_runtime_data_dir, get_project_root


def _get_current_branch() -> str | None:
    workspace_root = get_project_root().parents[1]
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = result.stdout.strip()
    return branch or None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="super-agent")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-data")
    subparsers.add_parser("status")
    subparsers.add_parser("list")
    subparsers.add_parser("snapshot")

    enqueue_parser = subparsers.add_parser("enqueue")
    enqueue_parser.add_argument("--title", required=True)
    enqueue_parser.add_argument("--description", required=True)
    enqueue_parser.add_argument("--risk", required=True, choices=["safe", "ask", "high_risk"])
    enqueue_parser.add_argument("--source", default="manual")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--task-id", required=True)
    approve_parser.add_argument("--note", default="")

    reject_parser = subparsers.add_parser("reject")
    reject_parser.add_argument("--task-id", required=True)
    reject_parser.add_argument("--note", default="")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "init-data":
            runtime_dir = ensure_runtime_files()
            print(f"runtime_data: {runtime_dir}")
            return 0

        if args.command == "status":
            ensure_runtime_files()
            summary = get_status_summary()
            branch = _get_current_branch()
            snapshot_exists = (get_runtime_data_dir() / "handoff_snapshot.md").exists()
            if branch:
                print(f"branch: {branch}")
            print(f"runtime_data: {get_runtime_data_dir()}")
            print(f"tasks_total: {summary.total_tasks}")
            print(f"tasks_queued: {summary.queued_tasks}")
            print(f"tasks_pending_approval: {summary.pending_approval_tasks}")
            print(f"tasks_rejected: {summary.rejected_tasks}")
            print(f"tasks_file: {TASKS_PATH}")
            print(f"approvals_file: {APPROVALS_PATH}")
            print(f"handoff_snapshot_exists: {'yes' if snapshot_exists else 'no'}")
            return 0

        if args.command == "enqueue":
            task = enqueue_task(
                title=args.title,
                description=args.description,
                risk_level=args.risk,
                source=args.source,
            )
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "list":
            tasks = list_tasks()
            if not tasks:
                print("No tasks found.")
                return 0
            for task in tasks:
                print(
                    f"{task.task_id} | {task.status} | {task.risk_level} | "
                    f"{task.approval_state} | {task.title}"
                )
            return 0

        if args.command == "approve":
            task = approve_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "reject":
            task = reject_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "snapshot":
            output_path = build_handoff_snapshot()
            print(f"handoff_snapshot: {output_path}")
            return 0

        parser.print_help()
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
