from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .storage import get_project_root

REPO_ROOT = get_project_root().parents[1]
MEMORY_ROOT = REPO_ROOT / "14_context" / "compact_memory"

MEMORY_FILES = {
    "index": MEMORY_ROOT / "index.md",
    "role_notes": MEMORY_ROOT / "role_notes.md",
    "decision_extracts": MEMORY_ROOT / "decision_extracts.md",
    "plan_extracts": MEMORY_ROOT / "plan_extracts.md",
    "task_summaries": MEMORY_ROOT / "task_summaries.md",
    "future_paths": MEMORY_ROOT / "future_paths.md",
    "current_working_summary": MEMORY_ROOT / "current_working_summary.md",
    "current_loop_state": MEMORY_ROOT / "current_loop_state.md",
    "compact_build_context": MEMORY_ROOT / "compact_build_context.md",
    "last_successful_step": MEMORY_ROOT / "last_successful_step.md",
    "next_exact_step": MEMORY_ROOT / "next_exact_step.md",
    "blocker_state": MEMORY_ROOT / "blocker_state.md",
    "operator_handoff_summary": MEMORY_ROOT / "operator_handoff_summary.md",
}


@dataclass
class MemoryLayerStatus:
    memory_root: Path
    ready: bool
    obsidian_markdown_ready: bool
    file_count: int
    missing_files: list[str]
    newest_modified_at: str
    notes: list[str]


def get_memory_layer_status() -> MemoryLayerStatus:
    missing_files = [
        path.name
        for path in MEMORY_FILES.values()
        if not path.exists()
    ]
    existing_files = [path for path in MEMORY_FILES.values() if path.exists()]
    newest_modified_at = "none"
    if existing_files:
        newest_path = max(existing_files, key=lambda item: item.stat().st_mtime)
        newest_modified_at = datetime.fromtimestamp(
            newest_path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat().replace("+00:00", "Z")

    notes = [
        "Compact markdown memory stays local-first and provider-swappable.",
        "This is scaffolded durable memory for later Obsidian-style use, not a replacement for approvals, actions, or the dashboard.",
        "Task-compressed summaries are template-backed right now; no autonomous memory rewriting loop exists yet.",
        "Relay-loop compact files exist to keep future Codex and ChatGPT passes smaller and more reusable.",
    ]
    if missing_files:
        notes.append("One or more compact-memory markdown files are missing and should be scaffolded before relying on this layer.")

    return MemoryLayerStatus(
        memory_root=MEMORY_ROOT,
        ready=len(missing_files) == 0,
        obsidian_markdown_ready=True,
        file_count=len(existing_files),
        missing_files=missing_files,
        newest_modified_at=newest_modified_at,
        notes=notes,
    )
