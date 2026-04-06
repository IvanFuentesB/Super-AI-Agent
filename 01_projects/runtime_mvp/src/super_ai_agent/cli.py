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
from .personal_ops import (
    get_personal_workflow,
    list_personal_workflows,
    scaffold_cv_pack,
    scaffold_inbox_triage_pack,
    scaffold_internship_application_pack,
    scaffold_linkedin_pack,
    scaffold_outreach_draft,
)
from .publishability import scan_publishability
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
