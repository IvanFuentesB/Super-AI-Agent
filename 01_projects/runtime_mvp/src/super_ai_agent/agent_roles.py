from __future__ import annotations

import json
from dataclasses import dataclass

from .storage import get_project_root
from .mcp_runtime import call_mcp_tool

CONFIG_PATH = get_project_root().parents[1] / "23_configs" / "agent_roles.example.json"


@dataclass
class SpecialistRole:
    role_id: str
    purpose: str
    allowed_tools: list[str]
    preferred_provider: str
    approval_sensitivity: str
    notes: str

    @classmethod
    def from_dict(cls, data: dict) -> "SpecialistRole":
        return cls(**data)


@dataclass
class SpecialistRoleStatus:
    current_role_id: str
    current_role_purpose: str
    current_role_provider: str
    current_role_sensitivity: str
    current_role_reason: str
    registry_count: int
    roles: list[SpecialistRole]


def _load_role_payload() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_agent_roles() -> list[SpecialistRole]:
    payload = _load_role_payload()
    return [
        SpecialistRole.from_dict(item)
        for item in payload.get("roles", [])
        if isinstance(item, dict)
    ]


def get_agent_role(role_id: str) -> SpecialistRole:
    for role in list_agent_roles():
        if role.role_id == role_id:
            return role
    raise ValueError(f"Agent role not found: {role_id}")


def infer_agent_role_for_task(task) -> tuple[str, str]:
    if not task:
        return ("supervisor", "No active task is running, so Ghoti stays in the supervisor role.")

    action_type = str(getattr(task, "executor_action_type", "") or "").strip().lower()
    target = str(getattr(task, "executor_target", "") or "").strip().lower()
    title = str(getattr(task, "title", "") or "").strip().lower()
    description = str(getattr(task, "description", "") or "").strip().lower()
    payload = dict(getattr(task, "executor_payload", {}) or {})
    recipe_name = str(payload.get("recipe_name", "") or "").strip().lower()
    haystack = " ".join(part for part in [title, description, target, recipe_name] if part)

    if any(keyword in haystack for keyword in ("outreach", "lead", "business", "offer")):
        return ("outreach_operator", "The active task is outreach-oriented and stays human-reviewed.")
    if any(keyword in haystack for keyword in ("video", "transcript", "ingest", "summar")):
        return ("research_video_ingest", "The active task is about ingesting or summarizing research/video material.")
    if any(keyword in haystack for keyword in ("finance", "budget", "spend", "price", "invest", "risk")):
        return ("finance_risk_gate", "The active task touches money or risk language and should stay tightly gated.")
    if any(keyword in haystack for keyword in ("memory", "handoff", "summary", "decision extract", "plan extract")):
        return ("memory_summarizer", "The active task is summarization or compact-memory oriented.")
    if action_type == "run_operator_recipe" and recipe_name == "codex_to_chatgpt_handoff_mvp":
        return ("browser_operator", "The active task is a browser-facing handoff workflow.")
    if action_type in {
        "focus_window",
        "open_allowed_app",
        "get_active_window",
        "list_windows",
        "paste_clipboard",
        "send_hotkey",
    } and any(keyword in haystack for keyword in ("browser", "chatgpt", "codex", "dashboard_browser")):
        return ("browser_operator", "The active task is browser-window oriented.")
    if any(keyword in haystack for keyword in ("dashboard", "frontend", "html", "css", "ui", "design")):
        return ("frontend_design", "The active task is UI- or dashboard-facing work.")
    if action_type in {
        "read_file",
        "write_file",
        "append_file",
        "create_artifact",
        "list_directory",
        "git_status",
        "git_diff",
        "run_checker",
    }:
        return ("backend_engineer", "The active task is repo-local engineering work.")

    return ("supervisor", "The active task stays under the narrow supervisor/operator role.")


def get_specialist_role_status(active_task=None) -> SpecialistRoleStatus:
    roles = list_agent_roles()
    current_role_id, current_role_reason = infer_agent_role_for_task(active_task)
    current_role = get_agent_role(current_role_id)
    return SpecialistRoleStatus(
        current_role_id=current_role.role_id,
        current_role_purpose=current_role.purpose,
        current_role_provider=current_role.preferred_provider,
        current_role_sensitivity=current_role.approval_sensitivity,
        current_role_reason=current_role_reason,
        registry_count=len(roles),
        roles=roles,
    )

_CAPABILITY_MAP: dict[str, tuple[str, dict | None]] = {
    # Basic health / repo reads
    "MCP_STATUS": ("ghoti_status", None),
    "MCP_REPO_SUMMARY": ("read_repo_summary", None),
    "MCP_CURRENT_STATE": ("read_current_state", None),
    "MCP_LATEST_OPERATOR_STATE": ("read_latest_operator_state", None),
    # Supervised pipeline reads (no-arg)
    "MCP_CONTROL_CENTER_STATE": ("read_control_center_state", None),
    "MCP_APPROVAL_INBOX": ("read_approval_inbox", None),
    "MCP_MANUAL_QUEUE": ("read_manual_execution_queue", None),
    "MCP_PIPELINE_ITEMS": ("read_pipeline_items_overview", None),
}


def call_agent_capability(capability_name: str, arguments: dict | None = None) -> dict:
    entry = _CAPABILITY_MAP.get(capability_name)
    if not entry:
        allowed = sorted(_CAPABILITY_MAP.keys())
        raise ValueError(f"Unknown capability: {capability_name!r}. Allowed: {allowed}")
    tool_name, default_args = entry
    effective_args = arguments if isinstance(arguments, dict) else default_args
    return {
        "capability": capability_name,
        "tool_name": tool_name,
        "result": call_mcp_tool(tool_name, effective_args),
    }

