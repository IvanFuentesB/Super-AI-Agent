from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from .storage import get_project_root

WORKSPACE_ROOT = get_project_root().parents[1]


@dataclass
class GitHubRepoStatusSummary:
    repo_root: str
    branch: str
    is_clean: bool
    staged_changes: int
    unstaged_changes: int
    untracked_changes: int


@dataclass
class RecentCommit:
    commit_hash: str
    subject: str


@dataclass
class RemoteInfo:
    origin_url: str | None
    gh_available: bool
    gh_authenticated: bool | None


@dataclass
class GhEnvironmentDiagnostics:
    gh_available: bool
    gh_path: str | None
    where_results: list[str]
    version: str | None
    auth_known: bool
    gh_authenticated: bool | None
    notes: list[str]


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["gh", *args],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def _ensure_repo() -> None:
    result = _run_git(["rev-parse", "--is-inside-work-tree"])
    if result.returncode != 0 or result.stdout.strip() != "true":
        message = result.stderr.strip() or "Current workspace is not a git repo."
        raise ValueError(message)


def is_gh_available() -> bool:
    return shutil.which("gh") is not None


def diagnose_gh_environment() -> GhEnvironmentDiagnostics:
    gh_path = shutil.which("gh")
    where_results: list[str] = []
    notes: list[str] = []
    version: str | None = None
    auth_known = False
    gh_authenticated: bool | None = None

    where_path = shutil.which("where.exe")
    if where_path:
        where_result = subprocess.run(
            [where_path, "gh"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if where_result.returncode == 0:
            where_results = [line.strip() for line in where_result.stdout.splitlines() if line.strip()]
        elif where_result.stderr.strip():
            notes.append(where_result.stderr.strip())

    if not gh_path:
        notes.append("gh is not installed or not available on PATH.")
        return GhEnvironmentDiagnostics(
            gh_available=False,
            gh_path=None,
            where_results=where_results,
            version=None,
            auth_known=False,
            gh_authenticated=None,
            notes=notes,
        )

    version_result = _run_gh(["--version"])
    if version_result.returncode == 0:
        version = version_result.stdout.splitlines()[0].strip() if version_result.stdout.strip() else "unknown"
    else:
        notes.append(version_result.stderr.strip() or "Unable to read gh version.")

    auth_result = _run_gh(["auth", "status"])
    auth_known = True
    gh_authenticated = auth_result.returncode == 0
    if auth_result.stdout.strip():
        notes.append(auth_result.stdout.strip())
    elif auth_result.stderr.strip():
        notes.append(auth_result.stderr.strip())

    return GhEnvironmentDiagnostics(
        gh_available=True,
        gh_path=gh_path,
        where_results=where_results,
        version=version,
        auth_known=auth_known,
        gh_authenticated=gh_authenticated,
        notes=notes,
    )


def get_current_branch() -> str:
    _ensure_repo()
    result = _run_git(["branch", "--show-current"])
    branch = result.stdout.strip()
    if result.returncode != 0 or not branch:
        message = result.stderr.strip() or "Unable to determine current branch."
        raise ValueError(message)
    return branch


def get_repo_status_summary() -> GitHubRepoStatusSummary:
    _ensure_repo()
    result = _run_git(["status", "--porcelain"])
    if result.returncode != 0:
        message = result.stderr.strip() or "Unable to read git status."
        raise ValueError(message)

    staged_changes = 0
    unstaged_changes = 0
    untracked_changes = 0

    for line in result.stdout.splitlines():
        if line.startswith("??"):
            untracked_changes += 1
            continue
        if len(line) >= 2:
            if line[0] not in {" ", "?"}:
                staged_changes += 1
            if line[1] not in {" ", "?"}:
                unstaged_changes += 1

    return GitHubRepoStatusSummary(
        repo_root=str(WORKSPACE_ROOT),
        branch=get_current_branch(),
        is_clean=not any([staged_changes, unstaged_changes, untracked_changes]),
        staged_changes=staged_changes,
        unstaged_changes=unstaged_changes,
        untracked_changes=untracked_changes,
    )


def get_recent_commits(limit: int = 5) -> list[RecentCommit]:
    _ensure_repo()
    bounded_limit = max(1, min(limit, 20))
    result = _run_git(["log", f"-{bounded_limit}", "--pretty=format:%h|%s"])
    if result.returncode != 0:
        message = result.stderr.strip() or "Unable to read recent commits."
        raise ValueError(message)

    commits: list[RecentCommit] = []
    for line in result.stdout.splitlines():
        commit_hash, _, subject = line.partition("|")
        commits.append(RecentCommit(commit_hash=commit_hash.strip(), subject=subject.strip()))
    return commits


def get_remote_info() -> RemoteInfo:
    _ensure_repo()
    origin_result = _run_git(["remote", "get-url", "origin"])
    origin_url = origin_result.stdout.strip() if origin_result.returncode == 0 else None

    if not is_gh_available():
        return RemoteInfo(origin_url=origin_url, gh_available=False, gh_authenticated=None)

    gh_result = _run_gh(["auth", "status"])
    return RemoteInfo(
        origin_url=origin_url,
        gh_available=True,
        gh_authenticated=gh_result.returncode == 0,
    )


def create_local_branch(branch_name: str) -> str:
    _ensure_repo()
    branch_name = branch_name.strip()
    if not branch_name:
        raise ValueError("Branch name must not be empty.")

    result = _run_git(["switch", "-c", branch_name])
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Unable to create local branch."
        raise ValueError(message)
    return f"created local branch: {branch_name}"


def create_remote_issue(title: str, body: str) -> str:
    _ensure_repo()
    if not is_gh_available():
        raise ValueError("gh is not available. Remote issue creation cannot run in this environment.")

    result = _run_gh(["issue", "create", "--title", title, "--body", body])
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Unable to create remote issue."
        raise ValueError(message)
    return result.stdout.strip() or "remote issue created"


def create_remote_pr(title: str, body: str, base_branch: str = "main") -> str:
    _ensure_repo()
    if not is_gh_available():
        raise ValueError("gh is not available. Remote PR creation cannot run in this environment.")

    current_branch = get_current_branch()
    result = _run_gh(
        [
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base_branch,
            "--head",
            current_branch,
        ]
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Unable to create remote PR."
        raise ValueError(message)
    return result.stdout.strip() or "remote PR created"
