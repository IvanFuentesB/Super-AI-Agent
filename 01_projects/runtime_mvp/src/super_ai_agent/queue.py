from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from uuid import uuid4

from .models import (
    ApprovalRecord,
    ApprovalRequest,
    EXECUTOR_ACTION_TYPES as MODEL_EXECUTOR_ACTION_TYPES,
    RuntimeStatusSummary,
    SupervisorState,
    Task,
    TaskExecutionRecord,
    TaskEvent,
    TASK_RISK_LEVELS,
)
from .storage import (
    get_allowed_workspace_root,
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
ALLOWED_EXECUTOR_ACTIONS = set(MODEL_EXECUTOR_ACTION_TYPES)
READ_ONLY_EXECUTOR_ACTIONS = {"read_file", "list_directory", "git_status", "git_diff"}
WRITE_EXECUTOR_ACTIONS = {"write_file", "append_file", "create_artifact"}
CHECKER_EXECUTOR_ACTIONS = {"run_checker"}
RECIPE_EXECUTOR_ACTIONS = {"run_operator_recipe"}
DESKTOP_OBSERVATION_ACTIONS = {
    "list_windows",
    "get_active_window",
    "get_clipboard_text",
    "wait_seconds",
    "wait_for_window",
}
DESKTOP_VISIBLE_ACTIONS = {
    "focus_window",
    "open_allowed_app",
    "capture_desktop_screenshot",
    "set_clipboard_text",
    "copy_selection",
    "paste_clipboard",
    "send_hotkey",
    "move_mouse",
    "left_click",
    "double_click",
    "right_click",
    "scroll_mouse",
}
DESKTOP_EXECUTOR_ACTIONS = DESKTOP_OBSERVATION_ACTIONS | DESKTOP_VISIBLE_ACTIONS
ALLOWED_CHECKER_TARGETS = {
    "runtime": "check_runtime_mvp.ps1",
    "dashboard": "check_dashboard_mvp.ps1",
}
ALLOWED_DESKTOP_FOCUS_TARGETS = {"cursor", "vscode", "codex", "chatgpt", "terminal", "dashboard_browser"}
ALLOWED_DESKTOP_APP_TARGETS = {"cursor", "vscode", "terminal", "dashboard_browser"}
ALLOWED_DESKTOP_HOTKEYS = {"ctrl+c", "ctrl+v", "ctrl+l", "enter", "escape"}
HANDOFF_SOURCE_WINDOW_ALIASES = {"codex"}
HANDOFF_TARGET_WINDOW_ALIASES = {"chatgpt"}
QUEUEABLE_TASK_STATUSES = {"queued", "running", "waiting", "blocked_human_needed", "ready_to_resume"}
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)\b[A-Z]:\\[^\s\"'<>|?*]+")
DEFAULT_OPERATOR_RECIPE_WAIT_SECONDS = 2
DEFAULT_DESKTOP_MAX_ATTEMPTS = 2
RESOURCE_GUARD_WAITING_FOR = "resource_guard_review"
VALID_HANDOFF_PAYLOAD_CLASSIFICATIONS = {"valid_handoff_text"}


class DesktopActionInterrupted(RuntimeError):
    """Raised when a desktop bridge action is interrupted by the local failsafe."""


class DesktopActionBlocked(RuntimeError):
    """Raised when the desktop bridge blocks an action for safety or clarity."""

    def __init__(self, message: str, *, values: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.values = values or {}


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


def _append_task_event(task: Task, event_type: str, note: str = "", actor: str = "system") -> None:
    task.history.append(
        TaskEvent(
            event_type=event_type,
            occurred_at=_now(),
            note=note,
            actor=actor,
        )
    )


def _ensure_task_history(task: Task) -> bool:
    if task.history:
        return False

    task.history.append(
        TaskEvent(
            event_type="created",
            occurred_at=task.created_at or _now(),
            note=task.title,
            actor="system",
        )
    )
    return True


def _task_next_action(task: Task) -> str:
    if task.status == "pending_approval":
        return "Resolve the approval request."
    if task.status == "blocked_human_needed":
        if (task.waiting_for or "") == RESOURCE_GUARD_WAITING_FOR or _task_has_resource_guard_reason(task):
            return "Reduce duplicate windows or processes, then review the blocked task before re-queueing it."
        if task.workspace_policy == "blocked_by_workspace_policy":
            return "Keep blocked until the target is moved inside the workspace or policy changes."
        return "Mark the human-needed step as reviewed."
    if task.status == "interrupted":
        return "Inspect the interruption reason, then mark the task reviewed before re-queueing it."
    if task.status == "waiting":
        return "Resume the task when the reply or external event arrives."
    if task.status == "ready_to_resume":
        return "Re-queue the task when you want it to continue."
    if task.status == "queued":
        if task.executor_action_type:
            return "Run the allowlisted executor action when ready."
        return "Run the task manually when ready."
    if task.status == "completed":
        return "Review the completed output."
    if task.status == "failed":
        return "Inspect the failure reason before deciding whether to retry manually."
    return "Review the current task state."


def _requires_approval(risk_level: str) -> bool:
    return risk_level != "safe"


def _requires_admin(risk_level: str) -> bool:
    return risk_level == "admin"


def _normalize_candidate_path(path_value: str) -> str:
    try:
        return str(Path(path_value).expanduser().resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        return path_value


def _extract_candidate_paths(*texts: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    for text in texts:
        for match in WINDOWS_ABSOLUTE_PATH_PATTERN.findall(text or ""):
            candidate = match.rstrip(".,;:!?)]}\"'")
            if candidate and candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)

    return candidates


def _is_inside_allowed_root(path_value: str) -> bool:
    try:
        return Path(path_value).resolve(strict=False).is_relative_to(get_allowed_workspace_root())
    except (OSError, ValueError):
        return False


def _classify_workspace_paths(
    *paths: str,
) -> tuple[list[str], str, str, str]:
    allowed_root = get_allowed_workspace_root()
    candidate_paths = [
        _normalize_candidate_path(item)
        for item in paths
        if str(item or "").strip()
    ]

    if not candidate_paths:
        return (
            [],
            "no_path_detected",
            "allowed",
            f"No explicit path target provided. Allowed workspace root: {allowed_root}",
        )

    outside = [item for item in candidate_paths if not _is_inside_allowed_root(item)]
    if outside:
        return (
            candidate_paths,
            "out_of_scope",
            "blocked_by_workspace_policy",
            (
                "Blocked by workspace policy. Target path is outside the allowed workspace root: "
                f"{allowed_root}"
            ),
        )

    return (
        candidate_paths,
        "in_scope",
        "allowed",
        f"Target path is inside the allowed workspace root: {allowed_root}",
    )


def _classify_workspace_targets(
    *texts: str,
) -> tuple[list[str], str, str, str]:
    candidate_paths = [_normalize_candidate_path(item) for item in _extract_candidate_paths(*texts)]

    if not candidate_paths:
        allowed_root = get_allowed_workspace_root()
        return (
            [],
            "no_path_detected",
            "allowed",
            f"No explicit absolute path target detected. Allowed workspace root: {allowed_root}",
        )

    return _classify_workspace_paths(*candidate_paths)


def _apply_workspace_policy(
    task: Task,
    *texts: str,
) -> Task:
    target_paths, workspace_scope, workspace_policy, workspace_reason = _classify_workspace_targets(*texts)
    task.target_paths = target_paths
    task.workspace_scope = workspace_scope
    task.workspace_policy = workspace_policy
    task.workspace_reason = workspace_reason
    if workspace_scope == "out_of_scope" and task.risk_level == "safe":
        task.risk_level = "high_risk"
    return task


def _apply_workspace_policy_paths(task: Task, *paths: str) -> Task:
    target_paths, workspace_scope, workspace_policy, workspace_reason = _classify_workspace_paths(*paths)
    task.target_paths = target_paths
    task.workspace_scope = workspace_scope
    task.workspace_policy = workspace_policy
    task.workspace_reason = workspace_reason
    if workspace_scope == "out_of_scope" and task.risk_level == "safe":
        task.risk_level = "high_risk"
    return task


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
        target_paths=list(task.target_paths),
        workspace_scope=task.workspace_scope,
        workspace_policy=task.workspace_policy,
        workspace_reason=task.workspace_reason,
    )


def _resolve_executor_path(target: str) -> Path:
    raw_target = (target or "").strip()
    if not raw_target:
        raise ValueError("A target path is required for this executor action.")

    candidate = Path(raw_target).expanduser()
    if not candidate.is_absolute():
        candidate = get_allowed_workspace_root() / candidate
    return candidate.resolve(strict=False)


def _split_alias_payload(target: str) -> tuple[str, str]:
    normalized = (target or "").strip().lower()
    if "|" not in normalized:
        return "", normalized
    alias, payload = normalized.split("|", 1)
    return alias.strip(), payload.strip()


def _require_positive_int(
    raw_value: str,
    *,
    label: str,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(str(raw_value).strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be an integer.") from exc

    if value < minimum or value > maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return value


def _normalize_optional_window_target(
    raw_target: str,
    *,
    action_type: str,
) -> str:
    normalized = (raw_target or "").strip().lower()
    if not normalized:
        return ""
    if normalized not in ALLOWED_DESKTOP_FOCUS_TARGETS:
        raise ValueError(
            f"{action_type} target must be blank or one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
        )
    return normalized


def _normalize_hotkey_target(raw_target: str) -> str:
    alias, hotkey = _split_alias_payload(raw_target)
    if not hotkey:
        raise ValueError(
            "send_hotkey target must be one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_HOTKEYS))
        )
    if alias and alias not in ALLOWED_DESKTOP_FOCUS_TARGETS:
        raise ValueError(
            "send_hotkey alias must be blank or one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
        )
    if hotkey not in ALLOWED_DESKTOP_HOTKEYS:
        raise ValueError(
            "send_hotkey target must be one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_HOTKEYS))
        )
    return f"{alias}|{hotkey}" if alias else hotkey


def _normalize_wait_for_window_target(raw_target: str) -> str:
    alias, timeout_text = _split_alias_payload(raw_target)
    if not alias:
        alias = (raw_target or "").strip().lower()
        timeout_text = ""
    if alias not in ALLOWED_DESKTOP_FOCUS_TARGETS:
        raise ValueError(
            "wait_for_window target must be one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
            + " with an optional |timeoutSeconds suffix."
        )
    if timeout_text:
        timeout_value = _require_positive_int(
            timeout_text,
            label="wait_for_window timeout",
            minimum=1,
            maximum=120,
        )
        return f"{alias}|{timeout_value}"
    return alias


def _require_allowed_window_alias(raw_value: str, *, label: str) -> str:
    normalized = (raw_value or "").strip().lower()
    if normalized not in ALLOWED_DESKTOP_FOCUS_TARGETS:
        raise ValueError(
            f"{label} must be one of: "
            + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
        )
    return normalized


def _require_handoff_window_alias(raw_value: str, *, label: str, role: str) -> str:
    normalized = (raw_value or "").strip().lower()
    if role == "source":
        allowed_aliases = HANDOFF_SOURCE_WINDOW_ALIASES
    elif role == "target":
        allowed_aliases = HANDOFF_TARGET_WINDOW_ALIASES
    else:
        raise ValueError(f"Unsupported handoff window role: {role}")

    if normalized == "terminal":
        raise ValueError(
            f"{label} must not use terminal or shell targets. Codex to ChatGPT handoff never falls back to terminal or PowerShell."
        )
    if normalized not in allowed_aliases:
        raise ValueError(
            f"{label} must be one of: " + ", ".join(sorted(allowed_aliases))
        )
    return normalized


def _parse_operator_recipe_options(raw_content: str) -> dict:
    text = (raw_content or "").strip()
    if not text:
        return {}

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Operator recipe options must be valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Operator recipe options must decode to a JSON object.")

    return parsed


def _recipe_option_text(options: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = options.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _recipe_option_int(
    options: dict,
    *keys: str,
    default: int,
    minimum: int,
    maximum: int,
    label: str,
) -> int:
    for key in keys:
        if key not in options:
            continue
        return _require_positive_int(
            str(options[key]),
            label=label,
            minimum=minimum,
            maximum=maximum,
        )
    return default


def _recipe_option_bool(
    options: dict,
    *keys: str,
    default: bool,
    label: str,
) -> bool:
    truthy = {"1", "true", "yes", "y", "on"}
    falsy = {"0", "false", "no", "n", "off"}

    for key in keys:
        if key not in options:
            continue
        value = options[key]
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
        raise ValueError(f"{label} must be a boolean-like value.")
    return default


def _build_recipe_step(
    *,
    action_type: str,
    label: str,
    target: str = "",
    text_content: str = "",
    required: bool = True,
    max_attempts: int = DEFAULT_DESKTOP_MAX_ATTEMPTS,
) -> dict:
    return {
        "action_type": action_type,
        "label": label,
        "target": target,
        "text_content": text_content,
        "required": required,
        "max_attempts": max_attempts,
    }


def _recipe_observe_desktop_state(options: dict) -> dict:
    return {
        "name": "observe_desktop_state",
        "label": "Observe desktop state",
        "description": "Safe multi-step desktop observation only: list allowlisted windows, then record the active window without changing focus.",
        "steps": [
            _build_recipe_step(
                action_type="list_windows",
                label="List allowlisted windows",
            ),
            _build_recipe_step(
                action_type="get_active_window",
                label="Record the active window",
            ),
        ],
    }


def _recipe_focus_or_reuse_terminal(options: dict) -> dict:
    return {
        "name": "focus_or_reuse_terminal",
        "label": "Focus or reuse terminal",
        "description": "Prefer an existing allowlisted terminal window. Only open a terminal if no safe reusable terminal window is available.",
        "steps": [
            _build_recipe_step(
                action_type="open_allowed_app",
                target="terminal",
                label="Focus an existing terminal or open one if missing",
            ),
        ],
    }


def _recipe_copy_from_focused_window(options: dict) -> dict:
    source_window = _normalize_optional_window_target(
        _recipe_option_text(options, "sourceWindow", "source_window"),
        action_type="copy_from_focused_window source",
    )
    source_label = source_window or "focused allowlisted window"
    return {
        "name": "copy_from_focused_window",
        "label": "Copy from focused window",
        "description": "Copy the current selection from the focused allowlisted window, then read back the clipboard preview for a visible result.",
        "steps": [
            _build_recipe_step(
                action_type="copy_selection",
                target=source_window,
                label=f"Copy selection from {source_label}",
            ),
            _build_recipe_step(
                action_type="get_clipboard_text",
                label="Read clipboard preview",
            ),
        ],
    }


def _recipe_paste_into_target_window(options: dict) -> dict:
    target_window = _require_allowed_window_alias(
        _recipe_option_text(
            options,
            "targetWindow",
            "target_window",
            default="dashboard_browser",
        ),
        label="paste_into_target_window targetWindow",
    )
    return {
        "name": "paste_into_target_window",
        "label": "Paste into target window",
        "description": "Focus one allowed target window explicitly, then paste the current clipboard into it.",
        "steps": [
            _build_recipe_step(
                action_type="focus_window",
                target=target_window,
                label=f"Focus {target_window}",
            ),
            _build_recipe_step(
                action_type="paste_clipboard",
                target=target_window,
                label=f"Paste clipboard into {target_window}",
            ),
        ],
    }


def _recipe_wait_and_resume_operator_step(options: dict) -> dict:
    wait_seconds = _recipe_option_int(
        options,
        "waitSeconds",
        "wait_seconds",
        default=DEFAULT_OPERATOR_RECIPE_WAIT_SECONDS,
        minimum=1,
        maximum=60,
        label="wait_and_resume_operator_step waitSeconds",
    )
    return {
        "name": "wait_and_resume_operator_step",
        "label": "Wait and resume operator step",
        "description": "Pause visibly for a short operator wait, then record which allowlisted window is active before the next manual step.",
        "steps": [
            _build_recipe_step(
                action_type="wait_seconds",
                target=str(wait_seconds),
                label=f"Wait {wait_seconds} second(s)",
            ),
            _build_recipe_step(
                action_type="get_active_window",
                label="Record the active window after waiting",
            ),
        ],
    }


def _recipe_codex_to_dashboard_progress_handoff(options: dict) -> dict:
    source_window = _require_allowed_window_alias(
        _recipe_option_text(
            options,
            "sourceWindow",
            "source_window",
            default="terminal",
        ),
        label="codex_to_dashboard_progress_handoff sourceWindow",
    )
    target_window = _require_allowed_window_alias(
        _recipe_option_text(
            options,
            "targetWindow",
            "target_window",
            default="dashboard_browser",
        ),
        label="codex_to_dashboard_progress_handoff targetWindow",
    )
    wait_seconds = _recipe_option_int(
        options,
        "waitSeconds",
        "wait_seconds",
        default=1,
        minimum=1,
        maximum=10,
        label="codex_to_dashboard_progress_handoff waitSeconds",
    )
    return {
        "name": "codex_to_dashboard_progress_handoff",
        "label": "Codex to dashboard progress handoff",
        "description": "Narrow prototype handoff: reuse the source window, copy the current selection, wait briefly, focus the dashboard browser, and paste the clipboard there. This is not yet a true ChatGPT-specific workflow.",
        "steps": [
            _build_recipe_step(
                action_type="open_allowed_app",
                target=source_window,
                label=f"Focus or reuse {source_window}",
            ),
            _build_recipe_step(
                action_type="copy_selection",
                target=source_window,
                label=f"Copy selection from {source_window}",
            ),
            _build_recipe_step(
                action_type="wait_seconds",
                target=str(wait_seconds),
                label=f"Wait {wait_seconds} second(s)",
            ),
            _build_recipe_step(
                action_type="focus_window",
                target=target_window,
                label=f"Focus {target_window}",
            ),
            _build_recipe_step(
                action_type="paste_clipboard",
                target=target_window,
                label=f"Paste clipboard into {target_window}",
            ),
        ],
    }


def _recipe_codex_to_chatgpt_handoff_mvp(options: dict) -> dict:
    source_window = _require_handoff_window_alias(
        _recipe_option_text(
            options,
            "sourceWindow",
            "source_window",
            default="codex",
        ),
        label="codex_to_chatgpt_handoff_mvp sourceWindow",
        role="source",
    )
    target_window = _require_handoff_window_alias(
        _recipe_option_text(
            options,
            "targetWindow",
            "target_window",
            default="chatgpt",
        ),
        label="codex_to_chatgpt_handoff_mvp targetWindow",
        role="target",
    )
    wait_seconds = _recipe_option_int(
        options,
        "waitSeconds",
        "wait_seconds",
        default=1,
        minimum=0,
        maximum=10,
        label="codex_to_chatgpt_handoff_mvp waitSeconds",
    )
    use_prepared_clipboard = _recipe_option_bool(
        options,
        "usePreparedClipboard",
        "use_prepared_clipboard",
        default=False,
        label="codex_to_chatgpt_handoff_mvp usePreparedClipboard",
    )
    allow_send = _recipe_option_bool(
        options,
        "allowSend",
        "allow_send",
        default=False,
        label="codex_to_chatgpt_handoff_mvp allowSend",
    )

    steps: list[dict] = []
    if not use_prepared_clipboard:
        steps.extend(
            [
                _build_recipe_step(
                    action_type="focus_window",
                    target=source_window,
                    label=f"Focus {source_window}",
                ),
                _build_recipe_step(
                    action_type="copy_selection",
                    target=source_window,
                    label=f"Copy selection from {source_window}",
                ),
            ]
        )

    steps.append(
        _build_recipe_step(
            action_type="get_clipboard_text",
            label=(
                "Read prepared clipboard payload"
                if use_prepared_clipboard
                else "Classify copied clipboard payload"
            ),
        )
    )

    if wait_seconds > 0:
        steps.append(
            _build_recipe_step(
                action_type="wait_seconds",
                target=str(wait_seconds),
                label=f"Wait {wait_seconds} second(s)",
            )
        )

    steps.extend(
        [
            _build_recipe_step(
                action_type="focus_window",
                target=target_window,
                label=f"Focus {target_window}",
            ),
            _build_recipe_step(
                action_type="paste_clipboard",
                target=target_window,
                label=f"Paste clipboard into {target_window}",
            ),
        ]
    )

    if allow_send:
        steps.append(
            _build_recipe_step(
                action_type="send_hotkey",
                target=f"{target_window}|enter",
                label=f"Explicitly send pasted handoff in {target_window}",
            )
        )

    return {
        "name": "codex_to_chatgpt_handoff_mvp",
        "label": "Codex to ChatGPT handoff MVP",
        "description": "First narrow supervised handoff workflow: focus Codex, copy or reuse a prepared clipboard payload, classify it, focus ChatGPT, and paste only by default. Enter is blocked unless the recipe explicitly allows it.",
        "metadata": {
            "recipe_source_window": source_window,
            "recipe_target_window": target_window,
            "recipe_clipboard_mode": "prepared_clipboard" if use_prepared_clipboard else "copy_selection",
            "handoff_send_behavior": "explicit_enter_after_paste" if allow_send else "paste_only",
            "handoff_send_allowed": "explicit_after_paste" if allow_send else "blocked_by_default",
            "handoff_paste_allowed": "pending_classification",
            "handoff_payload_classification": "pending",
            "handoff_payload_preview": "none",
            "handoff_payload_reason": "Clipboard has not been classified yet.",
            "handoff_fallback_denied": "terminal_shell_fallback_blocked",
            "handoff_target_resolution_status": "pending_window_match",
            "handoff_manual_target_resolution": "not_needed",
            "handoff_source_match": (
                "clipboard_prepared_manually" if use_prepared_clipboard else "pending_source_match"
            ),
            "handoff_target_match": "pending_target_match",
            "handoff_stop_reason": "none",
            "handoff_blocked_payload_repeats": "0",
            "handoff_payload_fingerprint": "none",
        },
        "steps": steps,
    }


OPERATOR_RECIPE_BUILDERS = {
    "observe_desktop_state": _recipe_observe_desktop_state,
    "focus_or_reuse_terminal": _recipe_focus_or_reuse_terminal,
    "copy_from_focused_window": _recipe_copy_from_focused_window,
    "paste_into_target_window": _recipe_paste_into_target_window,
    "wait_and_resume_operator_step": _recipe_wait_and_resume_operator_step,
    "codex_to_dashboard_progress_handoff": _recipe_codex_to_dashboard_progress_handoff,
    "codex_to_chatgpt_handoff_mvp": _recipe_codex_to_chatgpt_handoff_mvp,
}


def _build_operator_recipe_definition(recipe_name: str, options: dict | None = None) -> dict:
    normalized_name = (recipe_name or "").strip().lower()
    builder = OPERATOR_RECIPE_BUILDERS.get(normalized_name)
    if builder is None:
        raise ValueError(
            "Unsupported operator recipe. Choose one of: "
            + ", ".join(sorted(OPERATOR_RECIPE_BUILDERS))
        )

    recipe = builder(options or {})
    steps = list(recipe.get("steps", []))
    if not steps:
        raise ValueError(f"Operator recipe has no steps: {normalized_name}")

    normalized_steps = []
    for index, step in enumerate(steps, 1):
        action_type = str(step.get("action_type", "")).strip().lower()
        if action_type not in DESKTOP_EXECUTOR_ACTIONS:
            raise ValueError(
                f"Operator recipe steps must use allowlisted desktop actions only: {action_type}"
            )
        normalized_steps.append(
            {
                "step": index,
                "label": str(step.get("label", f"Step {index}")).strip() or f"Step {index}",
                "action_type": action_type,
                "target": str(step.get("target", "")).strip(),
                "text_content": str(step.get("text_content", "")),
                "required": bool(step.get("required", True)),
                "max_attempts": max(
                    1,
                    min(
                        DEFAULT_DESKTOP_MAX_ATTEMPTS,
                        int(step.get("max_attempts", DEFAULT_DESKTOP_MAX_ATTEMPTS) or DEFAULT_DESKTOP_MAX_ATTEMPTS),
                    ),
                ),
            }
        )

    risk_level = (
        "safe"
        if all(item["action_type"] in DESKTOP_OBSERVATION_ACTIONS for item in normalized_steps)
        else "ask"
    )
    return {
        "name": normalized_name,
        "label": str(recipe.get("label", normalized_name.replace("_", " "))).strip(),
        "description": str(recipe.get("description", "Operator recipe")).strip(),
        "steps": normalized_steps,
        "risk_level": risk_level,
        "metadata": dict(recipe.get("metadata", {})),
    }


def _require_target_text(raw_target: str, action_type: str) -> str:
    normalized = (raw_target or "").strip()
    if not normalized:
        raise ValueError(f"{action_type} requires an explicit target.")
    return normalized


def _desktop_bridge_script_path() -> Path:
    return (
        get_allowed_workspace_root()
        / "01_projects"
        / "desktop_playground"
        / "desktop_bridge_actions.ps1"
    ).resolve(strict=False)


def _shorten_output(text: str, limit: int = 260) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= limit:
        return normalized or "none"
    return f"{normalized[: limit - 3].rstrip()}..."


def _parse_key_value_output(text: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    values: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    current_section = ""

    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.endswith(":") and " | " not in line:
            current_section = line[:-1]
            sections.setdefault(current_section, [])
            continue

        if current_section and line.startswith("- "):
            sections[current_section].append(line[2:])
            continue

        current_section = ""
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()

    return values, sections


def _set_desktop_execution_metadata(
    task: Task,
    *,
    attempt_count: int,
    max_attempts: int,
    failure_reason: str = "",
    interruption_reason: str = "",
    resource_guard_reason: str = "",
) -> None:
    task.executor_payload["last_attempt_count"] = attempt_count
    task.executor_payload["last_retry_limit"] = max_attempts
    task.executor_payload["last_failure_reason"] = failure_reason
    task.executor_payload["last_interruption_reason"] = interruption_reason
    task.executor_payload["last_resource_guard_reason"] = resource_guard_reason


def _task_has_resource_guard_reason(task: Task) -> bool:
    blocked = (task.blocked_reason or "").lower()
    waiting_for = (task.waiting_for or "").lower()
    if "resource guard" in blocked or waiting_for == RESOURCE_GUARD_WAITING_FOR:
        return True
    return any(item.event_type == "resource_guard_triggered" for item in task.history)


def _recent_resource_guard_events(tasks: list[Task], limit: int = 5) -> list[str]:
    recent_items: list[tuple[str, str]] = []
    for task in tasks:
        for item in task.history:
            if item.event_type != "resource_guard_triggered":
                continue
            note = item.note or task.blocked_reason or f"Resource guard stopped {task.task_id}."
            recent_items.append((item.occurred_at, _shorten_output(f"{task.task_id}: {note}", limit=240)))

    recent_items.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in recent_items[:limit]]


def _build_executor_title(action_type: str, target: str) -> str:
    title_map = {
        "read_file": "Read repo-local file",
        "write_file": "Write repo-local file",
        "append_file": "Append repo-local file",
        "create_artifact": "Create repo-local artifact",
        "list_directory": "List repo-local directory",
        "git_status": "Show git status",
        "git_diff": "Show git diff summary",
        "run_checker": "Run repo checker",
        "list_windows": "List allowlisted desktop windows",
        "get_active_window": "Check active desktop window",
        "focus_window": "Focus allowlisted desktop window",
        "open_allowed_app": "Open allowlisted local app",
        "capture_desktop_screenshot": "Capture local desktop screenshot",
        "get_clipboard_text": "Read clipboard text",
        "set_clipboard_text": "Set clipboard text",
        "copy_selection": "Copy selection from focused window",
        "paste_clipboard": "Paste clipboard into focused window",
        "send_hotkey": "Send allowlisted desktop hotkey",
        "wait_seconds": "Wait for a visible operator pause",
        "wait_for_window": "Wait for an allowlisted window",
        "move_mouse": "Move mouse to a known target",
        "left_click": "Left click a known target",
        "double_click": "Double click a known target",
        "right_click": "Right click a known target",
        "scroll_mouse": "Scroll inside an allowed window",
        "run_operator_recipe": "Run operator recipe",
    }
    label = title_map.get(action_type, "Run allowlisted local action")
    return f"{label}: {target}" if target else label


def _build_executor_description(action_type: str, target: str) -> str:
    descriptions = {
        "read_file": "Allowlisted repo-local read_file action.",
        "write_file": "Allowlisted repo-local write_file action.",
        "append_file": "Allowlisted repo-local append_file action.",
        "create_artifact": "Allowlisted repo-local create_artifact action.",
        "list_directory": "Allowlisted repo-local list_directory action.",
        "git_status": "Allowlisted repo-local git_status action.",
        "git_diff": "Allowlisted repo-local git_diff action.",
        "run_checker": "Allowlisted repo-local checker execution.",
        "list_windows": "Allowlisted desktop bridge action for visible allowlisted windows only.",
        "get_active_window": "Allowlisted desktop bridge action for the current foreground window only.",
        "focus_window": "Approval-aware desktop bridge action for focusing one allowlisted window.",
        "open_allowed_app": "Approval-aware desktop bridge action for opening one allowlisted local app.",
        "capture_desktop_screenshot": "Approval-aware desktop bridge action for a repo-local desktop screenshot artifact.",
        "get_clipboard_text": "Allowlisted desktop bridge action for reading the current clipboard text only.",
        "set_clipboard_text": "Approval-aware desktop bridge action for setting clipboard text explicitly.",
        "copy_selection": "Approval-aware desktop bridge action for copying the current selection from an allowed window.",
        "paste_clipboard": "Approval-aware desktop bridge action for pasting clipboard text into an allowed focused window.",
        "send_hotkey": "Approval-aware desktop bridge action for a narrow allowlisted hotkey only.",
        "wait_seconds": "Allowlisted desktop bridge action for an explicit visible wait.",
        "wait_for_window": "Allowlisted desktop bridge action for waiting on one allowlisted window only.",
        "move_mouse": "Approval-aware desktop bridge action for moving the mouse to a known target only.",
        "left_click": "Approval-aware desktop bridge action for left clicking a known target only.",
        "double_click": "Approval-aware desktop bridge action for double clicking a known target only.",
        "right_click": "Approval-aware desktop bridge action for right clicking a known target only.",
        "scroll_mouse": "Approval-aware desktop bridge action for scrolling inside an allowed context only.",
        "run_operator_recipe": "Allowlisted multi-step operator recipe built from existing desktop bridge actions.",
    }
    suffix = f" Target: {target}" if target else ""
    return f"{descriptions.get(action_type, 'Allowlisted local executor action.')}{suffix}"


def _executor_requires_approval(action_type: str) -> bool:
    return (
        action_type in WRITE_EXECUTOR_ACTIONS
        or action_type in CHECKER_EXECUTOR_ACTIONS
        or action_type in DESKTOP_VISIBLE_ACTIONS
        or action_type in RECIPE_EXECUTOR_ACTIONS
    )


def _last_execution_record(task: Task) -> TaskExecutionRecord | None:
    if not task.execution_records:
        return None
    return task.execution_records[-1]


def _prepare_executor_action(
    action_type: str,
    target: str,
    content: str,
) -> tuple[str, str, dict, list[str], str]:
    normalized_action = (action_type or "").strip().lower()
    if normalized_action not in ALLOWED_EXECUTOR_ACTIONS:
        raise ValueError(f"Unsupported executor action: {action_type}")

    payload: dict = {}
    target_paths: list[str] = []
    normalized_target = (target or "").strip()

    if normalized_action in {"read_file", "write_file", "append_file", "create_artifact", "list_directory"}:
        resolved_target = _resolve_executor_path(normalized_target)
        normalized_target = str(resolved_target)
        target_paths = [normalized_target]
        if normalized_action in WRITE_EXECUTOR_ACTIONS:
            payload["content"] = content
    elif normalized_action in {"git_status", "git_diff"}:
        normalized_target = str(get_allowed_workspace_root())
        target_paths = [normalized_target]
    elif normalized_action == "run_checker":
        checker_name = normalized_target.lower()
        if checker_name not in ALLOWED_CHECKER_TARGETS:
            raise ValueError("run_checker target must be one of: runtime, dashboard")
        script_path = (get_allowed_workspace_root() / "03_scripts" / ALLOWED_CHECKER_TARGETS[checker_name]).resolve(strict=False)
        normalized_target = checker_name
        target_paths = [str(script_path)]
        payload["script_path"] = str(script_path)
    elif normalized_action == "list_windows":
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
        target_filter = normalized_target.lower()
        if target_filter:
            if target_filter not in ALLOWED_DESKTOP_FOCUS_TARGETS:
                raise ValueError(
                    "list_windows target must be blank or one of: "
                    + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
                )
            normalized_target = target_filter
            payload["bridge_target"] = target_filter
        else:
            normalized_target = "all_allowed_windows"
            payload["bridge_target"] = ""
    elif normalized_action == "get_active_window":
        normalized_target = "foreground_window"
        payload["bridge_target"] = ""
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "focus_window":
        target_alias = normalized_target.lower()
        if target_alias not in ALLOWED_DESKTOP_FOCUS_TARGETS:
            raise ValueError(
                "focus_window target must be one of: "
                + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
            )
        normalized_target = target_alias
        payload["bridge_target"] = target_alias
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "open_allowed_app":
        target_alias = normalized_target.lower()
        if target_alias not in ALLOWED_DESKTOP_APP_TARGETS:
            raise ValueError(
                "open_allowed_app target must be one of: "
                + ", ".join(sorted(ALLOWED_DESKTOP_APP_TARGETS))
            )
        normalized_target = target_alias
        payload["bridge_target"] = target_alias
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "capture_desktop_screenshot":
        screenshot_target = normalized_target or str(
            (
                get_allowed_workspace_root()
                / "05_logs"
                / "tmp"
                / "desktop"
                / f"desktop-capture-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.png"
            ).resolve(strict=False)
        )
        resolved_target = _resolve_executor_path(screenshot_target)
        normalized_target = str(resolved_target)
        target_paths = [normalized_target]
        payload["artifact_path"] = normalized_target
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "get_clipboard_text":
        normalized_target = "clipboard"
        payload["bridge_target"] = ""
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "set_clipboard_text":
        normalized_target = "clipboard"
        payload["bridge_target"] = ""
        payload["text_content"] = content
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "copy_selection":
        alias = _normalize_optional_window_target(normalized_target, action_type="copy_selection")
        normalized_target = alias or "active_allowed_window"
        payload["bridge_target"] = alias
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "paste_clipboard":
        alias = _normalize_optional_window_target(normalized_target, action_type="paste_clipboard")
        normalized_target = alias or "active_allowed_window"
        payload["bridge_target"] = alias
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "send_hotkey":
        normalized_target = _normalize_hotkey_target(normalized_target)
        payload["bridge_target"] = normalized_target
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "wait_seconds":
        wait_seconds = _require_positive_int(
            normalized_target,
            label="wait_seconds target",
            minimum=1,
            maximum=60,
        )
        normalized_target = str(wait_seconds)
        payload["bridge_target"] = normalized_target
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "wait_for_window":
        normalized_target = _normalize_wait_for_window_target(normalized_target)
        payload["bridge_target"] = normalized_target
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action in {"move_mouse", "left_click", "double_click", "right_click", "scroll_mouse"}:
        normalized_target = _require_target_text(normalized_target, normalized_action)
        payload["bridge_target"] = normalized_target
        payload["max_attempts"] = DEFAULT_DESKTOP_MAX_ATTEMPTS
    elif normalized_action == "run_operator_recipe":
        recipe_definition = _build_operator_recipe_definition(
            normalized_target,
            _parse_operator_recipe_options(content),
        )
        recipe_metadata = dict(recipe_definition.get("metadata", {}))
        normalized_target = recipe_definition["name"]
        payload.update(
            {
                "recipe_name": recipe_definition["name"],
                "recipe_label": recipe_definition["label"],
                "recipe_description": recipe_definition["description"],
                "recipe_risk_level": recipe_definition["risk_level"],
                "recipe_steps": recipe_definition["steps"],
                "max_attempts": DEFAULT_DESKTOP_MAX_ATTEMPTS,
                **recipe_metadata,
            }
        )
    else:
        raise ValueError(f"Unsupported executor action: {action_type}")

    if normalized_action == "run_operator_recipe":
        risk_level = str(payload.get("recipe_risk_level") or recipe_definition["risk_level"])
    else:
        risk_level = "safe" if normalized_action in (READ_ONLY_EXECUTOR_ACTIONS | DESKTOP_OBSERVATION_ACTIONS) else "ask"
    return normalized_action, normalized_target, payload, target_paths, risk_level


def enqueue_executor_task(
    action_type: str,
    target: str = "",
    content: str = "",
    source: str = "manual",
) -> Task:
    normalized_action, normalized_target, payload, target_paths, risk_level = _prepare_executor_action(
        action_type=action_type,
        target=target,
        content=content,
    )
    if normalized_action == "run_operator_recipe":
        display_target = str(payload.get("recipe_label") or normalized_target or "operator_recipe")
        title = f"Run operator recipe: {display_target}"
        description = str(payload.get("recipe_description") or "Allowlisted operator recipe.")
    else:
        display_target = normalized_target or "workspace_root"
        title = _build_executor_title(normalized_action, display_target)
        description = _build_executor_description(normalized_action, display_target)
    return enqueue_task(
        title=title,
        description=description,
        risk_level=risk_level,
        source=source,
        executor_action_type=normalized_action,
        executor_target=normalized_target,
        executor_payload=payload,
        target_paths=target_paths,
    )


def list_executor_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.executor_action_type]


def _run_repo_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=get_allowed_workspace_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if result.returncode != 0:
        raise RuntimeError(_shorten_output(stderr or stdout or f"Command failed: {' '.join(args)}"))
    return stdout or stderr


def _build_desktop_bridge_action_result(
    *,
    action_type: str,
    target: str,
    values: dict[str, str],
    sections: dict[str, list[str]],
    artifact_path: str,
) -> dict:
    headline = values.get("headline", "")

    if action_type == "list_windows":
        window_count = len([item for item in sections.get("windows", []) if item != "none"])
        summary = headline or f"Detected {window_count} allowlisted window(s)."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "get_active_window":
        alias = values.get("active_window_alias", "unsupported")
        title = values.get("active_window_title", "none")
        summary = headline or f"Active window alias: {alias}. Title: {title}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "focus_window":
        title = values.get("focused_window_title") or target or "allowlisted window"
        summary = headline or f"Focused {title}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "open_allowed_app":
        reused_existing_window = values.get("reused_existing_window", "no") == "yes"
        command_path = values.get("command_path", "unknown")
        summary = (
            headline
            or (
                f"Focused existing allowlisted app window: {target or 'allowed app'}."
                if reused_existing_window
                else f"Opened {target or 'allowed app'} using {command_path}."
            )
        )
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "capture_desktop_screenshot":
        captured_path = values.get("artifact_path", artifact_path)
        summary = headline or "Captured desktop screenshot artifact."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": captured_path, "values": values, "sections": sections}

    if action_type == "get_clipboard_text":
        preview = values.get("clipboard_preview", "empty")
        summary = headline or f"Clipboard text captured. Preview: {preview}"
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "set_clipboard_text":
        preview = values.get("clipboard_preview", "empty")
        summary = headline or f"Clipboard text updated. Preview: {preview}"
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "copy_selection":
        alias = values.get("active_window_alias") or values.get("focused_window_alias") or target or "allowed_window"
        preview = values.get("clipboard_preview", "empty")
        summary = headline or f"Copied the current selection from {alias}. Preview: {preview}"
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "paste_clipboard":
        alias = values.get("active_window_alias") or values.get("focused_window_alias") or target or "allowed_window"
        preview = values.get("clipboard_preview", "empty")
        summary = headline or f"Pasted clipboard text into {alias}. Preview: {preview}"
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "send_hotkey":
        hotkey = values.get("sent_hotkey", target or "unknown")
        alias = values.get("active_window_alias") or values.get("focused_window_alias") or "allowed_window"
        summary = headline or f"Sent allowlisted hotkey {hotkey} to {alias}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "wait_seconds":
        waited = values.get("waited_seconds", target or "0")
        summary = headline or f"Waited {waited} second(s)."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "wait_for_window":
        alias = values.get("wait_window_alias", target or "allowed_window")
        title = values.get("matched_window_title", "none")
        summary = headline or f"Detected {alias}. Title: {title}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "move_mouse":
        coordinates = values.get("coordinates", target or "unknown")
        summary = headline or f"Moved mouse to {coordinates}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type in {"left_click", "double_click", "right_click"}:
        coordinates = values.get("coordinates", target or "unknown")
        summary = headline or f"{action_type.replace('_', ' ')} succeeded at {coordinates}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    if action_type == "scroll_mouse":
        delta = values.get("scroll_delta", target or "unknown")
        summary = headline or f"Scrolled mouse input by {delta}."
        return {"summary": _shorten_output(summary, limit=320), "artifact_path": "", "values": values, "sections": sections}

    raise RuntimeError(f"Desktop bridge action is not allowlisted: {action_type}")


def _invoke_desktop_bridge_action(
    *,
    action_type: str,
    target: str = "",
    artifact_path: str = "",
    text_content: str = "",
) -> dict:
    script_path = _desktop_bridge_script_path()
    if not script_path.is_file():
        raise RuntimeError("Desktop bridge action script is missing.")

    command = [
        "powershell.exe",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-Action",
        action_type,
        "-AllowedRoot",
        str(get_allowed_workspace_root()),
    ]
    if target:
        command.extend(["-Target", target])
    if artifact_path:
        command.extend(["-ArtifactPath", artifact_path])
    if action_type == "set_clipboard_text":
        command.extend(["-TextContent", text_content])

    result = subprocess.run(
        command,
        cwd=get_allowed_workspace_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(
        part.strip()
        for part in ((result.stdout or "").strip(), (result.stderr or "").strip())
        if part.strip()
    ).strip()
    values, sections = _parse_key_value_output(output)

    if values.get("status") == "interrupted":
        interruption_reason = (
            values.get("interruption_reason")
            or values.get("headline")
            or output
            or "Desktop action interrupted by local failsafe."
        )
        raise DesktopActionInterrupted(_shorten_output(interruption_reason, limit=320))

    if values.get("status") == "blocked":
        failure_reason = (
            values.get("failure_reason")
            or values.get("headline")
            or output
            or "Desktop bridge action was blocked by a local guard."
        )
        raise DesktopActionBlocked(_shorten_output(failure_reason, limit=320), values=values)

    if result.returncode != 0:
        failure_reason = values.get("failure_reason") or values.get("headline") or output or "Desktop bridge action failed."
        raise RuntimeError(_shorten_output(failure_reason, limit=320))

    return _build_desktop_bridge_action_result(
        action_type=action_type,
        target=target,
        values=values,
        sections=sections,
        artifact_path=artifact_path,
    )


def _run_desktop_bridge_action(
    *,
    task: Task,
    action_type: str,
    target: str = "",
    artifact_path: str = "",
    text_content: str = "",
) -> tuple[str, str]:
    max_attempts = int(task.executor_payload.get("max_attempts", DEFAULT_DESKTOP_MAX_ATTEMPTS) or DEFAULT_DESKTOP_MAX_ATTEMPTS)
    max_attempts = max(1, min(DEFAULT_DESKTOP_MAX_ATTEMPTS, max_attempts))
    last_error = ""

    for attempt in range(1, max_attempts + 1):
        try:
            result = _invoke_desktop_bridge_action(
                action_type=action_type,
                target=target,
                artifact_path=artifact_path,
                text_content=text_content,
            )
            _set_desktop_execution_metadata(
                task,
                attempt_count=attempt,
                max_attempts=max_attempts,
            )
            summary = str(result["summary"] or "")
            if attempt > 1:
                summary = _shorten_output(f"Succeeded on attempt {attempt}/{max_attempts}. {summary}", limit=320)
            return summary, str(result["artifact_path"] or "")
        except DesktopActionInterrupted as exc:
            _set_desktop_execution_metadata(
                task,
                attempt_count=attempt,
                max_attempts=max_attempts,
                interruption_reason=str(exc),
            )
            raise
        except DesktopActionBlocked as exc:
            _set_desktop_execution_metadata(
                task,
                attempt_count=attempt,
                max_attempts=max_attempts,
                failure_reason=str(exc),
                resource_guard_reason=str(exc) if "resource guard" in str(exc).lower() else "",
            )
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = _shorten_output(str(exc), limit=320)
            _set_desktop_execution_metadata(
                task,
                attempt_count=attempt,
                max_attempts=max_attempts,
                failure_reason=last_error,
            )
            if attempt >= max_attempts:
                break

    raise RuntimeError(_shorten_output(f"Failed after {max_attempts} attempt(s). Last error: {last_error or 'desktop action failed.'}", limit=320))


def _persist_recipe_run(task: Task, run_payload: dict) -> None:
    history = list(task.executor_payload.get("recipe_run_history", []))
    history.append(run_payload)
    task.executor_payload["recipe_last_run"] = run_payload
    task.executor_payload["recipe_run_history"] = history[-5:]


def _handoff_payload_reason(classification: str, reason: str, preview: str) -> str:
    normalized_classification = (classification or "").strip().lower()
    normalized_reason = (reason or "").strip()
    if normalized_reason and normalized_reason.lower() != "none":
        return normalized_reason
    if normalized_classification == "empty_payload":
        return "Clipboard is empty, so the handoff payload was blocked before paste."
    if normalized_classification == "junk_label_payload":
        return "Clipboard looks like a checker or recipe label instead of real handoff text."
    if normalized_classification == "repeated_ui_label_garbage":
        return "Clipboard looks like repeated concatenated UI labels, so the payload was blocked."
    if normalized_classification == "valid_handoff_text":
        return f"Clipboard payload looks safe for handoff. Preview: {preview or 'none'}"
    return "Clipboard payload classification is unknown, so the handoff cannot continue safely."


def _handoff_payload_fingerprint(raw_text: str) -> str:
    normalized = " ".join((raw_text or "").strip().lower().split())
    if not normalized:
        return "none"
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]


def _update_handoff_window_match_metadata(task: Task, *, step_result: dict) -> None:
    action_type = str(step_result.get("action_type", "")).strip().lower()
    target = str(step_result.get("target", "")).strip().lower()
    alias = str(step_result.get("window_alias", "")).strip().lower()
    title = str(step_result.get("window_title", "")).strip()
    if not alias:
        return

    match_value = alias if not title else f"{alias} | {title}"
    source_window = str(task.executor_payload.get("recipe_source_window", "")).strip().lower()
    target_window = str(task.executor_payload.get("recipe_target_window", "")).strip().lower()

    if action_type in {"focus_window", "copy_selection"} and target == source_window:
        task.executor_payload["handoff_source_match"] = match_value

    if action_type in {"focus_window", "paste_clipboard", "send_hotkey"} and (
        target == target_window or target.startswith(f"{target_window}|")
    ):
        task.executor_payload["handoff_target_match"] = match_value

    if (
        str(task.executor_payload.get("handoff_source_match", "")).strip()
        and str(task.executor_payload.get("handoff_target_match", "")).strip()
        and task.executor_payload.get("handoff_target_match") != "pending_target_match"
    ):
        task.executor_payload["handoff_target_resolution_status"] = "resolved"
        task.executor_payload["handoff_manual_target_resolution"] = "not_needed"


def _apply_handoff_blocked_metadata(
    task: Task,
    *,
    step_result: dict,
    blocked_message: str,
    blocked_values: dict[str, str] | None = None,
) -> None:
    blocked_values = blocked_values or {}
    lowered_message = blocked_message.lower()
    guard_state = str(blocked_values.get("guard_state", "")).strip().lower()
    target = str(step_result.get("target", "")).strip().lower()
    source_window = str(task.executor_payload.get("recipe_source_window", "")).strip().lower()
    target_window = str(task.executor_payload.get("recipe_target_window", "")).strip().lower()

    task.executor_payload["handoff_stop_reason"] = blocked_message
    task.executor_payload["handoff_send_allowed"] = "no"

    if any(
        phrase in lowered_message
        for phrase in (
            "checker or recipe label",
            "repeated concatenated ui labels",
            "payload was blocked",
            "clipboard is empty",
            "handoff payload blocked before paste",
        )
    ):
        task.executor_payload["handoff_paste_allowed"] = "no"

    needs_manual_resolution = guard_state == "manual_focus_required" or any(
        phrase in lowered_message
        for phrase in (
            "no visible allowlisted window found",
            "manual focus is required",
            "did not move focus",
            "requested allowlisted window",
            "target is unclear",
        )
    )
    if not needs_manual_resolution:
        return

    task.executor_payload["handoff_target_resolution_status"] = "manual_target_resolution_required"
    task.executor_payload["handoff_manual_target_resolution"] = "required"
    task.executor_payload["handoff_fallback_denied"] = "yes"
    task.executor_payload["handoff_paste_allowed"] = "no"

    if target == source_window:
        task.executor_payload["handoff_source_match"] = "not_resolved"
    if target == target_window or target.startswith(f"{target_window}|"):
        task.executor_payload["handoff_target_match"] = "not_resolved"


def _handoff_manual_resolution_failure(failure_message: str) -> bool:
    lowered_message = (failure_message or "").lower()
    return any(
        phrase in lowered_message
        for phrase in (
            "no visible allowlisted window found",
            "manual focus is required",
            "did not move focus",
            "requested allowlisted window",
            "target is unclear",
        )
    )


def _apply_handoff_recipe_step_metadata(
    task: Task,
    *,
    step_result: dict,
    values: dict[str, str],
) -> None:
    classification = str(values.get("clipboard_classification", "")).strip().lower()
    preview = str(values.get("clipboard_preview", "")).strip()
    fingerprint = _handoff_payload_fingerprint(str(values.get("clipboard_fingerprint", "")) or preview)
    reason = _handoff_payload_reason(
        classification,
        str(values.get("clipboard_guard_reason", "")),
        preview,
    )

    if step_result["action_type"] in {"copy_selection", "get_clipboard_text"}:
        if not classification:
            classification = "empty_payload" if not preview or preview.lower() == "empty" else "valid_handoff_text"
            reason = _handoff_payload_reason(classification, "", preview)

        task.executor_payload["handoff_payload_classification"] = classification
        task.executor_payload["handoff_payload_preview"] = preview or "none"
        task.executor_payload["handoff_payload_reason"] = reason
        task.executor_payload["handoff_payload_fingerprint"] = fingerprint
        task.executor_payload["handoff_paste_allowed"] = (
            "yes" if classification in VALID_HANDOFF_PAYLOAD_CLASSIFICATIONS else "no"
        )
        if classification not in VALID_HANDOFF_PAYLOAD_CLASSIFICATIONS:
            previous_fingerprint = str(task.executor_payload.get("handoff_blocked_payload_fingerprint", ""))
            previous_count = int(task.executor_payload.get("handoff_blocked_payload_repeats", "0") or 0)
            repeated_count = previous_count + 1 if fingerprint != "none" and fingerprint == previous_fingerprint else 1
            task.executor_payload["handoff_blocked_payload_fingerprint"] = fingerprint
            task.executor_payload["handoff_blocked_payload_repeats"] = str(repeated_count)
            task.executor_payload["handoff_send_allowed"] = "no"
            if repeated_count >= 2:
                reason = _shorten_output(
                    f"{reason} Repeated identical blocked handoff payload detected again. Stop retrying and resolve the clipboard content manually.",
                    limit=320,
                )
                task.executor_payload["handoff_payload_reason"] = reason
            raise DesktopActionBlocked(
                _shorten_output(f"Handoff payload blocked before paste. {reason}", limit=320),
                values={
                    "clipboard_classification": classification,
                    "clipboard_preview": preview,
                    "clipboard_fingerprint": fingerprint,
                    "clipboard_guard_reason": reason,
                },
            )
        task.executor_payload["handoff_blocked_payload_repeats"] = "0"
        if task.executor_payload.get("handoff_send_behavior") == "explicit_enter_after_paste":
            task.executor_payload["handoff_send_allowed"] = "explicit_after_paste"
        return

    if step_result["action_type"] == "paste_clipboard":
        task.executor_payload["handoff_paste_allowed"] = "yes"
        return

    if step_result["action_type"] == "send_hotkey":
        task.executor_payload["handoff_send_allowed"] = "yes"


def _run_operator_recipe(task: Task) -> tuple[str, str]:
    recipe_name = str(task.executor_payload.get("recipe_name") or task.executor_target).strip().lower()
    recipe_label = str(task.executor_payload.get("recipe_label") or recipe_name or "operator recipe")
    recipe_steps = list(task.executor_payload.get("recipe_steps", []))
    if not recipe_name or not recipe_steps:
        raise RuntimeError("Operator recipe payload is incomplete.")

    started_at = _now()
    completed_steps: list[dict] = []
    last_artifact_path = ""
    task.executor_payload["recipe_name"] = recipe_name
    task.executor_payload["recipe_label"] = recipe_label
    task.executor_payload["recipe_step_count"] = len(recipe_steps)

    for step in recipe_steps:
        action_type = str(step.get("action_type", "")).strip().lower()
        label = str(step.get("label", action_type or "recipe step")).strip() or "recipe step"
        target = str(step.get("target", "")).strip()
        text_content = str(step.get("text_content", ""))
        required = bool(step.get("required", True))
        max_attempts = max(
            1,
            min(
                DEFAULT_DESKTOP_MAX_ATTEMPTS,
                int(step.get("max_attempts", DEFAULT_DESKTOP_MAX_ATTEMPTS) or DEFAULT_DESKTOP_MAX_ATTEMPTS),
            ),
        )
        step_started_at = _now()
        step_result = {
            "step": int(step.get("step", len(completed_steps) + 1)),
            "label": label,
            "action_type": action_type,
            "target": target,
            "started_at": step_started_at,
            "status": "started",
            "summary": "",
            "artifact_path": "",
            "clipboard_preview": "",
            "clipboard_classification": "",
            "window_alias": "",
            "window_title": "",
            "coordinates": "",
            "finished_at": "",
            "attempt_count": 0,
            "max_attempts": max_attempts,
            "required": required,
            "retry_notes": [],
        }
        step_completed = False

        for attempt in range(1, max_attempts + 1):
            step_result["attempt_count"] = attempt
            try:
                if action_type not in DESKTOP_EXECUTOR_ACTIONS:
                    raise RuntimeError(f"Recipe step action is not allowlisted: {action_type}")

                result = _invoke_desktop_bridge_action(
                    action_type=action_type,
                    target=target,
                    artifact_path=str(step.get("artifact_path", "")),
                    text_content=text_content,
                )
                values = dict(result.get("values", {}))
                last_artifact_path = str(result.get("artifact_path") or last_artifact_path)
                step_result["status"] = "succeeded"
                step_summary = str(result.get("summary", "step completed"))
                if attempt > 1:
                    step_summary = _shorten_output(
                        f"Succeeded on attempt {attempt}/{max_attempts}. {step_summary}",
                        limit=320,
                )
                step_result["summary"] = step_summary
                step_result["artifact_path"] = str(result.get("artifact_path") or "")
                step_result["clipboard_preview"] = str(values.get("clipboard_preview", ""))
                step_result["clipboard_classification"] = str(values.get("clipboard_classification", ""))
                step_result["window_alias"] = str(
                    values.get("active_window_alias")
                    or values.get("focused_window_alias")
                    or values.get("wait_window_alias")
                    or ""
                )
                step_result["window_title"] = str(
                    values.get("active_window_title")
                    or values.get("focused_window_title")
                    or values.get("matched_window_title")
                    or ""
                )
                step_result["coordinates"] = str(values.get("coordinates", ""))
                if recipe_name == "codex_to_chatgpt_handoff_mvp":
                    _apply_handoff_recipe_step_metadata(
                        task,
                        step_result=step_result,
                        values=values,
                    )
                    _update_handoff_window_match_metadata(task, step_result=step_result)
                step_result["finished_at"] = _now()
                completed_steps.append(step_result)
                step_completed = True
                break
            except DesktopActionInterrupted as exc:
                interruption_message = _shorten_output(str(exc), limit=320)
                step_result["status"] = "interrupted"
                step_result["summary"] = interruption_message
                step_result["finished_at"] = _now()
                step_result["retry_notes"].append(
                    f"Attempt {attempt}/{max_attempts}: {interruption_message}"
                )
                completed_steps.append(step_result)
                run_payload = {
                    "recipe_name": recipe_name,
                    "recipe_label": recipe_label,
                    "started_at": started_at,
                    "finished_at": step_result["finished_at"],
                    "status": "interrupted",
                    "summary": interruption_message,
                    "steps": completed_steps,
                }
                _persist_recipe_run(task, run_payload)
                raise DesktopActionInterrupted(
                    _shorten_output(
                        f"Recipe {recipe_label} interrupted during step {step_result['step']} ({label}). {interruption_message}",
                        limit=320,
                    )
                ) from exc
            except DesktopActionBlocked as exc:
                blocked_message = _shorten_output(str(exc), limit=320)
                if recipe_name == "codex_to_chatgpt_handoff_mvp":
                    _apply_handoff_blocked_metadata(
                        task,
                        step_result=step_result,
                        blocked_message=blocked_message,
                        blocked_values=getattr(exc, "values", {}),
                    )
                step_result["status"] = "blocked"
                step_result["summary"] = blocked_message
                step_result["finished_at"] = _now()
                step_result["retry_notes"].append(
                    f"Attempt {attempt}/{max_attempts}: {blocked_message}"
                )
                completed_steps.append(step_result)
                run_payload = {
                    "recipe_name": recipe_name,
                    "recipe_label": recipe_label,
                    "started_at": started_at,
                    "finished_at": step_result["finished_at"],
                    "status": "blocked",
                    "summary": blocked_message,
                    "steps": completed_steps,
                }
                _persist_recipe_run(task, run_payload)
                raise DesktopActionBlocked(
                    _shorten_output(
                        f"Recipe {recipe_label} stopped at step {step_result['step']} ({label}). {blocked_message}",
                        limit=320,
                    )
                ) from exc
            except Exception as exc:  # noqa: BLE001
                failure_message = _shorten_output(str(exc), limit=320)
                step_result["retry_notes"].append(
                    f"Attempt {attempt}/{max_attempts}: {failure_message}"
                )
                if attempt < max_attempts:
                    continue

                step_result["finished_at"] = _now()
                if required:
                    if (
                        recipe_name == "codex_to_chatgpt_handoff_mvp"
                        and _handoff_manual_resolution_failure(failure_message)
                    ):
                        blocked_message = _shorten_output(
                            f"Failed after {max_attempts} attempt(s). Last error: {failure_message}",
                            limit=320,
                        )
                        _apply_handoff_blocked_metadata(
                            task,
                            step_result=step_result,
                            blocked_message=blocked_message,
                            blocked_values={"guard_state": "manual_focus_required"},
                        )
                        step_result["status"] = "blocked"
                        step_result["summary"] = blocked_message
                        completed_steps.append(step_result)
                        run_payload = {
                            "recipe_name": recipe_name,
                            "recipe_label": recipe_label,
                            "started_at": started_at,
                            "finished_at": step_result["finished_at"],
                            "status": "blocked",
                            "summary": blocked_message,
                            "steps": completed_steps,
                        }
                        _persist_recipe_run(task, run_payload)
                        raise DesktopActionBlocked(
                            _shorten_output(
                                f"Recipe {recipe_label} stopped at step {step_result['step']} ({label}). {blocked_message}",
                                limit=320,
                            )
                        ) from exc

                    step_result["status"] = "failed"
                    step_result["summary"] = _shorten_output(
                        f"Failed after {max_attempts} attempt(s). Last error: {failure_message}",
                        limit=320,
                    )
                    completed_steps.append(step_result)
                    run_payload = {
                        "recipe_name": recipe_name,
                        "recipe_label": recipe_label,
                        "started_at": started_at,
                        "finished_at": step_result["finished_at"],
                        "status": "failed",
                        "summary": step_result["summary"],
                        "steps": completed_steps,
                    }
                    _persist_recipe_run(task, run_payload)
                    raise RuntimeError(
                        _shorten_output(
                            f"Recipe {recipe_label} stopped at step {step_result['step']} ({label}). {step_result['summary']}",
                            limit=320,
                        )
                    ) from exc

                step_result["status"] = "skipped"
                step_result["summary"] = _shorten_output(
                    f"Skipped after {max_attempts} failed attempt(s). Last error: {failure_message}",
                    limit=320,
                )
                completed_steps.append(step_result)
                step_completed = True
                break

        if not step_completed:
            break

    finished_at = _now()
    summary = _shorten_output(
        f"Recipe {recipe_label} completed {len(completed_steps)} step(s). Last step: {completed_steps[-1]['summary']}",
        limit=320,
    )
    run_payload = {
        "recipe_name": recipe_name,
        "recipe_label": recipe_label,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": "succeeded",
        "summary": summary,
        "steps": completed_steps,
    }
    _persist_recipe_run(task, run_payload)
    return summary, last_artifact_path


def _execute_allowlisted_action(task: Task) -> tuple[str, str]:
    action_type = task.executor_action_type
    artifact_path = ""

    if action_type == "read_file":
        target_path = Path(task.executor_target)
        if not target_path.is_file():
            raise RuntimeError("Target file does not exist or is not a file.")
        content = target_path.read_text(encoding="utf-8", errors="replace")
        return _shorten_output(content, limit=320) or f"Read {target_path.name}.", ""

    if action_type == "write_file":
        target_path = Path(task.executor_target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = str(task.executor_payload.get("content", ""))
        target_path.write_text(content, encoding="utf-8")
        artifact_path = str(target_path)
        return f"Wrote {len(content)} character(s) to {target_path.name}.", artifact_path

    if action_type == "append_file":
        target_path = Path(task.executor_target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = str(task.executor_payload.get("content", ""))
        with target_path.open("a", encoding="utf-8") as handle:
            handle.write(content)
        artifact_path = str(target_path)
        return f"Appended {len(content)} character(s) to {target_path.name}.", artifact_path

    if action_type == "create_artifact":
        target_path = Path(task.executor_target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = str(task.executor_payload.get("content", ""))
        target_path.write_text(content, encoding="utf-8")
        artifact_path = str(target_path)
        return f"Created artifact {target_path.name}.", artifact_path

    if action_type == "list_directory":
        target_path = Path(task.executor_target)
        if not target_path.is_dir():
            raise RuntimeError("Target directory does not exist or is not a directory.")
        entries = sorted(item.name + ("\\" if item.is_dir() else "") for item in target_path.iterdir())
        if not entries:
            return "Directory is empty.", ""
        return _shorten_output(", ".join(entries), limit=320), ""

    if action_type == "git_status":
        output = _run_repo_command(["git", "status", "--short", "--branch"])
        return _shorten_output(output or "Working tree clean."), ""

    if action_type == "git_diff":
        output = _run_repo_command(["git", "diff", "--stat", "HEAD", "--", "."])
        if not output:
            return "Working tree clean. No diff summary to show.", ""
        return _shorten_output(output), ""

    if action_type == "run_checker":
        script_path = Path(str(task.executor_payload.get("script_path", "")))
        if not script_path.is_file():
            raise RuntimeError("Checker script path is missing or invalid.")
        command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
        if (task.executor_target or "").strip().lower() == "dashboard":
            # Avoid deadlocking on the runtime data lock when the dashboard checker
            # shells back into runtime-mutating paths through the local server.
            command.append("-RuntimeLockSafe")
        result = subprocess.run(
            command,
            cwd=get_allowed_workspace_root(),
            capture_output=True,
            text=True,
            check=False,
        )
        output = ((result.stdout or "").strip() + "\n" + (result.stderr or "").strip()).strip()
        if result.returncode != 0:
            raise RuntimeError(_shorten_output(output or f"Checker failed: {script_path.name}"))
        summary_line = output.splitlines()[-1] if output else f"{task.executor_target} checker passed."
        return _shorten_output(summary_line), ""

    if action_type in DESKTOP_EXECUTOR_ACTIONS:
        return _run_desktop_bridge_action(
            task=task,
            action_type=action_type,
            target=str(task.executor_payload.get("bridge_target", task.executor_target)),
            artifact_path=str(task.executor_payload.get("artifact_path", "")),
            text_content=str(task.executor_payload.get("text_content", "")),
        )

    if action_type == "run_operator_recipe":
        return _run_operator_recipe(task)

    raise RuntimeError(f"Executor action is not allowlisted: {action_type}")


def _backfill_pending_approval_requests() -> tuple[list[Task], list[ApprovalRequest]]:
    tasks = read_tasks()
    requests = read_approval_requests()
    known_request_ids = {request.approval_id for request in requests}
    request_lookup = {request.approval_id: request for request in requests}
    changed = False

    for task in tasks:
        if _ensure_task_history(task):
            changed = True

        if not task.workspace_reason and not task.target_paths:
            _apply_workspace_policy(task, task.title, task.description, task.source)
            changed = True

        if task.approval_request_id and task.approval_request_id in request_lookup:
            request = request_lookup[task.approval_request_id]
            if not request.workspace_reason and not request.target_paths:
                request.target_paths = list(task.target_paths)
                request.workspace_scope = task.workspace_scope
                request.workspace_policy = task.workspace_policy
                request.workspace_reason = task.workspace_reason
                changed = True

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
    pending_approval_count = sum(1 for request in approval_requests if request.status == "pending")
    blocked_human_needed_count = sum(1 for task in tasks if task.status == "blocked_human_needed")
    interrupted_count = sum(1 for task in tasks if task.status == "interrupted")
    waiting_count = sum(1 for task in tasks if task.status == "waiting")
    ready_to_resume_count = sum(1 for task in tasks if task.status == "ready_to_resume")
    queued_count = sum(1 for task in tasks if task.status == "queued")
    running_count = sum(1 for task in tasks if task.status == "running")
    resource_guard_events = _recent_resource_guard_events(tasks)

    status = "idle"
    active_task_id = ""

    if any(task.status == "pending_approval" for task in tasks):
        status = "pending_approval"
        active_task_id = _select_active_task_id(tasks, "pending_approval")
    elif any(task.status == "blocked_human_needed" for task in tasks):
        status = "blocked_human_needed"
        active_task_id = _select_active_task_id(tasks, "blocked_human_needed")
    elif any(task.status == "interrupted" for task in tasks):
        status = "interrupted"
        active_task_id = _select_active_task_id(tasks, "interrupted")
    elif any(task.status == "waiting" for task in tasks):
        status = "waiting"
        active_task_id = _select_active_task_id(tasks, "waiting")
    elif any(task.status == "ready_to_resume" for task in tasks):
        status = "ready_to_resume"
        active_task_id = _select_active_task_id(tasks, "ready_to_resume")
    elif any(task.status == "running" for task in tasks):
        status = "running"
        active_task_id = _select_active_task_id(tasks, "running")
    elif any(task.status == "queued" for task in tasks):
        status = "queued"
        active_task_id = _select_active_task_id(tasks, "queued")

    ghoti_state = "idle"
    ghoti_reason = "Ghoti is idle."
    operator_next_step = "Queue or review a local task when you want Ghoti to act."

    if resource_guard_events:
        ghoti_state = "resource_guard_triggered"
        ghoti_reason = resource_guard_events[0]
        operator_next_step = "Reduce duplicate windows or processes, then review the blocked task before re-queueing it."
    elif pending_approval_count > 0:
        ghoti_state = "approval_needed"
        ghoti_reason = f"{pending_approval_count} approval request(s) are waiting for review."
        operator_next_step = "Inspect and approve, deny, or defer the pending approval items."
    elif interrupted_count > 0:
        ghoti_state = "interrupted"
        ghoti_reason = f"{interrupted_count} task(s) were interrupted by the local failsafe."
        operator_next_step = "Review the interrupted task, then re-queue it only if the state is safe."
    elif waiting_count > 0:
        ghoti_state = "waiting"
        ghoti_reason = f"{waiting_count} task(s) are waiting for a reply or timeout."
        operator_next_step = "Resume the waiting task only when the expected reply or event has arrived."
    elif running_count > 0 or queued_count > 0 or ready_to_resume_count > 0 or blocked_human_needed_count > 0:
        ghoti_state = "active"
        ghoti_reason = "Ghoti has queued or operator-reviewed work ready to inspect."
        operator_next_step = "Inspect the selected task and run, review, or re-queue the next safe step."

    state = SupervisorState(
        supervisor_id=previous_state.supervisor_id or "local-supervisor",
        mode=previous_state.mode or "local_only",
        status=status,
        active_task_id=active_task_id,
        pending_approval_count=pending_approval_count,
        blocked_human_needed_count=blocked_human_needed_count,
        interrupted_count=interrupted_count,
        waiting_count=waiting_count,
        ready_to_resume_count=ready_to_resume_count,
        queued_count=queued_count,
        running_count=running_count,
        notification_mode=previous_state.notification_mode or "dashboard",
        updated_at=_now(),
        ghoti_state=ghoti_state,
        ghoti_reason=ghoti_reason,
        operator_next_step=operator_next_step,
        resource_guard_event_count=len(resource_guard_events),
        recent_resource_guard_events=resource_guard_events,
        last_event=last_event if last_event is not None else previous_state.last_event,
        notes=[
            "Local-only supervisor foundation is active.",
            "Remote or admin actions must remain explicit and approval-gated.",
            "Stopped tasks move forward only through explicit operator actions.",
            "Desktop input and mouse actions stay allowlisted, visible, and interruptible with Ctrl+8.",
            "Desktop actions stop after two attempts by default instead of retrying forever.",
        ],
    )
    write_supervisor_state(state)
    return state


def enqueue_task(
    title: str,
    description: str,
    risk_level: str,
    source: str = "manual",
    *,
    executor_action_type: str = "",
    executor_target: str = "",
    executor_payload: dict | None = None,
    target_paths: list[str] | None = None,
) -> Task:
    if risk_level not in ALLOWED_RISKS:
        raise ValueError(f"Unsupported risk level: {risk_level}")
    timestamp = _now()
    task = Task(
        task_id=_new_task_id(),
        title=title,
        description=description,
        risk_level=risk_level,
        status="queued",
        requires_approval=False,
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
        executor_action_type=executor_action_type,
        executor_target=executor_target,
        executor_payload=dict(executor_payload or {}),
    )
    if target_paths:
        _apply_workspace_policy_paths(task, *target_paths)
    else:
        _apply_workspace_policy(task, title, description, source)
    _append_task_event(task, "created", note=title)
    task.admin_required = _requires_admin(task.risk_level)
    requires_approval = _requires_approval(task.risk_level)
    task.requires_approval = requires_approval

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
        task.waiting_for = (
            "workspace_policy_review"
            if task.workspace_policy == "blocked_by_workspace_policy"
            else "human_approval"
        )
        task.requires_human = True
        task.blocked_reason = (
            task.workspace_reason
            if task.workspace_policy == "blocked_by_workspace_policy"
            else ""
        )
        approval_requests.append(approval_request)
        _append_task_event(
            task,
            "escalated",
            note=(
                task.workspace_reason
                if task.workspace_policy == "blocked_by_workspace_policy"
                else "Task requires human approval before execution."
            ),
        )
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
    _, requests = _backfill_pending_approval_requests()
    return _find_approval_request(requests, approval_id)


def list_approval_records(
    *,
    approval_id: str = "",
    task_id: str = "",
) -> list[ApprovalRecord]:
    records = read_approvals()
    if approval_id:
        records = [record for record in records if record.approval_id == approval_id]
    if task_id:
        records = [record for record in records if record.task_id == task_id]
    return sorted(records, key=lambda record: record.decided_at, reverse=True)


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

    if task.executor_action_type and task.target_paths:
        _apply_workspace_policy_paths(task, *task.target_paths)
    else:
        _apply_workspace_policy(
            task,
            action_label,
            reason,
            source,
            scope,
            rollback_plan,
        )
    task.requires_approval = True
    task.admin_required = _requires_admin(task.risk_level) if requires_admin is None else requires_admin
    task.status = "pending_approval"
    task.approval_state = "pending"
    task.waiting_for = (
        "workspace_policy_review"
        if task.workspace_policy == "blocked_by_workspace_policy"
        else "human_approval"
    )
    task.requires_human = True
    task.blocked_reason = (
        task.workspace_reason
        if task.workspace_policy == "blocked_by_workspace_policy"
        else ""
    )
    task.last_note = reason
    task.updated_at = timestamp
    _ensure_task_history(task)
    _append_task_event(task, "escalated", note=reason)

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


def _resolve_approval_request(
    approval_id: str,
    decision: str,
    note: str = "",
) -> tuple[Task, ApprovalRequest]:
    if decision not in {"approved", "denied", "deferred"}:
        raise ValueError(f"Unsupported approval decision: {decision}")

    tasks = read_tasks()
    task_lookup = {task.task_id: task for task in tasks}
    requests = read_approval_requests()
    request = _find_approval_request(requests, approval_id)
    task = task_lookup.get(request.task_id)
    if task is None:
        raise ValueError(f"Task not found for approval request: {approval_id}")

    if request.status not in {"pending", "deferred"}:
        raise ValueError(f"Approval request is not actionable: {approval_id}")

    timestamp = _now()
    request.status = decision
    request.updated_at = timestamp
    request.human_note = note

    task.approval_request_id = request.approval_id
    task.updated_at = timestamp
    task.last_note = note
    _ensure_task_history(task)

    workspace_blocked = task.workspace_policy == "blocked_by_workspace_policy"

    if decision == "approved" and workspace_blocked:
        task.status = "blocked_human_needed"
        task.approval_state = "approved"
        task.waiting_for = "workspace_policy_override"
        task.blocked_reason = (
            task.workspace_reason
            or "Blocked by workspace policy until the allowed workspace root is expanded."
        )
        task.requires_human = True
        _append_task_event(task, "approved", note=note or "Human approved the request.")
        _append_task_event(
            task,
            "blocked_by_workspace_policy",
            note=task.blocked_reason,
        )
    elif decision == "approved":
        task.status = "queued"
        task.approval_state = "approved"
        task.waiting_for = ""
        task.blocked_reason = ""
        task.requires_human = False
        _append_task_event(task, "approved", note=note or "Human approved the request.")
    elif decision == "denied":
        task.status = "rejected"
        task.approval_state = "denied"
        task.waiting_for = ""
        task.blocked_reason = "Human denied the requested action."
        task.requires_human = False
        _append_task_event(task, "denied", note=note or task.blocked_reason)
    else:
        task.status = "waiting"
        task.approval_state = "deferred"
        task.waiting_for = "approval deferred by human"
        task.blocked_reason = note or "Human deferred the requested action."
        task.requires_human = True
        _append_task_event(task, "deferred", note=note or task.blocked_reason)

    write_tasks(tasks)
    write_approval_requests(requests)

    approvals = read_approvals()
    approvals.append(
        ApprovalRecord(
            task_id=task.task_id,
            decision=decision,
            decided_at=timestamp,
            note=note,
            approval_id=approval_id,
        )
    )
    write_approvals(approvals)

    event_map = {
        "approved": (
            f"Approval recorded, but workspace policy still blocks task {task.task_id}"
            if workspace_blocked
            else f"Approval granted for task {task.task_id}"
        ),
        "denied": f"Approval denied for task {task.task_id}",
        "deferred": f"Approval deferred for task {task.task_id}",
    }
    refresh_supervisor_state(last_event=event_map[decision])
    return task, request


def approve_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="approved", note=note)


def deny_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="denied", note=note)


def defer_approval_request(approval_id: str, note: str = "") -> tuple[Task, ApprovalRequest]:
    return _resolve_approval_request(approval_id=approval_id, decision="deferred", note=note)


def approve_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")
    if task.approval_request_id:
        task, _ = approve_approval_request(task.approval_request_id, note=note)
        return task
    raise ValueError(f"Task is missing an approval request id: {task_id}")


def reject_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.approval_state not in {"pending", "deferred"}:
        raise ValueError(f"Task is not pending approval: {task_id}")
    if task.approval_request_id:
        task, _ = deny_approval_request(task.approval_request_id, note=note)
        return task
    raise ValueError(f"Task is missing an approval request id: {task_id}")


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
    _ensure_task_history(task)
    _append_task_event(task, "waiting", note=reason)
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task waiting: {task.task_id}")
    return task


def resume_task(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "waiting":
        raise ValueError(f"Task {task_id} must be waiting before resume.")
    if task.approval_state == "pending":
        raise ValueError(f"Task {task_id} still needs approval before resume.")

    task.status = "queued"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    _ensure_task_history(task)
    _append_task_event(task, "resumed", note="Operator resumed the waiting task.")
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
    _ensure_task_history(task)
    _append_task_event(task, "human_needed", note=reason)
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task blocked for human input: {task.task_id}")
    return task


def review_task_for_resume(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status not in {"blocked_human_needed", "interrupted"}:
        raise ValueError(f"Task {task_id} must be human-needed or interrupted before review.")

    timestamp = _now()
    task.updated_at = timestamp
    task.last_note = note
    _ensure_task_history(task)

    if task.workspace_policy == "blocked_by_workspace_policy":
        task.waiting_for = "workspace_policy_override"
        task.blocked_reason = (
            task.workspace_reason
            or "Task remains blocked until the target is moved inside the workspace."
        )
        task.requires_human = True
        _append_task_event(
            task,
            "blocked_by_workspace_policy",
            note=note or task.blocked_reason,
        )
        write_tasks(tasks)
        refresh_supervisor_state(last_event=f"Task remains workspace-blocked: {task.task_id}")
        return task

    task.status = "ready_to_resume"
    task.waiting_for = "operator_requeue"
    task.blocked_reason = ""
    task.requires_human = False
    _append_task_event(
        task,
        "ready_to_resume",
        note=note or "Human-needed review completed; task is ready to re-queue.",
    )
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task ready to resume: {task.task_id}")
    return task


def requeue_task(task_id: str, note: str = "") -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "ready_to_resume":
        raise ValueError(f"Task {task_id} must be ready_to_resume before re-queue.")
    if task.workspace_policy == "blocked_by_workspace_policy":
        raise ValueError(
            "Task is blocked by workspace policy until the allowed workspace root is expanded "
            "or the target is moved inside the workspace."
        )

    task.status = "queued"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False
    task.updated_at = _now()
    task.last_note = note
    _ensure_task_history(task)
    _append_task_event(task, "resumed", note=note or "Operator re-queued the task.")
    write_tasks(tasks)
    refresh_supervisor_state(last_event=f"Task re-queued: {task.task_id}")
    return task


def execute_task(task_id: str) -> Task:
    tasks = read_tasks()
    task = _find_task(tasks, task_id)
    if task.status != "queued":
        raise ValueError(f"Task {task.task_id} must be queued before execution.")
    if task.approval_state not in {"approved", "not_required"}:
        raise ValueError(f"Task {task.task_id} must be approved before execution.")
    if task.workspace_policy == "blocked_by_workspace_policy":
        raise ValueError(
            "Task is blocked by workspace policy until the allowed workspace root is expanded "
            "or the target is moved inside the workspace."
        )

    _ensure_task_history(task)
    task.updated_at = _now()

    if not task.executor_action_type:
        task.status = "completed"
        task.waiting_for = ""
        task.blocked_reason = ""
        task.requires_human = False
        _append_task_event(task, "completed", note="Task completed in manual run-once mode.")
        write_tasks(tasks)
        refresh_supervisor_state(last_event=f"Task completed: {task.task_id}")
        return task

    task.status = "running"
    task.waiting_for = ""
    task.blocked_reason = ""
    task.requires_human = False

    started_at = _now()
    execution_record = TaskExecutionRecord(
        action_type=task.executor_action_type,
        target=task.executor_target or "workspace_root",
        started_at=started_at,
        status="started",
        success=False,
    )
    _append_task_event(
        task,
        "execution_started",
        note=f"Started {task.executor_action_type} for {task.executor_target or 'workspace_root'}.",
    )

    try:
        output_summary, artifact_path = _execute_allowlisted_action(task)
        execution_record.finished_at = _now()
        execution_record.status = "succeeded"
        execution_record.success = True
        execution_record.output_summary = output_summary
        execution_record.artifact_path = artifact_path
        execution_record.attempt_count = int(task.executor_payload.get("last_attempt_count", 1) or 1)
        task.execution_records.append(execution_record)
        task.status = "completed"
        task.last_note = output_summary
        task.updated_at = execution_record.finished_at
        _append_task_event(task, "completed", note=output_summary)
        last_event = f"Executor task completed: {task.task_id}"
    except DesktopActionBlocked as exc:
        blocked_message = _shorten_output(str(exc), limit=320)
        execution_record.finished_at = _now()
        execution_record.status = "failed"
        execution_record.success = False
        execution_record.output_summary = blocked_message
        execution_record.failure_reason = blocked_message
        execution_record.resource_guard_reason = blocked_message if "resource guard" in blocked_message.lower() else ""
        execution_record.attempt_count = int(task.executor_payload.get("last_attempt_count", 1) or 1)
        task.execution_records.append(execution_record)
        task.status = "blocked_human_needed"
        task.waiting_for = RESOURCE_GUARD_WAITING_FOR
        task.blocked_reason = blocked_message
        task.last_note = blocked_message
        task.updated_at = execution_record.finished_at
        task.requires_human = True
        _append_task_event(task, "resource_guard_triggered", note=blocked_message)
        last_event = f"Resource guard blocked task: {task.task_id}"
    except DesktopActionInterrupted as exc:
        interruption_message = _shorten_output(str(exc), limit=320)
        execution_record.finished_at = _now()
        execution_record.status = "interrupted"
        execution_record.success = False
        execution_record.output_summary = interruption_message
        execution_record.interruption_reason = interruption_message
        execution_record.attempt_count = int(task.executor_payload.get("last_attempt_count", 1) or 1)
        task.execution_records.append(execution_record)
        task.status = "interrupted"
        task.waiting_for = "operator_review_after_interrupt"
        task.blocked_reason = interruption_message
        task.last_note = interruption_message
        task.updated_at = execution_record.finished_at
        task.requires_human = True
        _append_task_event(task, "interrupted", note=interruption_message)
        last_event = f"Executor task interrupted: {task.task_id}"
    except Exception as exc:  # noqa: BLE001
        failure_message = _shorten_output(str(exc))
        execution_record.finished_at = _now()
        execution_record.status = "failed"
        execution_record.success = False
        execution_record.output_summary = failure_message
        execution_record.failure_reason = failure_message
        execution_record.attempt_count = int(task.executor_payload.get("last_attempt_count", 1) or 1)
        task.execution_records.append(execution_record)
        task.status = "failed"
        task.blocked_reason = failure_message
        task.last_note = failure_message
        task.updated_at = execution_record.finished_at
        task.requires_human = True
        _append_task_event(task, "failed", note=failure_message)
        last_event = f"Executor task failed: {task.task_id}"

    write_tasks(tasks)
    refresh_supervisor_state(last_event=last_event)
    return task


def run_task_once(task_id: str) -> Task:
    return execute_task(task_id)


def list_pending_approvals() -> list[ApprovalRequest]:
    return list_approval_requests(status="pending")


def list_blocked_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "blocked_human_needed"]


def list_interrupted_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "interrupted"]


def list_waiting_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "waiting"]


def list_ready_to_resume_tasks() -> list[Task]:
    return [task for task in list_tasks() if task.status == "ready_to_resume"]


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
        interrupted_tasks=sum(1 for task in tasks if task.status == "interrupted"),
        ready_to_resume_tasks=sum(
            1 for task in tasks if task.status == "ready_to_resume"
        ),
        completed_tasks=sum(1 for task in tasks if task.status == "completed"),
        rejected_tasks=sum(1 for task in tasks if task.status == "rejected"),
        failed_tasks=sum(1 for task in tasks if task.status == "failed"),
        pending_approval_requests=sum(
            1 for request in approval_requests if request.status == "pending"
        ),
    )


def get_task_history(task_id: str) -> list[TaskEvent]:
    task = get_task(task_id)
    return list(task.history)


def get_task_next_action(task: Task) -> str:
    return _task_next_action(task)
