#!/usr/bin/env python3
"""Build Ghoti's deterministic, source-linked context memory map.

This script reads a reviewed allowlist of repo-local durable memory files. It
never calls a model, network service, or command runner. Source files are
read-only; writes are limited to the repo-local 14_context/memory tree.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"
CONTEXT_MAP_WORD_BUDGET = 1200
LATEST_STATE_WORD_BUDGET = 800

SOURCE_SPECS = [
    {"path": "14_context/00_main_memory/current-state.md", "category": "stable_truth", "priority": 1},
    {"path": "14_context/00_main_memory/local-vs-sync-boundaries.md", "category": "safety", "priority": 1},
    {"path": "14_context/compact_memory/project_state.md", "category": "compact_state", "priority": 1},
    {"path": "14_context/compact_memory/safety_rules.md", "category": "safety", "priority": 1},
    {"path": "14_context/compact_memory/next_exact_step.md", "category": "next_action", "priority": 1},
    {"path": "14_context/compact_memory/blocker_state.md", "category": "blockers", "priority": 1},
    {"path": "14_context/agent_handoff_vault/AGENT_RULES.md", "category": "agent_handoff", "priority": 1},
    {"path": "14_context/agent_handoff_vault/00_Inbox/START_HERE.md", "category": "agent_handoff", "priority": 2},
    {"path": "14_context/agent_handoff_vault/02_Agent_Handoffs/CURRENT_TASK.md", "category": "agent_handoff", "priority": 1},
    {"path": "14_context/agent_handoff_vault/04_Logs/CLAUDE_LAST_RUN.md", "category": "run_record", "priority": 2},
    {"path": "14_context/agent_handoff_vault/04_Logs/CODEX_LAST_AUDIT.md", "category": "run_record", "priority": 2},
    {"path": "14_context/obsidian_vault/00_Index.md", "category": "obsidian_view", "priority": 2},
    {"path": "14_context/obsidian_vault/01_Current_State.md", "category": "obsidian_view", "priority": 2},
    {"path": "14_context/obsidian_vault/02_Next_Actions.md", "category": "obsidian_view", "priority": 2},
    {"path": "14_context/obsidian_vault/06_Safety_Gates.md", "category": "safety", "priority": 2},
]

_PRIVATE_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.I),
    re.compile(r"/mnt/[a-z]/Users/", re.I),
    re.compile(r"/home/[^/\s]+/", re.I),
]
_SECRET_VALUE_PATTERNS = [
    re.compile(r"\b(?:OPENAI|ANTHROPIC|GEMINI|GOOGLE|TELEGRAM|GITHUB)_?[A-Z_]*(?:KEY|TOKEN|SECRET)\s*=\s*\S+", re.I),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}", re.I),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}", re.I),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", re.I),
]
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w.+/-]+\b", text))


def is_summary_safe(text: str) -> bool:
    return not any(pattern.search(text) for pattern in [*_PRIVATE_PATH_PATTERNS, *_SECRET_VALUE_PATTERNS])


def _ascii_text(text: str) -> str:
    replacements = {
        "\ufeff": "",
        "\u2013": "-",
        "\u2014": "-",
        "\u2192": "->",
        "\u2194": "<->",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _repo_relative_path(root: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"source path must be repo-relative: {raw_path}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"source path escapes repo root: {raw_path}") from exc
    return resolved


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return _ascii_text(stripped[2:].strip())[:100]
    return _ascii_text(fallback)


def _highlights(text: str, limit: int = 3) -> list[str]:
    if not is_summary_safe(text):
        return []
    result: list[str] = []
    inside_frontmatter = False
    for raw in text.splitlines():
        line = raw.strip()
        if line == "---":
            inside_frontmatter = not inside_frontmatter
            continue
        if inside_frontmatter or not line or line.startswith(("#", "```", ">")):
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        if len(line) < 12 or "`" in line or not is_summary_safe(line):
            continue
        result.append(_ascii_text(line[:220]))
        if len(result) >= limit:
            break
    return result


def build_raw_index(repo_root: Path = REPO_ROOT, source_specs: list[dict] | None = None) -> dict:
    root = repo_root.resolve()
    specs = source_specs if source_specs is not None else SOURCE_SPECS
    sources: list[dict] = []
    for spec in sorted(specs, key=lambda item: (item["priority"], item["category"], item["path"])):
        path = _repo_relative_path(root, spec["path"])
        if not path.is_file():
            raise FileNotFoundError(spec["path"])
        text = path.read_text(encoding="utf-8", errors="replace")
        digest = sha256_file(path)
        summary_safe = is_summary_safe(text)
        sources.append(
            {
                "path": Path(spec["path"]).as_posix(),
                "category": spec["category"],
                "priority": spec["priority"],
                "sha256": digest,
                "bytes": path.stat().st_size,
                "summary_safe": summary_safe,
                "title": _title(text, Path(spec["path"]).name) if summary_safe else Path(spec["path"]).name,
                "highlights": _highlights(text) if summary_safe else [],
            }
        )
    state_material = "\n".join(f"{source['path']}:{source['sha256']}" for source in sources)
    return {
        "schema_version": "1.0",
        "memory_type": "source_linked_pointer_index",
        "generated_at": None,
        "generated_at_source": "not_recorded_for_deterministic_output",
        "source_state_sha256": hashlib.sha256(state_material.encode("utf-8")).hexdigest(),
        "local_only": True,
        "read_only_sources": True,
        "canonical_truth": False,
        "live_actions_enabled": False,
        "network_used": False,
        "model_used": False,
        "source_count": len(sources),
        "sources": sources,
    }


def _context_map(index: dict) -> str:
    handoff_index_path = MEMORY_ROOT / "index" / "handoff_index.json"
    handoff_index = json.loads(handoff_index_path.read_text(encoding="utf-8")) if handoff_index_path.is_file() else {}
    lines = [
        "# Ghoti Context Memory Map",
        "",
        "> Generated pointer layer; not canonical truth. Durable source files win on conflict.",
        "",
        f"- Source state SHA-256: `{index['source_state_sha256']}`",
        f"- Generated at: `{index['generated_at'] or 'not recorded'}` from `{index['generated_at_source']}`",
        f"- Reviewed sources: {index['source_count']}",
        "- Local only: true",
        "- Source files read only: true",
        "- Network/model/live actions used: false",
        "",
        "## Shared Agent Handoffs",
        "",
        f"- Index: `14_context/memory/index/handoff_index.json` - SHA-256 `{sha256_file(handoff_index_path) if handoff_index_path.is_file() else 'missing'}`",
        f"- Published packets: {handoff_index.get('packet_count', 0)}",
        f"- Inbox deliveries: {handoff_index.get('delivery_count', 0)}",
        "- Commands in packets are evidence only and are never executed.",
        "",
    ]
    categories = sorted({source["category"] for source in index["sources"]})
    for category in categories:
        lines.extend([f"## {category.replace('_', ' ').title()}", ""])
        for source in [item for item in index["sources"] if item["category"] == category]:
            status = "summary-safe" if source["summary_safe"] else "metadata-only"
            lines.append(
                f"- [`{source['path']}`](../../{source['path'].removeprefix('14_context/')}) "
                f"- `{status}` - SHA-256 `{source['sha256']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Rules",
            "",
            "- Raw and durable source files are never deleted or overwritten by this generator.",
            "- Every generated claim must remain traceable to a repo-relative source path and SHA-256 hash.",
            "- Metadata-only sources contain content that must not be copied into generated summaries.",
            "- Vector search may help discovery later, but it is never canonical truth.",
            "- Model output never authorizes commands or live actions.",
            "",
        ]
    )
    text = "\n".join(lines)
    if word_count(text) > CONTEXT_MAP_WORD_BUDGET:
        raise ValueError("context map exceeds word budget")
    return _ascii_text(text)


def _latest_state(index: dict) -> str:
    handoff_index_path = MEMORY_ROOT / "index" / "handoff_index.json"
    handoff_index = json.loads(handoff_index_path.read_text(encoding="utf-8")) if handoff_index_path.is_file() else {}
    lines = [
        "# Ghoti Latest State Pointer",
        "",
        "> Generated source-linked startup context; not canonical truth.",
        "",
        "## Safety Truth",
        "",
        "- Local-only memory indexing.",
        "- No network, provider, model, browser, account, money, posting, or live-agent action.",
        "- Source files are read-only and remain authoritative.",
        "- Human approval remains required for risky or live actions.",
        "",
        "## Shared agent handoffs",
        "",
        f"- Published packets: {handoff_index.get('packet_count', 0)}",
        f"- Inbox deliveries: {handoff_index.get('delivery_count', 0)}",
        "- Sender outboxes are immutable; recipient inboxes contain hash-linked read-only pointers.",
        "- Commands are evidence only and are never executed.",
        "",
        "## Source-linked highlights",
        "",
        "These are review-required excerpts, not validated current truth.",
        "",
    ]
    highlighted = 0
    for source in index["sources"]:
        if not source["highlights"]:
            continue
        lines.append(f"### {source['title']}")
        lines.append("")
        lines.append(f"Source: `{source['path']}` - SHA-256 `{source['sha256']}`")
        lines.append("")
        lines.extend(f"- {highlight}" for highlight in source["highlights"])
        lines.append("")
        highlighted += 1
        if highlighted >= 7:
            break
    lines.extend(
        [
            "## Startup sequence",
            "",
            "1. Read this pointer.",
            "2. Open only the linked source files needed for the task.",
            "3. Verify source hashes before trusting a cached summary.",
            "4. Record blockers and evidence in a reviewed handoff packet.",
            "5. Never execute model output directly.",
            "",
            f"Source state SHA-256: `{index['source_state_sha256']}`",
            "",
        ]
    )
    text = "\n".join(lines)
    if word_count(text) > LATEST_STATE_WORD_BUDGET:
        raise ValueError("latest state exceeds word budget")
    return _ascii_text(text)


def render_outputs(index: dict) -> dict[str, str]:
    return {
        "context_map.md": _context_map(index),
        "latest_state.md": _latest_state(index),
    }


def _safe_output_root(output_root: Path, allowed_root: Path | None = None) -> Path:
    if ".." in output_root.parts:
        raise ValueError("output path may not contain parent traversal")
    resolved = output_root.resolve()
    if allowed_root is not None:
        try:
            resolved.relative_to(allowed_root.resolve())
        except ValueError as exc:
            raise ValueError("output path must stay inside the memory root") from exc
    return resolved


def _safe_write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path), encoded],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise OSError(f"safe write fallback failed for {path.name}: {result.stderr.strip()}")


def write_outputs(index: dict, output_root: Path = MEMORY_ROOT, allowed_root: Path | None = None) -> list[Path]:
    root = _safe_output_root(output_root, allowed_root or MEMORY_ROOT)
    generated_dir = root / "generated"
    index_dir = root / "index"
    rendered = render_outputs(index)
    paths = [
        generated_dir / "context_map.md",
        generated_dir / "latest_state.md",
        index_dir / "raw_index.json",
    ]
    _safe_write_text(paths[0], rendered["context_map.md"])
    _safe_write_text(paths[1], rendered["latest_state.md"])
    _safe_write_text(paths[2], json.dumps(index, indent=2, sort_keys=True) + "\n")
    return paths


def verify_index(repo_root: Path, index: dict) -> dict:
    mismatches = []
    for source in index.get("sources", []):
        path = _repo_relative_path(repo_root.resolve(), source["path"])
        actual = sha256_file(path) if path.is_file() else None
        if actual != source["sha256"]:
            mismatches.append({"path": source["path"], "expected": source["sha256"], "actual": actual})
    return {"ok": not mismatches, "mismatches": mismatches, "verified_sources": len(index.get("sources", []))}


def check() -> dict:
    index = build_raw_index()
    outputs = render_outputs(index)
    return {
        "ok": True,
        "milestone": "N+6.42A",
        "source_count": index["source_count"],
        "source_state_sha256": index["source_state_sha256"],
        "context_map_words": word_count(outputs["context_map.md"]),
        "latest_state_words": word_count(outputs["latest_state.md"]),
        "local_only": True,
        "read_only_sources": True,
        "network_used": False,
        "model_used": False,
        "live_actions_enabled": False,
        "next_milestone": "N+6.42B Shared Agent Handoff Inbox/Outbox",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="validate the reviewed source registry and budgets")
    action.add_argument("--write", action="store_true", help="write repo-local generated memory outputs")
    action.add_argument("--verify", action="store_true", help="verify the committed raw index against current sources")
    action.add_argument("--index-json", action="store_true", help="print the current raw index without writing")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if args.check:
        payload = check()
    elif args.index_json:
        payload = build_raw_index()
    elif args.write:
        index = build_raw_index()
        written = write_outputs(index, MEMORY_ROOT, MEMORY_ROOT)
        payload = {
            "ok": True,
            "written": [path.relative_to(REPO_ROOT).as_posix() for path in written],
            "source_count": index["source_count"],
            "source_state_sha256": index["source_state_sha256"],
            "local_only": True,
            "read_only_sources": True,
            "network_used": False,
            "model_used": False,
            "live_actions_enabled": False,
        }
    else:
        index_path = MEMORY_ROOT / "index" / "raw_index.json"
        if not index_path.is_file():
            payload = {"ok": False, "error": "raw index missing; run --write first"}
        else:
            payload = verify_index(REPO_ROOT, json.loads(index_path.read_text(encoding="utf-8")))

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
