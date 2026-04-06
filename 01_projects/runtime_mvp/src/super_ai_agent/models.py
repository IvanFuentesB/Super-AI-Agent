from __future__ import annotations

from dataclasses import asdict, dataclass


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

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)


@dataclass
class ApprovalRecord:
    task_id: str
    decision: str
    decided_at: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ApprovalRecord":
        return cls(**data)


@dataclass
class RuntimeStatusSummary:
    total_tasks: int
    queued_tasks: int
    pending_approval_tasks: int
    rejected_tasks: int
