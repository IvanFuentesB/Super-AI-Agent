from __future__ import annotations

from datetime import datetime, timezone
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
DESKTOP_OBSERVATION_ACTIONS = {"list_windows", "get_active_window"}
DESKTOP_VISIBLE_ACTIONS = {"focus_window", "open_allowed_app", "capture_desktop_screenshot"}
DESKTOP_EXECUTOR_ACTIONS = DESKTOP_OBSERVATION_ACTIONS | DESKTOP_VISIBLE_ACTIONS
ALLOWED_CHECKER_TARGETS = {
    "runtime": "check_runtime_mvp.ps1",
    "dashboard": "check_dashboard_mvp.ps1",
}
ALLOWED_DESKTOP_FOCUS_TARGETS = {"cursor", "vscode", "terminal", "dashboard_browser"}
ALLOWED_DESKTOP_APP_TARGETS = {"cursor", "vscode", "terminal", "dashboard_browser"}
QUEUEABLE_TASK_STATUSES = {"queued", "running", "waiting", "blocked_human_needed", "ready_to_resume"}
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)\b[A-Z]:\\[^\s\"'<>|?*]+")


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
        if task.workspace_policy == "blocked_by_workspace_policy":
            return "Keep blocked until the target is moved inside the workspace or policy changes."
        return "Mark the human-needed step as reviewed."
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
    }
    suffix = f" Target: {target}" if target else ""
    return f"{descriptions.get(action_type, 'Allowlisted local executor action.')}{suffix}"


def _executor_requires_approval(action_type: str) -> bool:
    return (
        action_type in WRITE_EXECUTOR_ACTIONS
        or action_type in CHECKER_EXECUTOR_ACTIONS
        or action_type in DESKTOP_VISIBLE_ACTIONS
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
    elif normalized_action == "focus_window":
        target_alias = normalized_target.lower()
        if target_alias not in ALLOWED_DESKTOP_FOCUS_TARGETS:
            raise ValueError(
                "focus_window target must be one of: "
                + ", ".join(sorted(ALLOWED_DESKTOP_FOCUS_TARGETS))
            )
        normalized_target = target_alias
        payload["bridge_target"] = target_alias
    elif normalized_action == "open_allowed_app":
        target_alias = normalized_target.lower()
        if target_alias not in ALLOWED_DESKTOP_APP_TARGETS:
            raise ValueError(
                "open_allowed_app target must be one of: "
                + ", ".join(sorted(ALLOWED_DESKTOP_APP_TARGETS))
            )
        normalized_target = target_alias
        payload["bridge_target"] = target_alias
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
    else:
        raise ValueError(f"Unsupported executor action: {action_type}")

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
    display_target = normalized_target or "workspace_root"
    return enqueue_task(
        title=_build_executor_title(normalized_action, display_target),
        description=_build_executor_description(normalized_action, display_target),
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


def _run_desktop_bridge_action(
    *,
    action_type: str,
    target: str = "",
    artifact_path: str = "",
) -> tuple[str, str]:
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

    if result.returncode != 0:
        failure_reason = values.get("failure_reason") or values.get("headline") or output or "Desktop bridge action failed."
        raise RuntimeError(_shorten_output(failure_reason, limit=320))

    headline = values.get("headline", "")
    if action_type == "list_windows":
        window_count = len([item for item in sections.get("windows", []) if item != "none"])
        summary = headline or f"Detected {window_count} allowlisted window(s)."
        return _shorten_output(summary, limit=320), ""

    if action_type == "get_active_window":
        alias = values.get("active_window_alias", "unsupported")
        title = values.get("active_window_title", "none")
        summary = headline or f"Active window alias: {alias}. Title: {title}."
        return _shorten_output(summary, limit=320), ""

    if action_type == "focus_window":
        title = values.get("focused_window_title") or target or "allowlisted window"
        summary = headline or f"Focused {title}."
        return _shorten_output(summary, limit=320), ""

    if action_type == "open_allowed_app":
        command_path = values.get("command_path", "unknown")
        summary = headline or f"Opened {target or 'allowed app'} using {command_path}."
        return _shorten_output(summary, limit=320), ""

    if action_type == "capture_desktop_screenshot":
        captured_path = values.get("artifact_path", artifact_path)
        summary = headline or "Captured desktop screenshot artifact."
        return _shorten_output(summary, limit=320), captured_path

    raise RuntimeError(f"Desktop bridge action is not allowlisted: {action_type}")


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
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
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
            action_type=action_type,
            target=str(task.executor_payload.get("bridge_target", task.executor_target)),
            artifact_path=str(task.executor_payload.get("artifact_path", "")),
        )

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

    status = "idle"
    active_task_id = ""

    if any(task.status == "pending_approval" for task in tasks):
        status = "pending_approval"
        active_task_id = _select_active_task_id(tasks, "pending_approval")
    elif any(task.status == "blocked_human_needed" for task in tasks):
        status = "blocked_human_needed"
        active_task_id = _select_active_task_id(tasks, "blocked_human_needed")
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

    state = SupervisorState(
        supervisor_id=previous_state.supervisor_id or "local-supervisor",
        mode=previous_state.mode or "local_only",
        status=status,
        active_task_id=active_task_id,
        pending_approval_count=sum(
            1 for request in approval_requests if request.status == "pending"
        ),
        blocked_human_needed_count=sum(
            1 for task in tasks if task.status == "blocked_human_needed"
        ),
        waiting_count=sum(1 for task in tasks if task.status == "waiting"),
        ready_to_resume_count=sum(1 for task in tasks if task.status == "ready_to_resume"),
        queued_count=sum(1 for task in tasks if task.status == "queued"),
        running_count=sum(1 for task in tasks if task.status == "running"),
        notification_mode=previous_state.notification_mode or "dashboard",
        updated_at=_now(),
        last_event=last_event if last_event is not None else previous_state.last_event,
        notes=[
            "Local-only supervisor foundation is active.",
            "Remote or admin actions must remain explicit and approval-gated.",
            "Stopped tasks move forward only through explicit operator actions.",
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
    if task.status != "blocked_human_needed":
        raise ValueError(f"Task {task_id} must be human-needed before review.")

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
        task.execution_records.append(execution_record)
        task.status = "completed"
        task.last_note = output_summary
        task.updated_at = execution_record.finished_at
        _append_task_event(task, "completed", note=output_summary)
        last_event = f"Executor task completed: {task.task_id}"
    except Exception as exc:  # noqa: BLE001
        failure_message = _shorten_output(str(exc))
        execution_record.finished_at = _now()
        execution_record.status = "failed"
        execution_record.success = False
        execution_record.output_summary = failure_message
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
