"""Ghoti Agent OS - suggestion-only local worker.

The first bridge from simulation toward real agent operation, kept
deliberately inert: this module never imports subprocess, never opens a
network connection, and never edits arbitrary repo files. It reads
verified local memory sources, reads a workflow template, and writes
proposed plans/handoffs ONLY into the agent OS generated folders. Any
other output directory is refused unless it is repo-local AND listed in
14_context/agent_os/APPROVED_ACTIONS.json (a file only the human edits).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import workflow_templates

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_OS_DIR = REPO_ROOT / "14_context" / "agent_os"
HANDOFFS_DIR = AGENT_OS_DIR / "handoffs"
WORKFLOWS_DIR = AGENT_OS_DIR / "workflows"
RUNS_DIR = AGENT_OS_DIR / "runs"
EVIDENCE_DIR = AGENT_OS_DIR / "evidence"
APPROVAL_FILE = AGENT_OS_DIR / "APPROVED_ACTIONS.json"

# The only places the worker may write without an explicit approval file.
DEFAULT_WRITE_ROOTS = [HANDOFFS_DIR, WORKFLOWS_DIR, RUNS_DIR, EVIDENCE_DIR]

# Verified memory sources surfaced as compact pointers (read-only).
MEMORY_POINTER_SOURCES = [
    "14_context/compact_memory/generated/ghoti_status_short.md",
    "14_context/compact_memory/current_working_summary.md",
    "14_context/compact_memory/next_exact_step.md",
    "14_context/obsidian_vault/00_Index.md",
]

# Directories the memory search may scan (all repo-local markdown).
SEARCH_ROOTS = [
    "14_context/compact_memory",
    "14_context/obsidian_vault",
    "14_context/repo_knowledge/generated",
    "docs",
]

_TERM_RE = re.compile(r"^[A-Za-z0-9 _.\-]{1,64}$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _ascii(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def _approved_extra_roots() -> list[Path]:
    """Extra output roots the human approved; repo-local only, never default."""
    try:
        data = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    roots: list[Path] = []
    for entry in data.get("allow_output_dirs", []):
        candidate = (REPO_ROOT / str(entry)).resolve()
        try:
            candidate.relative_to(REPO_ROOT)
        except ValueError:
            continue  # outside the repo is never approvable here
        roots.append(candidate)
    return roots


def _is_allowed_write(path: Path) -> bool:
    resolved = path.resolve()
    for root in DEFAULT_WRITE_ROOTS + _approved_extra_roots():
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False


def _write_text(path: Path, content: str) -> dict:
    if not _is_allowed_write(path):
        return {"written": False, "path": _rel(path),
                "refused": "path outside the worker's allowed output folders"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_ascii(content), encoding="utf-8")
    return {"written": True, "path": _rel(path), "refused": None}


def read_memory_pointers() -> list[dict]:
    """Compact pointers into verified memory sources: path, line, snippet."""
    pointers: list[dict] = []
    for rel_path in MEMORY_POINTER_SOURCES:
        source = REPO_ROOT / rel_path
        if not source.is_file():
            continue
        try:
            for line_no, line in enumerate(
                    source.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                stripped = line.strip()
                if stripped and not stripped.startswith("---"):
                    pointers.append({"path": rel_path, "line": line_no,
                                     "snippet": _ascii(stripped[:160])})
                    break
        except OSError:
            continue
    return pointers


def search_memory(term: str, limit: int = 20) -> dict:
    """Case-insensitive substring search over verified local markdown sources.

    Returns compact source pointers (repo-relative path, line, snippet) -
    never file bodies - so results stay safe to embed in handoffs.
    """
    if not _TERM_RE.match(term or ""):
        return {"ok": False, "term": term, "hits": [],
                "error": "term must be 1-64 chars of letters, digits, space, _ . -"}
    needle = term.lower()
    hits: list[dict] = []
    for root_rel in SEARCH_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.is_dir():
            continue
        for md_file in sorted(root.rglob("*.md")):
            if len(hits) >= limit:
                break
            try:
                lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if needle in line.lower():
                    hits.append({"path": _rel(md_file), "line": line_no,
                                 "snippet": _ascii(line.strip()[:160])})
                    break  # one pointer per file keeps results compact
    return {"ok": True, "term": term, "hit_count": len(hits), "hits": hits,
            "sources_scanned": SEARCH_ROOTS, "limit": limit}


def run_suggestion(workflow_id: str, generated_at: str | None = None,
                   branch: str = "unknown") -> dict:
    """Read memory + a template, write a proposed plan/handoff. Suggestion only."""
    template = workflow_templates.get_template(workflow_id)
    if template is None:
        return {"ok": False, "workflow": workflow_id, "error": "unknown workflow id"}
    stamp = generated_at or _now()
    pointers = read_memory_pointers()
    keyword = template["title"].split(" ")[0].lower()
    related = search_memory(keyword, limit=5)

    plan_md = workflow_templates.render_plan_markdown(
        workflow_id, stamp, branch, memory_pointers=pointers)
    suggestion_lines = [
        plan_md,
        "## Worker suggestion (no command was executed)",
        "",
        "The local worker read the sources above and proposes the steps in",
        "this packet. It executed nothing: no shell command, no network call,",
        "no file edit outside 14_context/agent_os/. A human must review this",
        "suggestion and run any live step manually.",
        "",
        "Related memory hits for '%s': %d" % (keyword, related.get("hit_count", 0)),
        "",
    ]
    for hit in related.get("hits", []):
        suggestion_lines.append("- `%s:%s` %s" % (hit["path"], hit["line"], hit["snippet"]))
    suggestion_md = "\n".join(suggestion_lines) + "\n"

    base = "worker_suggestion_%s_%s" % (workflow_id.replace("-", "_"), stamp)
    md_result = _write_text(HANDOFFS_DIR / (base + ".md"), suggestion_md)
    payload = {
        "ok": md_result["written"],
        "action": "worker-suggest",
        "workflow": workflow_id,
        "mode": "suggestion_only",
        "generated_at": stamp,
        "memory_pointers": pointers,
        "related_hits": related.get("hits", []),
        "suggestion_path": md_result["path"] if md_result["written"] else None,
        "refused": md_result["refused"],
        "executed_commands": [],
        "safety": {
            "subprocess_used": False,
            "network_used": False,
            "writes_outside_agent_os": False,
            "human_approval_required": True,
        },
    }
    json_result = _write_text(HANDOFFS_DIR / (base + ".json"),
                              json.dumps(payload, indent=2) + "\n")
    payload["suggestion_json_path"] = json_result["path"] if json_result["written"] else None
    return payload


def build_handoffs(workflow_id: str | None = None, generated_at: str | None = None,
                   branch: str = "unknown") -> dict:
    """Write copy-paste handoff packets for Claude, Codex, and Hermes."""
    stamp = generated_at or _now()
    template = workflow_templates.get_template(workflow_id) if workflow_id else None
    subject = template["title"] if template else "Ghoti Agent OS status"
    context_lines = ["Memory pointers:"] + [
        "- %s:%s %s" % (p["path"], p["line"], p["snippet"])
        for p in read_memory_pointers()
    ]
    packets = {
        "claude": [
            "# Claude Code Prompt - %s" % subject,
            "",
            "Generated: %s" % stamp,
            "Branch: %s" % branch,
            "",
            "---",
            "",
            "Implementation lane. Work only inside the planned file ownership.",
            "",
        ] + context_lines + [
            "",
            "Human copy-paste required: YES",
            "relay_mode: copy_paste_only",
        ],
        "codex": [
            "# Codex Prompt - audit %s" % subject,
            "",
            "Generated: %s" % stamp,
            "Branch: %s" % branch,
            "",
            "---",
            "",
            "Audit lane. Verify the implementation against its brief; report",
            "findings only, change nothing.",
            "",
        ] + context_lines + [
            "",
            "Human copy-paste required: YES",
            "relay_mode: copy_paste_only",
        ],
        "hermes": [
            "# Hermes Note - %s" % subject,
            "",
            "Generated: %s" % stamp,
            "Branch: %s" % branch,
            "",
            "---",
            "",
            "Coordinator status note for the agent handoff vault. Read-only",
            "context; route via the existing hermes_router wrappers.",
            "",
        ] + context_lines + [
            "",
            "Human copy-paste required: YES",
            "relay_mode: copy_paste_only",
        ],
    }
    written: dict[str, str | None] = {}
    all_ok = True
    for target, lines in packets.items():
        name = "handoff_%s_%s%s.md" % (
            target, ("%s_" % workflow_id.replace("-", "_")) if workflow_id else "", stamp)
        result = _write_text(HANDOFFS_DIR / name, "\n".join(lines) + "\n")
        written[target] = result["path"] if result["written"] else None
        all_ok = all_ok and result["written"]
    return {
        "ok": all_ok,
        "action": "build-handoff",
        "workflow": workflow_id,
        "mode": "suggestion_only",
        "generated_at": stamp,
        "packets": written,
        "relay_mode": "copy_paste_only",
        "autonomous_launch": False,
        "human_approval_required": True,
    }
