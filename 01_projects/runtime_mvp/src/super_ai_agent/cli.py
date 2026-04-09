from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone

from .council import build_council_plan
from .environment import build_capability_summary, diagnose_environment
from .github_actions import (
    create_branch_with_approval,
    create_issue_with_approval,
    create_pr_with_approval,
    create_smoke_issue_with_approval,
    create_smoke_pr_with_approval,
    scaffold_issue_draft,
    scaffold_pr_draft,
)
from .github_adapter import diagnose_gh_environment, get_remote_capability
from .github_adapter import get_current_branch as get_github_branch
from .github_adapter import get_recent_commits, get_remote_info, get_repo_status_summary
from .handoff import build_handoff_snapshot
from .integrations import list_supported_integrations
from .mail_adapter import build_inbox_triage_plan
from .notion_adapter import build_notion_update_plan
from .notification_adapter import (
    build_approval_notification,
    build_human_needed_notification,
    build_supervisor_notification,
)
from .personal_ops import (
    get_personal_workflow,
    list_personal_workflows,
    scaffold_cv_pack,
    scaffold_inbox_triage_pack,
    scaffold_internship_application_pack,
    scaffold_linkedin_pack,
    scaffold_outreach_draft,
    scaffold_portfolio_project_page,
    scaffold_showcase_case_study,
)
from .publishability import scan_publishability
from .providers import list_provider_profiles
from .queue import (
    approve_approval_request,
    approve_task,
    defer_approval_request,
    deny_approval_request,
    enqueue_executor_task,
    enqueue_task,
    execute_task,
    get_approval_request,
    get_task,
    get_task_history,
    get_task_next_action,
    get_status_summary,
    get_supervisor_state,
    list_approval_records,
    list_approval_requests,
    list_blocked_tasks,
    list_executor_tasks,
    list_interrupted_tasks,
    list_pending_approvals,
    list_ready_to_resume_tasks,
    list_tasks,
    list_waiting_tasks,
    mark_task_human_needed,
    requeue_task,
    reject_task,
    request_task_approval,
    review_task_for_resume,
    resume_task,
    run_task_once,
    wait_task,
)
from .report_builder import build_report_scaffold
from .storage import (
    APPROVALS_PATH,
    APPROVAL_REQUESTS_PATH,
    SUPERVISOR_STATE_PATH,
    TASKS_PATH,
    ensure_runtime_files,
    get_allowed_workspace_root,
    get_runtime_data_dir,
    get_project_root,
    read_tasks,
    runtime_data_lock,
)
from .truth_council import build_truth_council_result
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


def _approval_target(scope: str, task_id: str) -> str:
    normalized_scope = (scope or "").strip()
    if normalized_scope and normalized_scope != "runtime task execution":
        return normalized_scope
    return task_id


def _short_description(text: str, limit: int = 120) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value or "none"
    return f"{value[: limit - 3].rstrip()}..."


def _workspace_reason(text: str, limit: int = 140) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value or "none"
    return f"{value[: limit - 3].rstrip()}..."


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="super-agent")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-data")
    subparsers.add_parser("status")
    subparsers.add_parser("list")
    subparsers.add_parser("snapshot")
    subparsers.add_parser("list-providers")
    subparsers.add_parser("list-workflows")
    subparsers.add_parser("publish-check")
    subparsers.add_parser("list-personal-workflows")
    subparsers.add_parser("list-integrations")
    subparsers.add_parser("github-status")
    subparsers.add_parser("publish-check-core")
    subparsers.add_parser("github-gh-diagnose")
    subparsers.add_parser("github-remote-capability")
    subparsers.add_parser("env-diagnose")
    subparsers.add_parser("gh-auth-status")
    subparsers.add_parser("capability-matrix")
    subparsers.add_parser("pending-approvals")
    subparsers.add_parser("supervisor-status")
    subparsers.add_parser("list-executor-tasks")

    enqueue_parser = subparsers.add_parser("enqueue")
    enqueue_parser.add_argument("--title", required=True)
    enqueue_parser.add_argument("--description", required=True)
    enqueue_parser.add_argument(
        "--risk",
        required=True,
        choices=["safe", "ask", "high_risk", "admin"],
    )
    enqueue_parser.add_argument("--source", default="manual")

    executor_parser = subparsers.add_parser("queue-executor-action")
    executor_parser.add_argument(
        "--action-type",
        required=True,
        choices=[
            "read_file",
            "write_file",
            "append_file",
            "create_artifact",
            "list_directory",
            "git_status",
            "git_diff",
            "run_checker",
            "list_windows",
            "get_active_window",
            "focus_window",
            "open_allowed_app",
            "capture_desktop_screenshot",
            "get_clipboard_text",
            "set_clipboard_text",
            "copy_selection",
            "paste_clipboard",
            "send_hotkey",
            "wait_seconds",
            "wait_for_window",
            "move_mouse",
            "left_click",
            "double_click",
            "right_click",
            "scroll_mouse",
        ],
    )
    executor_parser.add_argument("--target", default="")
    executor_parser.add_argument("--content", default="")
    executor_parser.add_argument("--source", default="manual")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--task-id", required=True)
    approve_parser.add_argument("--note", default="")

    reject_parser = subparsers.add_parser("reject")
    reject_parser.add_argument("--task-id", required=True)
    reject_parser.add_argument("--note", default="")

    wait_parser = subparsers.add_parser("wait")
    wait_parser.add_argument("--task-id", required=True)
    wait_parser.add_argument(
        "--reason",
        default="waiting for human reply or external event",
    )

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--task-id", required=True)

    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--task-id", required=True)

    execute_task_parser = subparsers.add_parser("execute-task")
    execute_task_parser.add_argument("--task-id", required=True)

    task_status_parser = subparsers.add_parser("task-status")
    task_status_parser.add_argument("--task-id", required=True)

    review_task_parser = subparsers.add_parser("review-task")
    review_task_parser.add_argument("--task-id", required=True)
    review_task_parser.add_argument("--note", default="")

    requeue_task_parser = subparsers.add_parser("requeue-task")
    requeue_task_parser.add_argument("--task-id", required=True)
    requeue_task_parser.add_argument("--note", default="")

    approval_status_parser = subparsers.add_parser("approval-status")
    approval_status_parser.add_argument("--approval-id", default="")

    approve_approval_parser = subparsers.add_parser("approve-approval")
    approve_approval_parser.add_argument("--approval-id", required=True)
    approve_approval_parser.add_argument("--note", default="")

    deny_approval_parser = subparsers.add_parser("deny-approval")
    deny_approval_parser.add_argument("--approval-id", required=True)
    deny_approval_parser.add_argument("--note", default="")

    defer_approval_parser = subparsers.add_parser("defer-approval")
    defer_approval_parser.add_argument("--approval-id", required=True)
    defer_approval_parser.add_argument("--note", default="")

    request_approval_parser = subparsers.add_parser("request-approval")
    request_approval_parser.add_argument("--task-id", required=True)
    request_approval_parser.add_argument("--action-label", required=True)
    request_approval_parser.add_argument("--reason", required=True)
    request_approval_parser.add_argument(
        "--risk-level",
        default="ask",
        choices=["safe", "ask", "high_risk", "admin"],
    )
    request_approval_parser.add_argument("--scope", default="runtime task execution")
    request_approval_parser.add_argument(
        "--requires-admin",
        default="no",
        choices=["yes", "no"],
    )
    request_approval_parser.add_argument("--rollback-plan", default="")
    request_approval_parser.add_argument("--source", default="manual")

    human_needed_parser = subparsers.add_parser("mark-human-needed")
    human_needed_parser.add_argument("--task-id", required=True)
    human_needed_parser.add_argument("--reason", required=True)

    council_parser = subparsers.add_parser("council-plan")
    council_parser.add_argument("--goal-type", required=True)
    council_parser.add_argument("--privacy", default="balanced")
    council_parser.add_argument("--speed", default="balanced")
    council_parser.add_argument("--require-reviewer", action="store_true")

    show_workflow_parser = subparsers.add_parser("show-workflow")
    show_workflow_parser.add_argument("--workflow-id", required=True)

    show_personal_workflow_parser = subparsers.add_parser("show-personal-workflow")
    show_personal_workflow_parser.add_argument("--workflow-id", required=True)

    mail_plan_parser = subparsers.add_parser("mail-plan")
    mail_plan_parser.add_argument("--account-label", required=True)
    mail_plan_parser.add_argument("--goal", required=True)

    notion_plan_parser = subparsers.add_parser("notion-plan")
    notion_plan_parser.add_argument("--page-label", required=True)
    notion_plan_parser.add_argument("--objective", required=True)

    github_issue_draft_parser = subparsers.add_parser("github-issue-draft")
    github_issue_draft_parser.add_argument("--title", required=True)
    github_issue_draft_parser.add_argument("--objective", required=True)
    github_issue_draft_parser.add_argument("--context", required=True)
    github_issue_draft_parser.add_argument("--body", required=True)
    github_issue_draft_parser.add_argument("--labels", default="")

    github_pr_draft_parser = subparsers.add_parser("github-pr-draft")
    github_pr_draft_parser.add_argument("--title", required=True)
    github_pr_draft_parser.add_argument("--objective", required=True)
    github_pr_draft_parser.add_argument("--source-branch", required=True)
    github_pr_draft_parser.add_argument("--target-branch", required=True)
    github_pr_draft_parser.add_argument("--summary", required=True)
    github_pr_draft_parser.add_argument("--risk-notes", default="")

    github_create_branch_parser = subparsers.add_parser("github-create-branch")
    github_create_branch_parser.add_argument("--branch-name", required=True)
    github_create_branch_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_create_issue_parser = subparsers.add_parser("github-create-issue")
    github_create_issue_parser.add_argument("--title", required=True)
    github_create_issue_parser.add_argument("--body", required=True)
    github_create_issue_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_create_pr_parser = subparsers.add_parser("github-create-pr")
    github_create_pr_parser.add_argument("--title", required=True)
    github_create_pr_parser.add_argument("--body", required=True)
    github_create_pr_parser.add_argument("--base-branch", default="main")
    github_create_pr_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_smoke_issue_parser = subparsers.add_parser("github-smoke-issue")
    github_smoke_issue_parser.add_argument("--title", required=True)
    github_smoke_issue_parser.add_argument("--body", required=True)
    github_smoke_issue_parser.add_argument("--labels", default="")
    github_smoke_issue_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_smoke_pr_parser = subparsers.add_parser("github-smoke-pr")
    github_smoke_pr_parser.add_argument("--title", required=True)
    github_smoke_pr_parser.add_argument("--body", required=True)
    github_smoke_pr_parser.add_argument("--base-branch", default="main")
    github_smoke_pr_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    scaffold_report_parser = subparsers.add_parser("scaffold-report")
    scaffold_report_parser.add_argument("--title", required=True)
    scaffold_report_parser.add_argument("--workflow-id", required=True)
    scaffold_report_parser.add_argument("--summary", required=True)

    inbox_triage_parser = subparsers.add_parser("scaffold-inbox-triage")
    inbox_triage_parser.add_argument("--account-label", required=True)
    inbox_triage_parser.add_argument("--goal", required=True)

    linkedin_pack_parser = subparsers.add_parser("scaffold-linkedin-pack")
    linkedin_pack_parser.add_argument("--profile-label", required=True)
    linkedin_pack_parser.add_argument("--target-role", required=True)
    linkedin_pack_parser.add_argument("--focus", required=True)

    cv_pack_parser = subparsers.add_parser("scaffold-cv-pack")
    cv_pack_parser.add_argument("--target-role", required=True)
    cv_pack_parser.add_argument("--summary", required=True)

    outreach_draft_parser = subparsers.add_parser("scaffold-outreach-draft")
    outreach_draft_parser.add_argument("--recipient-label", required=True)
    outreach_draft_parser.add_argument("--purpose", required=True)
    outreach_draft_parser.add_argument("--notes", default="")

    internship_pack_parser = subparsers.add_parser("scaffold-internship-pack")
    internship_pack_parser.add_argument("--target-role", required=True)
    internship_pack_parser.add_argument("--company", required=True)
    internship_pack_parser.add_argument("--job-source", required=True)
    internship_pack_parser.add_argument("--fit-summary", required=True)

    showcase_case_study_parser = subparsers.add_parser("scaffold-showcase-case-study")
    showcase_case_study_parser.add_argument("--project-name", required=True)
    showcase_case_study_parser.add_argument("--objective", required=True)
    showcase_case_study_parser.add_argument("--highlights", required=True)

    portfolio_project_page_parser = subparsers.add_parser("scaffold-portfolio-project-page")
    portfolio_project_page_parser.add_argument("--project-name", required=True)
    portfolio_project_page_parser.add_argument("--summary", required=True)
    portfolio_project_page_parser.add_argument("--stack", required=True)

    truth_plan_parser = subparsers.add_parser("truth-plan")
    truth_plan_parser.add_argument("--question", required=True)
    truth_plan_parser.add_argument("--proposer", required=True)
    truth_plan_parser.add_argument("--challenger", required=True)
    truth_plan_parser.add_argument("--evidence", required=True)
    truth_plan_parser.add_argument("--evidence-quality", default="medium")
    truth_plan_parser.add_argument("--disagreement", default="medium")
    truth_plan_parser.add_argument("--source-count", default=1, type=int)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "env-diagnose":
            diagnosis = diagnose_environment()
            for label, tool in (
                ("python", diagnosis.python),
                ("git", diagnosis.git),
                ("gh", diagnosis.gh),
            ):
                print(f"{label}_found: {'yes' if tool.found else 'no'}")
                print(f"{label}_source: {tool.source}")
                print(f"{label}_path_visible: {'yes' if tool.path_visible else 'no'}")
                print(f"{label}_path: {tool.resolved_path or 'none'}")
                print(f"{label}_version: {tool.version or 'unknown'}")
                if label == "gh":
                    print(f"{label}_auth_known: {'yes' if tool.auth_known else 'no'}")
                    if tool.authenticated is None:
                        print(f"{label}_authenticated: unknown")
                    else:
                        print(f"{label}_authenticated: {'yes' if tool.authenticated else 'no'}")
                if tool.notes:
                    print(f"{label}_notes:")
                    for item in tool.notes:
                        print(f"- {item}")
            print("capabilities:")
            for capability in build_capability_summary(diagnosis):
                block = capability.blocking_issue or "none"
                print(
                    f"- {capability.capability_id} | {capability.state} | "
                    f"requires: {', '.join(capability.required_tools) or 'none'} | block: {block}"
                )
            return 0

        if args.command == "gh-auth-status":
            diagnostics = diagnose_gh_environment()
            print(f"gh_available: {'yes' if diagnostics.gh_available else 'no'}")
            print(f"gh_source: {diagnostics.source}")
            print(f"gh_path_visible: {'yes' if diagnostics.path_visible else 'no'}")
            print(f"gh_path: {diagnostics.gh_path or 'none'}")
            print(f"gh_version: {diagnostics.version or 'unknown'}")
            if not diagnostics.gh_available:
                print("status: skipped")
                print("reason: gh is missing in the current runtime environment")
            elif diagnostics.auth_known:
                print("status: checked")
                print(f"gh_authenticated: {'yes' if diagnostics.gh_authenticated else 'no'}")
            else:
                print("status: unknown")
                print("gh_authenticated: unknown")
            if diagnostics.notes:
                print("notes:")
                for item in diagnostics.notes:
                    print(f"- {item}")
            return 0

        if args.command == "capability-matrix":
            for capability in build_capability_summary():
                block = capability.blocking_issue or "none"
                print(
                    f"{capability.capability_id} | {capability.state} | "
                    f"requires: {', '.join(capability.required_tools) or 'none'} | block: {block}"
                )
            return 0

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
            if branch:
                print(f"branch: {branch}")
            print(f"runtime_data: {get_runtime_data_dir()}")
            print(f"tasks_total: {summary.total_tasks}")
            print(f"tasks_queued: {summary.queued_tasks}")
            print(f"tasks_running: {summary.running_tasks}")
            print(f"tasks_pending_approval: {summary.pending_approval_tasks}")
            print(f"tasks_waiting: {summary.waiting_tasks}")
            print(f"tasks_blocked_human_needed: {summary.blocked_human_needed_tasks}")
            print(f"tasks_interrupted: {summary.interrupted_tasks}")
            print(f"tasks_ready_to_resume: {summary.ready_to_resume_tasks}")
            print(f"tasks_completed: {summary.completed_tasks}")
            print(f"tasks_rejected: {summary.rejected_tasks}")
            print(f"tasks_failed: {summary.failed_tasks}")
            print(f"approval_requests_pending: {summary.pending_approval_requests}")
            print(f"tasks_file: {TASKS_PATH}")
            print(f"approvals_file: {APPROVALS_PATH}")
            print(f"approval_requests_file: {APPROVAL_REQUESTS_PATH}")
            print(f"supervisor_state_file: {SUPERVISOR_STATE_PATH}")
            print(f"handoff_snapshot_exists: {'yes' if snapshot_exists else 'no'}")
            return 0

        if args.command == "enqueue":
            with runtime_data_lock():
                task = enqueue_task(
                    title=args.title,
                    description=args.description,
                    risk_level=args.risk,
                    source=args.source,
                )
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            if task.approval_request_id:
                print(f"approval_request_id: {task.approval_request_id}")
            return 0

        if args.command == "queue-executor-action":
            with runtime_data_lock():
                task = enqueue_executor_task(
                    action_type=args.action_type,
                    target=args.target,
                    content=args.content,
                    source=args.source,
                )
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"executor_action_type: {task.executor_action_type}")
            print(f"executor_target: {task.executor_target or 'none'}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            if task.approval_request_id:
                print(f"approval_request_id: {task.approval_request_id}")
            return 0

        if args.command == "list":
            tasks = list_tasks()
            if not tasks:
                print("No tasks found.")
                return 0
            for task in tasks:
                print(
                    f"{task.task_id} | {task.status} | {task.risk_level} | "
                    f"{task.approval_state} | scope={task.workspace_scope} | "
                    f"policy={task.workspace_policy} | next={get_task_next_action(task)} | "
                    f"{task.title}"
                )
            return 0

        if args.command == "list-executor-tasks":
            tasks = list_executor_tasks()
            print(f"count: {len(tasks)}")
            if not tasks:
                print("tasks: none")
                return 0
            print("tasks:")
            for task in tasks:
                last_execution = task.execution_records[-1] if task.execution_records else None
                last_summary = last_execution.output_summary if last_execution else "not_run"
                print(
                    f"- {task.task_id} | {task.status} | action={task.executor_action_type} | "
                    f"target={task.executor_target or 'none'} | approval={task.approval_state} | "
                    f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                    f"last={_short_description(last_summary, limit=100)}"
                )
            return 0

        if args.command == "task-status":
            task = get_task(args.task_id)
            history = get_task_history(args.task_id)
            last_execution = task.execution_records[-1] if task.execution_records else None
            print(f"task_id: {task.task_id}")
            print(f"title: {task.title}")
            print(f"description: {task.description}")
            print(f"status: {task.status}")
            print(f"risk_level: {task.risk_level}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            print(f"source: {task.source}")
            print(f"executor_action_type: {task.executor_action_type or 'none'}")
            print(f"executor_target: {task.executor_target or 'none'}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            print(f"waiting_for: {task.waiting_for or 'none'}")
            print(f"blocked_reason: {task.blocked_reason or 'none'}")
            print(f"requires_human: {'yes' if task.requires_human else 'no'}")
            print(f"admin_required: {'yes' if task.admin_required else 'no'}")
            print(f"last_note: {task.last_note or 'none'}")
            print(f"created_at: {task.created_at}")
            print(f"updated_at: {task.updated_at}")
            print(f"next_action: {get_task_next_action(task)}")
            print(f"execution_count: {len(task.execution_records)}")
            print(f"last_execution_status: {last_execution.status if last_execution else 'not_run'}")
            print(f"last_execution_summary: {last_execution.output_summary if last_execution else 'none'}")
            print(f"last_artifact_path: {last_execution.artifact_path if last_execution and last_execution.artifact_path else 'none'}")
            print("target_paths:")
            if task.target_paths:
                for item in task.target_paths:
                    print(f"- {item}")
            else:
                print("- none")
            print("execution_history:")
            if task.execution_records:
                for item in task.execution_records:
                    print(
                        f"- {item.status} | started={item.started_at} | "
                        f"finished={item.finished_at or 'none'} | target={item.target or 'none'} | "
                        f"summary={item.output_summary or 'none'} | artifact={item.artifact_path or 'none'}"
                    )
            else:
                print("- none")
            print("history:")
            if history:
                for item in history:
                    print(
                        f"- {item.event_type} | {item.occurred_at} | "
                        f"actor={item.actor} | note={item.note or 'none'}"
                    )
            else:
                print("- none")
            return 0

        if args.command == "pending-approvals":
            requests = list_pending_approvals()
            print(f"count: {len(requests)}")
            if not requests:
                print("requests: none")
                return 0
            print("requests:")
            for request in requests:
                target = _approval_target(request.scope, request.task_id)
                description = _short_description(request.reason)
                print(
                    f"- {request.approval_id} | {request.status} | "
                    f"risk={request.risk_level} | task={request.task_id} | "
                    f"action={request.action_label} | target={target} | "
                    f"description={description} | workspace={request.workspace_scope} | "
                    f"policy={request.workspace_policy} | admin="
                    f"{'yes' if request.requires_admin else 'no'}"
                )
            return 0

        if args.command == "approval-status":
            if args.approval_id:
                request = get_approval_request(args.approval_id)
                history = list_approval_records(approval_id=request.approval_id)
                print(f"approval_id: {request.approval_id}")
                print(f"task_id: {request.task_id}")
                print(f"status: {request.status}")
                print(f"risk_level: {request.risk_level}")
                print(f"action_label: {request.action_label}")
                print(f"requested_at: {request.requested_at}")
                print(f"updated_at: {request.updated_at}")
                print(f"source: {request.source}")
                print(f"scope: {request.scope or 'none'}")
                print(f"workspace_scope: {request.workspace_scope}")
                print(f"workspace_policy: {request.workspace_policy}")
                print(f"workspace_reason: {request.workspace_reason or 'none'}")
                print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
                print(f"requires_admin: {'yes' if request.requires_admin else 'no'}")
                print(f"reason: {request.reason}")
                print(f"rollback_plan: {request.rollback_plan or 'none'}")
                print(f"human_note: {request.human_note or 'none'}")
                print("target_paths:")
                if request.target_paths:
                    for item in request.target_paths:
                        print(f"- {item}")
                else:
                    print("- none")
                print("decision_history:")
                if history:
                    for record in history:
                        print(
                            f"- {record.decision} | {record.decided_at} | "
                            f"note={record.note or 'none'}"
                        )
                else:
                    print("- none")
                return 0

            requests = list_approval_requests()
            print(f"count: {len(requests)}")
            if not requests:
                print("requests: none")
                return 0
            print("requests:")
            for request in requests:
                target = _approval_target(request.scope, request.task_id)
                description = _short_description(request.reason)
                print(
                    f"- {request.approval_id} | {request.status} | "
                    f"risk={request.risk_level} | task={request.task_id} | "
                    f"action={request.action_label} | target={target} | "
                    f"description={description} | workspace={request.workspace_scope} | "
                    f"policy={request.workspace_policy}"
                )
            return 0

        if args.command == "approve-approval":
            with runtime_data_lock():
                task, request = approve_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: approved")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "deny-approval":
            with runtime_data_lock():
                task, request = deny_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: denied")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "defer-approval":
            with runtime_data_lock():
                task, request = defer_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: deferred")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "request-approval":
            with runtime_data_lock():
                request = request_task_approval(
                    task_id=args.task_id,
                    action_label=args.action_label,
                    reason=args.reason,
                    risk_level=args.risk_level,
                    source=args.source,
                    scope=args.scope,
                    rollback_plan=args.rollback_plan,
                    requires_admin=args.requires_admin == "yes",
                )
            notification = build_approval_notification(request)
            print(f"approval_id: {request.approval_id}")
            print(f"task_id: {request.task_id}")
            print(f"status: {request.status}")
            print(f"risk_level: {request.risk_level}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"requires_admin: {'yes' if request.requires_admin else 'no'}")
            print(f"action_label: {request.action_label}")
            print(f"notification_mode: {notification.channel}")
            print(f"notification_title: {notification.title}")
            return 0

        if args.command == "approve":
            with runtime_data_lock():
                task = approve_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            return 0

        if args.command == "reject":
            with runtime_data_lock():
                task = reject_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            return 0

        if args.command == "wait":
            with runtime_data_lock():
                task = wait_task(args.task_id, reason=args.reason)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"waiting_for: {task.waiting_for}")
            return 0

        if args.command == "resume":
            with runtime_data_lock():
                task = resume_task(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "run-once":
            with runtime_data_lock():
                task = run_task_once(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            if task.execution_records:
                last_execution = task.execution_records[-1]
                print(f"execution_status: {last_execution.status}")
                print(f"execution_summary: {last_execution.output_summary or 'none'}")
                print(f"artifact_path: {last_execution.artifact_path or 'none'}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "execute-task":
            with runtime_data_lock():
                task = execute_task(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"executor_action_type: {task.executor_action_type or 'none'}")
            if task.execution_records:
                last_execution = task.execution_records[-1]
                print(f"execution_status: {last_execution.status}")
                print(f"execution_summary: {last_execution.output_summary or 'none'}")
                print(f"artifact_path: {last_execution.artifact_path or 'none'}")
            else:
                print("execution_status: not_run")
                print("execution_summary: none")
                print("artifact_path: none")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "mark-human-needed":
            with runtime_data_lock():
                task = mark_task_human_needed(task_id=args.task_id, reason=args.reason)
            notification = build_human_needed_notification(task)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"waiting_for: {task.waiting_for}")
            print(f"blocked_reason: {task.blocked_reason}")
            print(f"notification_mode: {notification.channel}")
            print(f"notification_title: {notification.title}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "review-task":
            with runtime_data_lock():
                task = review_task_for_resume(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"blocked_reason: {task.blocked_reason or 'none'}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "requeue-task":
            with runtime_data_lock():
                task = requeue_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "supervisor-status":
            state = get_supervisor_state()
            notification = build_supervisor_notification(state)
            print(f"supervisor_id: {state.supervisor_id}")
            print(f"mode: {state.mode}")
            print(f"status: {state.status}")
            print(f"active_task_id: {state.active_task_id or 'none'}")
            print(f"queued_count: {state.queued_count}")
            print(f"running_count: {state.running_count}")
            print(f"waiting_count: {state.waiting_count}")
            print(f"ready_to_resume_count: {state.ready_to_resume_count}")
            print(f"pending_approval_count: {state.pending_approval_count}")
            print(f"blocked_human_needed_count: {state.blocked_human_needed_count}")
            print(f"interrupted_count: {state.interrupted_count}")
            print(f"notification_mode: {state.notification_mode}")
            print(f"notification_title: {notification.title}")
            print(f"last_event: {state.last_event or 'none'}")
            print(f"updated_at: {state.updated_at}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")

            pending_requests = list_pending_approvals()
            print("pending_approvals:")
            if pending_requests:
                for request in pending_requests:
                    target = _approval_target(request.scope, request.task_id)
                    description = _short_description(request.reason)
                    print(
                        f"- {request.approval_id} | {request.status} | "
                        f"risk={request.risk_level} | task={request.task_id} | "
                        f"action={request.action_label} | target={target} | "
                        f"description={description} | workspace={request.workspace_scope} | "
                        f"policy={request.workspace_policy} | admin="
                        f"{'yes' if request.requires_admin else 'no'}"
                    )
            else:
                print("- none")

            blocked_tasks = list_blocked_tasks()
            print("human_needed_tasks:")
            if blocked_tasks:
                for task in blocked_tasks:
                    detail = task.blocked_reason or task.waiting_for or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            interrupted_tasks = list_interrupted_tasks()
            print("interrupted_tasks:")
            if interrupted_tasks:
                for task in interrupted_tasks:
                    detail = task.blocked_reason or task.last_note or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            waiting_tasks = list_waiting_tasks()
            print("waiting_tasks:")
            if waiting_tasks:
                for task in waiting_tasks:
                    detail = task.waiting_for or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            ready_to_resume_tasks = list_ready_to_resume_tasks()
            print("ready_to_resume_tasks:")
            if ready_to_resume_tasks:
                for task in ready_to_resume_tasks:
                    detail = task.last_note or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")
            return 0

        if args.command == "list-providers":
            for profile in list_provider_profiles():
                print(
                    f"{profile.provider_id} | {profile.display_name} | "
                    f"{profile.privacy_mode} | {profile.speed_bias}"
                )
            return 0

        if args.command == "list-integrations":
            for integration in list_supported_integrations():
                print(f"{integration.integration_id} | {integration.mode} | {integration.summary}")
            return 0

        if args.command == "github-status":
            summary = get_repo_status_summary()
            remote = get_remote_info()
            commits = get_recent_commits()
            print(f"repo_root: {summary.repo_root}")
            print(f"branch: {get_github_branch()}")
            print(f"clean: {'yes' if summary.is_clean else 'no'}")
            print(f"staged_changes: {summary.staged_changes}")
            print(f"unstaged_changes: {summary.unstaged_changes}")
            print(f"untracked_changes: {summary.untracked_changes}")
            print(f"origin_url: {remote.origin_url or 'none'}")
            print(f"gh_available: {'yes' if remote.gh_available else 'no'}")
            if remote.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if remote.gh_authenticated else 'no'}")
            print("recent_commits:")
            for commit in commits:
                print(f"- {commit.commit_hash} {commit.subject}")
            return 0

        if args.command == "github-gh-diagnose":
            diagnostics = diagnose_gh_environment()
            print(f"gh_available: {'yes' if diagnostics.gh_available else 'no'}")
            print(f"gh_path: {diagnostics.gh_path or 'none'}")
            print(f"source: {diagnostics.source}")
            print(f"path_visible: {'yes' if diagnostics.path_visible else 'no'}")
            print(f"version: {diagnostics.version or 'unknown'}")
            print(f"auth_known: {'yes' if diagnostics.auth_known else 'no'}")
            if diagnostics.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if diagnostics.gh_authenticated else 'no'}")
            if diagnostics.where_results:
                print("where_results:")
                for item in diagnostics.where_results:
                    print(f"- {item}")
            if diagnostics.notes:
                print("notes:")
                for item in diagnostics.notes:
                    print(f"- {item}")
            return 0

        if args.command == "github-remote-capability":
            capability = get_remote_capability()
            print(f"repo_root: {capability.repo_root}")
            print(f"branch: {capability.branch}")
            print(f"origin_url: {capability.origin_url or 'none'}")
            print(f"gh_available: {'yes' if capability.gh_available else 'no'}")
            if capability.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if capability.gh_authenticated else 'no'}")
            print(
                f"remote_write_possible: "
                f"{'yes' if capability.remote_actions_possible else 'no'}"
            )
            print(f"blocking_issue: {capability.blocking_issue or 'none'}")
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

        if args.command == "list-personal-workflows":
            for workflow in list_personal_workflows():
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

        if args.command == "show-personal-workflow":
            workflow = get_personal_workflow(args.workflow_id)
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

        if args.command == "mail-plan":
            plan = build_inbox_triage_plan(
                account_label=args.account_label,
                goal=args.goal,
            )
            print(f"account_label: {plan.account_label}")
            print(f"objective: {plan.objective}")
            print(f"mode: {plan.mode}")
            print("steps:")
            for item in plan.steps:
                print(f"- {item}")
            print("outputs:")
            for item in plan.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in plan.approval_points:
                print(f"- {item}")
            return 0

        if args.command == "notion-plan":
            plan = build_notion_update_plan(
                page_label=args.page_label,
                objective=args.objective,
            )
            print(f"page_label: {plan.page_label}")
            print(f"objective: {plan.objective}")
            print(f"mode: {plan.mode}")
            print("steps:")
            for item in plan.steps:
                print(f"- {item}")
            print("outputs:")
            for item in plan.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in plan.approval_points:
                print(f"- {item}")
            return 0

        if args.command == "github-issue-draft":
            output_path = scaffold_issue_draft(
                title=args.title,
                objective=args.objective,
                context=args.context,
                body=args.body,
                labels=args.labels,
            )
            print(f"github_draft_path: {output_path}")
            return 0

        if args.command == "github-pr-draft":
            output_path = scaffold_pr_draft(
                title=args.title,
                objective=args.objective,
                source_branch=args.source_branch,
                target_branch=args.target_branch,
                summary=args.summary,
                risk_notes=args.risk_notes,
            )
            print(f"github_draft_path: {output_path}")
            return 0

        if args.command == "github-create-branch":
            result = create_branch_with_approval(
                branch_name=args.branch_name,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-create-issue":
            result = create_issue_with_approval(
                title=args.title,
                body=args.body,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-create-pr":
            result = create_pr_with_approval(
                title=args.title,
                body=args.body,
                base_branch=args.base_branch,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-smoke-issue":
            result = create_smoke_issue_with_approval(
                title=args.title,
                body=args.body,
                labels=args.labels,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-smoke-pr":
            result = create_smoke_pr_with_approval(
                title=args.title,
                body=args.body,
                base_branch=args.base_branch,
                approved=args.approve == "yes",
            )
            print(result)
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

        if args.command == "scaffold-inbox-triage":
            output_path = scaffold_inbox_triage_pack(
                account_label=args.account_label,
                goal=args.goal,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-linkedin-pack":
            output_path = scaffold_linkedin_pack(
                profile_label=args.profile_label,
                target_role=args.target_role,
                focus=args.focus,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-cv-pack":
            output_path = scaffold_cv_pack(
                target_role=args.target_role,
                summary=args.summary,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-outreach-draft":
            output_path = scaffold_outreach_draft(
                recipient_label=args.recipient_label,
                purpose=args.purpose,
                notes=args.notes,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-internship-pack":
            output_path = scaffold_internship_application_pack(
                target_role=args.target_role,
                company=args.company,
                job_source=args.job_source,
                fit_summary=args.fit_summary,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-showcase-case-study":
            output_path = scaffold_showcase_case_study(
                project_name=args.project_name,
                objective=args.objective,
                highlights=args.highlights,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-portfolio-project-page":
            output_path = scaffold_portfolio_project_page(
                project_name=args.project_name,
                summary=args.summary,
                stack=args.stack,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "truth-plan":
            result = build_truth_council_result(
                question=args.question,
                proposer_summary=args.proposer,
                challenger_summary=args.challenger,
                evidence_summary=args.evidence,
                evidence_quality=args.evidence_quality,
                disagreement_level=args.disagreement,
                source_count=args.source_count,
            )
            print(f"question: {result.question}")
            print(f"lead_answer: {result.lead_answer}")
            print(f"dissent: {result.dissent}")
            print(f"consensus_level: {result.consensus_level}")
            print(f"confidence_score: {result.confidence_score}")
            print(f"evidence_quality_notes: {result.evidence_quality_notes}")
            if result.notes:
                print("notes:")
                for note in result.notes:
                    print(f"- {note}")
            return 0

        if args.command == "publish-check":
            report = scan_publishability()
            print(f"scanned_files: {report.scanned_files}")
            print(f"finding_count: {report.finding_count}")
            counts = report.category_counts()
            if counts:
                print("categories:")
                for category in sorted(counts):
                    print(f"- {category}: {counts[category]}")
            if report.findings:
                print("findings:")
                for finding in report.findings:
                    print(f"- [{finding.category}] {finding.path} :: {finding.detail}")
            else:
                print("findings: none")
            return 0

        if args.command == "publish-check-core":
            report = scan_publishability(core_only=True)
            print(f"scanned_files: {report.scanned_files}")
            print(f"finding_count: {report.finding_count}")
            counts = report.category_counts()
            if counts:
                print("categories:")
                for category in sorted(counts):
                    print(f"- {category}: {counts[category]}")
            if report.findings:
                print("findings:")
                for finding in report.findings:
                    print(f"- [{finding.category}] {finding.path} :: {finding.detail}")
            else:
                print("findings: none")
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
