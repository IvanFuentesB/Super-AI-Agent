from __future__ import annotations

import re
from pathlib import Path

from .storage import _ensure_directory, _write_text, get_project_root

REPORTS_DIR = get_project_root().parents[1] / "11_exports" / "reports"


def _slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "report"


def build_report_scaffold(title: str, workflow_id: str, summary: str) -> Path:
    _ensure_directory(REPORTS_DIR)
    output_path = REPORTS_DIR / f"{_slugify(title)}.md"

    content = "\n".join(
        [
            f"# {title}",
            "",
            f"Workflow ID: `{workflow_id}`",
            "",
            "## Objective",
            summary,
            "",
            "## Starting State",
            "- to be filled in",
            "",
            "## Actions Taken",
            "- to be filled in",
            "",
            "## Outputs Produced",
            "- to be filled in",
            "",
            "## Risks / Issues",
            "- to be filled in",
            "",
            "## Lessons",
            "- to be filled in",
            "",
            "## Next Step",
            "- to be filled in",
            "",
        ]
    )
    _write_text(output_path, content)
    return output_path
