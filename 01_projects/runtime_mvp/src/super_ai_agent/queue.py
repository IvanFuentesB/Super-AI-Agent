from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from .models import (
    ApprovalRecord,
    ApprovalRequest,
    RuntimeStatusSummary,
    SupervisorState,
    Task,
    TaskEvent,
    TASK_RISK_LEVELS,
)
from .storage import (
    get_allowed_workspace_root,
    read_approval_requests,
    read_approvals,
    read_supervisor_state,
    read_tasks,
    write_approval_requests,
    write_approvals,
    write_supervisor_state,
    write_tasks,
)

ALLOWED_RISKS = set(TASK_RISK_LEVELS)
QUEUEABLE_TASK_STATUSES = {"queued", "running", "waiting", "blocked_human_needed", "ready_to_resume"}
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)\b[A-Z]:\\[^\s\"'<>|?*]+")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_task_id() -> str:
    return f"task-{uuid4().hex[:12]}"


def _new_approval_id() -> str:
    return f"approval-{uuid4().hex[:12]}"


def _find_task(tasks: list[Task], task_id: str) -> Task:
    for task in tasks:
        if task.task_id == task_id:
            return task
    raise ValueError(f"Task not found: {task_id}")


def _find_approval_request(
    requests: list[ApprovalRequest],
    approval_id: str,
) -> ApprovalRequest:
    for request in requests:
        if request.approval_id == approval_id:
            return request
    raise ValueError(f"Approval request not found: {approval_id}")


def _append_task_event(task: Task, event_type: str, note: str = "", actor: str = "system") -> None:
    task.history.append(
        TaskEvent(
            event_type=event_type,
            occurred_at=_now(),
            note=note,
            actor=actor,
        )
    )


def _ensure_task_history(task: Task) -> bool:
    if task.history:
        return False

    task.history.append(
        TaskEvent(
            event_type="created",
            occurred_at=task.created_at or _now(),
            note=task.title,
            actor="system",
        )
    )
    return True


def _task_next_action(task: Task) -> str:
    if task.status == "pending_approval":
        return "Resolve the approval request."
    if task.status == "blocked_human_needed":
        if task.workspace_policy == "blocked_by_workspace_policy":
            return "Keep blocked until the target is moved inside the workspace or policy changes."
        return "Mark the human-needed step as reviewed."
    if task.status == "waiting":
        return "Resume the task when the reply or external event arrives."
    if task.status == "ready_to_resume":
        return "Re-queue the task when you want it to continue."
    if task.status == "queued":
        return "Run the task manually when ready."
    if task.status == "completed":
        return "Review the completed output."
    return "Review the current task state."


def _requires_approval(risk_level: str) -> bool:
    return risk_level != "safe"


def _requires_admin(risk_level: str) -> bool:
    return risk_level == "admin"


def _normalize_candidate_path(path_value: str) -> str:
    try:
        return str(Path(path_value).expanduser().resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        return path_value


def _extract_candidate_paths(*texts: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    for text in texts:
        for match in WINDOWS_ABSOLUTE_PATH_PATTERN.findall(text or ""):
            candidate = match.rstrip(".,;:!?)]}\"'")
            if candidate and candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)

    return candidates


def _is_inside_allowed_root(path_value: str) -> bool:
    try:
        return Path(path_value).resolve(strict=False).is_relative_to(get_allowed_workspace_root())
    except (OSError, ValueError):
        return False


def _classify_workspace_targets(
    *texts: str,
) -> tuple[list[str], str, str, str]:
    allowed_root = get_allowed_workspace_root()
    candidate_paths = [_normalize_candidate_path(item) for item in _extract_candidate_paths(*texts)]

    if not candidate_paths:
        return (
            [],
            "no_path_detected",
            "allowed",
            f"No explicit absolute path target detected. Allowed workspace root: {allowed_root}",
        )

    outside = [item for item in candidate_paths if not _is_inside_allowed_root(item)]
    if outside:
        return (
            candidate_paths,
            "out_of_scope",
            "blocked_by_workspace_policy",
            (
                "Blocked by workspace policy. Target path is outside the allowed workspace root: "
                f"{allowed_root}"
            ),
        )

    return (
        candidate_paths,
        "in_scope",
        "allowed",
        f"Target path is inside the allowed workspace root: {allowed_root}",
    )


def _apply_workspace_policy(
    task: Task,
    *texts: str,
) -> Task:
    target_paths, workspace_scope, workspace_policy, workspace_reason = _classify_workspace_targets(*texts)
    task.target_paths = target_paths
    task.workspace_scope = workspace_scope
    task.workspace_policy = workspace_policy
    task.workspace_reason = workspace_reason
    if workspace_scope == "out_of_scope" and task.risk_level == "safe":
        task.risk_level = "high_risk"
    return task


def _build_approval_request(
    task: Task,
    action_label: str,
    reason: str,
    timestamp: str,
    source: str,
    scope: str = "",
    rollback_plan: str = "",
    requires_admin: bool | None = None,
) -> ApprovalRequest:
    admin_required = _requires_admin(task.risk_level) if requires_admin is None else requires_admin
    return ApprovalRequest(
        approval_id=_new_approval_id(),
        task_id=task.task_id,
        action_label=action_label,
        reason=reason,
        risk_level=task.risk_level,
        status="pending",
        requested_at=timestamp,
        updated_at=timestamp,
        source=source,
        scope=scope,
        requires_admin=admin_required,
        rollback_plan=rollback_plan,
        human_note="",
        target_paths=list(task.target_paths),
        workspace_scope=task.workspace_scope,
        workspace_policy=task.workspace_policy,
        workspace_reason=task.workspace_reason,
    )


def _backfill_pending_approval_requests() -> tuple[list[Task], list[ApprovalRequest]]:
    tasks = read_tasks()
    requests = read_approval_requests()
    known_request_ids = {request.approval_id for request in requests}
    request_lookup = {request.approval_id: request for request in requests}
    changed = False

    for task in tasks:
        if _ensure_task_history(task):
            changed = True

        if not task.workspace_reason and not task.target_paths:
            _apply_workspace_policy(task, task.title, task.description, task.source)
            changed = True

        if task.approval_request_id and task.approval_request_id in request_lookup:
            request = request_lookup[task.approval_request_id]
            if not request.workspace_reason and not request.target_paths:
                request.target_paths = list(task.target_paths)
                request.workspace_scope = task.workspace_scope
                request.workspace_policy = task.workspace_policy
                request.workspace_reason = task.workspace_reason
                changed = True

        needs_backfill = (
            task.status == "pending_approval"
            and task.approval_state in {"pending", "deferred"}
            and (
                not task.approval_request_id
                or task.approval_request_id not in known_request_ids
            )
        )
        if not needs_backfill:
            continue

        timestamp = _now()
        request = _build_approval_request(
            task=task,
            action_label=task.title,
            reason=task.description or task.title,
            timestamp=timestamp,
            source=task.source,
            scope="backfilled from existing pending task state",
            rollback_plan="Do not proceed until the human explicitly approves.",
            requires_admin=task.admin_required,
        )
        task.approval_request_id = request.approval_id
        task.updated_at = timestamp
        requests.append(request)
        known_request_ids.add(request.approval_id)
        changed = True

    if changed:
        write_tasks(tasks)
        write_approval_requests(requests)

    return tasks, requests


def _select_active_task_id(tasks: list[Task], target_status: str) -> str:
    matching = [task for task in tasks if task.status == target_status]
    if not matching:
        return ""
    matching.sort(key=lambda task: task.updated_at, reverse=True)
    return matching[0].task_id


def refresh_supervisor_state(last_event: str | None = None) -> SupervisorState:
    tasks, approval_requests = _backfill_pending_approval_requests()
    previous_state = read_supervisor_state()

    status = "idle"
    active_task_id = ""

    if any(task.status == "pending_approval" for task in tasks):
        status = "pending_approval"
        active_task_id = _select_active_task_id(tasks, "pending_approval")
    elif any(task.status == "blocked_human_needed" for task in tasks):
        status = "blocked_human_needed"
        active_task_id = _select_active_task_id(tasks, "blocked_human_needed")
    elif any(task.status == "waiting" for task in tasks):
        status = "waiting"
        active_task_id = _select_active_task_id(tasks, "waiting")
    elif any(task.status == "ready_to_resume" for task in tasks):
        status = "ready_to_resume"
        active_task_id = _select_active_task_id(tasks, "ready_to_resume")
    elif any(task.status == "running" for task in tasks):
        status = "running"
        active_task_id = _select_active_task_id(tasks, "running")
    elif any(task.status == "queued" for task in tasks):
        status = "queued"
        active_task_id = _select_active_task_id(tasks, "queued")

    state = SupervisorState(
        supervisor_id=previous_state.supervisor_id or "local-supervisor",
        mode=previous_state.mode or "local_only",
        status=status,
        active_task_id=active_task_id,
        pending_approval_count=sum(
            1 for request in approval_requests if request.status == "pending"
        ),
        blocked_human_needed_count=sum(
            1 for task in tasks if task.status == "blocked_human_needed"
        ),
        waiting_count=sum(1 for task in tasks if task.status == "waiting"),
        ready_to_resume_count=sum(1 for task in tasks if task.status == "ready_to_resume"),
        queued_count=sum(1 for task in tasks if task.status == "queued"),
        running_count=sum(1 for task in tasks if task.status == "running"),
        notification_mode=previous_state.notification_mode or "dashboard",
        updated_at=_now(),
        last_event=last_event if last_event is not None else previous_state.last_event,
        notes=[
            "Local-only supervisor foundation is active.",
            "Remote or admin actions must remain explicit and approval-gated.",
            "Stopped tasks move forward only through explicit operator actions.",
        ],
    )
    write_supervisor_state(state)
    return state


def enqueue_task(title: str, description: str, risk_level: str, source: str = "manual") -> Task:
    if risk_level not in ALLOWED_RISKS:
        raise ValueError(f"Unsupported risk level: {risk_level}")
    timestamp = _now()
    task = Task(
        task_id=_new_task_id(),
        title=title,
        description=description,
        risk_level=risk_level,
        status="queued",
        requires_approval=False,
        approval_state="not_required",
        created_at=timestamp,
        updated_at=timestamp,
        source=source,
        approval_request_id="",
        waiting_for="",
        blocked_reason="",
        requires_human=False,
        admin_required=_requires_admin(risk_level),
        last_note="",
    )
    _apply_workspace_policy(task, title, description, source)
    _append_task_event(task, "created", note=title)
    task.admin_required = _requires_admin(task.risk_level)
    requires_approval = _requires_approval(task.risk_level)
    task.requires_approval = requires_approval

    approval_requests = read_approval_requests()
    if requires_approval:
        approval_request = _build_approval_request(
            task=task,
            action_label=title,
            reason=description,
            timestamp=timestamp,
            source=source,
            scope="runtime task execution",
            rollback_plan="Do not proceed until the human explicitly approves.",
        )
        task.status = "pending_approval"
        task.approval_state = "pending"
        task.approval_request_id = approval_request.approval_id
        task.waiting_for = (
            "workspace_policy_review"
            if task.workspace_policy == "blocked_by_workspace_policy"
            else "human_approval"
        )
        task.requires_human = True
        task.blocked_reason = (
            task.workspace_reason
            if task.workspace_policy == "blocked_by_workspace_policy"
            else ""
        )
        approval_requests.append(approval_request)
        _append_task_event(
            task,
            "escalated",
            note=(
                task.workspace_reason
                if task.workspace_policy == "blocked_by_workspace_policy"
                else "Task requires human approval before execution."
            ),
        )
        write_approval_requests(approval_requests)

    tasks = read_tasks()
    tasks.append(task)
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task queued: {task.title}")
    return task


def list_tasks() -> list[Task]:
    tasks = read_tasks()
    return sorted(tasks, key=lambda task: task.created_at, reverse=True)


def get_task(task_id: str) -> Task:
    tasks = read_tasks()
    return _find_task(tasks, task_id)


def list_approval_requests(status: str | None = None) -> list[ApprovalRequest]:
    _, requests = _backfill_pending_approval_requests()
    if status:
        requests = [request for request in requests if request.status == status]
    return sorted(requests, key=lambda request: request.requested_at, reverse=True)


def get_approval_request(approval_id: str) -> ApprovalRequest:
    _, requests = _backfill_pending_approval_requests()
    return _find_approval_request(requests, approval_id)


def list_approval_records(
    *,
    approval_id: str = "",
    task_id: str = "",
) -> list[ApprovalRecord]:
    records = read_approvals()
    if approval_id:
        records = [record for record in records if record.approval_id == approval_id]
    if task_id:
        records = [record for record in records if record.task_id == task_id]
    return sorted(records, key=lambda record: record.decided_at, reverse=True)


def request_task_approval(
    task_id: str,
    action_label: str,
    reason: str,
    risk_level: str | None = None,
    source: str = "manual",
    scope: str = "",
    rollback_plan: str = "",
    requires_admin: bool | None = None,
) -> ApprovalRequest:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    timestamp = _now()

    if risk_level:
        if risk_level not in ALLOWED_RISKS:
            raise ValueError(f"Unsupported risk level: {risk_level}")
        task.risk_level = risk_level

    _apply_workspace_policy(
        task,
        action_label,
        reason,
        source,
        scope,
        rollback_plan,
    )
    task.requires_approval = True
    task.admin_required = _requires_admin(task.risk_level) if requires_admin is None else requires_admin
    task.status = "pending_approval"
    task.approval_state = "pending"
    task.waiting_for = (
        "workspace_policy_review"
        if task.workspace_policy == "blocked_by_workspace_policy"
        else "human_approval"
    )
    task.requires_human = True
    task.blocked_reason = (
        task.workspace_reason
        if task.workspace_policy == "blocked_by_workspace_policy"
        else ""
    )
    task.last_note = reason
    task.updated_at = timestamp
    _ensure_task_history(task)
    _append_task_event(task, "escalated", note=reason)

    requests = read_approval_requests()
    approval_request = _build_approval_request(
        task=task,
        action_label=action_label,
        reason=reason,
        timestamp=timestamp,
        source=source,
        scope=scope or "runtime task execution",
        rollback_plan=rollback_plan,
        requires_admin=task.admin_required,
    )
    task.approval_request_id = approval_request.approval_id
    requests.append(approval_request)

    write_tasks(tasks)
    write_approval_requests(requests)
    refresh_supervisor_state(last_event=f"Approval requested for task {task.task_id}")
    return approval_request


def _resolve_approval_request(
    approval_id: str,
    decision: str,
    note: str = "",
) -> tuple[Task, ApprovalRequest]:
    if decision not in {"approved", "denied", "deferred"}:
        raise ValueError(f"Unsupported approval decision: {decision}")

    tasks = read_tasks()
    task_lookup = {task.task_id: task for task in tasks}
    requests = read_approval_requests()
    request = _find_approval_request(requests, approval_id)
    task = task_lookup.get(request.task_id)
    if task is None:
        raise ValueError(f"Task not found for approval request: {approval_id}")

    if request.status not in {"pending", "deferred"}:
        raise ValueError(f"Approval request is not actionable: {approval_id}")

    timestamp = _now()
    request.status = decision
    request.updated_at = timestamp
    request.human_note = note

    task.approval_request_id = request.approval_id
    task.updated_at = timestamp
    task.last_note = note
    _ensure_task_history(task)

    workspace_blocked = task.workspace_policy == "blocked_by_workspace_policy"

    if decision == "approved" and workspace_blocked:
        task.status = "blocked_human_needed"
        task.approval_state = "approved"
        task.waiting_for = "workspace_policy_override"
        task.blocked_reason = (
            task.workspace_reason
            or "Blocked by workspace policy until the allowed workspace root is expanded."
        )
        task.requires_human = True
        _append_task_event(task, "approved", note=note or "Human approved the request.")
        _append_task_event(
            task,
            "blocked_by_workspace_policy",
            note=task.blocked_reason,
        )
    elif decision == "approved":
        task.status = "queued"
        task.approval_state = "approved"
        task.waiting_for = ""
        task.blocked_reason = ""
        task.requires_human = False
        _append_task_event(task, "approved", note=note or "Human approved the request.")
    elif decision == "denied":
        task.status = "rejected"
        task.approval_state = "denied"
        task.waiting_for = ""
        task.blocked_reason = "Human denied the requested action."
        task.requires_human = False
        _append_task_event(task, "denied", note=note or task.blocked_reason)
    else:
        task.status = "waiting"
        task.approval_state = "deferred"
        task.waiting_for = "approval deferred by human"
        task.blocked_reason = note or "Human deferred the requested action."
        task.requires_human = True
        _append_task_event(task, "deferred", note=note or task.blocked_reason)

    write_tasks(tasks)
    write_approval_requests(requests)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision=decision,
            decided_at=timestamp,
            note=note,
            approval_id=approval_id,
        )
    )
    write_approvals(approvals)

    event_map = {
        "approved": (
            f"Approval recorded, but workspace policy still blocks task {task.task_id}"
            if workspace_blocked
            else f"Approval granted for task {task.task_id}"
        ),
        "denied": f"Approval denied for task {task.task_id}",
        "deferred": f"Approval deferred for task {task.task_id}",
    }
    refresh_supervisor_state(last_event=event_map[decision])
    return task, request


def approve_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="approved", note=note)


def deny_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="denied", note=note)


def defer_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="deferred", note=note)


def approve_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")
    if task.approval_request_id:
        task, _ = approve_approval_request(task.approval_request_id, note=note)
        return task
    raise ValueError(f"Task is missing an approval request id: {task_id}")


def reject_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")
    if task.approval_request_id:
        task, _ = deny_approval_request(task.approval_request_id, note=note)
        return task
    raise ValueError(f"Task is missing an approval request id: {task_id}")


def wait_task(task_id: str, reason: str = "waiting for human reply or external event") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status not in {"queued", "running"}:
        raise ValueError(f"Task {task_id} must be queued or running before wait.")

    task.status = "waiting"
    task.waiting_for = reason
    task.requires_human = True
    task.last_note = reason
    task.updated_at = _now()
    _ensure_task_history(task)
    _append_task_event(task, "waiting", note=reason)
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task waiting: {task.task_id}")
    return task


def resume_task(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "waiting":
        raise ValueError(f"Task {task_id} must be waiting before resume.")
    if task.approval_state == "pending":
        raise ValueError(f"Task {task_id} still needs approval before resume.")

    task.status = "queued"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    _ensure_task_history(task)
    _append_task_event(task, "resumed", note="Operator resumed the waiting task.")
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task resumed: {task.task_id}")
    return task


def mark_task_human_needed(task_id: str, reason: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status in {"completed", "rejected", "failed"}:
        raise ValueError(f"Task {task_id} is already finished and cannot be marked human-needed.")

    task.status = "blocked_human_needed"
    task.waiting_for = "human_reply"
    task.blocked_reason = reason
    task.requires_human = True
    task.last_note = reason
    task.updated_at = _now()
    _ensure_task_history(task)
    _append_task_event(task, "human_needed", note=reason)
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task blocked for human input: {task.task_id}")
    return task


def review_task_for_resume(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "blocked_human_needed":
        raise ValueError(f"Task {task_id} must be human-needed before review.")

    timestamp = _now()
    task.updated_at = timestamp
    task.last_note = note
    _ensure_task_history(task)

    if task.workspace_policy == "blocked_by_workspace_policy":
        task.waiting_for = "workspace_policy_override"
        task.blocked_reason = (
            task.workspace_reason
            or "Task remains blocked until the target is moved inside the workspace."
        )
        task.requires_human = True
        _append_task_event(
            task,
            "blocked_by_workspace_policy",
            note=note or task.blocked_reason,
        )
        write_tasks(tasks)
        refresh_supervisor_state(last_event=f"Task remains workspace-blocked: {task.task_id}")
        return task

    task.status = "ready_to_resume"
    task.waiting_for = "operator_requeue"
    task.blocked_reason = ""
    task.requires_human = False
    _append_task_event(
        task,
        "ready_to_resume",
        note=note or "Human-needed review completed; task is ready to re-queue.",
    )
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task ready to resume: {task.task_id}")
    return task


def requeue_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "ready_to_resume":
        raise ValueError(f"Task {task_id} must be ready_to_resume before re-queue.")
    if task.workspace_policy == "blocked_by_workspace_policy":
        raise ValueError(
            "Task is blocked by workspace policy until the allowed workspace root is expanded "
            "or the target is moved inside the workspace."
        )

    task.status = "queued"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    task.last_note = note
    _ensure_task_history(task)
    _append_task_event(task, "resumed", note=note or "Operator re-queued the task.")
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task re-queued: {task.task_id}")
    return task


def run_task_once(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "queued":
        raise ValueError(f"Task {task.task_id} must be queued before run-once.")
    if task.approval_state not in {"approved", "not_required"}:
        raise ValueError(f"Task {task.task_id} must be approved before run-once.")
    if task.workspace_policy == "blocked_by_workspace_policy":
        raise ValueError(
            "Task is blocked by workspace policy until the allowed workspace root is expanded "
            "or the target is moved inside the workspace."
        )

    task.status = "completed"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    _ensure_task_history(task)
    _append_task_event(task, "completed", note="Task completed in manual run-once mode.")
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task completed: {task.task_id}")
    return task


def list_pending_approvals() -> list[ApprovalRequest]:
    return list_approval_requests(status="pending")


def list_blocked_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "blocked_human_needed"]


def list_waiting_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "waiting"]


def list_ready_to_resume_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "ready_to_resume"]


def get_supervisor_state() -> SupervisorState:
    return refresh_supervisor_state()


def get_status_summary() -> RuntimeStatusSummary:
    tasks = read_tasks()
    approval_requests = read_approval_requests()
    return RuntimeStatusSummary(
        total_tasks=len(tasks),
        queued_tasks=sum(1 for task in tasks if task.status == "queued"),
        running_tasks=sum(1 for task in tasks if task.status == "running"),
        waiting_tasks=sum(1 for task in tasks if task.status == "waiting"),
        pending_approval_tasks=sum(1 for task in tasks if task.status == "pending_approval"),
        blocked_human_needed_tasks=sum(
            1 for task in tasks if task.status == "blocked_human_needed"
        ),
        ready_to_resume_tasks=sum(
            1 for task in tasks if task.status == "ready_to_resume"
        ),
        completed_tasks=sum(1 for task in tasks if task.status == "completed"),
        rejected_tasks=sum(1 for task in tasks if task.status == "rejected"),
        failed_tasks=sum(1 for task in tasks if task.status == "failed"),
        pending_approval_requests=sum(
            1 for request in approval_requests if request.status == "pending"
        ),
    )


def get_task_history(task_id: str) -> list[TaskEvent]:
    task = get_task(task_id)
    return list(task.history)


def get_task_next_action(task: Task) -> str:
    return _task_next_action(task)
