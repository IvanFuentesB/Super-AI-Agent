#!/usr/bin/env python3
"""Build compact Ghoti context packs for local memory handoff.

N+5.5A adds a deterministic, repo-local way to summarize the current Ghoti
truth into small files Ivan can paste into ChatGPT, Codex, Claude, or Obsidian.

No external API calls. No provider setup. No token reading. No live account
actions. The default output stays under 14_context/compact_memory/generated/.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap
from typing import Dict, Iterable, List


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
GENERATED_DIR = REPO_ROOT / "14_context" / "compact_memory" / "generated"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
LATEST_CLEAN_MILESTONE = "N+5.7B - Repo Knowledge Context Retrieval landed on main"
CURRENT_MILESTONE = "N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness"
NEXT_RECOMMENDED_MILESTONE = "N+5.9A - Real Gemma Install/Model Availability Decision + Local Task Quality Evaluation"
REPO_KNOWLEDGE_DIR = REPO_ROOT / "14_context" / "repo_knowledge" / "generated"
HERMES_WORKFLOW_DIR = REPO_ROOT / "14_context" / "hermes_workflow" / "generated"
REPO_MAP_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-map --json"
REPO_BUNDLE_NEXT_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json"
HERMES_BRIDGE_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json"
HERMES_BRIDGE_WRITE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json"

OUTPUT_FILES = {
    "ghoti_current_context_pack.md": "context_pack_markdown",
    "ghoti_current_context_pack.json": "context_pack_json",
    "ghoti_codex_next_prompt.md": "codex_next_prompt",
    "ghoti_chatgpt_migration_summary.md": "chatgpt_migration_summary",
    "ghoti_status_short.md": "status_short",
}

FORBIDDEN_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY"),
    re.compile(r"TELEGRAM_BOT_TOKEN\s*=\s*[^<\s]"),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*[^<\s]"),
    re.compile(r"OPENAI_API_KEY\s*=\s*[^<\s]"),
]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, timeout=timeout)


def _is_inside_repo(path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _resolve_output_dir(value: str | None) -> pathlib.Path:
    if not value:
        return GENERATED_DIR
    candidate = pathlib.Path(value)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if not _is_inside_repo(resolved):
        raise ValueError("output-dir must stay inside the repo root")
    return resolved


def _repo_rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _git_rev(ref: str) -> str:
    try:
        completed = _run(["git", "rev-parse", ref], timeout=10)
    except Exception:
        return "unknown"
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _current_main_hash() -> str:
    main_hash = _git_rev("origin/main")
    if main_hash != "unknown":
        return main_hash
    return _git_rev("HEAD")


def _read_text_safe(path: pathlib.Path, limit: int = 2000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[:limit]


def _detect_report_kind(name: str) -> str:
    lowered = name.lower()
    if "final_main" in lowered or "main_merge" in lowered:
        return "main"
    if "audit" in lowered:
        return "audit"
    if "product" in lowered or "finish" in lowered or "usability" in lowered:
        return "product"
    return "report"


def _report_rank(name: str) -> List[int]:
    match = re.search(r"codex_n(\d+)_([0-9]+)([a-z]?)", name.lower())
    if not match:
        return [0, 0, 0]
    suffix = match.group(3)
    suffix_rank = (ord(suffix) - ord("a") + 1) if suffix else 0
    return [int(match.group(1)), int(match.group(2)), suffix_rank]


def discover_recent_reports(limit: int = 8) -> List[Dict[str, object]]:
    context_dir = REPO_ROOT / "14_context"
    reports: List[Dict[str, object]] = []
    try:
        candidates = list(context_dir.glob("codex_*.md"))
    except Exception:
        candidates = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        snippet = _read_text_safe(path, limit=1200)
        verdict = "unknown"
        for line in snippet.splitlines():
            cleaned = line.strip()
            if "CLEAN PASS" in cleaned or cleaned.startswith("Final verdict"):
                verdict = cleaned.replace("#", "").strip()
                break
        reports.append({
            "path": _repo_rel(path),
            "name": path.name,
            "kind": _detect_report_kind(path.name),
            "rank": _report_rank(path.name),
            "modified_unix": int(stat.st_mtime),
            "verdict_hint": verdict,
        })
    reports.sort(key=lambda item: (item["rank"], item["modified_unix"], item["name"]), reverse=True)
    return reports[:limit]


def _probe_ollama_truth() -> Dict[str, object]:
    truth = {
        "ollama_available": False,
        "ollama_version": "not_found",
        "gemma_model_found": False,
        "gemma_status": "missing",
        "fallback_mode": "local_demo",
        "status_line": "Ollama not found; Gemma unavailable; local_demo fallback active.",
    }
    try:
        version = _run(["ollama", "--version"], timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return truth
    if version.returncode != 0:
        return truth
    truth["ollama_available"] = True
    truth["ollama_version"] = version.stdout.strip() or "available"
    try:
        models = _run(["ollama", "list"], timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        truth["status_line"] = f"Ollama available ({truth['ollama_version']}); Gemma list unavailable; local_demo fallback active."
        return truth
    model_text = models.stdout.lower() if models.returncode == 0 else ""
    if "gemma" in model_text:
        truth["gemma_model_found"] = True
        truth["gemma_status"] = "installed"
        truth["fallback_mode"] = "ollama_gemma"
        truth["status_line"] = f"Ollama available ({truth['ollama_version']}); Gemma model found."
    else:
        truth["status_line"] = f"Ollama available ({truth['ollama_version']}); Gemma model missing; local_demo fallback active."
    return truth


def _static_truth() -> Dict[str, object]:
    return {
        "launcher_command": LAUNCHER_COMMAND,
        "dashboard_url": DASHBOARD_URL,
        "latest_clean_milestone": LATEST_CLEAN_MILESTONE,
        "current_milestone": CURRENT_MILESTONE,
        "next_recommended_milestone": NEXT_RECOMMENDED_MILESTONE,
        "hermes": {
            "wsl_status": "installed",
            "path": "/home/ai_sandbox/.local/bin/hermes",
            "version": "v0.14.0",
            "browser_playwright": "degraded/not claimed unless separately verified",
            "codex_provider": "pending/not proven",
            "telegram": "manual later/no token",
            "vps": "No VPS",
            "manual_bridge": "available",
            "readiness_percent": 58,
            "status_path": _repo_rel(HERMES_WORKFLOW_DIR / "hermes_workflow_status.md"),
            "skills_index_path": _repo_rel(HERMES_WORKFLOW_DIR / "hermes_skills_index.md"),
            "bridge_packet_path": _repo_rel(HERMES_WORKFLOW_DIR / "hermes_operator_bridge_packet.md"),
            "bridge_status_command": HERMES_BRIDGE_STATUS_COMMAND,
            "bridge_write_command": HERMES_BRIDGE_WRITE_COMMAND,
        },
        "memory": {
            "obsidian_local_memory": "present",
            "generated_dir": _repo_rel(GENERATED_DIR),
            "vault_pattern": "14_context/obsidian_vault/",
            "compact_memory_pattern": "14_context/compact_memory/",
        },
        "repo_knowledge": {
            "status": "available",
            "readiness_percent": 55,
            "generated_dir": _repo_rel(REPO_KNOWLEDGE_DIR),
            "map_path": _repo_rel(REPO_KNOWLEDGE_DIR / "repo_knowledge_map.md"),
            "map_json_path": _repo_rel(REPO_KNOWLEDGE_DIR / "repo_knowledge_map.json"),
            "latest_reports_index_path": _repo_rel(REPO_KNOWLEDGE_DIR / "latest_reports_index.md"),
            "next_milestone_bundle_path": _repo_rel(REPO_KNOWLEDGE_DIR / "task_bundle_next_milestone.md"),
            "codex_prompt_path": _repo_rel(REPO_KNOWLEDGE_DIR / "codex_next_prompt_graph_context.md"),
            "graphify_runtime": "roadmap only/not wired",
            "external_repo_runtime": "not wired",
            "network": "no network",
            "repo_map_command": REPO_MAP_COMMAND,
            "next_bundle_command": REPO_BUNDLE_NEXT_COMMAND,
        },
        "works_now": [
            "Launcher starts the dashboard.",
            "Product Control Center is visible.",
            "Local supervised content demo exists: 8 agents, 100 titles, 100 thumbnails, local preview, no posting.",
            "Public/security audit gates run locally.",
            "Model council scan is local-only.",
            "UI-TARS observation dry-run is available and observation-only.",
            "Adapter dry-run/status is approval-gated and local-only.",
            "External sandbox remains static inspection/planning-only.",
            "Local memory status and fallback are repo-local.",
            "Repo Knowledge / Graphify Lane creates a local file map, latest report index, and task bundles.",
            "Hermes Agent / Manual Bridge exposes safe probes, skills index, manual checklist, and bridge packet.",
            "Reports live under 14_context/.",
        ],
        "pending_manual": [
            "Hermes provider setup.",
            "Hermes Codex provider verification.",
            "Telegram connection.",
            "Real Gemma model availability.",
            "Ruflo runtime/source availability.",
            "External Graphify runtime integration.",
            "Browser/Playwright verification.",
            "Future audited computer-use click/type.",
            "Production public release human review.",
        ],
        "safety_locks": [
            "No bot/captcha/cloak bypass.",
            "No fake engagement.",
            "No spam.",
            "No credential/session scraping.",
            "No autonomous posting.",
            "No autonomous money/trading/legal actions.",
            "No live providers without human approval.",
            "No external repo runtime wiring without approval.",
        ],
    }


def _build_facts(generated_at: str) -> Dict[str, object]:
    facts = _static_truth()
    facts.update({
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "generated_at": generated_at,
        "main_hash": _current_main_hash(),
        "latest_reports": discover_recent_reports(limit=8),
        "local_model_truth": _probe_ollama_truth(),
    })
    return facts


def _report_lines(reports: Iterable[Dict[str, object]]) -> str:
    rows = []
    for report in reports:
        verdict = report.get("verdict_hint") or "unknown"
        rows.append(f"- `{report['path']}` ({report['kind']}): {verdict}")
    return "\n".join(rows) if rows else "- No `14_context/codex_*.md` reports found; regenerate from audit branch if needed."


def _strip_template_indent(text: str) -> str:
    return re.sub(r"^ {8}", "", textwrap.dedent(text), flags=re.MULTILINE).lstrip()


def _render_status_short(facts: Dict[str, object]) -> str:
    main_hash = str(facts["main_hash"])
    model = facts["local_model_truth"]
    return (
        f"Ghoti status: {facts['latest_clean_milestone']} at origin/main "
        f"{main_hash[:12]}. Launch with `{LAUNCHER_COMMAND}` and open {DASHBOARD_URL}. "
        "Hermes WSL is installed at /home/ai_sandbox/.local/bin/hermes (v0.14.0); "
        "browser/Playwright is degraded/not claimed, Codex provider is pending/not proven, "
        "Telegram is manual later/no token, No VPS is in use, and Hermes Agent / Manual Bridge readiness files are available. "
        f"{model['status_line']} Obsidian/local memory is present; UI-TARS is observation-only; "
        "adapters are approval-gated/local-only; external sandbox is static inspection only; "
        "repo knowledge map/task bundles are available with Graphify roadmap only/not wired. "
        f"Next recommended milestone: {NEXT_RECOMMENDED_MILESTONE}."
    )


def _render_context_pack(facts: Dict[str, object], status_short: str) -> str:
    reports = _report_lines(facts["latest_reports"])
    works = "\n".join(f"- {item}" for item in facts["works_now"])
    pending = "\n".join(f"- {item}" for item in facts["pending_manual"])
    locks = "\n".join(f"- {item}" for item in facts["safety_locks"])
    model = facts["local_model_truth"]
    return _strip_template_indent(f"""\
        # Ghoti Current Context Pack

        Generated: `{facts['generated_at']}`

        ## Compact Status

        {status_short}

        ## Current Main

        - Main hash: `{facts['main_hash']}`
        - Latest clean milestone: {facts['latest_clean_milestone']}
        - Current milestone: {facts['current_milestone']}
        - Next recommended milestone: {facts['next_recommended_milestone']}

        ## Launch

        - Launcher command: `{LAUNCHER_COMMAND}`
        - Dashboard URL: `{DASHBOARD_URL}`
        - Context pack command: `python 03_scripts/ghoti_context_pack_builder.py --write --json`
        - Repo map command: `{REPO_MAP_COMMAND}`
        - Next bundle command: `{REPO_BUNDLE_NEXT_COMMAND}`
        - Hermes bridge status: `{HERMES_BRIDGE_STATUS_COMMAND}`
        - Hermes bridge write: `{HERMES_BRIDGE_WRITE_COMMAND}`

        ## What Works Now

        {works}

        ## Pending / Manual

        {pending}

        ## Local Model Truth

        - Ollama available: {str(model['ollama_available']).lower()}
        - Ollama version: {model['ollama_version']}
        - Gemma model found: {str(model['gemma_model_found']).lower()}
        - Gemma status: {model['gemma_status']}
        - Fallback mode: {model['fallback_mode']}
        - Truth line: {model['status_line']}

        ## Hermes / WSL Truth

        - Hermes WSL: installed
        - Hermes path: `/home/ai_sandbox/.local/bin/hermes`
        - Hermes version: v0.14.0
        - Hermes browser/Playwright: degraded/not claimed unless separately verified
        - Codex provider in Hermes: pending/not proven
        - Telegram: manual later/no token
        - No VPS

        ## Hermes Agent / Manual Bridge

        - Hermes workflow readiness: {facts['hermes']['readiness_percent']}%
        - Status file: `{facts['hermes']['status_path']}`
        - Skills index: `{facts['hermes']['skills_index_path']}`
        - Operator bridge packet: `{facts['hermes']['bridge_packet_path']}`
        - Status command: `{facts['hermes']['bridge_status_command']}`
        - Write command: `{facts['hermes']['bridge_write_command']}`
        - Hermes setup remains manual later.
        - Safe probes only; no live provider setup, no provider config, no Telegram setup, no tokens, no browser automation, no live APIs.

        ## Obsidian / Local Memory Truth

        - Obsidian/local memory: present
        - Generated context pack directory: `{facts['memory']['generated_dir']}`
        - Obsidian-compatible vault pattern: `{facts['memory']['vault_pattern']}`
        - Compact memory pattern: `{facts['memory']['compact_memory_pattern']}`
        - This context pack is file-based and does not require Obsidian installation.

        ## Repo Knowledge / Graphify Lane

        - Repo knowledge readiness: {facts['repo_knowledge']['readiness_percent']}%
        - Local repo knowledge map: `{facts['repo_knowledge']['map_path']}`
        - Repo knowledge JSON: `{facts['repo_knowledge']['map_json_path']}`
        - Latest report index: `{facts['repo_knowledge']['latest_reports_index_path']}`
        - Best next milestone bundle: `{facts['repo_knowledge']['next_milestone_bundle_path']}`
        - Copy-paste repo prompt: `{facts['repo_knowledge']['codex_prompt_path']}`
        - Graphify runtime: {facts['repo_knowledge']['graphify_runtime']}
        - External repo runtime: {facts['repo_knowledge']['external_repo_runtime']}
        - Network: {facts['repo_knowledge']['network']}
        - Generate: `{facts['repo_knowledge']['repo_map_command']}`
        - Bundle: `{facts['repo_knowledge']['next_bundle_command']}`

        ## Operator Lanes

        - UI-TARS: observation-only
        - Adapter runner: approval-gated/local-only
        - External sandbox: static inspection only
        - Repo Knowledge / Graphify Lane: local map and task bundles; Graphify runtime roadmap only/not wired
        - Hermes Agent / Manual Bridge: safe probes, generated readiness files, and manual setup plan

        ## Latest Reports

        {reports}

        ## Safety Locks

        {locks}

        ## Copy-Paste Codex Prompt

        See `14_context/compact_memory/generated/ghoti_codex_next_prompt.md`.

        ## ChatGPT Migration Summary

        See `14_context/compact_memory/generated/ghoti_chatgpt_migration_summary.md`.
    """)


def _render_codex_prompt(facts: Dict[str, object]) -> str:
    return _strip_template_indent(f"""\
        Continue Ghoti / Super-AI-Agent from the current local-first supervised baseline.

        Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary
        worktree read-only except inspection. No force-push, no history rewrite, no
        secrets, no live account/API/posting/money/trading/legal actions, no bot/captcha/
        cloak bypass, no fake autonomy claims, no shell-true command execution, and no live providers/tokens.

        Current main hash: `{facts['main_hash']}`
        Latest clean milestone: {facts['latest_clean_milestone']}
        Current context pack milestone: {facts['current_milestone']}
        Previous repo knowledge milestone: N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval
        Launcher: `{LAUNCHER_COMMAND}`
        Dashboard: `{DASHBOARD_URL}`

        Status truth:
        - Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0.
        - Hermes Agent / Manual Bridge exposes safe status, skills index, manual checklist, and bridge packet.
        - Hermes browser/Playwright degraded/not claimed.
        - Codex provider in Hermes pending/not proven.
        - Telegram manual later/no token; No VPS.
        - Gemma model missing unless a new local check proves otherwise; local_demo fallback active.
        - Obsidian/local memory present.
        - UI-TARS observation-only.
        - Adapter runner approval-gated/local-only.
        - External sandbox static inspection/planning-only.
        - Repo Knowledge / Graphify Lane available as local JSON/Markdown files.

        Next safe milestone after this pack:
        {NEXT_RECOMMENDED_MILESTONE}

        Ask Codex to create a feature branch, add focused tests first, implement only the
        next local model/Gemma decision and local task quality evaluation changes, validate,
        push feature, then create a separate audit branch. Do not run `ollama pull` unless
        the human explicitly approves it in that milestone.
    """)


def _render_chatgpt_summary(facts: Dict[str, object], status_short: str) -> str:
    return _strip_template_indent(f"""\
        # ChatGPT migration summary

        Ghoti / Super-AI-Agent is a local-first supervised operator control center,
        not an autonomous agent. It coordinates coding/audit workflows, local memory,
        local model truth, safe content demos, model council planning, Hermes WSL truth,
        and future computer-use lanes behind human approval gates.

        Compact status paragraph:

        {status_short}

        Important constraints: no secrets, no live providers/tokens, no posting, no
        account actions, no money/trading/legal actions, no bot/captcha/cloak bypass,
        no fake engagement, no broad process kills, and no primary worktree mutation.

        Use the context pack command to refresh this summary:

        `{LAUNCHER_COMMAND}`
        `python 03_scripts/ghoti_context_pack_builder.py --write --json`
    """)


def _json_pack(facts: Dict[str, object], status_short: str) -> Dict[str, object]:
    return {
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "generated_at": facts["generated_at"],
        "main_hash": facts["main_hash"],
        "latest_clean_milestone": facts["latest_clean_milestone"],
        "current_milestone": facts["current_milestone"],
        "next_recommended_milestone": facts["next_recommended_milestone"],
        "launcher_command": LAUNCHER_COMMAND,
        "dashboard_url": DASHBOARD_URL,
        "status_short": status_short,
        "hermes": facts["hermes"],
        "local_model_truth": facts["local_model_truth"],
        "memory": facts["memory"],
        "repo_knowledge": facts["repo_knowledge"],
        "latest_reports": facts["latest_reports"],
        "safety_locks": facts["safety_locks"],
    }


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated context pack matched forbidden secret pattern: {pattern.pattern}")


def build_pack(generated_at: str | None = None) -> Dict[str, object]:
    facts = _build_facts(generated_at or _utc_now())
    status_short = _render_status_short(facts)
    json_pack = _json_pack(facts, status_short)
    files = {
        "ghoti_current_context_pack.md": _render_context_pack(facts, status_short),
        "ghoti_current_context_pack.json": json.dumps(json_pack, indent=2) + "\n",
        "ghoti_codex_next_prompt.md": _render_codex_prompt(facts),
        "ghoti_chatgpt_migration_summary.md": _render_chatgpt_summary(facts, status_short),
        "ghoti_status_short.md": status_short + "\n",
    }
    _assert_secret_safe(files.values())
    return {
        "facts": facts,
        "status_short": status_short,
        "json_pack": json_pack,
        "files": files,
    }


def write_pack(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    pack = build_pack(generated_at=generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in pack["files"].items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write context pack outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "generated_at": pack["facts"]["generated_at"],
        "main_hash": pack["facts"]["main_hash"],
        "latest_clean_milestone": pack["facts"]["latest_clean_milestone"],
        "current_milestone": pack["facts"]["current_milestone"],
        "next_recommended_milestone": pack["facts"]["next_recommended_milestone"],
        "status_short": pack["status_short"],
        "paths": paths,
        "latest_reports": pack["facts"]["latest_reports"],
        "local_model_truth": pack["facts"]["local_model_truth"],
        "safety_locks": pack["facts"]["safety_locks"],
    }


def status_payload(output_dir: pathlib.Path) -> Dict[str, object]:
    json_path = output_dir / "ghoti_current_context_pack.json"
    base_paths = {filename: _repo_rel(output_dir / filename) for filename in OUTPUT_FILES}
    if not json_path.exists():
        return {
            "ok": True,
            "local_only": True,
            "exists": False,
            "generated_at": None,
            "latest_context_pack_path": base_paths["ghoti_current_context_pack.md"],
            "copy_paste_prompt_path": base_paths["ghoti_codex_next_prompt.md"],
            "status_short": "No generated context pack yet. Run `python 03_scripts/ghoti_context_pack_builder.py --write --json`.",
            "paths": base_paths,
        }
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "local_only": True,
            "exists": True,
            "error": f"context pack JSON could not be read: {exc}",
            "paths": base_paths,
        }
    return {
        "ok": True,
        "local_only": True,
        "exists": True,
        "generated_at": data.get("generated_at"),
        "latest_context_pack_path": base_paths["ghoti_current_context_pack.md"],
        "copy_paste_prompt_path": base_paths["ghoti_codex_next_prompt.md"],
        "chatgpt_migration_summary_path": base_paths["ghoti_chatgpt_migration_summary.md"],
        "status_short": data.get("status_short", ""),
        "main_hash": data.get("main_hash"),
        "latest_clean_milestone": data.get("latest_clean_milestone"),
        "next_recommended_milestone": data.get("next_recommended_milestone"),
        "paths": base_paths,
    }


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("paths"):
        print("Ghoti context pack generated:")
        for filename, relpath in payload["paths"].items():
            print(f"  {filename}: {relpath}")
        print("")
        print(payload.get("status_short", ""))
    else:
        print(json.dumps(payload, indent=2))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or inspect the Ghoti local memory context pack.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/ghoti_context_pack_builder.py --write --json\n"
            "  python 03_scripts/ghoti_context_pack_builder.py --status --json\n"
            "  python 03_scripts/ghoti_context_pack_builder.py --list-reports --json\n"
        ),
    )
    parser.add_argument("--write", action="store_true", help="write the current context pack files")
    parser.add_argument("--status", action="store_true", help="show generated context pack status")
    parser.add_argument("--list-reports", action="store_true", help="list recent 14_context/codex_*.md reports")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override for tests")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.list_reports:
            payload = {"ok": True, "local_only": True, "reports": discover_recent_reports(limit=12)}
        elif args.write:
            payload = write_pack(output_dir=output_dir, generated_at=args.generated_at)
        else:
            payload = status_payload(output_dir=output_dir)
    except Exception as exc:
        payload = {"ok": False, "local_only": True, "error": str(exc)}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_human(payload)

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
