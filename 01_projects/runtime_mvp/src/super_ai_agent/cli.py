from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .agent_roles import get_specialist_role_status, list_agent_roles
from .brain import (
    BrainInferenceError,
    get_brain_status,
    run_brain_inference,
    save_brain_config_override,
)
from .browser_agent import get_browser_capability_status
from .council import build_council_plan
from .environment import build_capability_summary, diagnose_environment
from .github_actions import (
    create_branch_with_approval,
    create_issue_with_approval,
    create_pr_with_approval,
    create_smoke_issue_with_approval,
    create_smoke_pr_with_approval,
    scaffold_issue_draft,
    scaffold_pr_draft,
)
from .github_adapter import diagnose_gh_environment, get_remote_capability
from .github_adapter import get_current_branch as get_github_branch
from .github_adapter import get_recent_commits, get_remote_info, get_repo_status_summary
from .handoff import build_handoff_snapshot
from .integrations import list_supported_integrations
from .mail_adapter import build_inbox_triage_plan
from .memory_layer import get_memory_layer_status
from .mcp_runtime import call_mcp_tool
from .relay_loop import (
    get_relay_loop_status,
    save_codex_preset,
    save_relay_target_binding,
    update_relay_loop_state,
)
from .notion_adapter import build_notion_update_plan
from .action_intent import (
    create_action_intent,
    consume_action_intent,
    get_action_intent_read_model,
    list_capability_adapters,
)
from .control_center_state import get_full_control_center_state, get_pipeline_items_overview
from .operator_loop import (
    APPROVAL_INBOX_PATH,
    MANUAL_EXECUTION_QUEUE_PATH,
    OPERATOR_STATE_FILE,
    explain_manual_queue_item,
    find_latest_approved_approval_item,
    get_approval_item,
    get_audit_trace,
    get_manual_queue_item,
    read_approval_inbox_state,
    read_latest_operator_state,
    read_manual_queue_state,
    simple_operator_tick,
    update_approval_item_status,
    update_manual_queue_item_review,
)
from .notification_adapter import (
    build_approval_notification,
    build_human_needed_notification,
    build_supervisor_notification,
)
from .personal_ops import (
    get_personal_workflow,
    list_personal_workflows,
    scaffold_cv_pack,
    scaffold_inbox_triage_pack,
    scaffold_internship_application_pack,
    scaffold_linkedin_pack,
    scaffold_outreach_draft,
    scaffold_portfolio_project_page,
    scaffold_showcase_case_study,
)
from .publishability import scan_publishability
from .providers import list_provider_profiles
from .queue import (
    approve_approval_request,
    approve_task,
    defer_approval_request,
    deny_approval_request,
    enqueue_executor_task,
    enqueue_task,
    execute_task,
    get_approval_request,
    get_task,
    get_task_history,
    get_task_next_action,
    get_status_summary,
    get_supervisor_state,
    list_approval_records,
    list_approval_requests,
    list_blocked_tasks,
    list_executor_tasks,
    list_interrupted_tasks,
    list_pending_approvals,
    list_ready_to_resume_tasks,
    list_tasks,
    list_waiting_tasks,
    mark_task_human_needed,
    requeue_task,
    reject_task,
    request_task_approval,
    review_task_for_resume,
    resume_task,
    run_task_once,
    wait_task,
)
from .report_builder import build_report_scaffold
from .storage import (
    APPROVALS_PATH,
    APPROVAL_REQUESTS_PATH,
    RUNTIME_BRAIN_CONFIG_PATH,
    RUNTIME_BRAIN_STATE_PATH,
    RUNTIME_BROWSER_STATE_PATH,
    RUNTIME_RELAY_LOOP_STATE_PATH,
    SUPERVISOR_STATE_PATH,
    TASKS_PATH,
    ensure_runtime_files,
    get_allowed_workspace_root,
    get_runtime_data_dir,
    get_project_root,
    read_tasks,
    runtime_data_lock,
)
from .truth_council import build_truth_council_result
from .workflow_catalog import get_workflow, list_workflows


def _get_current_branch() -> str | None:
    workspace_root = get_project_root().parents[1]
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = result.stdout.strip()
    return branch or None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _approval_target(scope: str, task_id: str) -> str:
    normalized_scope = (scope or "").strip()
    if normalized_scope and normalized_scope != "runtime task execution":
        return normalized_scope
    return task_id


def _short_description(text: str, limit: int = 120) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value or "none"
    return f"{value[: limit - 3].rstrip()}..."


def _workspace_reason(text: str, limit: int = 140) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value or "none"
    return f"{value[: limit - 3].rstrip()}..."


def _task_model_usage(task) -> tuple[bool, str, str, str]:
    if not task or not getattr(task, "execution_records", None):
        return (False, "none", "none", "not_used")
    last_execution = task.execution_records[-1]
    used = bool(getattr(last_execution, "used_model_inference", False))
    provider = str(getattr(last_execution, "model_provider", "") or "none")
    model = str(getattr(last_execution, "model_name", "") or "none")
    call_status = str(getattr(last_execution, "model_call_status", "") or ("succeeded" if used else "not_used"))
    return (used, provider, model, call_status)


def _print_brain_status_block(*, active_task=None) -> None:
    status = get_brain_status()
    used_inference, task_provider, task_model, task_call_status = _task_model_usage(active_task)
    print(f"active_brain_provider: {status.active_provider}")
    print(f"active_brain_model: {status.active_model or 'none'}")
    print(f"brain_config_source: {status.config_source}")
    print(f"brain_provider_ready: {'yes' if status.provider_ready else 'no'}")
    print(f"brain_inference_ready: {'yes' if status.inference_ready else 'no'}")
    print(f"brain_live_call_path: {status.live_call_path}")
    print(f"brain_ollama_base_url: {status.ollama_base_url}")
    print(f"brain_ollama_available: {'yes' if status.ollama_available else 'no'}")
    print(f"brain_model_installed: {'yes' if status.model_installed else 'no'}")
    print(f"current_task_used_model_inference: {'yes' if used_inference else 'no'}")
    print(f"current_task_model_provider: {task_provider}")
    print(f"current_task_model_name: {task_model}")
    print(f"current_task_model_call_status: {task_call_status}")
    print(f"last_model_call_status: {status.last_call_status}")
    print(f"last_model_call_at: {status.last_called_at or 'none'}")
    print(f"last_model_call_source: {status.last_call_source or 'none'}")
    print(f"last_model_call_task_id: {status.last_task_id or 'none'}")
    print(f"last_model_call_error: {status.last_error or 'none'}")
    print(f"last_model_response_preview: {status.last_response_preview or 'none'}")
    print("brain_notes:")
    if status.notes:
        for note in status.notes:
            print(f"- {note}")
    else:
        print("- none")
    print("brain_installed_models:")
    if status.installed_models:
        for model_name in status.installed_models:
            print(f"- {model_name}")
    else:
        print("- none")


DESKTOP_EXECUTOR_ACTIONS = {
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
    "type_text",
    "wait_seconds",
    "wait_for_window",
    "move_mouse",
    "left_click",
    "double_click",
    "right_click",
    "scroll_mouse",
}

GHOTI_ACTIONABLE_STATUSES = {
    "queued",
    "running",
    "waiting",
    "pending_approval",
    "blocked_human_needed",
    "interrupted",
    "ready_to_resume",
    "failed",
}

GHOTI_ACTIVE_STATUSES = {
    "queued",
    "running",
    "waiting",
    "pending_approval",
    "blocked_human_needed",
    "interrupted",
    "ready_to_resume",
}

GHOTI_FAILURE_STATUSES = {
    "failed",
    "blocked_human_needed",
    "interrupted",
}


def _repo_root() -> Path:
    return get_project_root().parents[1]


def _dashboard_url() -> str:
    return "http://127.0.0.1:3210"


def _mcp_server_script_path() -> Path:
    return _repo_root() / "01_projects" / "mcp_server" / "server.py"


def _detect_running_mcp_server_processes() -> list[dict[str, str]]:
    script_path = _mcp_server_script_path()
    script_glob = str(script_path).replace(chr(92), chr(92) * 2)
    command = (
        "Get-CimInstance Win32_Process | "
        f"Where-Object {{ $_.CommandLine -like '*{script_glob}*' }} | "
        "Select-Object ProcessId, Name, CommandLine | ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        return []
    stdout = result.stdout.strip()
    if not stdout:
        return []
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        parsed = [parsed]
    processes: list[dict[str, str]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        processes.append({
            "pid": str(item.get("ProcessId", "") or ""),
            "name": str(item.get("Name", "") or ""),
            "command_line": str(item.get("CommandLine", "") or ""),
        })
    return processes


def _probe_mcp_server() -> tuple[bool, str, str]:
    script_path = _mcp_server_script_path()
    if not script_path.exists():
        return (False, "missing_script", f"MCP server script not found: {script_path}")

    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }) + "\n"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=request,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        cwd=str(_repo_root()),
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0 and not stdout:
        detail = stderr or f"probe exited with code {result.returncode}"
        return (False, "probe_failed", detail)
    first_line = stdout.splitlines()[0].strip() if stdout else ""
    if not first_line:
        return (False, "probe_failed", stderr or "MCP probe returned no output.")
    try:
        response = json.loads(first_line)
    except json.JSONDecodeError as exc:
        return (False, "invalid_response", f"MCP probe returned invalid JSON: {exc}")
    server_name = str(((response.get("result") or {}).get("serverInfo") or {}).get("name") or "")
    if response.get("id") == 1 and server_name == "ghoti-mcp":
        return (True, "reachable", "MCP initialize probe succeeded.")
    return (False, "invalid_response", f"Unexpected MCP initialize response: {first_line}")



def _build_supervised_payload(
    *,
    status: str,
    summary: dict | None = None,
    items: list | None = None,
    item: dict | None = None,
    trace: dict | None = None,
    errors: list[str] | None = None,
    **extra,
) -> dict:
    payload = {
        "status": status,
        "summary": summary or {},
        "items": items if items is not None else [],
        "item": item,
        "trace": trace,
        "errors": errors or [],
    }
    payload.update(extra)
    return payload


def _emit_supervised_json(header: str, payload: dict) -> None:
    print(header)
    print("---")
    print(json.dumps(payload, indent=2))


def _control_center_doc_path() -> Path:
    return _repo_root() / "04_docs" / "ghoti_control_center.md"


def _classify_executor_task(task) -> str:
    action_type = str(task.executor_action_type or "").strip().lower()
    if action_type == "run_operator_recipe":
        recipe_name = str(task.executor_payload.get("recipe_name", "")).strip().lower()
        if recipe_name == "codex_to_chatgpt_handoff_mvp":
            return "handoff"
        return "recipe"
    if action_type in DESKTOP_EXECUTOR_ACTIONS:
        return "desktop"
    return "repo"


def _sort_tasks_by_recent(tasks):
    return sorted(
        tasks,
        key=lambda task: (
            str(getattr(task, "updated_at", "") or ""),
            str(getattr(task, "created_at", "") or ""),
            str(getattr(task, "task_id", "") or ""),
        ),
        reverse=True,
    )


def _iter_recent_artifacts(limit: int = 6) -> list[Path]:
    repo_root = _repo_root()
    artifact_dirs = [
        repo_root / "11_exports" / "personal_ops",
        repo_root / "11_exports" / "github",
        repo_root / "01_projects" / "browser_playground" / "artifacts",
        repo_root / "05_logs" / "tmp" / "desktop",
        repo_root / "01_projects" / "runtime_mvp" / "runtime_data",
    ]

    files: list[Path] = []
    for directory in artifact_dirs:
        if not directory.exists():
            continue
        files.extend(path for path in directory.rglob("*") if path.is_file())

    files.sort(key=lambda path: (path.stat().st_mtime, str(path)), reverse=True)
    return files[:limit]


def _print_ghoti_task_lines(tasks, limit: int = 5) -> None:
    if not tasks:
        print("- none")
        return

    for task in _sort_tasks_by_recent(tasks)[:limit]:
        print(
            f"- {task.task_id} | {task.status} | {_classify_executor_task(task)} | "
            f"{_short_description(task.title, limit=90)}"
        )


def _parse_iso_timestamp(value: str) -> datetime | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _task_age_minutes(task) -> int | None:
    parsed = _parse_iso_timestamp(
        getattr(task, "updated_at", "") or getattr(task, "created_at", "")
    )
    if not parsed:
        return None
    return max(0, int(round((datetime.now(timezone.utc) - parsed).total_seconds() / 60)))


def _task_summary_haystack(task) -> str:
    payload = dict(getattr(task, "executor_payload", {}) or {})
    execution_records = list(getattr(task, "execution_records", []) or [])
    last_record = execution_records[-1] if execution_records else None
    parts = [
        getattr(task, "title", ""),
        getattr(task, "description", ""),
        getattr(task, "executor_target", ""),
        getattr(task, "blocked_reason", ""),
        getattr(task, "waiting_for", ""),
        getattr(task, "last_note", ""),
        payload.get("recipe_name", ""),
        payload.get("recipe_source_window", ""),
        payload.get("recipe_target_window", ""),
        payload.get("handoff_target_resolution_status", ""),
        payload.get("handoff_stop_reason", ""),
        payload.get("handoff_source_match", ""),
        payload.get("handoff_target_match", ""),
        getattr(last_record, "summary", "") if last_record else "",
        getattr(last_record, "reason", "") if last_record else "",
    ]
    return " ".join(str(part or "").strip().lower() for part in parts if str(part or "").strip())


def _task_wrong_window_block(task) -> bool:
    haystack = _task_summary_haystack(task)
    return any(
        needle in haystack
        for needle in (
            "wrong active window",
            "active window mismatch",
            "terminal stayed foreground",
            "manual target resolution is required",
            "powershell",
        )
    )


def _is_task_stalled(task) -> bool:
    status = str(getattr(task, "status", "") or "").lower()
    if status not in {"queued", "running", "waiting"}:
        return False
    age_minutes = _task_age_minutes(task)
    if age_minutes is None:
        return False
    threshold = 15 if status == "running" else 20
    return age_minutes >= threshold


def _describe_overlay_target(task) -> tuple[str, str]:
    if not task:
        return (
            "No visible target",
            "Queue or inspect one narrow task to show Ghoti's next local target.",
        )

    action_type = str(getattr(task, "executor_action_type", "") or "").lower()
    task_type = _classify_executor_task(task)
    target = str(getattr(task, "executor_target", "") or "").strip()
    payload = dict(getattr(task, "executor_payload", {}) or {})
    fallback_detail = target or _short_description(getattr(task, "title", ""), limit=100)

    if task_type == "handoff":
        source_window = str(payload.get("recipe_source_window", "codex") or "codex").strip()
        target_window = str(payload.get("recipe_target_window", "chatgpt") or "chatgpt").strip()
        detail = f"{source_window} -> {target_window}"
        if target:
            detail = f"{detail} | {target}"
        return ("Handoff target", detail)

    if action_type in {"move_mouse", "left_click", "double_click", "right_click", "scroll_mouse"}:
        return ("Pointer target", fallback_detail or "Pointer action is queued without extra target detail.")

    if action_type in {"focus_window", "open_allowed_app", "wait_for_window", "get_active_window"}:
        return ("Window target", fallback_detail or "Window-targeted desktop action.")

    if action_type in {"paste_clipboard", "copy_selection", "set_clipboard_text", "send_hotkey", "get_clipboard_text", "type_text"}:
        return ("Input target", fallback_detail or "Input-targeted desktop action.")

    return ("Current task target", fallback_detail or "No specific target recorded yet.")


def _desktop_action_truth(task) -> dict[str, str]:
    payload = dict(getattr(task, "executor_payload", {}) or {})
    action_type = str(getattr(task, "executor_action_type", "") or "").lower()
    if action_type not in DESKTOP_EXECUTOR_ACTIONS:
        return {
            "current_action": "none",
            "current_target": "none",
            "current_typing_enabled": "no",
            "last_action": "none",
            "last_target": "none",
            "last_typing_enabled": "no",
            "last_status": "not_run",
            "cue_status": "not_reported",
            "cue_action": "none",
            "cue_target": "none",
            "text_preview": "none",
        }
    return {
        "current_action": str(payload.get("desktop_current_action") or action_type or "none"),
        "current_target": str(payload.get("desktop_current_target") or getattr(task, "executor_target", "") or "none"),
        "current_typing_enabled": str(payload.get("desktop_current_typing_enabled") or ("yes" if action_type == "type_text" else "no")),
        "last_action": str(payload.get("desktop_last_action") or action_type or "none"),
        "last_target": str(payload.get("desktop_last_target") or getattr(task, "executor_target", "") or "none"),
        "last_typing_enabled": str(payload.get("desktop_last_typing_enabled") or ("yes" if action_type == "type_text" else "no")),
        "last_status": str(payload.get("desktop_last_action_status") or "not_run"),
        "cue_status": str(payload.get("desktop_last_visual_cue_status") or "not_reported"),
        "cue_action": str(payload.get("desktop_last_visual_cue_action") or action_type or "none"),
        "cue_target": str(payload.get("desktop_last_visual_cue_target") or payload.get("desktop_last_target") or getattr(task, "executor_target", "") or "none"),
        "text_preview": str(payload.get("desktop_last_text_preview") or "none"),
    }


def _print_desktop_action_block(*, active_task=None) -> None:
    truth = _desktop_action_truth(active_task) if active_task else {
        "current_action": "none",
        "current_target": "none",
        "current_typing_enabled": "no",
        "last_action": "none",
        "last_target": "none",
        "last_typing_enabled": "no",
        "last_status": "not_run",
        "cue_status": "not_reported",
        "cue_action": "none",
        "cue_target": "none",
        "text_preview": "none",
    }
    print(f"desktop_current_action: {truth['current_action']}")
    print(f"desktop_current_target: {truth['current_target']}")
    print(f"desktop_current_typing_enabled: {truth['current_typing_enabled']}")
    print(f"desktop_last_action: {truth['last_action']}")
    print(f"desktop_last_target: {truth['last_target']}")
    print(f"desktop_last_typing_enabled: {truth['last_typing_enabled']}")
    print(f"desktop_last_action_status: {truth['last_status']}")
    print(f"desktop_visual_cue_status: {truth['cue_status']}")
    print(f"desktop_visual_cue_action: {truth['cue_action']}")
    print(f"desktop_visual_cue_target: {truth['cue_target']}")
    print(f"desktop_last_text_preview: {truth['text_preview']}")


def _print_role_status_block(*, active_task=None) -> None:
    status = get_specialist_role_status(active_task)
    print(f"current_specialist_role: {status.current_role_id}")
    print(f"current_specialist_role_purpose: {status.current_role_purpose}")
    print(f"current_specialist_role_provider: {status.current_role_provider}")
    print(f"current_specialist_role_sensitivity: {status.current_role_sensitivity}")
    print(f"current_specialist_role_reason: {status.current_role_reason}")
    print(f"specialist_role_registry_count: {status.registry_count}")


def _print_browser_status_block() -> None:
    status = get_browser_capability_status()
    print(f"browser_use_installed: {'yes' if status.browser_use_installed else 'no'}")
    print(f"browser_use_version: {status.browser_use_version}")
    print(f"browser_use_ready: {'yes' if status.browser_use_ready else 'no'}")
    print(f"browser_session_support: {status.browser_session_support}")
    print(f"browser_task_support: {status.browser_task_support}")
    print(f"playwright_installed: {'yes' if status.playwright_installed else 'no'}")
    print(f"playwright_version: {status.playwright_version}")
    print(f"playwright_cli_available: {'yes' if status.playwright_cli_available else 'no'}")
    print(f"playwright_browser_binaries_installed: {'yes' if status.playwright_browser_binaries_installed else 'no'}")
    print(f"playwright_ready: {'yes' if status.playwright_ready else 'no'}")
    print(f"current_browser_role: {status.current_browser_role}")
    print(f"current_browser_action: {status.current_browser_action}")
    print(f"current_browser_session_id: {status.current_browser_session_id}")
    print(f"last_browser_status: {status.last_browser_status}")
    print(f"runtime_browser_state_file: {RUNTIME_BROWSER_STATE_PATH}")
    print("browser_notes:")
    for note in status.notes:
        print(f"- {note}")


def _print_memory_status_block() -> None:
    status = get_memory_layer_status()
    print(f"compact_memory_ready: {'yes' if status.ready else 'no'}")
    print(f"compact_memory_root: {status.memory_root}")
    print(f"compact_memory_obsidian_markdown_ready: {'yes' if status.obsidian_markdown_ready else 'no'}")
    print(f"compact_memory_file_count: {status.file_count}")
    print(f"compact_memory_newest_modified_at: {status.newest_modified_at}")
    print("compact_memory_missing_files:")
    if status.missing_files:
        for item in status.missing_files:
            print(f"- {item}")
    else:
        print("- none")
    print("compact_memory_notes:")
    for note in status.notes:
        print(f"- {note}")

def _print_relay_status_block() -> None:
    status = get_relay_loop_status()
    print(f"relay_state: {status.relay_state}")
    print(f"relay_current_step: {status.current_step}")
    print(f"relay_source_target_alias: {status.source_target_alias}")
    print(f"relay_source_target_candidate_id: {status.source_target_candidate_id or 'none'}")
    print(f"relay_source_target_title: {status.source_target_title or 'none'}")
    print(f"relay_source_target_status: {status.source_target_status}")
    print(f"relay_destination_target_alias: {status.destination_target_alias}")
    print(f"relay_destination_target_candidate_id: {status.destination_target_candidate_id or 'none'}")
    print(f"relay_destination_target_title: {status.destination_target_title or 'none'}")
    print(f"relay_destination_target_status: {status.destination_target_status}")
    print(f"relay_codex_mode_preset: {status.codex_mode_preset}")
    print(f"relay_codex_reasoning_preset: {status.codex_reasoning_preset}")
    print(f"relay_preset_application_status: {status.preset_application_status}")
    print(f"relay_codex_execution_status: {status.codex_execution_status}")
    print(f"relay_next_usage_reset_at: {status.next_usage_reset_at or 'none'}")
    print(f"relay_resume_after_usage_reset: {'yes' if status.resume_after_usage_reset else 'no'}")
    print(f"relay_waiting_reason: {status.waiting_reason or 'none'}")
    print(f"relay_blocked_reason: {status.blocked_reason or 'none'}")
    print(f"relay_last_payload_preview: {status.last_payload_preview or 'none'}")
    print(f"relay_last_result_preview: {status.last_result_preview or 'none'}")
    print(f"relay_last_completion_status: {status.last_completion_status or 'none'}")
    print(f"relay_last_transition_at: {status.last_transition_at or 'none'}")
    print(f"relay_last_updated_at: {status.last_updated_at or 'none'}")
    print(f"relay_last_used_task_id: {status.last_used_task_id or 'none'}")
    print(f"relay_last_known_dialog_status: {status.last_known_dialog_status}")
    print(f"relay_last_known_dialog_note: {status.last_known_dialog_note or 'none'}")
    print(f"runtime_relay_state_file: {RUNTIME_RELAY_LOOP_STATE_PATH}")
    print("relay_notes:")
    for note in status.notes:
        print(f"- {note}")

def _build_ghoti_watchdog(state, tasks, active_task) -> dict:
    sorted_tasks = _sort_tasks_by_recent(tasks)
    failure_tasks = [
        task for task in sorted_tasks if str(getattr(task, "status", "") or "").lower() in GHOTI_FAILURE_STATUSES
    ]
    wrong_window_blocks = [task for task in failure_tasks if _task_wrong_window_block(task)]
    stalled_tasks = [task for task in sorted_tasks if _is_task_stalled(task)]
    waiting_count = int(getattr(state, "waiting_count", 0) or 0) + int(getattr(state, "ready_to_resume_count", 0) or 0)
    pending_approval_count = int(getattr(state, "pending_approval_count", 0) or 0)
    blocked_count = int(getattr(state, "blocked_human_needed_count", 0) or 0)
    interrupted_count = int(getattr(state, "interrupted_count", 0) or 0)
    running_count = int(getattr(state, "running_count", 0) or 0)
    did_not_complete_count = len(failure_tasks)

    status = "idle"
    headline = "Ghoti is visible and waiting for the next narrow local action."
    if pending_approval_count > 0:
        status = "approval_needed"
        headline = f"{pending_approval_count} approval request(s) need review before more guarded work can proceed."
    elif wrong_window_blocks:
        status = "blocked"
        headline = f"Blocked before input on {len(wrong_window_blocks)} wrong-window handoff attempt(s)."
    elif blocked_count > 0 or did_not_complete_count > 0:
        status = "blocked"
        headline = (
            f"{blocked_count} task(s) are blocked and need manual intervention."
            if blocked_count > 0
            else f"{did_not_complete_count} recent task(s) did not complete cleanly."
        )
    elif interrupted_count > 0:
        status = "interrupted"
        headline = f"{interrupted_count} task(s) were interrupted and must be reviewed before re-queue."
    elif running_count > 0 or str(getattr(active_task, "status", "") or "").lower() == "running":
        status = "active"
        headline = (
            f"{getattr(active_task, 'task_id', 'current task')} is active."
            if active_task
            else "Ghoti is actively running a local task."
        )
    elif waiting_count > 0 or stalled_tasks:
        status = "waiting"
        headline = (
            f"{waiting_count} task(s) are waiting or ready to resume."
            if waiting_count > 0
            else f"{len(stalled_tasks)} task(s) look stalled and need operator attention."
        )

    alerts = []
    if wrong_window_blocks:
        alerts.append(
            f"{len(wrong_window_blocks)} recent handoff block(s) stopped before input because the active window did not match the intended Codex or ChatGPT destination."
        )
    if stalled_tasks:
        alerts.append(
            f"{len(stalled_tasks)} queued, running, or waiting task(s) have been unchanged for 15-20+ minutes."
        )
    if did_not_complete_count > 0:
        alerts.append(
            f"{did_not_complete_count} recent task(s) ended blocked, interrupted, or failed and still need review."
        )
    if pending_approval_count > 0:
        alerts.append(f"{pending_approval_count} approval request(s) are waiting on the operator.")
    if blocked_count > 0:
        alerts.append(f"{blocked_count} human-needed task(s) remain blocked in the current queue state.")
    if interrupted_count > 0:
        alerts.append(f"{interrupted_count} interrupted task(s) are visible and require review before any re-queue.")

    focus_task = (
        active_task
        or (wrong_window_blocks[0] if wrong_window_blocks else None)
        or (stalled_tasks[0] if stalled_tasks else None)
        or next(
            (
                task
                for task in sorted_tasks
                if str(getattr(task, "status", "") or "").lower() in GHOTI_ACTIONABLE_STATUSES
            ),
            None,
        )
    )
    overlay_target, overlay_target_detail = _describe_overlay_target(focus_task)
    handoff_hint = (
        "Codex-to-ChatGPT handoff stays paste-only by default and blocks before input whenever the wrong window stays foreground or the destination is not confident."
        if wrong_window_blocks or _classify_executor_task(focus_task) == "handoff"
        else "Ctrl+8 is still the emergency stop if a desktop action or operator recipe needs immediate interruption."
    )

    return {
        "status": status,
        "headline": headline,
        "alerts": alerts,
        "wrong_window_block_count": len(wrong_window_blocks),
        "stalled_task_count": len(stalled_tasks),
        "did_not_complete_count": did_not_complete_count,
        "overlay_target": overlay_target,
        "overlay_target_detail": overlay_target_detail,
        "handoff_hint": handoff_hint,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="super-agent")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-data")
    subparsers.add_parser("status")
    subparsers.add_parser("list")
    subparsers.add_parser("snapshot")
    subparsers.add_parser("list-providers")
    subparsers.add_parser("brain-status")
    subparsers.add_parser("list-agent-roles")
    subparsers.add_parser("browser-status")
    subparsers.add_parser("ghoti-mcp-status")
    mcp_call_parser = subparsers.add_parser("ghoti-mcp-call")
    mcp_call_parser.add_argument("tool_name")
    subparsers.add_parser("memory-status")
    subparsers.add_parser("relay-status")
    subparsers.add_parser("list-workflows")
    subparsers.add_parser("publish-check")
    subparsers.add_parser("list-personal-workflows")
    subparsers.add_parser("list-integrations")
    subparsers.add_parser("github-status")
    subparsers.add_parser("publish-check-core")
    subparsers.add_parser("github-gh-diagnose")
    subparsers.add_parser("github-remote-capability")
    subparsers.add_parser("env-diagnose")
    subparsers.add_parser("gh-auth-status")
    subparsers.add_parser("capability-matrix")
    subparsers.add_parser("pending-approvals")
    subparsers.add_parser("supervisor-status")
    subparsers.add_parser("list-executor-tasks")
    subparsers.add_parser("ghoti-help")
    subparsers.add_parser("ghoti-status")
    subparsers.add_parser("ghoti-operator-tick")
    subparsers.add_parser("ghoti-operator-state")
    subparsers.add_parser("ghoti-approval-list")
    approval_view_parser = subparsers.add_parser("ghoti-approval-view")
    approval_view_parser.add_argument("approval_id")
    approval_approve_parser = subparsers.add_parser("ghoti-approval-approve")
    approval_approve_parser.add_argument("approval_id")
    approval_reject_parser = subparsers.add_parser("ghoti-approval-reject")
    approval_reject_parser.add_argument("approval_id")
    approval_reject_parser.add_argument("--reason", required=True)
    subparsers.add_parser("ghoti-manual-queue-list")
    manual_queue_view_parser = subparsers.add_parser("ghoti-manual-queue-view")
    manual_queue_view_parser.add_argument("item_id")
    subparsers.add_parser("ghoti-manual-queue-state")
    manual_queue_review_parser = subparsers.add_parser("ghoti-manual-queue-mark-reviewed")
    manual_queue_review_parser.add_argument("item_id")
    manual_queue_review_parser.add_argument("--note", required=True)
    manual_queue_explain_parser = subparsers.add_parser("ghoti-manual-queue-explain")
    manual_queue_explain_parser.add_argument("item_id")
    audit_trace_parser = subparsers.add_parser("ghoti-audit-trace")
    audit_trace_parser.add_argument("approval_id", nargs="?", default=None)
    audit_trace_parser.add_argument("--latest-approved", action="store_true")
    subparsers.add_parser("ghoti-control-center-state")
    pipeline_items_parser = subparsers.add_parser("ghoti-pipeline-items")
    pipeline_items_parser.add_argument(
        "--status",
        choices=["pending", "approved", "rejected", "ready", "reviewed"],
        default=None,
    )
    action_intents_parser = subparsers.add_parser("ghoti-action-intents")
    action_intents_parser.add_argument("--limit", type=int, default=20)
    subparsers.add_parser("ghoti-capability-adapters")
    action_intent_create_parser = subparsers.add_parser("ghoti-action-intent-create")
    action_intent_create_parser.add_argument("--requested-by-agent", default="operator")
    action_intent_create_parser.add_argument("--adapter-id", default="native-demo-adapter")
    action_intent_create_parser.add_argument("--action-type", required=True)
    action_intent_create_parser.add_argument("--target", default="")
    action_intent_create_parser.add_argument("--payload-json", default="{}")
    action_intent_create_parser.add_argument("--reason", default="")
    action_intent_consume_parser = subparsers.add_parser("ghoti-action-intent-consume")
    action_intent_consume_parser.add_argument("intent_id")
    action_intent_consume_parser.add_argument("--adapter-id", required=True)
    action_intent_consume_parser.add_argument("--action-type", required=True)
    action_intent_consume_parser.add_argument("--payload-json", default="{}")
    subparsers.add_parser("ghoti-hotkeys")
    subparsers.add_parser("ghoti-recent")

    relay_bind_parser = subparsers.add_parser("relay-bind-target")
    relay_bind_parser.add_argument("--alias", required=True, choices=["chatgpt", "codex"])
    relay_bind_parser.add_argument("--candidate-id", required=True)

    relay_preset_parser = subparsers.add_parser("relay-set-preset")
    relay_preset_parser.add_argument("--mode", default="Implementing new feature")
    relay_preset_parser.add_argument("--reasoning", default="Medium")
    relay_preset_parser.add_argument("--application-status", default="stored_only", choices=["stored_only", "pending_manual_application", "applied", "blocked"])

    relay_update_parser = subparsers.add_parser("relay-update-state")
    relay_update_parser.add_argument("--state", default="")
    relay_update_parser.add_argument("--step", default="")
    relay_update_parser.add_argument("--source-alias", default="")
    relay_update_parser.add_argument("--destination-alias", default="")
    relay_update_parser.add_argument("--waiting-reason", default="")
    relay_update_parser.add_argument("--blocked-reason", default="")
    relay_update_parser.add_argument("--payload-preview", default="")
    relay_update_parser.add_argument("--result-preview", default="")
    relay_update_parser.add_argument("--codex-status", default="")
    relay_update_parser.add_argument("--next-usage-reset-at", default="")
    relay_update_parser.add_argument("--resume-after-usage-reset", choices=["yes", "no"], default="")
    relay_update_parser.add_argument("--completion-status", default="")
    relay_update_parser.add_argument("--task-id", default="")
    relay_update_parser.add_argument("--preset-application-status", default="", choices=["", "stored_only", "pending_manual_application", "applied", "blocked"])
    relay_update_parser.add_argument("--dialog-status", default="", choices=["", "none", "blocked_unrecognized", "allowlisted_dialog_ready", "allowlisted_dialog_handled"])
    relay_update_parser.add_argument("--dialog-note", default="")

    brain_set_parser = subparsers.add_parser("brain-set-active")
    brain_set_parser.add_argument("--provider", required=True)
    brain_set_parser.add_argument("--model", required=True)
    brain_set_parser.add_argument("--ollama-base-url", default="")

    brain_infer_parser = subparsers.add_parser("brain-infer")
    brain_infer_parser.add_argument("--prompt", required=True)
    brain_infer_parser.add_argument("--task-id", default="")
    brain_infer_parser.add_argument("--source", default="cli")

    enqueue_parser = subparsers.add_parser("enqueue")
    enqueue_parser.add_argument("--title", required=True)
    enqueue_parser.add_argument("--description", required=True)
    enqueue_parser.add_argument(
        "--risk",
        required=True,
        choices=["safe", "ask", "high_risk", "admin"],
    )
    enqueue_parser.add_argument("--source", default="manual")

    executor_parser = subparsers.add_parser("queue-executor-action")
    executor_parser.add_argument(
        "--action-type",
        required=True,
        choices=[
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
            "type_text",
            "wait_seconds",
            "wait_for_window",
            "move_mouse",
            "left_click",
            "double_click",
            "right_click",
            "scroll_mouse",
            "run_operator_recipe",
        ],
    )
    executor_parser.add_argument("--target", default="")
    executor_parser.add_argument("--content", default="")
    executor_parser.add_argument("--source", default="manual")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--task-id", required=True)
    approve_parser.add_argument("--note", default="")

    reject_parser = subparsers.add_parser("reject")
    reject_parser.add_argument("--task-id", required=True)
    reject_parser.add_argument("--note", default="")

    wait_parser = subparsers.add_parser("wait")
    wait_parser.add_argument("--task-id", required=True)
    wait_parser.add_argument(
        "--reason",
        default="waiting for human reply or external event",
    )

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--task-id", required=True)

    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--task-id", required=True)

    execute_task_parser = subparsers.add_parser("execute-task")
    execute_task_parser.add_argument("--task-id", required=True)

    task_status_parser = subparsers.add_parser("task-status")
    task_status_parser.add_argument("--task-id", required=True)

    review_task_parser = subparsers.add_parser("review-task")
    review_task_parser.add_argument("--task-id", required=True)
    review_task_parser.add_argument("--note", default="")

    requeue_task_parser = subparsers.add_parser("requeue-task")
    requeue_task_parser.add_argument("--task-id", required=True)
    requeue_task_parser.add_argument("--note", default="")

    approval_status_parser = subparsers.add_parser("approval-status")
    approval_status_parser.add_argument("--approval-id", default="")

    approve_approval_parser = subparsers.add_parser("approve-approval")
    approve_approval_parser.add_argument("--approval-id", required=True)
    approve_approval_parser.add_argument("--note", default="")

    deny_approval_parser = subparsers.add_parser("deny-approval")
    deny_approval_parser.add_argument("--approval-id", required=True)
    deny_approval_parser.add_argument("--note", default="")

    defer_approval_parser = subparsers.add_parser("defer-approval")
    defer_approval_parser.add_argument("--approval-id", required=True)
    defer_approval_parser.add_argument("--note", default="")

    request_approval_parser = subparsers.add_parser("request-approval")
    request_approval_parser.add_argument("--task-id", required=True)
    request_approval_parser.add_argument("--action-label", required=True)
    request_approval_parser.add_argument("--reason", required=True)
    request_approval_parser.add_argument(
        "--risk-level",
        default="ask",
        choices=["safe", "ask", "high_risk", "admin"],
    )
    request_approval_parser.add_argument("--scope", default="runtime task execution")
    request_approval_parser.add_argument(
        "--requires-admin",
        default="no",
        choices=["yes", "no"],
    )
    request_approval_parser.add_argument("--rollback-plan", default="")
    request_approval_parser.add_argument("--source", default="manual")

    human_needed_parser = subparsers.add_parser("mark-human-needed")
    human_needed_parser.add_argument("--task-id", required=True)
    human_needed_parser.add_argument("--reason", required=True)

    council_parser = subparsers.add_parser("council-plan")
    council_parser.add_argument("--goal-type", required=True)
    council_parser.add_argument("--privacy", default="balanced")
    council_parser.add_argument("--speed", default="balanced")
    council_parser.add_argument("--require-reviewer", action="store_true")

    show_workflow_parser = subparsers.add_parser("show-workflow")
    show_workflow_parser.add_argument("--workflow-id", required=True)

    show_personal_workflow_parser = subparsers.add_parser("show-personal-workflow")
    show_personal_workflow_parser.add_argument("--workflow-id", required=True)

    mail_plan_parser = subparsers.add_parser("mail-plan")
    mail_plan_parser.add_argument("--account-label", required=True)
    mail_plan_parser.add_argument("--goal", required=True)

    notion_plan_parser = subparsers.add_parser("notion-plan")
    notion_plan_parser.add_argument("--page-label", required=True)
    notion_plan_parser.add_argument("--objective", required=True)

    github_issue_draft_parser = subparsers.add_parser("github-issue-draft")
    github_issue_draft_parser.add_argument("--title", required=True)
    github_issue_draft_parser.add_argument("--objective", required=True)
    github_issue_draft_parser.add_argument("--context", required=True)
    github_issue_draft_parser.add_argument("--body", required=True)
    github_issue_draft_parser.add_argument("--labels", default="")

    github_pr_draft_parser = subparsers.add_parser("github-pr-draft")
    github_pr_draft_parser.add_argument("--title", required=True)
    github_pr_draft_parser.add_argument("--objective", required=True)
    github_pr_draft_parser.add_argument("--source-branch", required=True)
    github_pr_draft_parser.add_argument("--target-branch", required=True)
    github_pr_draft_parser.add_argument("--summary", required=True)
    github_pr_draft_parser.add_argument("--risk-notes", default="")

    github_create_branch_parser = subparsers.add_parser("github-create-branch")
    github_create_branch_parser.add_argument("--branch-name", required=True)
    github_create_branch_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_create_issue_parser = subparsers.add_parser("github-create-issue")
    github_create_issue_parser.add_argument("--title", required=True)
    github_create_issue_parser.add_argument("--body", required=True)
    github_create_issue_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_create_pr_parser = subparsers.add_parser("github-create-pr")
    github_create_pr_parser.add_argument("--title", required=True)
    github_create_pr_parser.add_argument("--body", required=True)
    github_create_pr_parser.add_argument("--base-branch", default="main")
    github_create_pr_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_smoke_issue_parser = subparsers.add_parser("github-smoke-issue")
    github_smoke_issue_parser.add_argument("--title", required=True)
    github_smoke_issue_parser.add_argument("--body", required=True)
    github_smoke_issue_parser.add_argument("--labels", default="")
    github_smoke_issue_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    github_smoke_pr_parser = subparsers.add_parser("github-smoke-pr")
    github_smoke_pr_parser.add_argument("--title", required=True)
    github_smoke_pr_parser.add_argument("--body", required=True)
    github_smoke_pr_parser.add_argument("--base-branch", default="main")
    github_smoke_pr_parser.add_argument("--approve", required=True, choices=["yes", "no"])

    scaffold_report_parser = subparsers.add_parser("scaffold-report")
    scaffold_report_parser.add_argument("--title", required=True)
    scaffold_report_parser.add_argument("--workflow-id", required=True)
    scaffold_report_parser.add_argument("--summary", required=True)

    inbox_triage_parser = subparsers.add_parser("scaffold-inbox-triage")
    inbox_triage_parser.add_argument("--account-label", required=True)
    inbox_triage_parser.add_argument("--goal", required=True)

    linkedin_pack_parser = subparsers.add_parser("scaffold-linkedin-pack")
    linkedin_pack_parser.add_argument("--profile-label", required=True)
    linkedin_pack_parser.add_argument("--target-role", required=True)
    linkedin_pack_parser.add_argument("--focus", required=True)

    cv_pack_parser = subparsers.add_parser("scaffold-cv-pack")
    cv_pack_parser.add_argument("--target-role", required=True)
    cv_pack_parser.add_argument("--summary", required=True)

    outreach_draft_parser = subparsers.add_parser("scaffold-outreach-draft")
    outreach_draft_parser.add_argument("--recipient-label", required=True)
    outreach_draft_parser.add_argument("--purpose", required=True)
    outreach_draft_parser.add_argument("--notes", default="")

    internship_pack_parser = subparsers.add_parser("scaffold-internship-pack")
    internship_pack_parser.add_argument("--target-role", required=True)
    internship_pack_parser.add_argument("--company", required=True)
    internship_pack_parser.add_argument("--job-source", required=True)
    internship_pack_parser.add_argument("--fit-summary", required=True)

    showcase_case_study_parser = subparsers.add_parser("scaffold-showcase-case-study")
    showcase_case_study_parser.add_argument("--project-name", required=True)
    showcase_case_study_parser.add_argument("--objective", required=True)
    showcase_case_study_parser.add_argument("--highlights", required=True)

    portfolio_project_page_parser = subparsers.add_parser("scaffold-portfolio-project-page")
    portfolio_project_page_parser.add_argument("--project-name", required=True)
    portfolio_project_page_parser.add_argument("--summary", required=True)
    portfolio_project_page_parser.add_argument("--stack", required=True)

    truth_plan_parser = subparsers.add_parser("truth-plan")
    truth_plan_parser.add_argument("--question", required=True)
    truth_plan_parser.add_argument("--proposer", required=True)
    truth_plan_parser.add_argument("--challenger", required=True)
    truth_plan_parser.add_argument("--evidence", required=True)
    truth_plan_parser.add_argument("--evidence-quality", default="medium")
    truth_plan_parser.add_argument("--disagreement", default="medium")
    truth_plan_parser.add_argument("--source-count", default=1, type=int)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "env-diagnose":
            diagnosis = diagnose_environment()
            for label, tool in (
                ("python", diagnosis.python),
                ("git", diagnosis.git),
                ("gh", diagnosis.gh),
            ):
                print(f"{label}_found: {'yes' if tool.found else 'no'}")
                print(f"{label}_source: {tool.source}")
                print(f"{label}_path_visible: {'yes' if tool.path_visible else 'no'}")
                print(f"{label}_path: {tool.resolved_path or 'none'}")
                print(f"{label}_version: {tool.version or 'unknown'}")
                if label == "gh":
                    print(f"{label}_auth_known: {'yes' if tool.auth_known else 'no'}")
                    if tool.authenticated is None:
                        print(f"{label}_authenticated: unknown")
                    else:
                        print(f"{label}_authenticated: {'yes' if tool.authenticated else 'no'}")
                if tool.notes:
                    print(f"{label}_notes:")
                    for item in tool.notes:
                        print(f"- {item}")
            print("capabilities:")
            for capability in build_capability_summary(diagnosis):
                block = capability.blocking_issue or "none"
                print(
                    f"- {capability.capability_id} | {capability.state} | "
                    f"requires: {', '.join(capability.required_tools) or 'none'} | block: {block}"
                )
            return 0

        if args.command == "gh-auth-status":
            diagnostics = diagnose_gh_environment()
            print(f"gh_available: {'yes' if diagnostics.gh_available else 'no'}")
            print(f"gh_source: {diagnostics.source}")
            print(f"gh_path_visible: {'yes' if diagnostics.path_visible else 'no'}")
            print(f"gh_path: {diagnostics.gh_path or 'none'}")
            print(f"gh_version: {diagnostics.version or 'unknown'}")
            if not diagnostics.gh_available:
                print("status: skipped")
                print("reason: gh is missing in the current runtime environment")
            elif diagnostics.auth_known:
                print("status: checked")
                print(f"gh_authenticated: {'yes' if diagnostics.gh_authenticated else 'no'}")
            else:
                print("status: unknown")
                print("gh_authenticated: unknown")
            if diagnostics.notes:
                print("notes:")
                for item in diagnostics.notes:
                    print(f"- {item}")
            return 0

        if args.command == "capability-matrix":
            for capability in build_capability_summary():
                block = capability.blocking_issue or "none"
                print(
                    f"{capability.capability_id} | {capability.state} | "
                    f"requires: {', '.join(capability.required_tools) or 'none'} | block: {block}"
                )
            return 0

        if args.command == "init-data":
            runtime_dir = ensure_runtime_files()
            print(f"runtime_data: {runtime_dir}")
            return 0

        if args.command == "ghoti-help":
            available_capabilities = [
                capability.capability_id
                for capability in build_capability_summary()
                if capability.state == "available"
            ]
            print("ghoti_help: supervised local-first operator control overview")
            print(f"branch: {_get_current_branch() or 'unknown'}")
            print(f"dashboard_url: {_dashboard_url()}")
            print(f"control_center_doc: {_control_center_doc_path()}")
            print("dashboard_mode:")
            print(f"- start from repo root: node {_repo_root() / '01_projects' / 'dashboard_mvp' / 'server.js'}")
            print(f"- open in browser: {_dashboard_url()}")
            print("- use the Ghoti control center to see state, approvals, blocked tasks, recent actionable work, failures, and artifacts")
            print("- keep the floating Ghoti overlay visible for watchdog alerts, target focus, and the Ctrl+8 reminder")
            print("cli_mode:")
            print("- python -m super_ai_agent.cli ghoti-status")
            print("- python -m super_ai_agent.cli brain-status")
            print("- python -m super_ai_agent.cli list-agent-roles")
            print("- python -m super_ai_agent.cli browser-status")
            print("- python -m super_ai_agent.cli memory-status")
            print("- python -m super_ai_agent.cli relay-status")
            print("- python -m super_ai_agent.cli relay-bind-target --alias chatgpt --candidate-id <candidate_id>")
            print("- python -m super_ai_agent.cli relay-set-preset --mode Implementing_new_feature --reasoning Medium")
            print("- python -m super_ai_agent.cli ghoti-hotkeys")
            print("- python -m super_ai_agent.cli ghoti-recent")
            print("stop:")
            print("- Ctrl+8 stops the current desktop action or operator recipe run")
            print("- after interruption, the task stays interrupted until the operator reviews it and re-queues it manually")
            print("what_ghoti_can_do_now:")
            if available_capabilities:
                for capability_id in available_capabilities[:6]:
                    print(f"- {capability_id}")
            else:
                print("- no available capability summary returned")
            print("safety:")
            print(f"- allowed workspace root: {get_allowed_workspace_root()}")
            print("- no arbitrary shell passthrough")
            print("- no unrestricted desktop control")
            print("- no admin automation")
            print("- no task deletion without explicit user approval; prefer archive, filter, and history visibility instead")
            print("- Codex-to-ChatGPT handoff never falls back to terminal or PowerShell")
            print("next:")
            print("- run ghoti-status to see the live local state and next operator step")
            print("- run brain-status to verify whether Ghoti is using Gemma/Ollama or only local rules")
            print("- run list-agent-roles, browser-status, and memory-status to inspect role, browser, and compact-memory truth")
            print("- open the dashboard if you want the visual control center and recent artifact view")
            print("- run ghoti-recent when you want the shortest read on actionable tasks, failures, approvals, and artifacts")
            return 0

        if args.command == "ghoti-hotkeys":
            print("primary_hotkey: Ctrl+8")
            print("scope: stops the current desktop action or operator recipe run")
            print("after_interrupt: the task is marked interrupted and requires operator review before re-queue")
            print("dashboard_visibility: the interrupt reason appears in the dashboard task detail and supervisor views")
            print("overlay_visibility: the floating Ghoti overlay keeps the stop reminder and current target summary visible")
            print("handoff_safety: Codex-to-ChatGPT handoff blocks before input if the wrong window stays active")
            return 0

        if args.command == "ghoti-status":
            ensure_runtime_files()
            state = get_supervisor_state()
            summary = get_status_summary()
            tasks = list_executor_tasks()
            actionable_tasks = [
                task for task in tasks if str(task.status or "").lower() in GHOTI_ACTIONABLE_STATUSES
            ]
            failure_tasks = [
                task for task in tasks if str(task.status or "").lower() in GHOTI_FAILURE_STATUSES
            ]
            active_task = get_task(state.active_task_id) if state.active_task_id else None
            available_capabilities = [
                capability.capability_id
                for capability in build_capability_summary()
                if capability.state == "available"
            ]
            watchdog = _build_ghoti_watchdog(state, tasks, active_task)
            print("ghoti_status: local operator control snapshot")
            print(f"branch: {_get_current_branch() or 'unknown'}")
            print(f"dashboard_url: {_dashboard_url()}")
            print(f"control_center_doc: {_control_center_doc_path()}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            print(f"ghoti_state: {state.ghoti_state}")
            print(f"ghoti_reason: {state.ghoti_reason or 'none'}")
            print(f"active_task_id: {state.active_task_id or 'none'}")
            print(
                "current_task: "
                + (
                    f"{active_task.task_id} | {_classify_executor_task(active_task)} | "
                    f"{_short_description(active_task.title, limit=90)}"
                    if active_task
                    else "none"
                )
            )
            print(f"queued_tasks: {summary.queued_tasks}")
            print(f"running_tasks: {summary.running_tasks}")
            print(f"pending_approvals: {state.pending_approval_count}")
            print(f"blocked_tasks: {state.blocked_human_needed_count}")
            print(f"waiting_tasks: {state.waiting_count}")
            print(f"ready_to_resume_tasks: {state.ready_to_resume_count}")
            print(f"interrupted_tasks: {state.interrupted_count}")
            print(f"recent_actionable_count: {len(actionable_tasks)}")
            print(f"recent_failure_count: {len(failure_tasks)}")
            print(f"recent_artifact_count: {len(_iter_recent_artifacts(limit=6))}")
            print(f"watchdog_status: {watchdog['status']}")
            print(f"watchdog_headline: {watchdog['headline']}")
            print(f"watchdog_wrong_window_blocks: {watchdog['wrong_window_block_count']}")
            print(f"watchdog_stalled_tasks: {watchdog['stalled_task_count']}")
            print(f"watchdog_did_not_complete: {watchdog['did_not_complete_count']}")
            print(f"overlay_target: {watchdog['overlay_target']}")
            print(f"overlay_target_detail: {watchdog['overlay_target_detail']}")
            print(f"watchdog_handoff_hint: {watchdog['handoff_hint']}")
            _print_role_status_block(active_task=active_task)
            _print_browser_status_block()
            _print_memory_status_block()
            _print_relay_status_block()
            _print_brain_status_block(active_task=active_task)
            _print_desktop_action_block(active_task=active_task)
            print("recent_actionable_tasks:")
            _print_ghoti_task_lines(actionable_tasks, limit=5)
            print("recent_failures:")
            _print_ghoti_task_lines(failure_tasks, limit=5)
            print("watchdog_alerts:")
            if watchdog["alerts"]:
                for alert in watchdog["alerts"]:
                    print(f"- {alert}")
            else:
                print("- none")
            print("what_ghoti_can_do_now:")
            if available_capabilities:
                for capability_id in available_capabilities[:5]:
                    print(f"- {capability_id}")
            else:
                print("- no available capability summary returned")
            print("what_to_do_next:")
            print(f"- {state.operator_next_step or 'Review the dashboard control center or queue a narrow local action.'}")
            print("- use Ctrl+8 if a desktop action or recipe needs to stop immediately")
            if state.pending_approval_count > 0:
                print("- review pending approvals before trying to run blocked work")
            elif state.blocked_human_needed_count > 0:
                print("- inspect blocked human-needed tasks and decide whether to review, resume, or re-queue them")
            elif state.interrupted_count > 0:
                print("- inspect interrupted tasks before any re-queue")
            else:
                print("- queue one narrow repo, desktop, or recipe action from the dashboard or CLI")
            return 0

        if args.command == "ghoti-recent":
            ensure_runtime_files()
            tasks = list_executor_tasks()
            actionable_tasks = [
                task for task in tasks if str(task.status or "").lower() in GHOTI_ACTIONABLE_STATUSES
            ]
            active_tasks = [
                task for task in tasks if str(task.status or "").lower() in GHOTI_ACTIVE_STATUSES
            ]
            failure_tasks = [
                task for task in tasks if str(task.status or "").lower() in GHOTI_FAILURE_STATUSES
            ]
            pending_requests = list_pending_approvals()
            state = get_supervisor_state()
            active_task = get_task(state.active_task_id) if state.active_task_id else None
            watchdog = _build_ghoti_watchdog(state, tasks, active_task)
            print("ghoti_recent: recent actionable work, failures, approvals, and artifacts")
            print(f"watchdog_status: {watchdog['status']}")
            print(f"watchdog_headline: {watchdog['headline']}")
            print(f"overlay_target: {watchdog['overlay_target']}")
            print(f"overlay_target_detail: {watchdog['overlay_target_detail']}")
            _print_role_status_block(active_task=active_task)
            _print_browser_status_block()
            _print_memory_status_block()
            _print_relay_status_block()
            _print_brain_status_block(active_task=active_task)
            _print_desktop_action_block(active_task=active_task)
            print("recent_actionable_tasks:")
            _print_ghoti_task_lines(actionable_tasks, limit=6)
            print("active_only_tasks:")
            _print_ghoti_task_lines(active_tasks, limit=6)
            print("recent_failures:")
            _print_ghoti_task_lines(failure_tasks, limit=6)
            print("watchdog_alerts:")
            if watchdog["alerts"]:
                for alert in watchdog["alerts"]:
                    print(f"- {alert}")
            else:
                print("- none")
            print("pending_approvals:")
            if pending_requests:
                for request in pending_requests[:5]:
                    print(
                        f"- {request.approval_id} | {request.status} | "
                        f"{request.action_label} | {_approval_target(request.scope, request.task_id)}"
                    )
            else:
                print("- none")
            print("recent_artifacts:")
            recent_artifacts = _iter_recent_artifacts(limit=6)
            if recent_artifacts:
                repo_root = _repo_root()
                for artifact_path in recent_artifacts:
                    relative_path = artifact_path.relative_to(repo_root)
                    print(f"- {relative_path} | modified={datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc).isoformat().replace('+00:00', 'Z')}")
            else:
                print("- none")
            return 0

        if args.command == "list-agent-roles":
            status = get_specialist_role_status()
            print("agent_roles: specialist role registry snapshot")
            print(f"current_specialist_role: {status.current_role_id}")
            print(f"specialist_role_registry_count: {status.registry_count}")
            print(f"current_specialist_role_purpose: {status.current_role_purpose}")
            print(f"current_specialist_role_provider: {status.current_role_provider}")
            print(f"current_specialist_role_sensitivity: {status.current_role_sensitivity}")
            print(f"current_specialist_role_reason: {status.current_role_reason}")
            print("roles:")
            for role in status.roles:
                print(
                    f"- {role.role_id} | provider={role.preferred_provider} | sensitivity={role.approval_sensitivity} | tools={', '.join(role.allowed_tools)}"
                )
            return 0

        if args.command == "browser-status":
            print("browser_status: browser-agent capability snapshot")
            _print_browser_status_block()
            return 0

        if args.command == "ghoti-mcp-status":
            running_processes = _detect_running_mcp_server_processes()
            probe_ok, probe_status, probe_detail = _probe_mcp_server()
            if probe_ok and running_processes:
                headline = "MCP server reachable"
            elif probe_ok:
                headline = "MCP server not running"
            else:
                headline = "MCP server error"
            print(f"ghoti_mcp_status: {headline}")
            print(f"mcp_server_script: {_mcp_server_script_path()}")
            print(f"mcp_process_running: {'yes' if running_processes else 'no'}")
            print(f"mcp_running_process_count: {len(running_processes)}")
            print(f"mcp_probe_status: {probe_status}")
            print(f"mcp_probe_reachable: {'yes' if probe_ok else 'no'}")
            print(f"mcp_probe_detail: {probe_detail}")
            print("mcp_running_processes:")
            if running_processes:
                for process in running_processes:
                    print(f"- pid={process['pid']} | name={process['name']}")
            else:
                print("- none")
            return 0

        if args.command == "ghoti-mcp-call":
            try:
                payload = call_mcp_tool(args.tool_name)
            except Exception as exc:
                print("ghoti_mcp_call: failed")
                print(f"reason: {exc}")
                return 1
            print("ghoti_mcp_call: success")
            print(f"result: {json.dumps(payload, indent=2)}")
            return 0

        if args.command == "ghoti-operator-tick":
            tick = simple_operator_tick()
            print("ghoti_operator:")
            print(f"status: {tick.get('status', 'unknown')}")
            print(f"decision: {tick.get('decision', 'none')}")
            print(f"proposed_next_action: {tick.get('proposed_next_action', 'none')}")
            print(f"approval_required: {'yes' if tick.get('approval_required', False) else 'no'}")
            print(f"timestamp_utc: {tick.get('timestamp_utc', 'none')}")
            print(f"operator_state_path: {tick.get('operator_state_path', str(OPERATOR_STATE_FILE))}")
            print(f"approval_inbox_path: {tick.get('approval_inbox_path', str(APPROVAL_INBOX_PATH))}")
            print(f"approval_item_status: {tick.get('approval_item_status', 'none')}")
            print(f"approval_item_id: {tick.get('approval_item_id', 'none') or 'none'}")
            if tick.get('reason'):
                print(f"reason: {tick['reason']}")
            print(f"repo: {json.dumps(tick.get('repo_summary', {}), indent=2)}")
            print(f"state: {json.dumps(tick.get('current_state_preview_info', {}), indent=2)}")
            return 0 if tick.get('status') == 'ok' else 1

        if args.command == "ghoti-operator-state":
            state = read_latest_operator_state()
            print("ghoti_operator_state:")
            print(f"path: {OPERATOR_STATE_FILE}")
            print(f"status: {state.get('status', 'unknown')}")
            if state.get('reason'):
                print(f"reason: {state['reason']}")
            else:
                print(f"decision: {state.get('decision', 'none')}")
                print(f"proposed_next_action: {state.get('proposed_next_action', 'none')}")
                print(f"approval_required: {'yes' if state.get('approval_required', False) else 'no'}")
                print(f"timestamp_utc: {state.get('timestamp_utc', 'none')}")
            print(json.dumps(state, indent=2))
            return 0 if state.get('status') == 'ok' else 1

        if args.command == "ghoti-approval-list":
            inbox = read_approval_inbox_state()
            items = inbox.get("items", []) if inbox.get("status") == "ok" else []
            counts = {
                "total_count": len(items),
                "pending_count": sum(1 for item in items if item.get("status") == "pending"),
                "approved_count": sum(1 for item in items if item.get("status") == "approved"),
                "rejected_count": sum(1 for item in items if item.get("status") == "rejected"),
            }
            payload = _build_supervised_payload(
                status=inbox.get("status", "unknown"),
                summary={
                    "path": inbox.get("path", str(APPROVAL_INBOX_PATH)),
                    "counts": counts,
                    "items": items,
                },
                items=items,
                errors=[inbox.get("reason", "unknown")] if inbox.get("status") != "ok" else [],
            )
            _emit_supervised_json("ghoti_approval_list:", payload)
            return 0 if inbox.get("status") == "ok" else 1

        if args.command == "ghoti-approval-view":
            result = get_approval_item(args.approval_id)
            item = result.get("item") if result.get("status") == "ok" else None
            payload = _build_supervised_payload(
                status=result.get("status", "unknown"),
                summary={
                    "path": result.get("path", str(APPROVAL_INBOX_PATH)),
                    "approval_id": args.approval_id,
                    "item": item,
                },
                item=item,
                errors=[result.get("reason", "unknown")] if result.get("status") != "ok" else [],
            )
            _emit_supervised_json("ghoti_approval_view:", payload)
            return 0 if result.get("status") == "ok" else 1

        if args.command == "ghoti-approval-approve":
            result = update_approval_item_status(args.approval_id, new_status="approved")
            item = result.get("item") if isinstance(result.get("item"), dict) else None
            bridge_result = result.get("bridge_result") if isinstance(result.get("bridge_result"), dict) else None
            bridge_status = bridge_result.get("status", "not_attempted") if bridge_result else "not_attempted"
            transition_succeeded = bool(result.get("transition_succeeded", False))
            bridge_attempted = bool(result.get("bridge_attempted", False))
            bridge_succeeded = result.get("bridge_succeeded")
            status = result.get("status", "unknown")
            if status == "ok" and bridge_status == "created":
                headline = "Approval approved and manual queue item created."
            elif status == "ok" and bridge_status == "deduped":
                headline = "Approval approved and existing manual queue item reused."
            elif status == "partial":
                headline = "Approval approved, but manual queue bridge failed."
            elif status == "ok":
                headline = "Approval approved."
            else:
                headline = result.get("reason", "Approval approve failed.")
            payload = _build_supervised_payload(
                status=status,
                summary={
                    "headline": headline,
                    "action": "approve",
                    "approval_id": args.approval_id,
                    "path": result.get("path", str(APPROVAL_INBOX_PATH)),
                    "item_status": item.get("status", "none") if item else "none",
                    "transition_succeeded": transition_succeeded,
                    "transition_status": result.get("transition_status", item.get("status", "unknown") if item else "unknown"),
                    "bridge_attempted": bridge_attempted,
                    "bridge_succeeded": bridge_succeeded,
                    "bridge_status": bridge_status,
                },
                item=item,
                errors=[result.get("reason", "unknown")] if status != "ok" and result.get("reason") else [],
                transition_succeeded=transition_succeeded,
                transition_status=result.get("transition_status", item.get("status", "unknown") if item else "unknown"),
                bridge_attempted=bridge_attempted,
                bridge_succeeded=bridge_succeeded,
                bridge_result=bridge_result,
            )
            _emit_supervised_json("ghoti_approval_approve:", payload)
            return 0 if status == "ok" else 1

        if args.command == "ghoti-approval-reject":
            result = update_approval_item_status(args.approval_id, new_status="rejected", reason=args.reason)
            item = result.get("item") if isinstance(result.get("item"), dict) else None
            status = result.get("status", "unknown")
            headline = "Approval rejected." if status == "ok" else result.get("reason", "Approval reject failed.")
            payload = _build_supervised_payload(
                status=status,
                summary={
                    "headline": headline,
                    "action": "reject",
                    "approval_id": args.approval_id,
                    "path": result.get("path", str(APPROVAL_INBOX_PATH)),
                    "item_status": item.get("status", "none") if item else "none",
                    "transition_succeeded": bool(result.get("transition_succeeded", status == "ok")),
                    "transition_status": result.get("transition_status", item.get("status", "unknown") if item else "unknown"),
                    "bridge_attempted": bool(result.get("bridge_attempted", False)),
                    "bridge_succeeded": result.get("bridge_succeeded"),
                },
                item=item,
                errors=[result.get("reason", "unknown")] if status != "ok" and result.get("reason") else [],
                transition_succeeded=bool(result.get("transition_succeeded", status == "ok")),
                transition_status=result.get("transition_status", item.get("status", "unknown") if item else "unknown"),
                bridge_attempted=bool(result.get("bridge_attempted", False)),
                bridge_succeeded=result.get("bridge_succeeded"),
            )
            _emit_supervised_json("ghoti_approval_reject:", payload)
            return 0 if status == "ok" else 1

        if args.command == "ghoti-manual-queue-list":
            queue = read_manual_queue_state()
            items = queue.get("items", []) if queue.get("status") == "ok" else []
            counts = {
                "total_count": len(items),
                "ready_count": sum(1 for item in items if item.get("status") == "ready_for_manual_execution"),
                "reviewed_count": sum(1 for item in items if item.get("status") == "reviewed_by_operator"),
            }
            payload = _build_supervised_payload(
                status=queue.get("status", "unknown"),
                summary={
                    "path": queue.get("path", str(MANUAL_EXECUTION_QUEUE_PATH)),
                    "counts": counts,
                    "items": items,
                },
                items=items,
                errors=[queue.get("reason", "unknown")] if queue.get("status") != "ok" else [],
            )
            _emit_supervised_json("ghoti_manual_queue_list:", payload)
            return 0 if queue.get("status") == "ok" else 1

        if args.command == "ghoti-manual-queue-view":
            result = get_manual_queue_item(args.item_id)
            item = result.get("item") if result.get("status") == "ok" else None
            payload = _build_supervised_payload(
                status=result.get("status", "unknown"),
                summary={
                    "path": result.get("path", str(MANUAL_EXECUTION_QUEUE_PATH)),
                    "item_id": args.item_id,
                    "item": item,
                },
                item=item,
                errors=[result.get("reason", "unknown")] if result.get("status") != "ok" else [],
            )
            _emit_supervised_json("ghoti_manual_queue_view:", payload)
            return 0 if result.get("status") == "ok" else 1

        if args.command == "ghoti-manual-queue-state":
            queue = read_manual_queue_state()
            print("ghoti_manual_queue_state:")
            print(f"path: {queue.get('path', str(MANUAL_EXECUTION_QUEUE_PATH))}")
            print(f"status: {queue.get('status', 'unknown')}")
            if queue.get("status") != "ok":
                print(f"reason: {queue.get('reason', 'unknown')}")
                return 1
            items = queue.get("items", [])
            print(f"item_count: {len(items)}")
            status_counts: dict[str, int] = {}
            for item in items:
                s = str(item.get("status", "unknown"))
                status_counts[s] = status_counts.get(s, 0) + 1
            for s, c in status_counts.items():
                print(f"  {s}: {c}")
            return 0

        if args.command == "ghoti-manual-queue-explain":
            result = explain_manual_queue_item(args.item_id)
            print("ghoti_manual_queue_explain:")
            print(f"path: {result.get('path', str(MANUAL_EXECUTION_QUEUE_PATH))}")
            print(f"status: {result.get('status', 'unknown')}")
            if result.get("status") != "ok":
                print(f"reason: {result.get('reason', 'unknown')}")
                return 1
            print(json.dumps(result.get("explanation", {}), indent=2))
            return 0

        if args.command == "ghoti-audit-trace":
            approval_id = args.approval_id
            if not approval_id and getattr(args, "latest_approved", False):
                latest = find_latest_approved_approval_item()
                approval_id = latest.get("id", "") if latest else ""
            if not approval_id:
                trace = {
                    "trace_status": "error",
                    "reason": "approval_id_required_or_use_latest_approved",
                    "approval_id": "",
                }
                payload = _build_supervised_payload(
                    status="error",
                    summary=trace,
                    trace=trace,
                    errors=[trace["reason"]],
                )
                _emit_supervised_json("ghoti_audit_trace:", payload)
                return 1
            trace = get_audit_trace(approval_id)
            trace_status = trace.get("trace_status", "unknown")
            payload = _build_supervised_payload(
                status=trace_status,
                summary=trace,
                trace=trace,
                errors=[trace.get("reason", "unknown")] if trace_status == "error" and trace.get("reason") else [],
            )
            _emit_supervised_json("ghoti_audit_trace:", payload)
            return 0 if trace_status in {"ok", "partial"} else 1

        if args.command == "ghoti-control-center-state":
            state = get_full_control_center_state()
            payload = _build_supervised_payload(
                status=state.get("status", "unknown"),
                summary=state,
                errors=[state.get("reason", "unknown")] if state.get("status") == "error" and state.get("reason") else [],
            )
            _emit_supervised_json("ghoti_control_center_state:", payload)
            return 0 if state.get("status") in {"ok", "partial"} else 1

        if args.command == "ghoti-pipeline-items":
            status_filter = getattr(args, "status", None)
            overview = get_pipeline_items_overview(status_filter)
            payload = _build_supervised_payload(
                status=overview.get("status", "unknown"),
                summary=overview,
                items=overview.get("items", []) if overview.get("status") != "error" else [],
                errors=[overview.get("reason", "unknown")] if overview.get("status") == "error" and overview.get("reason") else [],
            )
            _emit_supervised_json("ghoti_pipeline_items:", payload)
            return 0 if overview.get("status") in {"ok", "partial"} else 1

        if args.command == "ghoti-action-intents":
            state = get_action_intent_read_model(getattr(args, "limit", 20))
            payload = _build_supervised_payload(
                status=state.get("status", "unknown"),
                summary=state.get("summary", {}),
                items=state.get("intents", []) if state.get("status") != "error" else [],
                errors=[state.get("reason", "unknown")] if state.get("status") == "error" and state.get("reason") else [],
                adapters=state.get("adapters", []),
                audit=state.get("audit", []),
                honest_status=state.get("honest_status", {}),
            )
            _emit_supervised_json("ghoti_action_intents:", payload)
            return 0 if state.get("status") == "ok" else 1

        if args.command == "ghoti-capability-adapters":
            adapters = list_capability_adapters()
            payload = _build_supervised_payload(
                status="ok",
                summary={
                    "adapter_count": len(adapters),
                    "runtime_wired_adapters": sum(1 for adapter in adapters if adapter.get("can_execute") is True),
                    "external_adapters_wired": False,
                    "autonomous_execution": False,
                },
                items=adapters,
                adapters=adapters,
            )
            _emit_supervised_json("ghoti_capability_adapters:", payload)
            return 0

        if args.command == "ghoti-action-intent-create":
            try:
                payload_json = json.loads(args.payload_json)
                if not isinstance(payload_json, dict):
                    raise ValueError("payload_json_must_be_object")
            except (json.JSONDecodeError, ValueError) as exc:
                payload = _build_supervised_payload(
                    status="error",
                    summary={"headline": "ActionIntent create failed.", "reason": f"invalid_payload_json: {exc}"},
                    errors=[f"invalid_payload_json: {exc}"],
                )
                _emit_supervised_json("ghoti_action_intent_create:", payload)
                return 1
            result = create_action_intent(
                requested_by_agent=args.requested_by_agent,
                adapter_id=args.adapter_id,
                action_type=args.action_type,
                target=args.target,
                payload=payload_json,
                reason=args.reason,
                audit_tags=["cli_created"],
            )
            intent = result.get("intent") if isinstance(result.get("intent"), dict) else None
            approval_item = result.get("approval_item") if isinstance(result.get("approval_item"), dict) else None
            status = result.get("status", "unknown")
            headline = (
                "ActionIntent created and approval item opened."
                if status == "ok" and approval_item
                else "ActionIntent blocked by safety policy."
                if status == "blocked"
                else result.get("reason", "ActionIntent create failed.")
            )
            payload = _build_supervised_payload(
                status=status,
                summary={
                    "headline": headline,
                    "intent_id": intent.get("intent_id") if intent else None,
                    "approval_id": approval_item.get("id") if approval_item else None,
                    "risk_level": intent.get("risk_level") if intent else None,
                    "intent_status": intent.get("status") if intent else None,
                    "approval_bound": bool(result.get("approval_bound", False)),
                    "payload_bound": bool(result.get("payload_bound", True)),
                    "execution_performed": False,
                },
                item=intent,
                errors=result.get("intent", {}).get("errors", []) if status == "blocked" else ([result.get("reason", "unknown")] if status == "error" and result.get("reason") else []),
                approval_item=approval_item,
                execution_performed=False,
            )
            _emit_supervised_json("ghoti_action_intent_create:", payload)
            return 0 if status == "ok" else 1

        if args.command == "ghoti-action-intent-consume":
            try:
                payload_json = json.loads(args.payload_json)
                if not isinstance(payload_json, dict):
                    raise ValueError("payload_json_must_be_object")
            except (json.JSONDecodeError, ValueError) as exc:
                payload = _build_supervised_payload(
                    status="error",
                    summary={"headline": "ActionIntent consume failed.", "reason": f"invalid_payload_json: {exc}"},
                    errors=[f"invalid_payload_json: {exc}"],
                )
                _emit_supervised_json("ghoti_action_intent_consume:", payload)
                return 1
            result = consume_action_intent(
                intent_id=args.intent_id,
                adapter_id=args.adapter_id,
                action_type=args.action_type,
                payload=payload_json,
            )
            intent = result.get("intent") if isinstance(result.get("intent"), dict) else None
            status = result.get("status", "unknown")
            headline = (
                "ActionIntent approval consumed. No adapter execution performed."
                if status == "ok"
                else result.get("reason", "ActionIntent consume failed.")
            )
            payload = _build_supervised_payload(
                status=status,
                summary={
                    "headline": headline,
                    "intent_id": args.intent_id,
                    "adapter_id": args.adapter_id,
                    "approval_bound": bool(result.get("approval_bound", False)),
                    "payload_bound": bool(result.get("payload_bound", False)),
                    "execution_performed": False,
                    "reason": result.get("reason", ""),
                },
                item=intent,
                errors=[result.get("reason", "unknown")] if status != "ok" and result.get("reason") else [],
                approval_item=result.get("approval_item") if isinstance(result.get("approval_item"), dict) else None,
                execution_performed=False,
                next_required_step=result.get("next_required_step", ""),
            )
            _emit_supervised_json("ghoti_action_intent_consume:", payload)
            return 0 if status == "ok" else 1

        if args.command == "ghoti-manual-queue-mark-reviewed":
            result = update_manual_queue_item_review(args.item_id, args.note)
            item = result.get("item") if isinstance(result.get("item"), dict) else None
            status = result.get("status", "unknown")
            transition_succeeded = status == "ok"
            headline = "Queue item marked reviewed by operator." if transition_succeeded else result.get("reason", "Queue item review failed.")
            payload = _build_supervised_payload(
                status=status,
                summary={
                    "headline": headline,
                    "action": "mark_reviewed",
                    "item_id": args.item_id,
                    "path": result.get("path", str(MANUAL_EXECUTION_QUEUE_PATH)),
                    "item_status": item.get("status", "none") if item else "none",
                    "transition_succeeded": transition_succeeded,
                    "transition_status": item.get("status", "unknown") if item else "unknown",
                    "bridge_attempted": False,
                    "bridge_succeeded": None,
                },
                item=item,
                errors=[result.get("reason", "unknown")] if status != "ok" and result.get("reason") else [],
                transition_succeeded=transition_succeeded,
                transition_status=item.get("status", "unknown") if item else "unknown",
                bridge_attempted=False,
                bridge_succeeded=None,
            )
            _emit_supervised_json("ghoti_manual_queue_mark_reviewed:", payload)
            return 0 if status == "ok" else 1

        if args.command == "memory-status":
            print("memory_status: compact markdown memory snapshot")
            _print_memory_status_block()
            return 0

        if args.command == "relay-status":
            print("relay_status: supervised chatgpt to codex relay snapshot")
            _print_relay_status_block()
            return 0

        if args.command == "relay-bind-target":
            status = save_relay_target_binding(alias=args.alias, candidate_id=args.candidate_id)
            print("relay_bind_target: succeeded")
            print(f"alias: {args.alias}")
            print(f"candidate_id: {args.candidate_id}")
            binding_status = status.source_binding.binding_status if args.alias == status.source_target_alias else status.destination_binding.binding_status
            print(f"binding_status: {binding_status}")
            print(f"runtime_relay_state_file: {RUNTIME_RELAY_LOOP_STATE_PATH}")
            return 0

        if args.command == "relay-set-preset":
            status = save_codex_preset(mode=args.mode, reasoning=args.reasoning, application_status=args.application_status)
            print("relay_set_preset: succeeded")
            print(f"relay_codex_mode_preset: {status.codex_mode_preset}")
            print(f"relay_codex_reasoning_preset: {status.codex_reasoning_preset}")
            print(f"relay_preset_application_status: {status.preset_application_status}")
            print(f"runtime_relay_state_file: {RUNTIME_RELAY_LOOP_STATE_PATH}")
            return 0

        if args.command == "relay-update-state":
            status = update_relay_loop_state(
                relay_state=args.state or None,
                current_step=args.step or None,
                source_alias=args.source_alias or None,
                destination_alias=args.destination_alias or None,
                waiting_reason=args.waiting_reason or None,
                blocked_reason=args.blocked_reason or None,
                last_payload_preview=args.payload_preview or None,
                last_result_preview=args.result_preview or None,
                codex_execution_status=args.codex_status or None,
                next_usage_reset_at=args.next_usage_reset_at or None,
                resume_after_usage_reset=(args.resume_after_usage_reset == "yes") if args.resume_after_usage_reset else None,
                last_completion_status=args.completion_status or None,
                task_id=args.task_id or None,
                preset_application_status=args.preset_application_status or None,
                dialog_status=args.dialog_status or None,
                dialog_note=args.dialog_note or None,
            )
            print("relay_update_state: succeeded")
            print(f"relay_state: {status.relay_state}")
            print(f"relay_current_step: {status.current_step}")
            print(f"relay_codex_execution_status: {status.codex_execution_status}")
            print(f"relay_next_usage_reset_at: {status.next_usage_reset_at or 'none'}")
            print(f"runtime_relay_state_file: {RUNTIME_RELAY_LOOP_STATE_PATH}")
            return 0

        if args.command == "brain-status":
            ensure_runtime_files()
            state = get_supervisor_state()
            active_task = get_task(state.active_task_id) if state.active_task_id else None
            print("brain_status: local brain/provider snapshot")
            print(f"runtime_brain_config_file: {RUNTIME_BRAIN_CONFIG_PATH}")
            print(f"runtime_brain_state_file: {RUNTIME_BRAIN_STATE_PATH}")
            _print_brain_status_block(active_task=active_task)
            return 0

        if args.command == "brain-set-active":
            config = save_brain_config_override(
                provider=args.provider,
                model=args.model,
                ollama_base_url=args.ollama_base_url or None,
            )
            print(f"active_brain_provider: {config.active_provider}")
            print(f"active_brain_model: {config.active_model}")
            print(f"brain_ollama_base_url: {config.ollama_base_url}")
            print(f"brain_config_source: {config.config_source}")
            print(f"runtime_brain_config_file: {RUNTIME_BRAIN_CONFIG_PATH}")
            return 0

        if args.command == "brain-infer":
            result = run_brain_inference(
                args.prompt,
                source=args.source,
                task_id=args.task_id,
            )
            print("brain_infer: succeeded")
            print(f"provider: {get_brain_status().active_provider}")
            print(f"model: {get_brain_status().active_model}")
            print(f"task_id: {args.task_id or 'none'}")
            print(f"response: {result}")
            return 0

        if args.command == "status":
            ensure_runtime_files()
            summary = get_status_summary()
            tasks = list_tasks()
            branch = _get_current_branch()
            snapshot_exists = (get_runtime_data_dir() / "handoff_snapshot.md").exists()
            if branch:
                print(f"branch: {branch}")
            print(f"runtime_data: {get_runtime_data_dir()}")
            print(f"tasks_total: {summary.total_tasks}")
            print(f"tasks_queued: {summary.queued_tasks}")
            print(f"tasks_running: {summary.running_tasks}")
            print(f"tasks_pending_approval: {summary.pending_approval_tasks}")
            print(f"tasks_waiting: {summary.waiting_tasks}")
            print(f"tasks_blocked_human_needed: {summary.blocked_human_needed_tasks}")
            print(f"tasks_interrupted: {summary.interrupted_tasks}")
            print(f"tasks_ready_to_resume: {summary.ready_to_resume_tasks}")
            print(f"tasks_completed: {summary.completed_tasks}")
            print(f"tasks_rejected: {summary.rejected_tasks}")
            print(f"tasks_failed: {summary.failed_tasks}")
            print(f"approval_requests_pending: {summary.pending_approval_requests}")
            print(f"tasks_file: {TASKS_PATH}")
            print(f"approvals_file: {APPROVALS_PATH}")
            print(f"approval_requests_file: {APPROVAL_REQUESTS_PATH}")
            print(f"supervisor_state_file: {SUPERVISOR_STATE_PATH}")
            print(f"handoff_snapshot_exists: {'yes' if snapshot_exists else 'no'}")
            return 0

        if args.command == "enqueue":
            with runtime_data_lock():
                task = enqueue_task(
                    title=args.title,
                    description=args.description,
                    risk_level=args.risk,
                    source=args.source,
                )
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            if task.approval_request_id:
                print(f"approval_request_id: {task.approval_request_id}")
            return 0

        if args.command == "queue-executor-action":
            with runtime_data_lock():
                task = enqueue_executor_task(
                    action_type=args.action_type,
                    target=args.target,
                    content=args.content,
                    source=args.source,
                )
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"executor_action_type: {task.executor_action_type}")
            print(f"executor_target: {task.executor_target or 'none'}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            if task.executor_action_type == "run_operator_recipe":
                print(f"recipe_name: {task.executor_payload.get('recipe_name', 'none')}")
                print(f"recipe_label: {task.executor_payload.get('recipe_label', 'none')}")
                print(f"recipe_step_count: {len(task.executor_payload.get('recipe_steps', []))}")
                print(f"recipe_source_window: {task.executor_payload.get('recipe_source_window', 'none')}")
                print(f"recipe_target_window: {task.executor_payload.get('recipe_target_window', 'none')}")
                print(f"recipe_clipboard_mode: {task.executor_payload.get('recipe_clipboard_mode', 'none')}")
                print(f"handoff_send_behavior: {task.executor_payload.get('handoff_send_behavior', 'none')}")
                print(f"handoff_fallback_denied: {task.executor_payload.get('handoff_fallback_denied', 'none')}")
                print(f"handoff_target_resolution_status: {task.executor_payload.get('handoff_target_resolution_status', 'none')}")
            if task.approval_request_id:
                print(f"approval_request_id: {task.approval_request_id}")
            return 0

        if args.command == "list":
            tasks = list_tasks()
            if not tasks:
                print("No tasks found.")
                return 0
            for task in tasks:
                print(
                    f"{task.task_id} | {task.status} | {task.risk_level} | "
                    f"{task.approval_state} | scope={task.workspace_scope} | "
                    f"policy={task.workspace_policy} | next={get_task_next_action(task)} | "
                    f"{task.title}"
                )
            return 0

        if args.command == "list-executor-tasks":
            tasks = list_executor_tasks()
            print(f"count: {len(tasks)}")
            if not tasks:
                print("tasks: none")
                return 0
            print("tasks:")
            for task in tasks:
                last_execution = task.execution_records[-1] if task.execution_records else None
                last_summary = last_execution.output_summary if last_execution else "not_run"
                task_type = _classify_executor_task(task)
                desktop_truth = _desktop_action_truth(task)
                recipe_bits = []
                if task.executor_action_type == "run_operator_recipe":
                    recipe_name = task.executor_payload.get("recipe_name", "")
                    recipe_source = task.executor_payload.get("recipe_source_window", "")
                    recipe_target = task.executor_payload.get("recipe_target_window", "")
                    source_candidate = task.executor_payload.get("recipe_source_window_candidate_id", "")
                    target_candidate = task.executor_payload.get("recipe_target_window_candidate_id", "")
                    source_mode = task.executor_payload.get("handoff_source_selection_mode", "")
                    target_mode = task.executor_payload.get("handoff_target_selection_mode", "")
                    payload_classification = task.executor_payload.get("handoff_payload_classification", "")
                    send_behavior = task.executor_payload.get("handoff_send_behavior", "")
                    if recipe_name:
                        recipe_bits.append(f"recipe={recipe_name}")
                    if recipe_source:
                        recipe_bits.append(f"source_window={recipe_source}")
                    if recipe_target:
                        recipe_bits.append(f"target_window={recipe_target}")
                    if source_candidate:
                        recipe_bits.append(f"source_candidate={source_candidate}")
                    if target_candidate:
                        recipe_bits.append(f"target_candidate={target_candidate}")
                    if source_mode:
                        recipe_bits.append(f"source_mode={source_mode}")
                    if target_mode:
                        recipe_bits.append(f"target_mode={target_mode}")
                    if payload_classification:
                        recipe_bits.append(f"classification={payload_classification}")
                    if send_behavior:
                        recipe_bits.append(f"send_behavior={send_behavior}")
                print(
                    f"- {task.task_id} | {task.status} | action={task.executor_action_type} | "
                    f"target={task.executor_target or 'none'} | approval={task.approval_state} | "
                    f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                    f"type={task_type} | title={_short_description(task.title, limit=80)} | "
                    f"updated={task.updated_at or 'none'} | "
                    f"last={_short_description(last_summary, limit=100)} | "
                    f"desktop_action={desktop_truth['last_action']} | "
                    f"desktop_target={desktop_truth['last_target']} | "
                    f"typing_enabled={desktop_truth['last_typing_enabled']} | "
                    f"desktop_status={desktop_truth['last_status']} | "
                    f"cue_status={desktop_truth['cue_status']} | "
                    f"inference={'yes' if (last_execution.used_model_inference if last_execution else False) else 'no'} | "
                    f"model_provider={(last_execution.model_provider if last_execution and last_execution.model_provider else 'none')} | "
                    f"model_name={(last_execution.model_name if last_execution and last_execution.model_name else 'none')} | "
                    f"model_status={(last_execution.model_call_status if last_execution and last_execution.model_call_status else 'not_used')}"
                    + (f" | {' | '.join(recipe_bits)}" if recipe_bits else "")
                )
            return 0

        if args.command == "task-status":
            task = get_task(args.task_id)
            history = get_task_history(args.task_id)
            last_execution = task.execution_records[-1] if task.execution_records else None
            desktop_truth = _desktop_action_truth(task)
            print(f"task_id: {task.task_id}")
            print(f"title: {task.title}")
            print(f"description: {task.description}")
            print(f"status: {task.status}")
            print(f"risk_level: {task.risk_level}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            print(f"source: {task.source}")
            print(f"executor_action_type: {task.executor_action_type or 'none'}")
            print(f"executor_target: {task.executor_target or 'none'}")
            recipe_last_run = task.executor_payload.get("recipe_last_run", {}) if task.executor_action_type == "run_operator_recipe" else {}
            print(f"recipe_name: {task.executor_payload.get('recipe_name', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_label: {task.executor_payload.get('recipe_label', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_status: {recipe_last_run.get('status', 'not_run') if task.executor_action_type == 'run_operator_recipe' else 'not_run'}")
            print(f"recipe_summary: {recipe_last_run.get('summary', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_run_count: {len(task.executor_payload.get('recipe_run_history', [])) if task.executor_action_type == 'run_operator_recipe' else 0}")
            print(f"recipe_last_run_started_at: {recipe_last_run.get('started_at', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_last_run_finished_at: {recipe_last_run.get('finished_at', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_source_window: {task.executor_payload.get('recipe_source_window', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_target_window: {task.executor_payload.get('recipe_target_window', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_source_window_candidate_id: {task.executor_payload.get('recipe_source_window_candidate_id', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_target_window_candidate_id: {task.executor_payload.get('recipe_target_window_candidate_id', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"recipe_clipboard_mode: {task.executor_payload.get('recipe_clipboard_mode', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_source_selection_mode: {task.executor_payload.get('handoff_source_selection_mode', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_target_selection_mode: {task.executor_payload.get('handoff_target_selection_mode', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_payload_classification: {task.executor_payload.get('handoff_payload_classification', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_payload_preview: {task.executor_payload.get('handoff_payload_preview', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_payload_reason: {task.executor_payload.get('handoff_payload_reason', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_paste_allowed: {task.executor_payload.get('handoff_paste_allowed', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_send_behavior: {task.executor_payload.get('handoff_send_behavior', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_send_allowed: {task.executor_payload.get('handoff_send_allowed', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_fallback_denied: {task.executor_payload.get('handoff_fallback_denied', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_target_resolution_status: {task.executor_payload.get('handoff_target_resolution_status', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_manual_target_resolution: {task.executor_payload.get('handoff_manual_target_resolution', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_source_match: {task.executor_payload.get('handoff_source_match', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_target_match: {task.executor_payload.get('handoff_target_match', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_stop_reason: {task.executor_payload.get('handoff_stop_reason', 'none') if task.executor_action_type == 'run_operator_recipe' else 'none'}")
            print(f"handoff_blocked_payload_repeats: {task.executor_payload.get('handoff_blocked_payload_repeats', '0') if task.executor_action_type == 'run_operator_recipe' else '0'}")
            print(f"workspace_scope: {task.workspace_scope}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"workspace_reason: {task.workspace_reason or 'none'}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            print(f"waiting_for: {task.waiting_for or 'none'}")
            print(f"blocked_reason: {task.blocked_reason or 'none'}")
            print(f"requires_human: {'yes' if task.requires_human else 'no'}")
            print(f"admin_required: {'yes' if task.admin_required else 'no'}")
            print(f"last_note: {task.last_note or 'none'}")
            print(f"created_at: {task.created_at}")
            print(f"updated_at: {task.updated_at}")
            print(f"next_action: {get_task_next_action(task)}")
            print(f"execution_count: {len(task.execution_records)}")
            print(f"last_execution_status: {last_execution.status if last_execution else 'not_run'}")
            print(f"last_execution_summary: {last_execution.output_summary if last_execution else 'none'}")
            print(f"last_artifact_path: {last_execution.artifact_path if last_execution and last_execution.artifact_path else 'none'}")
            print(f"last_attempt_count: {last_execution.attempt_count if last_execution else 0}")
            print(f"last_failure_reason: {last_execution.failure_reason if last_execution and last_execution.failure_reason else 'none'}")
            print(f"last_interruption_reason: {last_execution.interruption_reason if last_execution and last_execution.interruption_reason else 'none'}")
            print(f"last_resource_guard_reason: {last_execution.resource_guard_reason if last_execution and last_execution.resource_guard_reason else 'none'}")
            print(f"last_used_model_inference: {'yes' if last_execution and last_execution.used_model_inference else 'no'}")
            print(f"last_model_provider: {last_execution.model_provider if last_execution and last_execution.model_provider else 'none'}")
            print(f"last_model_name: {last_execution.model_name if last_execution and last_execution.model_name else 'none'}")
            print(f"last_model_call_status: {last_execution.model_call_status if last_execution and last_execution.model_call_status else 'not_used'}")
            print(f"desktop_current_action: {desktop_truth['current_action']}")
            print(f"desktop_current_target: {desktop_truth['current_target']}")
            print(f"desktop_current_typing_enabled: {desktop_truth['current_typing_enabled']}")
            print(f"desktop_last_action: {desktop_truth['last_action']}")
            print(f"desktop_last_target: {desktop_truth['last_target']}")
            print(f"desktop_last_typing_enabled: {desktop_truth['last_typing_enabled']}")
            print(f"desktop_last_action_status: {desktop_truth['last_status']}")
            print(f"desktop_visual_cue_status: {desktop_truth['cue_status']}")
            print(f"desktop_visual_cue_action: {desktop_truth['cue_action']}")
            print(f"desktop_visual_cue_target: {desktop_truth['cue_target']}")
            print(f"desktop_last_text_preview: {desktop_truth['text_preview']}")
            print(f"retry_limit: {task.executor_payload.get('last_retry_limit', task.executor_payload.get('max_attempts', 0)) or 0}")
            print("target_paths:")
            if task.target_paths:
                for item in task.target_paths:
                    print(f"- {item}")
            else:
                print("- none")
            print("recipe_steps:")
            if task.executor_action_type == "run_operator_recipe" and task.executor_payload.get("recipe_steps"):
                for item in task.executor_payload.get("recipe_steps", []):
                    print(
                        f"- planned | step={item.get('step', '?')} | "
                        f"action={item.get('action_type', 'unknown')} | "
                        f"target={item.get('target', 'none') or 'none'} | "
                        f"label={item.get('label', 'recipe step')}"
                    )
            else:
                print("- none")
            print("recipe_last_run_steps:")
            if task.executor_action_type == "run_operator_recipe" and recipe_last_run.get("steps"):
                for item in recipe_last_run.get("steps", []):
                    print(
                        f"- {item.get('status', 'unknown')} | step={item.get('step', '?')} | "
                        f"action={item.get('action_type', 'unknown')} | "
                        f"target={item.get('target', 'none') or 'none'} | "
                        f"bridge_target={item.get('bridge_target', 'none') or 'none'} | "
                        f"label={item.get('label', 'recipe step')} | "
                        f"attempts={item.get('attempt_count', 0)} | "
                        f"max_attempts={item.get('max_attempts', 0)} | "
                        f"required={'yes' if item.get('required', True) else 'no'} | "
                        f"started={item.get('started_at', 'none') or 'none'} | "
                        f"finished={item.get('finished_at', 'none') or 'none'} | "
                        f"summary={item.get('summary', 'none') or 'none'} | "
                        f"artifact={item.get('artifact_path', 'none') or 'none'} | "
                        f"clipboard={item.get('clipboard_preview', 'none') or 'none'} | "
                        f"classification={item.get('clipboard_classification', 'none') or 'none'} | "
                        f"window={item.get('window_alias', 'none') or 'none'} | "
                        f"candidate={item.get('window_candidate_id', 'none') or 'none'} | "
                        f"resolution_mode={item.get('window_resolution_mode', 'none') or 'none'} | "
                        f"coordinates={item.get('coordinates', 'none') or 'none'}"
                    )
            else:
                print("- none")
            print("recipe_run_history:")
            if task.executor_action_type == "run_operator_recipe" and task.executor_payload.get("recipe_run_history"):
                for item in task.executor_payload.get("recipe_run_history", []):
                    print(
                        f"- {item.get('status', 'unknown')} | started={item.get('started_at', 'none') or 'none'} | "
                        f"finished={item.get('finished_at', 'none') or 'none'} | "
                        f"summary={item.get('summary', 'none') or 'none'}"
                    )
            else:
                print("- none")
            print("execution_history:")
            if task.execution_records:
                for item in task.execution_records:
                    print(
                        f"- {item.status} | started={item.started_at} | "
                        f"finished={item.finished_at or 'none'} | target={item.target or 'none'} | "
                        f"attempts={item.attempt_count} | summary={item.output_summary or 'none'} | "
                        f"artifact={item.artifact_path or 'none'} | reason={item.failure_reason or item.interruption_reason or item.resource_guard_reason or 'none'} | "
                        f"inference={'yes' if item.used_model_inference else 'no'} | "
                        f"model_provider={item.model_provider or 'none'} | "
                        f"model_name={item.model_name or 'none'} | "
                        f"model_status={item.model_call_status or 'not_used'}"
                    )
            else:
                print("- none")
            print("history:")
            if history:
                for item in history:
                    print(
                        f"- {item.event_type} | {item.occurred_at} | "
                        f"actor={item.actor} | note={item.note or 'none'}"
                    )
            else:
                print("- none")
            return 0

        if args.command == "pending-approvals":
            requests = list_pending_approvals()
            print(f"count: {len(requests)}")
            if not requests:
                print("requests: none")
                return 0
            print("requests:")
            for request in requests:
                target = _approval_target(request.scope, request.task_id)
                description = _short_description(request.reason)
                print(
                    f"- {request.approval_id} | {request.status} | "
                    f"risk={request.risk_level} | task={request.task_id} | "
                    f"action={request.action_label} | target={target} | "
                    f"description={description} | workspace={request.workspace_scope} | "
                    f"policy={request.workspace_policy} | admin="
                    f"{'yes' if request.requires_admin else 'no'}"
                )
            return 0

        if args.command == "approval-status":
            if args.approval_id:
                request = get_approval_request(args.approval_id)
                history = list_approval_records(approval_id=request.approval_id)
                print(f"approval_id: {request.approval_id}")
                print(f"task_id: {request.task_id}")
                print(f"status: {request.status}")
                print(f"risk_level: {request.risk_level}")
                print(f"action_label: {request.action_label}")
                print(f"requested_at: {request.requested_at}")
                print(f"updated_at: {request.updated_at}")
                print(f"source: {request.source}")
                print(f"scope: {request.scope or 'none'}")
                print(f"workspace_scope: {request.workspace_scope}")
                print(f"workspace_policy: {request.workspace_policy}")
                print(f"workspace_reason: {request.workspace_reason or 'none'}")
                print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
                print(f"requires_admin: {'yes' if request.requires_admin else 'no'}")
                print(f"reason: {request.reason}")
                print(f"rollback_plan: {request.rollback_plan or 'none'}")
                print(f"human_note: {request.human_note or 'none'}")
                print("target_paths:")
                if request.target_paths:
                    for item in request.target_paths:
                        print(f"- {item}")
                else:
                    print("- none")
                print("decision_history:")
                if history:
                    for record in history:
                        print(
                            f"- {record.decision} | {record.decided_at} | "
                            f"note={record.note or 'none'}"
                        )
                else:
                    print("- none")
                return 0

            requests = list_approval_requests()
            print(f"count: {len(requests)}")
            if not requests:
                print("requests: none")
                return 0
            print("requests:")
            for request in requests:
                target = _approval_target(request.scope, request.task_id)
                description = _short_description(request.reason)
                print(
                    f"- {request.approval_id} | {request.status} | "
                    f"risk={request.risk_level} | task={request.task_id} | "
                    f"action={request.action_label} | target={target} | "
                    f"description={description} | workspace={request.workspace_scope} | "
                    f"policy={request.workspace_policy}"
                )
            return 0

        if args.command == "approve-approval":
            with runtime_data_lock():
                task, request = approve_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: approved")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "deny-approval":
            with runtime_data_lock():
                task, request = deny_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: denied")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "defer-approval":
            with runtime_data_lock():
                task, request = defer_approval_request(
                    approval_id=args.approval_id,
                    note=args.note,
                )
            print(f"approval_id: {request.approval_id}")
            print("decision: deferred")
            print(f"status: {request.status}")
            print(f"task_id: {task.task_id}")
            print(f"task_status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"human_note: {request.human_note or 'none'}")
            return 0

        if args.command == "request-approval":
            with runtime_data_lock():
                request = request_task_approval(
                    task_id=args.task_id,
                    action_label=args.action_label,
                    reason=args.reason,
                    risk_level=args.risk_level,
                    source=args.source,
                    scope=args.scope,
                    rollback_plan=args.rollback_plan,
                    requires_admin=args.requires_admin == "yes",
                )
            notification = build_approval_notification(request)
            print(f"approval_id: {request.approval_id}")
            print(f"task_id: {request.task_id}")
            print(f"status: {request.status}")
            print(f"risk_level: {request.risk_level}")
            print(f"workspace_scope: {request.workspace_scope}")
            print(f"workspace_policy: {request.workspace_policy}")
            print(f"workspace_reason: {request.workspace_reason or 'none'}")
            print(f"requires_admin: {'yes' if request.requires_admin else 'no'}")
            print(f"action_label: {request.action_label}")
            print(f"notification_mode: {notification.channel}")
            print(f"notification_title: {notification.title}")
            return 0

        if args.command == "approve":
            with runtime_data_lock():
                task = approve_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            return 0

        if args.command == "reject":
            with runtime_data_lock():
                task = reject_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"approval_request_id: {task.approval_request_id or 'none'}")
            return 0

        if args.command == "wait":
            with runtime_data_lock():
                task = wait_task(args.task_id, reason=args.reason)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"waiting_for: {task.waiting_for}")
            return 0

        if args.command == "resume":
            with runtime_data_lock():
                task = resume_task(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "run-once":
            with runtime_data_lock():
                task = run_task_once(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            if task.execution_records:
                last_execution = task.execution_records[-1]
                print(f"execution_status: {last_execution.status}")
                print(f"execution_summary: {last_execution.output_summary or 'none'}")
                print(f"artifact_path: {last_execution.artifact_path or 'none'}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "execute-task":
            with runtime_data_lock():
                task = execute_task(args.task_id)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"executor_action_type: {task.executor_action_type or 'none'}")
            if task.execution_records:
                last_execution = task.execution_records[-1]
                print(f"execution_status: {last_execution.status}")
                print(f"execution_summary: {last_execution.output_summary or 'none'}")
                print(f"artifact_path: {last_execution.artifact_path or 'none'}")
            else:
                print("execution_status: not_run")
                print("execution_summary: none")
                print("artifact_path: none")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "mark-human-needed":
            with runtime_data_lock():
                task = mark_task_human_needed(task_id=args.task_id, reason=args.reason)
            notification = build_human_needed_notification(task)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"waiting_for: {task.waiting_for}")
            print(f"blocked_reason: {task.blocked_reason}")
            print(f"notification_mode: {notification.channel}")
            print(f"notification_title: {notification.title}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "review-task":
            with runtime_data_lock():
                task = review_task_for_resume(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"blocked_reason: {task.blocked_reason or 'none'}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "requeue-task":
            with runtime_data_lock():
                task = requeue_task(task_id=args.task_id, note=args.note)
            print(f"task_id: {task.task_id}")
            print(f"status: {task.status}")
            print(f"approval_state: {task.approval_state}")
            print(f"workspace_policy: {task.workspace_policy}")
            print(f"next_action: {get_task_next_action(task)}")
            return 0

        if args.command == "supervisor-status":
            state = get_supervisor_state()
            notification = build_supervisor_notification(state)
            print(f"supervisor_id: {state.supervisor_id}")
            print(f"mode: {state.mode}")
            print(f"status: {state.status}")
            print(f"active_task_id: {state.active_task_id or 'none'}")
            print(f"queued_count: {state.queued_count}")
            print(f"running_count: {state.running_count}")
            print(f"waiting_count: {state.waiting_count}")
            print(f"ready_to_resume_count: {state.ready_to_resume_count}")
            print(f"pending_approval_count: {state.pending_approval_count}")
            print(f"blocked_human_needed_count: {state.blocked_human_needed_count}")
            print(f"interrupted_count: {state.interrupted_count}")
            print(f"notification_mode: {state.notification_mode}")
            print(f"notification_title: {notification.title}")
            print(f"last_event: {state.last_event or 'none'}")
            print(f"updated_at: {state.updated_at}")
            print(f"allowed_workspace_root: {get_allowed_workspace_root()}")
            print(f"ghoti_state: {state.ghoti_state}")
            print(f"ghoti_reason: {state.ghoti_reason or 'none'}")
            print(f"operator_next_step: {state.operator_next_step or 'none'}")
            print(f"resource_guard_event_count: {state.resource_guard_event_count}")

            pending_requests = list_pending_approvals()
            print("pending_approvals:")
            if pending_requests:
                for request in pending_requests:
                    target = _approval_target(request.scope, request.task_id)
                    description = _short_description(request.reason)
                    print(
                        f"- {request.approval_id} | {request.status} | "
                        f"risk={request.risk_level} | task={request.task_id} | "
                        f"action={request.action_label} | target={target} | "
                        f"description={description} | workspace={request.workspace_scope} | "
                        f"policy={request.workspace_policy} | admin="
                        f"{'yes' if request.requires_admin else 'no'}"
                    )
            else:
                print("- none")

            blocked_tasks = list_blocked_tasks()
            print("human_needed_tasks:")
            if blocked_tasks:
                for task in blocked_tasks:
                    detail = task.blocked_reason or task.waiting_for or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            interrupted_tasks = list_interrupted_tasks()
            print("interrupted_tasks:")
            if interrupted_tasks:
                for task in interrupted_tasks:
                    detail = task.blocked_reason or task.last_note or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            waiting_tasks = list_waiting_tasks()
            print("waiting_tasks:")
            if waiting_tasks:
                for task in waiting_tasks:
                    detail = task.waiting_for or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            ready_to_resume_tasks = list_ready_to_resume_tasks()
            print("ready_to_resume_tasks:")
            if ready_to_resume_tasks:
                for task in ready_to_resume_tasks:
                    detail = task.last_note or task.title
                    print(
                        f"- {task.task_id} | {task.status} | "
                        f"workspace={task.workspace_scope} | policy={task.workspace_policy} | "
                        f"approval={task.approval_state} | next={_workspace_reason(get_task_next_action(task))} | "
                        f"detail={_workspace_reason(detail)}"
                    )
            else:
                print("- none")

            print("resource_guard_events:")
            if state.recent_resource_guard_events:
                for item in state.recent_resource_guard_events:
                    print(f"- {item}")
            else:
                print("- none")
            return 0

        if args.command == "list-providers":
            for profile in list_provider_profiles():
                print(
                    f"{profile.provider_id} | {profile.display_name} | "
                    f"{profile.privacy_mode} | {profile.speed_bias}"
                )
            return 0

        if args.command == "list-integrations":
            for integration in list_supported_integrations():
                print(f"{integration.integration_id} | {integration.mode} | {integration.summary}")
            return 0

        if args.command == "github-status":
            summary = get_repo_status_summary()
            remote = get_remote_info()
            commits = get_recent_commits()
            print(f"repo_root: {summary.repo_root}")
            print(f"branch: {get_github_branch()}")
            print(f"clean: {'yes' if summary.is_clean else 'no'}")
            print(f"staged_changes: {summary.staged_changes}")
            print(f"unstaged_changes: {summary.unstaged_changes}")
            print(f"untracked_changes: {summary.untracked_changes}")
            print(f"origin_url: {remote.origin_url or 'none'}")
            print(f"gh_available: {'yes' if remote.gh_available else 'no'}")
            if remote.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if remote.gh_authenticated else 'no'}")
            print("recent_commits:")
            for commit in commits:
                print(f"- {commit.commit_hash} {commit.subject}")
            return 0

        if args.command == "github-gh-diagnose":
            diagnostics = diagnose_gh_environment()
            print(f"gh_available: {'yes' if diagnostics.gh_available else 'no'}")
            print(f"gh_path: {diagnostics.gh_path or 'none'}")
            print(f"source: {diagnostics.source}")
            print(f"path_visible: {'yes' if diagnostics.path_visible else 'no'}")
            print(f"version: {diagnostics.version or 'unknown'}")
            print(f"auth_known: {'yes' if diagnostics.auth_known else 'no'}")
            if diagnostics.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if diagnostics.gh_authenticated else 'no'}")
            if diagnostics.where_results:
                print("where_results:")
                for item in diagnostics.where_results:
                    print(f"- {item}")
            if diagnostics.notes:
                print("notes:")
                for item in diagnostics.notes:
                    print(f"- {item}")
            return 0

        if args.command == "github-remote-capability":
            capability = get_remote_capability()
            print(f"repo_root: {capability.repo_root}")
            print(f"branch: {capability.branch}")
            print(f"origin_url: {capability.origin_url or 'none'}")
            print(f"gh_available: {'yes' if capability.gh_available else 'no'}")
            if capability.gh_authenticated is None:
                print("gh_authenticated: unknown")
            else:
                print(f"gh_authenticated: {'yes' if capability.gh_authenticated else 'no'}")
            print(
                f"remote_write_possible: "
                f"{'yes' if capability.remote_actions_possible else 'no'}"
            )
            print(f"blocking_issue: {capability.blocking_issue or 'none'}")
            return 0

        if args.command == "council-plan":
            plan = build_council_plan(
                goal_type=args.goal_type,
                privacy_preference=args.privacy,
                speed_preference=args.speed,
                require_reviewer=args.require_reviewer,
            )
            print(f"goal_type: {plan.goal_type}")
            print(f"lead_provider: {plan.lead_provider}")
            print(f"reviewer_provider: {plan.reviewer_provider or 'none'}")
            print(f"local_fallback_provider: {plan.local_fallback_provider}")
            print(f"reasoning_summary: {plan.reasoning_summary}")
            if plan.notes:
                print("notes:")
                for note in plan.notes:
                    print(f"- {note}")
            return 0

        if args.command == "list-workflows":
            for workflow in list_workflows():
                print(f"{workflow.workflow_id} | {workflow.title}")
            return 0

        if args.command == "list-personal-workflows":
            for workflow in list_personal_workflows():
                print(f"{workflow.workflow_id} | {workflow.title}")
            return 0

        if args.command == "show-workflow":
            workflow = get_workflow(args.workflow_id)
            print(f"workflow_id: {workflow.workflow_id}")
            print(f"title: {workflow.title}")
            print(f"purpose: {workflow.purpose}")
            print("inputs:")
            for item in workflow.inputs:
                print(f"- {item}")
            print("outputs:")
            for item in workflow.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in workflow.approval_points:
                print(f"- {item}")
            print(f"notes: {workflow.notes}")
            return 0

        if args.command == "show-personal-workflow":
            workflow = get_personal_workflow(args.workflow_id)
            print(f"workflow_id: {workflow.workflow_id}")
            print(f"title: {workflow.title}")
            print(f"purpose: {workflow.purpose}")
            print("inputs:")
            for item in workflow.inputs:
                print(f"- {item}")
            print("outputs:")
            for item in workflow.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in workflow.approval_points:
                print(f"- {item}")
            print(f"notes: {workflow.notes}")
            return 0

        if args.command == "mail-plan":
            plan = build_inbox_triage_plan(
                account_label=args.account_label,
                goal=args.goal,
            )
            print(f"account_label: {plan.account_label}")
            print(f"objective: {plan.objective}")
            print(f"mode: {plan.mode}")
            print("steps:")
            for item in plan.steps:
                print(f"- {item}")
            print("outputs:")
            for item in plan.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in plan.approval_points:
                print(f"- {item}")
            return 0

        if args.command == "notion-plan":
            plan = build_notion_update_plan(
                page_label=args.page_label,
                objective=args.objective,
            )
            print(f"page_label: {plan.page_label}")
            print(f"objective: {plan.objective}")
            print(f"mode: {plan.mode}")
            print("steps:")
            for item in plan.steps:
                print(f"- {item}")
            print("outputs:")
            for item in plan.outputs:
                print(f"- {item}")
            print("approval_points:")
            for item in plan.approval_points:
                print(f"- {item}")
            return 0

        if args.command == "github-issue-draft":
            output_path = scaffold_issue_draft(
                title=args.title,
                objective=args.objective,
                context=args.context,
                body=args.body,
                labels=args.labels,
            )
            print(f"github_draft_path: {output_path}")
            return 0

        if args.command == "github-pr-draft":
            output_path = scaffold_pr_draft(
                title=args.title,
                objective=args.objective,
                source_branch=args.source_branch,
                target_branch=args.target_branch,
                summary=args.summary,
                risk_notes=args.risk_notes,
            )
            print(f"github_draft_path: {output_path}")
            return 0

        if args.command == "github-create-branch":
            result = create_branch_with_approval(
                branch_name=args.branch_name,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-create-issue":
            result = create_issue_with_approval(
                title=args.title,
                body=args.body,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-create-pr":
            result = create_pr_with_approval(
                title=args.title,
                body=args.body,
                base_branch=args.base_branch,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-smoke-issue":
            result = create_smoke_issue_with_approval(
                title=args.title,
                body=args.body,
                labels=args.labels,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "github-smoke-pr":
            result = create_smoke_pr_with_approval(
                title=args.title,
                body=args.body,
                base_branch=args.base_branch,
                approved=args.approve == "yes",
            )
            print(result)
            return 0

        if args.command == "scaffold-report":
            _ = get_workflow(args.workflow_id)
            output_path = build_report_scaffold(
                title=args.title,
                workflow_id=args.workflow_id,
                summary=args.summary,
            )
            print(f"report_path: {output_path}")
            return 0

        if args.command == "scaffold-inbox-triage":
            output_path = scaffold_inbox_triage_pack(
                account_label=args.account_label,
                goal=args.goal,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-linkedin-pack":
            output_path = scaffold_linkedin_pack(
                profile_label=args.profile_label,
                target_role=args.target_role,
                focus=args.focus,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-cv-pack":
            output_path = scaffold_cv_pack(
                target_role=args.target_role,
                summary=args.summary,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-outreach-draft":
            output_path = scaffold_outreach_draft(
                recipient_label=args.recipient_label,
                purpose=args.purpose,
                notes=args.notes,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-internship-pack":
            output_path = scaffold_internship_application_pack(
                target_role=args.target_role,
                company=args.company,
                job_source=args.job_source,
                fit_summary=args.fit_summary,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-showcase-case-study":
            output_path = scaffold_showcase_case_study(
                project_name=args.project_name,
                objective=args.objective,
                highlights=args.highlights,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "scaffold-portfolio-project-page":
            output_path = scaffold_portfolio_project_page(
                project_name=args.project_name,
                summary=args.summary,
                stack=args.stack,
            )
            print(f"personal_ops_path: {output_path}")
            return 0

        if args.command == "truth-plan":
            result = build_truth_council_result(
                question=args.question,
                proposer_summary=args.proposer,
                challenger_summary=args.challenger,
                evidence_summary=args.evidence,
                evidence_quality=args.evidence_quality,
                disagreement_level=args.disagreement,
                source_count=args.source_count,
            )
            print(f"question: {result.question}")
            print(f"lead_answer: {result.lead_answer}")
            print(f"dissent: {result.dissent}")
            print(f"consensus_level: {result.consensus_level}")
            print(f"confidence_score: {result.confidence_score}")
            print(f"evidence_quality_notes: {result.evidence_quality_notes}")
            if result.notes:
                print("notes:")
                for note in result.notes:
                    print(f"- {note}")
            return 0

        if args.command == "publish-check":
            report = scan_publishability()
            print(f"scanned_files: {report.scanned_files}")
            print(f"finding_count: {report.finding_count}")
            counts = report.category_counts()
            if counts:
                print("categories:")
                for category in sorted(counts):
                    print(f"- {category}: {counts[category]}")
            if report.findings:
                print("findings:")
                for finding in report.findings:
                    print(f"- [{finding.category}] {finding.path} :: {finding.detail}")
            else:
                print("findings: none")
            return 0

        if args.command == "publish-check-core":
            report = scan_publishability(core_only=True)
            print(f"scanned_files: {report.scanned_files}")
            print(f"finding_count: {report.finding_count}")
            counts = report.category_counts()
            if counts:
                print("categories:")
                for category in sorted(counts):
                    print(f"- {category}: {counts[category]}")
            if report.findings:
                print("findings:")
                for finding in report.findings:
                    print(f"- [{finding.category}] {finding.path} :: {finding.detail}")
            else:
                print("findings: none")
            return 0

        if args.command == "snapshot":
            output_path = build_handoff_snapshot()
            print(f"handoff_snapshot: {output_path}")
            return 0

        parser.print_help()
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())






