from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .models import ApprovalRequest, SupervisorState, Task


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class NotificationPayload:
    channel: str
    title: str
    body: str
    level: str
    created_at: str
    related_task_id: str = ""
    related_approval_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def get_notification_mode() -> str:
    return "local_dashboard"


def build_local_notification(
    title: str,
    body: str,
    level: str = "info",
    related_task_id: str = "",
    related_approval_id: str = "",
) -> NotificationPayload:
    return NotificationPayload(
        channel=get_notification_mode(),
        title=title,
        body=body,
        level=level,
        created_at=_now(),
        related_task_id=related_task_id,
        related_approval_id=related_approval_id,
    )


def build_approval_notification(request: ApprovalRequest) -> NotificationPayload:
    body = (
        f"{request.action_label} needs human approval. "
        f"Risk level: {request.risk_level}. "
        f"Admin required: {'yes' if request.requires_admin else 'no'}."
    )
    return build_local_notification(
        title="Approval requested",
        body=body,
        level="warning",
        related_task_id=request.task_id,
        related_approval_id=request.approval_id,
    )


def build_human_needed_notification(task: Task) -> NotificationPayload:
    detail = task.blocked_reason or task.waiting_for or "Human input is required."
    return build_local_notification(
        title="Human input needed",
        body=f"{task.title} is blocked. {detail}",
        level="warning",
        related_task_id=task.task_id,
        related_approval_id=task.approval_request_id,
    )


def build_supervisor_notification(state: SupervisorState) -> NotificationPayload:
    body = (
        f"Supervisor status is {state.status}. "
        f"Pending approvals: {state.pending_approval_count}. "
        f"Human-needed tasks: {state.blocked_human_needed_count}. "
        f"Waiting tasks: {state.waiting_count}."
    )
    return build_local_notification(
        title="Supervisor status",
        body=body,
        level="info",
        related_task_id=state.active_task_id,
    )
