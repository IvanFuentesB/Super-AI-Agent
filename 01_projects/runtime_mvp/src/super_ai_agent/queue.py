from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import (
    ApprovalRecord,
    ApprovalRequest,
    RuntimeStatusSummary,
    SupervisorState,
    Task,
    TASK_RISK_LEVELS,
)
from .storage import (
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
QUEUEABLE_TASK_STATUSES = {"queued", "running", "waiting", "blocked_human_needed"}


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


def _requires_approval(risk_level: str) -> bool:
    return risk_level != "safe"


def _requires_admin(risk_level: str) -> bool:
    return risk_level == "admin"


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
    )


def _backfill_pending_approval_requests() -> tuple[list[Task], list[ApprovalRequest]]:
    tasks = read_tasks()
    requests = read_approval_requests()
    known_request_ids = {request.approval_id for request in requests}
    changed = False

    for task in tasks:
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
        queued_count=sum(1 for task in tasks if task.status == "queued"),
        running_count=sum(1 for task in tasks if task.status == "running"),
        notification_mode=previous_state.notification_mode or "dashboard",
        updated_at=_now(),
        last_event=last_event if last_event is not None else previous_state.last_event,
        notes=[
            "Local-only supervisor foundation is active.",
            "Remote or admin actions must remain explicit and approval-gated.",
        ],
    )
    write_supervisor_state(state)
    return state


def enqueue_task(title: str, description: str, risk_level: str, source: str = "manual") -> Task:
    if risk_level not in ALLOWED_RISKS:
        raise ValueError(f"Unsupported risk level: {risk_level}")

    timestamp = _now()
    requires_approval = _requires_approval(risk_level)
    task = Task(
        task_id=_new_task_id(),
        title=title,
        description=description,
        risk_level=risk_level,
        status="queued",
        requires_approval=requires_approval,
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
        task.waiting_for = "human_approval"
        task.requires_human = True
        approval_requests.append(approval_request)
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
    requests = read_approval_requests()
    return _find_approval_request(requests, approval_id)


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

    task.requires_approval = True
    task.admin_required = _requires_admin(task.risk_level) if requires_admin is None else requires_admin
    task.status = "pending_approval"
    task.approval_state = "pending"
    task.waiting_for = "human_approval"
    task.requires_human = True
    task.blocked_reason = ""
    task.last_note = reason
    task.updated_at = timestamp

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


def approve_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")

    timestamp = _now()
    task.status = "queued"
    task.approval_state = "approved"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.last_note = note
    task.updated_at = timestamp
    write_tasks(tasks)

    approval_id = task.approval_request_id
    requests = read_approval_requests()
    if approval_id:
        request = _find_approval_request(requests, approval_id)
        request.status = "approved"
        request.updated_at = timestamp
        request.human_note = note
        write_approval_requests(requests)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision="approved",
            decided_at=timestamp,
            note=note,
            approval_id=approval_id,
        )
    )
    write_approvals(approvals)
    refresh_supervisor_state(last_event=f"Approval granted for task {task.task_id}")
    return task


def reject_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")

    timestamp = _now()
    task.status = "rejected"
    task.approval_state = "denied"
    task.waiting_for = ""
    task.blocked_reason = "Human denied the requested action."
    task.requires_human = False
    task.last_note = note
    task.updated_at = timestamp
    write_tasks(tasks)

    approval_id = task.approval_request_id
    requests = read_approval_requests()
    if approval_id:
        request = _find_approval_request(requests, approval_id)
        request.status = "denied"
        request.updated_at = timestamp
        request.human_note = note
        write_approval_requests(requests)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision="denied",
            decided_at=timestamp,
            note=note,
            approval_id=approval_id,
        )
    )
    write_approvals(approvals)
    refresh_supervisor_state(last_event=f"Approval denied for task {task.task_id}")
    return task


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
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task waiting: {task.task_id}")
    return task


def resume_task(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status not in {"waiting", "blocked_human_needed"}:
        raise ValueError(f"Task {task_id} must be waiting or human-needed before resume.")
    if task.approval_state == "pending":
        raise ValueError(f"Task {task_id} still needs approval before resume.")

    task.status = "queued"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
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
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task blocked for human input: {task.task_id}")
    return task


def run_task_once(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "queued":
        raise ValueError(f"Task {task.task_id} must be queued before run-once.")
    if task.approval_state not in {"approved", "not_required"}:
        raise ValueError(f"Task {task.task_id} must be approved before run-once.")

    task.status = "completed"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task completed: {task.task_id}")
    return task


def list_pending_approvals() -> list[ApprovalRequest]:
    return list_approval_requests(status="pending")


def list_blocked_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "blocked_human_needed"]


def list_waiting_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "waiting"]


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
        completed_tasks=sum(1 for task in tasks if task.status == "completed"),
        rejected_tasks=sum(1 for task in tasks if task.status == "rejected"),
        failed_tasks=sum(1 for task in tasks if task.status == "failed"),
        pending_approval_requests=sum(
            1 for request in approval_requests if request.status == "pending"
        ),
    )
