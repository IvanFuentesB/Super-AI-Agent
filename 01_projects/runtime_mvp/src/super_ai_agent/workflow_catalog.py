from __future__ import annotations

import json
from dataclasses import dataclass

from .storage import get_project_root

WORKFLOW_CATALOG_PATH = get_project_root().parents[1] / "23_configs" / "workflow_catalog.example.json"


@dataclass
class WorkflowDefinition:
    workflow_id: str
    title: str
    purpose: str
    inputs: list[str]
    outputs: list[str]
    approval_points: list[str]
    notes: str

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowDefinition":
        return cls(**data)


def _load_catalog_payload() -> dict:
    with WORKFLOW_CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_workflows() -> list[WorkflowDefinition]:
    payload = _load_catalog_payload()
    return [WorkflowDefinition.from_dict(item) for item in payload.get("workflows", [])]


def get_workflow(workflow_id: str) -> WorkflowDefinition:
    for workflow in list_workflows():
        if workflow.workflow_id == workflow_id:
            return workflow
    raise ValueError(f"Workflow not found: {workflow_id}")
