from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NotionPlan:
    page_label: str
    objective: str
    mode: str
    steps: list[str]
    outputs: list[str]
    approval_points: list[str]


def get_notion_adapter_mode() -> str:
    return "planning_only"


def build_notion_update_plan(page_label: str, objective: str) -> NotionPlan:
    return NotionPlan(
        page_label=page_label,
        objective=objective,
        mode=get_notion_adapter_mode(),
        steps=[
            "capture page or workspace context",
            "outline the update structure",
            "prepare a write plan and sync notes",
            "hold live writes behind approval",
        ],
        outputs=[
            "page update plan",
            "section outline",
            "sync checklist",
        ],
        approval_points=[
            "connecting live Notion integration",
            "writing to the workspace",
        ],
    )
