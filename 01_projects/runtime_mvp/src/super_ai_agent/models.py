from __future__ import annotations

from dataclasses import asdict, dataclass, field

TASK_RISK_LEVELS = ("safe", "ask", "high_risk", "admin")
WORKSPACE_SCOPES = ("no_path_detected", "in_scope", "out_of_scope")
WORKSPACE_POLICIES = ("allowed", "blocked_by_workspace_policy")
EXECUTOR_ACTION_TYPES = (
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
)
EXECUTION_STATUSES = ("started", "succeeded", "failed", "interrupted")
TASK_STATUSES = (
    "queued",
    "running",
    "waiting",
    "pending_approval",
    "blocked_human_needed",
    "interrupted",
    "ready_to_resume",
    "completed",
    "rejected",
    "failed",
)
APPROVAL_STATUSES = ("pending", "approved", "denied", "deferred", "expired", "not_required")


@dataclass
class TaskEvent:
    event_type: str
    occurred_at: str
    note: str = ""
    actor: str = "system"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskEvent":
        return cls(
            event_type=data.get("event_type", "unknown"),
            occurred_at=data.get("occurred_at", ""),
            note=data.get("note", ""),
            actor=data.get("actor", "system"),
        )


@dataclass
class TaskExecutionRecord:
    action_type: str
    target: str
    started_at: str
    status: str
    success: bool
    output_summary: str = ""
    finished_at: str = ""
    artifact_path: str = ""
    actor: str = "system"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskExecutionRecord":
        return cls(
            action_type=data.get("action_type", ""),
            target=data.get("target", ""),
            started_at=data.get("started_at", ""),
            status=data.get("status", "started"),
            success=bool(data.get("success", False)),
            output_summary=data.get("output_summary", ""),
            finished_at=data.get("finished_at", ""),
            artifact_path=data.get("artifact_path", ""),
            actor=data.get("actor", "system"),
        )


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
    target_paths: list[str] = field(default_factory=list)
    workspace_scope: str = "no_path_detected"
    workspace_policy: str = "allowed"
    workspace_reason: str = ""
    executor_action_type: str = ""
    executor_target: str = ""
    executor_payload: dict = field(default_factory=dict)
    history: list[TaskEvent] = field(default_factory=list)
    execution_records: list[TaskExecutionRecord] = field(default_factory=list)

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
            target_paths=list(data.get("target_paths", [])),
            workspace_scope=data.get("workspace_scope", "no_path_detected"),
            workspace_policy=data.get("workspace_policy", "allowed"),
            workspace_reason=data.get("workspace_reason", ""),
            executor_action_type=data.get("executor_action_type", ""),
            executor_target=data.get("executor_target", ""),
            executor_payload=dict(data.get("executor_payload", {})),
            history=[
                TaskEvent.from_dict(item)
                for item in data.get("history", [])
                if isinstance(item, dict)
            ],
            execution_records=[
                TaskExecutionRecord.from_dict(item)
                for item in data.get("execution_records", [])
                if isinstance(item, dict)
            ],
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
    target_paths: list[str] = field(default_factory=list)
    workspace_scope: str = "no_path_detected"
    workspace_policy: str = "allowed"
    workspace_reason: str = ""

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
            target_paths=list(data.get("target_paths", [])),
            workspace_scope=data.get("workspace_scope", "no_path_detected"),
            workspace_policy=data.get("workspace_policy", "allowed"),
            workspace_reason=data.get("workspace_reason", ""),
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
    interrupted_count: int
    waiting_count: int
    ready_to_resume_count: int
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
            interrupted_count=int(data.get("interrupted_count", 0)),
            waiting_count=int(data.get("waiting_count", 0)),
            ready_to_resume_count=int(data.get("ready_to_resume_count", 0)),
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
    interrupted_tasks: int = 0
    ready_to_resume_tasks: int = 0
    completed_tasks: int = 0
    rejected_tasks: int = 0
    failed_tasks: int = 0
    pending_approval_requests: int = 0
