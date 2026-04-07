from __future__ import annotations

from dataclasses import asdict, dataclass, field

TASK_RISK_LEVELS = ("safe", "ask", "high_risk", "admin")
TASK_STATUSES = (
    "queued",
    "running",
    "waiting",
    "pending_approval",
    "blocked_human_needed",
    "completed",
    "rejected",
    "failed",
)
APPROVAL_STATUSES = ("pending", "approved", "denied", "deferred", "expired", "not_required")


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    risk_level: str
    status: str
    requires_approval: bool
    approval_state: str
    created_at: str
    updated_at: str
    source: str
    approval_request_id: str = ""
    waiting_for: str = ""
    blocked_reason: str = ""
    requires_human: bool = False
    admin_required: bool = False
    last_note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            risk_level=data["risk_level"],
            status=data["status"],
            requires_approval=bool(data["requires_approval"]),
            approval_state=data["approval_state"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            source=data.get("source", "manual"),
            approval_request_id=data.get("approval_request_id", ""),
            waiting_for=data.get("waiting_for", ""),
            blocked_reason=data.get("blocked_reason", ""),
            requires_human=bool(data.get("requires_human", False)),
            admin_required=bool(data.get("admin_required", False)),
            last_note=data.get("last_note", ""),
        )


@dataclass
class ApprovalRequest:
    approval_id: str
    task_id: str
    action_label: str
    reason: str
    risk_level: str
    status: str
    requested_at: str
    updated_at: str
    source: str
    scope: str = ""
    requires_admin: bool = False
    rollback_plan: str = ""
    human_note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ApprovalRequest":
        return cls(
            approval_id=data["approval_id"],
            task_id=data["task_id"],
            action_label=data["action_label"],
            reason=data["reason"],
            risk_level=data["risk_level"],
            status=data["status"],
            requested_at=data["requested_at"],
            updated_at=data["updated_at"],
            source=data.get("source", "manual"),
            scope=data.get("scope", ""),
            requires_admin=bool(data.get("requires_admin", False)),
            rollback_plan=data.get("rollback_plan", ""),
            human_note=data.get("human_note", ""),
        )


@dataclass
class ApprovalRecord:
    task_id: str
    decision: str
    decided_at: str
    note: str
    approval_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ApprovalRecord":
        return cls(
            task_id=data["task_id"],
            decision=data["decision"],
            decided_at=data["decided_at"],
            note=data.get("note", ""),
            approval_id=data.get("approval_id", ""),
        )


@dataclass
class SupervisorState:
    supervisor_id: str
    mode: str
    status: str
    active_task_id: str
    pending_approval_count: int
    blocked_human_needed_count: int
    waiting_count: int
    queued_count: int
    running_count: int
    notification_mode: str
    updated_at: str
    last_event: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SupervisorState":
        return cls(
            supervisor_id=data.get("supervisor_id", "local-supervisor"),
            mode=data.get("mode", "local_only"),
            status=data.get("status", "idle"),
            active_task_id=data.get("active_task_id", ""),
            pending_approval_count=int(data.get("pending_approval_count", 0)),
            blocked_human_needed_count=int(data.get("blocked_human_needed_count", 0)),
            waiting_count=int(data.get("waiting_count", 0)),
            queued_count=int(data.get("queued_count", 0)),
            running_count=int(data.get("running_count", 0)),
            notification_mode=data.get("notification_mode", "dashboard"),
            updated_at=data.get("updated_at", ""),
            last_event=data.get("last_event", ""),
            notes=list(data.get("notes", [])),
        )


@dataclass
class RuntimeStatusSummary:
    total_tasks: int
    queued_tasks: int
    running_tasks: int = 0
    waiting_tasks: int = 0
    pending_approval_tasks: int = 0
    blocked_human_needed_tasks: int = 0
    completed_tasks: int = 0
    rejected_tasks: int = 0
    failed_tasks: int = 0
    pending_approval_requests: int = 0
