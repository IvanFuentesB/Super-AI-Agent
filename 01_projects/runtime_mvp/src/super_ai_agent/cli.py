from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone

from .council import build_council_plan
from .handoff import build_handoff_snapshot
from .providers import list_provider_profiles
from .queue import approve_task, enqueue_task, get_status_summary, list_tasks, reject_task
from .report_builder import build_report_scaffold
from .storage import (
    APPROVALS_PATH,
    TASKS_PATH,
    ensure_runtime_files,
    get_runtime_data_dir,
    get_project_root,
    read_tasks,
    write_tasks,
)
from .workflow_catalog import get_workflow, list_workflows


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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_task_for_update(task_id: str):
    tasks = read_tasks()
    for task in tasks:
        if task.task_id == task_id:
            return tasks, task
    raise ValueError(f"Task not found: {task_id}")


def _set_task_status(task_id: str, expected_statuses: set[str], new_status: str):
    tasks, task = _load_task_for_update(task_id)
    if task.status not in expected_statuses:
        allowed = ", ".join(sorted(expected_statuses))
        raise ValueError(f"Task {task_id} must be in one of: {allowed}")
    task.status = new_status
    task.updated_at = _now()
    write_tasks(tasks)
    return task


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="super-agent")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-data")
    subparsers.add_parser("status")
    subparsers.add_parser("list")
    subparsers.add_parser("snapshot")
    subparsers.add_parser("list-providers")
    subparsers.add_parser("list-workflows")

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

    wait_parser = subparsers.add_parser("wait")
    wait_parser.add_argument("--task-id", required=True)

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--task-id", required=True)

    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--task-id", required=True)

    council_parser = subparsers.add_parser("council-plan")
    council_parser.add_argument("--goal-type", required=True)
    council_parser.add_argument("--privacy", default="balanced")
    council_parser.add_argument("--speed", default="balanced")
    council_parser.add_argument("--require-reviewer", action="store_true")

    show_workflow_parser = subparsers.add_parser("show-workflow")
    show_workflow_parser.add_argument("--workflow-id", required=True)

    scaffold_report_parser = subparsers.add_parser("scaffold-report")
    scaffold_report_parser.add_argument("--title", required=True)
    scaffold_report_parser.add_argument("--workflow-id", required=True)
    scaffold_report_parser.add_argument("--summary", required=True)

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
            tasks = list_tasks()
            branch = _get_current_branch()
            snapshot_exists = (get_runtime_data_dir() / "handoff_snapshot.md").exists()
            waiting_count = sum(1 for task in tasks if task.status == "waiting")
            completed_count = sum(1 for task in tasks if task.status == "completed")
            if branch:
                print(f"branch: {branch}")
            print(f"runtime_data: {get_runtime_data_dir()}")
            print(f"tasks_total: {summary.total_tasks}")
            print(f"tasks_queued: {summary.queued_tasks}")
            print(f"tasks_pending_approval: {summary.pending_approval_tasks}")
            print(f"tasks_waiting: {waiting_count}")
            print(f"tasks_completed: {completed_count}")
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

        if args.command == "wait":
            task = _set_task_status(args.task_id, {"queued"}, "waiting")
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "resume":
            task = _set_task_status(args.task_id, {"waiting"}, "queued")
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "run-once":
            tasks, task = _load_task_for_update(args.task_id)
            if task.status != "queued":
                raise ValueError(f"Task {task.task_id} must be queued before run-once.")
            if task.approval_state not in {"approved", "not_required"}:
                raise ValueError(f"Task {task.task_id} must be approved before run-once.")
            task.status = "completed"
            task.updated_at = _now()
            write_tasks(tasks)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            return 0

        if args.command == "list-providers":
            for profile in list_provider_profiles():
                print(
                    f"{profile.provider_id} | {profile.display_name} | "
                    f"{profile.privacy_mode} | {profile.speed_bias}"
                )
            return 0

        if args.command == "council-plan":
            plan = build_council_plan(
                goal_type=args.goal_type,
                privacy_preference=args.privacy,
                speed_preference=args.speed,
                require_reviewer=args.require_reviewer,
            )
            print(f"goal_type: {plan.goal_type}")
            print(f"lead_provider: {plan.lead_provider}")
            print(f"reviewer_provider: {plan.reviewer_provider or 'none'}")
            print(f"local_fallback_provider: {plan.local_fallback_provider}")
            print(f"reasoning_summary: {plan.reasoning_summary}")
            if plan.notes:
                print("notes:")
                for note in plan.notes:
                    print(f"- {note}")
            return 0

        if args.command == "list-workflows":
            for workflow in list_workflows():
                print(f"{workflow.workflow_id} | {workflow.title}")
            return 0

        if args.command == "show-workflow":
            workflow = get_workflow(args.workflow_id)
            print(f"workflow_id: {workflow.workflow_id}")
            print(f"title: {workflow.title}")
            print(f"purpose: {workflow.purpose}")
            print("inputs:")
            for item in workflow.inputs:
                print(f"- {item}")
            print("outputs:")
            for item in workflow.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in workflow.approval_points:
                print(f"- {item}")
            print(f"notes: {workflow.notes}")
            return 0

        if args.command == "scaffold-report":
            _ = get_workflow(args.workflow_id)
            output_path = build_report_scaffold(
                title=args.title,
                workflow_id=args.workflow_id,
                summary=args.summary,
            )
            print(f"report_path: {output_path}")
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
