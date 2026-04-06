from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .storage import get_project_root

REPO_ROOT = get_project_root().parents[1]
TOOL_POLICY_PATH = REPO_ROOT / "23_configs" / "tool_detection_policy.example.json"

DEFAULT_POLICY = {
    "detect_python": True,
    "detect_git": True,
    "detect_gh": True,
    "python_common_windows_paths": [
        "%LocalAppData%\\Programs\\Python\\Python313\\python.exe",
        "%LocalAppData%\\Programs\\Python\\Python312\\python.exe",
        "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe",
        "C:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\Simulation\\Topology\\tools\\smapy\\python\\python.exe",
    ],
    "git_common_windows_paths": [
        "%ProgramFiles%\\Git\\cmd\\git.exe",
        "%ProgramFiles%\\Git\\bin\\git.exe",
        "%ProgramFiles(x86)%\\Git\\cmd\\git.exe",
    ],
    "gh_common_windows_paths": [
        "%ProgramFiles%\\GitHub CLI\\gh.exe",
        "%ProgramFiles(x86)%\\GitHub CLI\\gh.exe",
        "%LocalAppData%\\Programs\\GitHub CLI\\gh.exe",
        "%USERPROFILE%\\scoop\\apps\\gh\\current\\bin\\gh.exe",
    ],
    "allow_per_process_tool_resolution": True,
    "allow_global_path_mutation": False,
}


@dataclass
class ToolResolution:
    tool_id: str
    found: bool
    resolved_path: str | None
    source: str
    path_visible: bool
    version: str | None
    auth_known: bool = False
    authenticated: bool | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class EnvironmentDiagnosis:
    python: ToolResolution
    git: ToolResolution
    gh: ToolResolution


@dataclass
class CapabilityStatus:
    capability_id: str
    required_tools: list[str]
    state: str
    blocking_issue: str | None


def _load_detection_policy() -> dict:
    policy = dict(DEFAULT_POLICY)
    if TOOL_POLICY_PATH.exists():
        with TOOL_POLICY_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for key, value in payload.items():
            policy[key] = value
    return policy


def _expand_candidate_paths(raw_paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    seen: set[str] = set()
    for item in raw_paths:
        candidate = Path(os.path.expandvars(item)).expanduser()
        key = str(candidate)
        if key not in seen:
            expanded.append(candidate)
            seen.add(key)
    return expanded


def _existing_candidate_paths(raw_paths: list[str]) -> list[Path]:
    return [path for path in _expand_candidate_paths(raw_paths) if path.exists()]


def _first_line(text: str) -> str | None:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return None


def _run_tool(command: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [command, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _detect_tool(
    tool_id: str,
    executable_name: str,
    common_path_key: str,
    version_args: list[str] | None = None,
    detect_auth: bool = False,
) -> ToolResolution:
    policy = _load_detection_policy()
    if not policy.get(f"detect_{tool_id}", True):
        return ToolResolution(
            tool_id=tool_id,
            found=False,
            resolved_path=None,
            source="disabled",
            path_visible=False,
            version=None,
            notes=[f"{tool_id} detection is disabled by policy."],
        )

    resolved = shutil.which(executable_name)
    path_visible = resolved is not None
    source = "path" if resolved else "missing"
    notes: list[str] = []

    if not resolved and policy.get("allow_per_process_tool_resolution", True):
        fallback_hits = _existing_candidate_paths(policy.get(common_path_key, []))
        if fallback_hits:
            resolved = str(fallback_hits[0])
            source = "fallback"
            notes.append(f"Using fallback path: {resolved}")

    if not resolved:
        notes.append(f"{tool_id} not found on PATH or fallback paths.")
        return ToolResolution(
            tool_id=tool_id,
            found=False,
            resolved_path=None,
            source="missing",
            path_visible=path_visible,
            version=None,
            notes=notes,
        )

    version = None
    version_result = _run_tool(resolved, version_args or ["--version"])
    version_line = _first_line(version_result.stdout) or _first_line(version_result.stderr or "")
    if version_result.returncode == 0 and version_line:
        version = version_line
    elif version_line:
        notes.append(version_line)
    else:
        notes.append(f"Unable to read {tool_id} version cleanly.")

    auth_known = False
    authenticated: bool | None = None
    if detect_auth:
        auth_result = _run_tool(resolved, ["auth", "status"])
        auth_known = True
        authenticated = auth_result.returncode == 0
        auth_line = _first_line(auth_result.stdout) or _first_line(auth_result.stderr or "")
        if auth_line:
            notes.append(auth_line)

    return ToolResolution(
        tool_id=tool_id,
        found=True,
        resolved_path=resolved,
        source=source,
        path_visible=path_visible,
        version=version,
        auth_known=auth_known,
        authenticated=authenticated,
        notes=notes,
    )


def find_python_command() -> str | None:
    return _detect_tool("python", "python", "python_common_windows_paths").resolved_path


def find_git_command() -> str | None:
    return _detect_tool("git", "git", "git_common_windows_paths").resolved_path


def detect_common_gh_paths() -> list[str]:
    policy = _load_detection_policy()
    return [str(path) for path in _existing_candidate_paths(policy.get("gh_common_windows_paths", []))]


def find_gh_command() -> str | None:
    return _detect_tool("gh", "gh", "gh_common_windows_paths", detect_auth=True).resolved_path


def diagnose_environment() -> EnvironmentDiagnosis:
    return EnvironmentDiagnosis(
        python=_detect_tool("python", "python", "python_common_windows_paths"),
        git=_detect_tool("git", "git", "git_common_windows_paths"),
        gh=_detect_tool("gh", "gh", "gh_common_windows_paths", detect_auth=True),
    )


def build_capability_summary(
    diagnosis: EnvironmentDiagnosis | None = None,
) -> list[CapabilityStatus]:
    diagnosis = diagnosis or diagnose_environment()
    github_read_only_block = None if diagnosis.git.found else "git is not available to the runtime."

    if not diagnosis.git.found:
        github_remote_write_block = "git is not available to the runtime."
    elif not diagnosis.gh.found:
        github_remote_write_block = "gh is not available on PATH or fallback paths."
    elif diagnosis.gh.auth_known and diagnosis.gh.authenticated is False:
        github_remote_write_block = "gh is available but not authenticated."
    else:
        github_remote_write_block = None

    return [
        CapabilityStatus(
            capability_id="github_read_only",
            required_tools=["git"],
            state="available" if github_read_only_block is None else "blocked",
            blocking_issue=github_read_only_block,
        ),
        CapabilityStatus(
            capability_id="github_remote_write_possible",
            required_tools=["git", "gh", "gh_auth"],
            state="available" if github_remote_write_block is None else "blocked",
            blocking_issue=github_remote_write_block,
        ),
        CapabilityStatus(
            capability_id="mail_planning",
            required_tools=[],
            state="available",
            blocking_issue=None,
        ),
        CapabilityStatus(
            capability_id="notion_planning",
            required_tools=[],
            state="available",
            blocking_issue=None,
        ),
        CapabilityStatus(
            capability_id="browser_app_execution",
            required_tools=["future_executor"],
            state="blocked",
            blocking_issue="Browser and app execution is not implemented yet.",
        ),
        CapabilityStatus(
            capability_id="truth_council_scaffolding",
            required_tools=[],
            state="available",
            blocking_issue=None,
        ),
        CapabilityStatus(
            capability_id="personal_ops_scaffolding",
            required_tools=[],
            state="available",
            blocking_issue=None,
        ),
    ]
