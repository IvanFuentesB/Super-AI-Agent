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


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
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

    gh_path = shutil.which("gh")
    if not gh_path:
        return RemoteInfo(origin_url=origin_url, gh_available=False, gh_authenticated=None)

    gh_result = subprocess.run(
        ["gh", "auth", "status"],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return RemoteInfo(
        origin_url=origin_url,
        gh_available=True,
        gh_authenticated=gh_result.returncode == 0,
    )
