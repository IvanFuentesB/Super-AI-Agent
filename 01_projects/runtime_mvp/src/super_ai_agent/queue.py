from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import ApprovalRecord, RuntimeStatusSummary, Task
from .storage import read_approvals, read_tasks, write_approvals, write_tasks

ALLOWED_RISKS = {"safe", "ask", "high_risk"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_task_id() -> str:
    return f"task-{uuid4().hex[:12]}"


def _find_task(tasks: list[Task], task_id: str) -> Task:
    for task in tasks:
        if task.task_id == task_id:
            return task
    raise ValueError(f"Task not found: {task_id}")


def enqueue_task(title: str, description: str, risk_level: str, source: str = "manual") -> Task:
    if risk_level not in ALLOWED_RISKS:
        raise ValueError(f"Unsupported risk level: {risk_level}")

    timestamp = _now()
    requires_approval = risk_level != "safe"
    task = Task(
        task_id=_new_task_id(),
        title=title,
        description=description,
        risk_level=risk_level,
        status="pending_approval" if requires_approval else "queued",
        requires_approval=requires_approval,
        approval_state="pending" if requires_approval else "not_required",
        created_at=timestamp,
        updated_at=timestamp,
        source=source,
    )

    tasks = read_tasks()
    tasks.append(task)
    write_tasks(tasks)
    return task


def list_tasks() -> list[Task]:
    tasks = read_tasks()
    return sorted(tasks, key=lambda task: task.created_at, reverse=True)


def approve_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state != "pending":
        raise ValueError(f"Task is not pending approval: {task_id}")

    task.status = "queued"
    task.approval_state = "approved"
    task.updated_at = _now()
    write_tasks(tasks)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision="approved",
            decided_at=task.updated_at,
            note=note,
        )
    )
    write_approvals(approvals)
    return task


def reject_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state != "pending":
        raise ValueError(f"Task is not pending approval: {task_id}")

    task.status = "rejected"
    task.approval_state = "rejected"
    task.updated_at = _now()
    write_tasks(tasks)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision="rejected",
            decided_at=task.updated_at,
            note=note,
        )
    )
    write_approvals(approvals)
    return task


def get_status_summary() -> RuntimeStatusSummary:
    tasks = read_tasks()
    return RuntimeStatusSummary(
        total_tasks=len(tasks),
        queued_tasks=sum(1 for task in tasks if task.status == "queued"),
        pending_approval_tasks=sum(1 for task in tasks if task.status == "pending_approval"),
        rejected_tasks=sum(1 for task in tasks if task.status == "rejected"),
    )
