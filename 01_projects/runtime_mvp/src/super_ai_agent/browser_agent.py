from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .storage import RUNTIME_BROWSER_STATE_PATH, ensure_runtime_files, get_project_root

REPO_ROOT = get_project_root().parents[1]
BROWSER_PROJECT_ROOT = REPO_ROOT / "01_projects" / "browser_playground"
PLAYWRIGHT_PACKAGE_PATH = BROWSER_PROJECT_ROOT / "node_modules" / "playwright" / "package.json"
PLAYWRIGHT_CLI_PATH = BROWSER_PROJECT_ROOT / "node_modules" / ".bin" / "playwright.cmd"
PLAYWRIGHT_BROWSER_ROOT = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"


@dataclass
class BrowserRuntimeState:
    current_role: str = "none"
    current_action: str = "none"
    current_session_id: str = ""
    last_status: str = "not_used"
    notes: list[str] | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["notes"] = list(self.notes or [])
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> "BrowserRuntimeState":
        return cls(
            current_role=str(data.get("current_role", "none") or "none"),
            current_action=str(data.get("current_action", "none") or "none"),
            current_session_id=str(data.get("current_session_id", "") or ""),
            last_status=str(data.get("last_status", "not_used") or "not_used"),
            notes=list(data.get("notes", []) or []),
        )


@dataclass
class BrowserCapabilityStatus:
    browser_use_installed: bool
    browser_use_version: str
    browser_use_ready: bool
    browser_session_support: str
    browser_task_support: str
    playwright_installed: bool
    playwright_version: str
    playwright_cli_available: bool
    playwright_browser_binaries_installed: bool
    playwright_ready: bool
    current_browser_role: str
    current_browser_action: str
    current_browser_session_id: str
    last_browser_status: str
    notes: list[str]


def _read_json_object(path: Path, default: dict) -> dict:
    ensure_runtime_files()
    if not path.exists():
        return dict(default)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return dict(default)
    merged = dict(default)
    merged.update(payload)
    return merged


def _write_json_object(path: Path, payload: dict) -> None:
    ensure_runtime_files()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def get_browser_runtime_state() -> BrowserRuntimeState:
    return BrowserRuntimeState.from_dict(
        _read_json_object(RUNTIME_BROWSER_STATE_PATH, BrowserRuntimeState().to_dict())
    )


def record_browser_runtime_state(state: BrowserRuntimeState) -> None:
    _write_json_object(RUNTIME_BROWSER_STATE_PATH, state.to_dict())


def _detect_browser_use() -> tuple[bool, str]:
    spec = importlib.util.find_spec("browser_use")
    if spec is None:
        return (False, "")
    try:
        version = importlib.metadata.version("browser-use")
    except importlib.metadata.PackageNotFoundError:
        version = "installed"
    return (True, version)


def _detect_playwright() -> tuple[bool, str, bool, bool]:
    if not PLAYWRIGHT_PACKAGE_PATH.exists():
        return (False, "", False, False)
    with PLAYWRIGHT_PACKAGE_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    version = str(payload.get("version", "") or "")
    cli_available = PLAYWRIGHT_CLI_PATH.exists()
    browser_binaries_installed = PLAYWRIGHT_BROWSER_ROOT.exists() and any(
        item.is_dir() and item.name.startswith("chromium")
        for item in PLAYWRIGHT_BROWSER_ROOT.iterdir()
    )
    return (True, version, cli_available, browser_binaries_installed)


def get_browser_capability_status() -> BrowserCapabilityStatus:
    browser_use_installed, browser_use_version = _detect_browser_use()
    playwright_installed, playwright_version, playwright_cli_available, binaries_installed = _detect_playwright()
    runtime_state = get_browser_runtime_state()
    notes: list[str] = []

    if browser_use_installed:
        notes.append("Browser Use is importable for future browser-agent work, but no executor task path is wired to it yet.")
    else:
        notes.append("Browser Use is not installed in the current Python runtime yet.")

    if playwright_installed and binaries_installed:
        notes.append("Playwright remains the deterministic browser-control fallback in the local browser playground.")
    elif playwright_installed:
        notes.append("Playwright is installed in the local browser playground, but browser binaries are not fully present yet.")
    else:
        notes.append("Playwright is not installed in the local browser playground.")

    notes.append("No Browser Use session runner or browser task executor is wired into Ghoti's approval-aware runtime yet.")

    return BrowserCapabilityStatus(
        browser_use_installed=browser_use_installed,
        browser_use_version=browser_use_version or "none",
        browser_use_ready=browser_use_installed,
        browser_session_support="not_wired_yet" if browser_use_installed else "not_available",
        browser_task_support="not_wired_yet" if browser_use_installed else "not_available",
        playwright_installed=playwright_installed,
        playwright_version=playwright_version or "none",
        playwright_cli_available=playwright_cli_available,
        playwright_browser_binaries_installed=binaries_installed,
        playwright_ready=playwright_installed and playwright_cli_available and binaries_installed,
        current_browser_role=runtime_state.current_role or "none",
        current_browser_action=runtime_state.current_action or "none",
        current_browser_session_id=runtime_state.current_session_id or "none",
        last_browser_status=runtime_state.last_status or "not_used",
        notes=notes,
    )
