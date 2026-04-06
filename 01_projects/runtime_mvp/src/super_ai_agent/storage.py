from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

from .models import ApprovalRecord, Task

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DATA_DIR = PROJECT_ROOT / "runtime_data"
TASKS_PATH = RUNTIME_DATA_DIR / "tasks.json"
APPROVALS_PATH = RUNTIME_DATA_DIR / "approvals.json"


def get_project_root() -> Path:
    return PROJECT_ROOT


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
    try:
        path.write_text(text, encoding="utf-8")
    except OSError:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        escaped_path = _ps_literal(path)
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


def get_runtime_data_dir() -> Path:
    _ensure_directory(RUNTIME_DATA_DIR)
    return RUNTIME_DATA_DIR


def ensure_runtime_files() -> Path:
    runtime_dir = get_runtime_data_dir()
    if not TASKS_PATH.exists():
        _write_text(TASKS_PATH, "[]\n")
    if not APPROVALS_PATH.exists():
        _write_text(APPROVALS_PATH, "[]\n")
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


def read_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in _read_json_list(TASKS_PATH)]


def write_tasks(tasks: list[Task]) -> None:
    _write_json_list(TASKS_PATH, [task.to_dict() for task in tasks])


def read_approvals() -> list[ApprovalRecord]:
    return [ApprovalRecord.from_dict(item) for item in _read_json_list(APPROVALS_PATH)]


def write_approvals(records: list[ApprovalRecord]) -> None:
    _write_json_list(APPROVALS_PATH, [record.to_dict() for record in records])
