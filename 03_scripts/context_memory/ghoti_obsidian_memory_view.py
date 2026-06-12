#!/usr/bin/env python3
"""Build deterministic Obsidian views over Ghoti's source-linked memory.

The views are navigation pages only. They never replace canonical source files,
call a model or provider, use the network, launch Obsidian, or execute commands.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import posixpath
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"
SOURCE_INDEX_PATHS = (
    "14_context/memory/index/raw_index.json",
    "14_context/memory/index/handoff_index.json",
)
VIEW_NAMES = (
    "START_HERE.md",
    "CURRENT_STATE.md",
    "NEXT_ACTIONS.md",
    "SAFETY_GATES.md",
    "AGENT_HANDOFFS.md",
)
VIEW_WORD_BUDGETS = {name: 700 for name in VIEW_NAMES}
HASH_MODE = "sha256_canonical_text_lf_binary_raw"
TEXT_HASH_SUFFIXES = frozenset(
    (".css", ".html", ".js", ".json", ".md", ".ps1", ".py", ".toml", ".txt", ".yaml", ".yml")
)
_MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def canonical_file_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_HASH_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w.+/-]+\b", text))


def _ascii_text(text: str) -> str:
    replacements = {"\ufeff": "", "\u2013": "-", "\u2014": "-", "\u2192": "->", "\u2194": "<->"}
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _load_indexes(repo_root: Path) -> tuple[dict, dict]:
    raw_path = repo_root / SOURCE_INDEX_PATHS[0]
    handoff_path = repo_root / SOURCE_INDEX_PATHS[1]
    return (
        json.loads(raw_path.read_text(encoding="utf-8")),
        json.loads(handoff_path.read_text(encoding="utf-8")),
    )


def _link(repo_relative_path: str, label: str | None = None) -> str:
    target = posixpath.relpath(repo_relative_path, "14_context/memory/obsidian")
    return f"[{label or repo_relative_path}]({target})"


def _header(title: str, raw_state: str, handoff_state: str) -> list[str]:
    return [
        "---",
        "memory_view: generated_pointer",
        "canonical_truth: false",
        "local_only: true",
        f"raw_state_sha256: {raw_state}",
        f"handoff_state_sha256: {handoff_state}",
        "---",
        "",
        f"# {title}",
        "",
        "> Generated Obsidian-compatible pointer view; not canonical truth. Follow source links and hashes.",
        "",
    ]


def _source_bullets(raw_index: dict, categories: set[str], limit: int = 10) -> list[str]:
    lines = []
    for source in raw_index.get("sources", []):
        if source.get("category") not in categories:
            continue
        lines.append(f"- {_link(source['path'])} - SHA-256 `{source['sha256']}`")
        if len(lines) >= limit:
            break
    return lines or ["- No reviewed sources are currently indexed for this view."]


def render_views(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    raw, handoff = _load_indexes(repo_root)
    raw_state = raw.get("source_state_sha256", "missing")
    handoff_state = handoff.get("handoff_state_sha256", "missing")

    start = _header("Ghoti Shared Memory - Start Here", raw_state, handoff_state)
    start.extend(
        [
            "This folder is a human-friendly dashboard over Ghoti's deterministic memory indexes.",
            "Open only the linked source files needed for the current task; durable source files win on conflict.",
            "",
            "## Navigation",
            "",
            "- [Current State](CURRENT_STATE.md)",
            "- [Next Actions](NEXT_ACTIONS.md)",
            "- [Safety Gates](SAFETY_GATES.md)",
            "- [Agent Handoffs](AGENT_HANDOFFS.md)",
            f"- {_link('14_context/memory/generated/context_map.md', 'Full Context Map')}",
            f"- {_link('14_context/memory/generated/latest_state.md', 'Latest State Pointer')}",
            f"- {_link('14_context/memory/README.md', 'Memory Contract')}",
            "",
            "## Operating Rule",
            "",
            "Use these pages for navigation, not as authority. Verify linked hashes before relying on cached context.",
            "No model output, handoff packet, or Obsidian note authorizes commands or live actions.",
            "",
        ]
    )

    current = _header("Current State Pointer", raw_state, handoff_state)
    current.extend(
        [
            f"- {_link('14_context/memory/generated/latest_state.md', 'Latest State Pointer')}",
            f"- {_link('14_context/memory/generated/context_map.md', 'Context Memory Map')}",
            f"- {_link(SOURCE_INDEX_PATHS[0], 'Raw Source Index')}",
            f"- Reviewed source count: {raw.get('source_count', 0)}",
            f"- Published handoff packets: {handoff.get('packet_count', 0)}",
            f"- Inbox deliveries: {handoff.get('delivery_count', 0)}",
            "- Local only: true",
            "- Network/model/live actions used: false",
            "",
            "## Highest-Priority Source Pointers",
            "",
            *_source_bullets(raw, {"stable_truth", "compact_state"}, 8),
            "",
        ]
    )

    next_actions = _header("Next Actions Pointer", raw_state, handoff_state)
    next_actions.extend(
        [
            "Use reviewed next-action and blocker sources first. Open the newest handoff packet only as evidence.",
            "",
            "## Reviewed Next-Action Sources",
            "",
            *_source_bullets(raw, {"next_action", "blockers"}, 8),
            "",
            "## Published Handoff Packets",
            "",
        ]
    )
    for packet in handoff.get("packets", []):
        next_actions.append(
            f"- {_link('14_context/memory/' + packet['path'], packet['packet_id'])} "
            f"- agent `{packet['agent_name']}` - SHA-256 `{packet['sha256']}`"
        )
    if not handoff.get("packets"):
        next_actions.append("- No published handoff packets.")
    next_actions.extend(["", "Human review is required before promoting any recommendation.", ""])

    safety = _header("Safety Gates Pointer", raw_state, handoff_state)
    safety.extend(
        [
            "Human approval remains required for every risky or live action.",
            "",
            "## Always Blocked From Memory Views",
            "",
            "- Command execution or model-output-to-command loops",
            "- Secrets, tokens, cookies, auth files, browser sessions, or private memory",
            "- Account actions, email sending, posting, purchases, trading, or destructive actions",
            "- Uncontrolled agent launches, live browser control, or OS click/type",
            "- Treating generated views or vector search as canonical truth",
            "",
            "## Reviewed Safety Sources",
            "",
            *_source_bullets(raw, {"safety"}, 12),
            "",
        ]
    )

    handoffs = _header("Shared Agent Handoffs", raw_state, handoff_state)
    handoffs.extend(
        [
            f"- {_link(SOURCE_INDEX_PATHS[1], 'Handoff Index')}",
            f"- Published packets: {handoff.get('packet_count', 0)}",
            f"- Inbox deliveries: {handoff.get('delivery_count', 0)}",
            "- Commands inside packets are evidence only and are never executed.",
            "",
            "## Packets",
            "",
        ]
    )
    for packet in handoff.get("packets", []):
        handoffs.append(
            f"- {_link('14_context/memory/' + packet['path'], packet['packet_id'])} "
            f"- `{packet['agent_name']}` - SHA-256 `{packet['sha256']}`"
        )
    if not handoff.get("packets"):
        handoffs.append("- None")
    handoffs.extend(["", "## Deliveries", ""])
    for delivery in handoff.get("deliveries", []):
        handoffs.append(
            f"- {_link('14_context/memory/' + delivery['path'], delivery['delivery_id'])} "
            f"- recipient `{delivery['recipient_agent']}` - SHA-256 `{delivery['sha256']}`"
        )
    if not handoff.get("deliveries"):
        handoffs.append("- None")
    handoffs.append("")

    views = {
        "START_HERE.md": "\n".join(start),
        "CURRENT_STATE.md": "\n".join(current),
        "NEXT_ACTIONS.md": "\n".join(next_actions),
        "SAFETY_GATES.md": "\n".join(safety),
        "AGENT_HANDOFFS.md": "\n".join(handoffs),
    }
    rendered = {name: _ascii_text(text.rstrip() + "\n") for name, text in views.items()}
    for name, text in rendered.items():
        if word_count(text) > VIEW_WORD_BUDGETS[name]:
            raise ValueError(f"{name} exceeds word budget")
    return rendered


def build_view_index(repo_root: Path = REPO_ROOT) -> dict:
    raw, handoff = _load_indexes(repo_root)
    views = render_views(repo_root)
    source_indexes = [
        {"path": path, "sha256": sha256_file(repo_root / path)}
        for path in SOURCE_INDEX_PATHS
    ]
    indexed_views = [
        {
            "path": f"obsidian/{name}",
            "sha256": sha256_text(views[name]),
            "words": word_count(views[name]),
        }
        for name in VIEW_NAMES
    ]
    state_material = "\n".join(
        [*(f"{item['path']}:{item['sha256']}" for item in source_indexes), *(f"{item['path']}:{item['sha256']}" for item in indexed_views)]
    )
    return {
        "schema_version": "1.0",
        "memory_type": "obsidian_generated_pointer_view_index",
        "hash_mode": HASH_MODE,
        "generated_at": None,
        "generated_at_source": "not_recorded_for_deterministic_output",
        "source_state_sha256": raw.get("source_state_sha256"),
        "handoff_state_sha256": handoff.get("handoff_state_sha256"),
        "obsidian_view_state_sha256": hashlib.sha256(state_material.encode("utf-8")).hexdigest(),
        "local_only": True,
        "canonical_truth": False,
        "network_used": False,
        "model_used": False,
        "live_actions_enabled": False,
        "private_workspace_state_committed": False,
        "view_count": len(indexed_views),
        "source_indexes": source_indexes,
        "views": indexed_views,
    }


def expected_output_paths() -> list[str]:
    return [
        *(f"14_context/memory/obsidian/{name}" for name in VIEW_NAMES),
        "14_context/memory/index/obsidian_view_index.json",
    ]


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
            raise OSError(f"safe data-only write fallback failed for {path.name}: {result.stderr.strip()}")


def write_views(repo_root: Path = REPO_ROOT, output_root: Path = MEMORY_ROOT, allowed_root: Path | None = None) -> list[Path]:
    root = _safe_output_root(output_root, allowed_root or MEMORY_ROOT)
    views = render_views(repo_root)
    index = build_view_index(repo_root)
    written = []
    for name in VIEW_NAMES:
        path = root / "obsidian" / name
        _safe_write_text(path, views[name])
        written.append(path)
    index_path = root / "index" / "obsidian_view_index.json"
    _safe_write_text(index_path, json.dumps(index, indent=2, sort_keys=True) + "\n")
    written.append(index_path)
    return written


def verify_view_index(memory_root: Path, index: dict) -> dict:
    root = memory_root.resolve()
    mismatches = []
    for item in index.get("views", []):
        path = root / item["path"]
        actual = sha256_file(path) if path.is_file() else None
        if actual != item["sha256"]:
            mismatches.append({"path": item["path"], "expected": item["sha256"], "actual": actual})
    return {"ok": not mismatches, "mismatches": mismatches, "verified_views": len(index.get("views", []))}


def verify_rendered_links(repo_root: Path, views: dict[str, str]) -> dict:
    virtual_views = {(repo_root / "14_context" / "memory" / "obsidian" / name).resolve() for name in views}
    missing = []
    checked = 0
    for name, text in views.items():
        source = repo_root / "14_context" / "memory" / "obsidian" / name
        for target in _MARKDOWN_LINK_RE.findall(text):
            checked += 1
            if "://" in target or target.startswith(("/", "\\")):
                missing.append({"view": name, "target": target, "reason": "non-local link"})
                continue
            resolved = (source.parent / target.split("#", 1)[0]).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                missing.append({"view": name, "target": target, "reason": "escapes repo"})
                continue
            if not resolved.is_file() and resolved not in virtual_views:
                missing.append({"view": name, "target": target, "reason": "missing"})
    return {
        "ok": not missing,
        "checked_links": checked,
        "missing": missing,
        "network_links_allowed": False,
    }


def _verify_source_indexes(repo_root: Path, raw: dict, handoff: dict) -> dict:
    mismatches = []
    for source in raw.get("sources", []):
        path = repo_root / source["path"]
        actual = sha256_file(path) if path.is_file() else None
        if actual != source["sha256"]:
            mismatches.append({"path": source["path"], "expected": source["sha256"], "actual": actual})
    memory_root = repo_root / "14_context" / "memory"
    for item in [*handoff.get("packets", []), *handoff.get("deliveries", [])]:
        path = memory_root / item["path"]
        actual = sha256_file(path) if path.is_file() else None
        if actual != item["sha256"]:
            mismatches.append({"path": f"14_context/memory/{item['path']}", "expected": item["sha256"], "actual": actual})
    return {"ok": not mismatches, "mismatches": mismatches}


def check(repo_root: Path = REPO_ROOT) -> dict:
    raw, handoff = _load_indexes(repo_root)
    views = render_views(repo_root)
    links = verify_rendered_links(repo_root, views)
    sources = _verify_source_indexes(repo_root, raw, handoff)
    expected = build_view_index(repo_root)
    memory_root = repo_root / "14_context" / "memory"
    missing = [path for path in expected_output_paths() if not (repo_root / path).is_file()]
    drift = []
    for name, content in views.items():
        path = memory_root / "obsidian" / name
        if path.is_file() and sha256_file(path) != sha256_text(content):
            drift.append(f"14_context/memory/obsidian/{name}")
    index_path = memory_root / "index" / "obsidian_view_index.json"
    if index_path.is_file() and json.loads(index_path.read_text(encoding="utf-8")) != expected:
        drift.append("14_context/memory/index/obsidian_view_index.json")
    return {
        "ok": links["ok"] and sources["ok"] and not missing and not drift,
        "milestone": "N+6.42C",
        "view_count": len(views),
        "checked_links": links["checked_links"],
        "source_indexes_verified": sources["ok"],
        "missing": missing,
        "drift": drift,
        "local_only": True,
        "canonical_truth": False,
        "network_used": False,
        "model_used": False,
        "live_actions_enabled": False,
        "private_workspace_state_committed": False,
        "next_milestone": "N+6.43A Optional Local Embedding/Search Trial",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="check committed Obsidian views and source indexes")
    action.add_argument("--write", action="store_true", help="write deterministic repo-local Obsidian views")
    action.add_argument("--verify", action="store_true", help="verify the committed view index and links")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        if args.check:
            payload = check(REPO_ROOT)
        elif args.write:
            written = write_views(REPO_ROOT, MEMORY_ROOT, MEMORY_ROOT)
            payload = {
                "ok": True,
                "written": [path.relative_to(REPO_ROOT).as_posix() for path in written],
                "local_only": True,
                "canonical_truth": False,
                "network_used": False,
                "model_used": False,
                "live_actions_enabled": False,
                "private_workspace_state_committed": False,
            }
        else:
            index_path = MEMORY_ROOT / "index" / "obsidian_view_index.json"
            if not index_path.is_file():
                raise FileNotFoundError("Obsidian view index missing; run --write first")
            index = json.loads(index_path.read_text(encoding="utf-8"))
            views = {name: (MEMORY_ROOT / "obsidian" / name).read_text(encoding="utf-8") for name in VIEW_NAMES}
            verify = verify_view_index(MEMORY_ROOT, index)
            links = verify_rendered_links(REPO_ROOT, views)
            payload = {
                "ok": verify["ok"] and links["ok"],
                **verify,
                "checked_links": links["checked_links"],
                "missing_links": links["missing"],
                "local_only": True,
                "canonical_truth": False,
                "network_used": False,
                "model_used": False,
                "live_actions_enabled": False,
                "private_workspace_state_committed": False,
            }
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as exc:
        payload = {
            "ok": False,
            "error": str(exc),
            "local_only": True,
            "canonical_truth": False,
            "network_used": False,
            "model_used": False,
            "live_actions_enabled": False,
        }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
