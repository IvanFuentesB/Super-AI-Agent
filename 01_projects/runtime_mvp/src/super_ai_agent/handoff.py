from __future__ import annotations

from pathlib import Path

from .storage import _write_text, get_project_root, get_runtime_data_dir

WORKSPACE_ROOT = get_project_root().parents[1]
HANDOFF_DIR = WORKSPACE_ROOT / "14_context"
HANDOFF_FILES = [
    "current_state.md",
    "next_actions.md",
    "decisions.md",
    "open_questions.md",
    "recent_failures.md",
    "status_board.md",
]


def build_handoff_snapshot() -> Path:
    runtime_dir = get_runtime_data_dir()
    output_path = runtime_dir / "handoff_snapshot.md"

    sections: list[str] = ["# Runtime Handoff Snapshot", ""]
    for filename in HANDOFF_FILES:
        source_path = HANDOFF_DIR / filename
        if source_path.exists():
            content = source_path.read_text(encoding="utf-8").strip()
        else:
            content = "_Missing source file._"
        sections.extend([f"## {filename}", "", content, ""])

    _write_text(output_path, "\n".join(sections).rstrip() + "\n")
    return output_path
