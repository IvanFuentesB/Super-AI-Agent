from __future__ import annotations

import base64
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

from .models import ApprovalRecord, ApprovalRequest, SupervisorState, Task

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1].resolve()
RUNTIME_DATA_DIR = PROJECT_ROOT / "runtime_data"
TASKS_PATH = RUNTIME_DATA_DIR / "tasks.json"
APPROVALS_PATH = RUNTIME_DATA_DIR / "approvals.json"
APPROVAL_REQUESTS_PATH = RUNTIME_DATA_DIR / "approval_requests.json"
SUPERVISOR_STATE_PATH = RUNTIME_DATA_DIR / "supervisor_state.json"
RUNTIME_BRAIN_CONFIG_PATH = RUNTIME_DATA_DIR / "brain_config.json"
RUNTIME_BRAIN_STATE_PATH = RUNTIME_DATA_DIR / "brain_state.json"
RUNTIME_BROWSER_STATE_PATH = RUNTIME_DATA_DIR / "browser_state.json"
RUNTIME_RELAY_LOOP_STATE_PATH = RUNTIME_DATA_DIR / "relay_loop_state.json"
RUNTIME_LOCK_PATH = RUNTIME_DATA_DIR / ".runtime_data.lock"


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_workspace_root() -> Path:
    return WORKSPACE_ROOT


def get_allowed_workspace_root() -> Path:
    configured = os.environ.get("SUPER_AGENT_ALLOWED_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve(strict=False)
    return WORKSPACE_ROOT


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_supervisor_state() -> SupervisorState:
    return SupervisorState(
        supervisor_id="local-supervisor",
        mode="local_only",
        status="idle",
        active_task_id="",
        pending_approval_count=0,
        blocked_human_needed_count=0,
        interrupted_count=0,
        waiting_count=0,
        ready_to_resume_count=0,
        queued_count=0,
        running_count=0,
        notification_mode="dashboard",
        updated_at=_now(),
        last_event="Supervisor initialized.",
        notes=["Local-only supervisor foundation is active."],
    )


def _ps_literal(path: Path) -> str:
    return str(path).replace("'", "''")


def _ensure_directory(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        escaped_path = _ps_literal(path)
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    "[System.IO.Directory]::CreateDirectory("
                    f"'{escaped_path}') | Out-Null"
                ),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def _write_text(path: Path, text: str) -> None:
    _ensure_directory(path.parent)
    temp_path = path.with_name(
        f"{path.name}.tmp-{os.getpid()}-{int(time.time() * 1000)}"
    )
    try:
        try:
            temp_path.write_text(text, encoding="utf-8")
        except OSError:
            encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
            escaped_path = _ps_literal(temp_path)
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    (
                        "[System.IO.File]::WriteAllBytes("
                        f"'{escaped_path}', "
                        f"[Convert]::FromBase64String('{encoded}'))"
                    ),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        last_error: OSError | None = None
        for attempt in range(8):
            try:
                os.replace(temp_path, path)
                return
            except PermissionError as exc:
                last_error = exc
            except OSError as exc:
                if getattr(exc, "winerror", None) not in {5, 32}:
                    raise
                last_error = exc
            time.sleep(0.05 * (attempt + 1))

        if last_error is not None:
            raise last_error
        raise OSError(f"Failed to replace runtime file: {path}")
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _initialize_file_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    try:
        _write_text(path, text)
    except OSError:
        if not path.exists():
            raise


@contextmanager
def runtime_data_lock(timeout_seconds: float = 30.0, poll_seconds: float = 0.05):
    ensure_runtime_files()
    deadline = time.monotonic() + timeout_seconds
    lock_handle: int | None = None

    while lock_handle is None:
        try:
            lock_handle = os.open(
                RUNTIME_LOCK_PATH,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            os.write(
                lock_handle,
                f"pid={os.getpid()} created_at={_now()}".encode("utf-8"),
            )
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Timed out waiting for runtime data lock: {RUNTIME_LOCK_PATH}"
                ) from None
            time.sleep(poll_seconds)

    try:
        yield
    finally:
        if lock_handle is not None:
            os.close(lock_handle)
        try:
            RUNTIME_LOCK_PATH.unlink(missing_ok=True)
        except OSError:
            pass


def get_runtime_data_dir() -> Path:
    _ensure_directory(RUNTIME_DATA_DIR)
    return RUNTIME_DATA_DIR


def ensure_runtime_files() -> Path:
    runtime_dir = get_runtime_data_dir()
    _initialize_file_if_missing(TASKS_PATH, "[]\n")
    _initialize_file_if_missing(APPROVALS_PATH, "[]\n")
    _initialize_file_if_missing(APPROVAL_REQUESTS_PATH, "[]\n")
    _initialize_file_if_missing(
        SUPERVISOR_STATE_PATH,
        json.dumps(_default_supervisor_state().to_dict(), indent=2) + "\n",
    )
    _initialize_file_if_missing(
        RUNTIME_BRAIN_CONFIG_PATH,
        json.dumps({}, indent=2) + "\n",
    )
    _initialize_file_if_missing(
        RUNTIME_BRAIN_STATE_PATH,
        json.dumps(
            {
                "last_call_status": "never_called",
                "last_called_at": "",
                "last_provider": "",
                "last_model": "",
                "last_source": "",
                "last_task_id": "",
                "last_error": "",
                "last_response_preview": "",
                "last_inference_used": False,
            },
            indent=2,
        ) + "\n",
    )
    _initialize_file_if_missing(
        RUNTIME_BROWSER_STATE_PATH,
        json.dumps(
            {
                "current_role": "none",
                "current_action": "none",
                "current_session_id": "",
                "last_status": "not_used",
                "notes": [],
            },
            indent=2,
        ) + "\n",
    )
    _initialize_file_if_missing(
        RUNTIME_RELAY_LOOP_STATE_PATH,
        json.dumps(
            {
                "relay_state": "idle",
                "current_step": "idle",
                "source_target_alias": "chatgpt",
                "source_target_candidate_id": "",
                "source_target_title": "",
                "destination_target_alias": "codex",
                "destination_target_candidate_id": "",
                "destination_target_title": "",
                "codex_mode_preset": "Implementing new feature",
                "codex_reasoning_preset": "Medium",
                "preset_application_status": "stored_only",
                "codex_execution_status": "unknown",
                "next_usage_reset_at": "",
                "resume_after_usage_reset": False,
                "waiting_reason": "",
                "blocked_reason": "",
                "last_payload_preview": "",
                "last_result_preview": "",
                "last_completion_status": "not_started",
                "last_transition_at": "",
                "last_updated_at": "",
                "last_used_task_id": "",
                "last_known_dialog_status": "none",
                "last_known_dialog_note": "",
                "saved_targets": {
                    "chatgpt": {
                        "alias": "chatgpt",
                        "candidate_id": "",
                        "title": "",
                        "binding_status": "not_bound",
                        "last_checked_at": "",
                        "last_error": "",
                    },
                    "codex": {
                        "alias": "codex",
                        "candidate_id": "",
                        "title": "",
                        "binding_status": "not_bound",
                        "last_checked_at": "",
                        "last_error": "",
                    },
                },
            },
            indent=2,
        ) + "\n",
    )
    return runtime_dir


def _read_json_list(path: Path) -> list[dict]:
    ensure_runtime_files()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {path}")
    return data


def _write_json_list(path: Path, items: list[dict]) -> None:
    ensure_runtime_files()
    _write_text(path, json.dumps(items, indent=2) + "\n")


def _read_json_object(path: Path) -> dict:
    ensure_runtime_files()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected an object in {path}")
    return data


def _write_json_object(path: Path, payload: dict) -> None:
    ensure_runtime_files()
    _write_text(path, json.dumps(payload, indent=2) + "\n")


def read_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in _read_json_list(TASKS_PATH)]


def write_tasks(tasks: list[Task]) -> None:
    _write_json_list(TASKS_PATH, [task.to_dict() for task in tasks])


def read_approvals() -> list[ApprovalRecord]:
    return [ApprovalRecord.from_dict(item) for item in _read_json_list(APPROVALS_PATH)]


def write_approvals(records: list[ApprovalRecord]) -> None:
    _write_json_list(APPROVALS_PATH, [record.to_dict() for record in records])


def read_approval_requests() -> list[ApprovalRequest]:
    return [
        ApprovalRequest.from_dict(item)
        for item in _read_json_list(APPROVAL_REQUESTS_PATH)
    ]


def write_approval_requests(requests: list[ApprovalRequest]) -> None:
    _write_json_list(
        APPROVAL_REQUESTS_PATH,
        [request.to_dict() for request in requests],
    )


def read_supervisor_state() -> SupervisorState:
    return SupervisorState.from_dict(_read_json_object(SUPERVISOR_STATE_PATH))


def write_supervisor_state(state: SupervisorState) -> None:
    _write_json_object(SUPERVISOR_STATE_PATH, state.to_dict())


def read_brain_config_object() -> dict:
    return _read_json_object(RUNTIME_BRAIN_CONFIG_PATH)


def write_brain_config_object(payload: dict) -> None:
    _write_json_object(RUNTIME_BRAIN_CONFIG_PATH, payload)


def read_brain_state_object() -> dict:
    return _read_json_object(RUNTIME_BRAIN_STATE_PATH)


def write_brain_state_object(payload: dict) -> None:
    _write_json_object(RUNTIME_BRAIN_STATE_PATH, payload)


def read_browser_state_object() -> dict:
    return _read_json_object(RUNTIME_BROWSER_STATE_PATH)


def write_browser_state_object(payload: dict) -> None:
    _write_json_object(RUNTIME_BROWSER_STATE_PATH, payload)


def read_relay_loop_state_object() -> dict:
    return _read_json_object(RUNTIME_RELAY_LOOP_STATE_PATH)


def write_relay_loop_state_object(payload: dict) -> None:
    _write_json_object(RUNTIME_RELAY_LOOP_STATE_PATH, payload)

