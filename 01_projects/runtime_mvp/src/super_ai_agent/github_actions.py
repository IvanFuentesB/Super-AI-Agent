from __future__ import annotations

import re
from pathlib import Path

from .github_adapter import create_local_branch, create_remote_issue, create_remote_pr
from .storage import _ensure_directory, _write_text, get_project_root

GITHUB_EXPORTS_DIR = get_project_root().parents[1] / "11_exports" / "github"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "draft"


def _write_draft(filename: str, lines: list[str]) -> Path:
    _ensure_directory(GITHUB_EXPORTS_DIR)
    output_path = GITHUB_EXPORTS_DIR / filename
    _write_text(output_path, "\n".join(lines) + "\n")
    return output_path


def scaffold_issue_draft(
    title: str,
    objective: str,
    context: str,
    body: str,
    labels: str = "",
) -> Path:
    label_lines = [item.strip() for item in labels.split(",") if item.strip()]
    if not label_lines:
        label_lines = ["- none specified"]
    else:
        label_lines = [f"- {item}" for item in label_lines]

    return _write_draft(
        f"{_slugify(title)}-issue-draft.md",
        [
            "# GitHub Issue Draft",
            "",
            "## Title",
            title,
            "",
            "## Objective",
            objective,
            "",
            "## Context",
            context,
            "",
            "## Proposed Body",
            body,
            "",
            "## Labels",
            *label_lines,
            "",
            "## Approval Status",
            "Pending",
            "",
            "## Next Step",
            "- review before any live remote creation",
        ],
    )


def scaffold_pr_draft(
    title: str,
    objective: str,
    source_branch: str,
    target_branch: str,
    summary: str,
    risk_notes: str = "",
) -> Path:
    risk_text = risk_notes if risk_notes else "No extra risk notes provided."
    return _write_draft(
        f"{_slugify(title)}-pr-draft.md",
        [
            "# GitHub PR Draft",
            "",
            "## Title",
            title,
            "",
            "## Objective",
            objective,
            "",
            "## Source Branch",
            source_branch,
            "",
            "## Target Branch",
            target_branch,
            "",
            "## Summary",
            summary,
            "",
            "## Risk Notes",
            risk_text,
            "",
            "## Approval Status",
            "Pending",
            "",
            "## Next Step",
            "- review before any live remote creation",
        ],
    )


def approve_required_or_raise(approved: bool, action_label: str) -> None:
    if not approved:
        raise ValueError(f"Approval required for {action_label}. Re-run with --approve yes.")


def create_branch_with_approval(branch_name: str, approved: bool) -> str:
    approve_required_or_raise(approved, "local branch creation")
    return create_local_branch(branch_name)


def create_issue_with_approval(title: str, body: str, approved: bool) -> str:
    approve_required_or_raise(approved, "remote issue creation")
    return create_remote_issue(title, body)


def create_pr_with_approval(title: str, body: str, base_branch: str, approved: bool) -> str:
    approve_required_or_raise(approved, "remote PR creation")
    return create_remote_pr(title, body, base_branch=base_branch)
