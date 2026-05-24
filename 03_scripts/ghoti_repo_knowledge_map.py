#!/usr/bin/env python3
"""Build a local Ghoti repo knowledge map and compact task bundles.

N+5.7A adds a safe, local-only repo understanding lane. It does not use a
Graphify runtime yet, does not clone external repos, and does not call network
or provider APIs. The output is a small JSON/Markdown map plus task-specific
context bundles under 14_context/repo_knowledge/generated/.
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
GENERATED_DIR = REPO_ROOT / "14_context" / "repo_knowledge" / "generated"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
LOCAL_WORKER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json"
REPO_MAP_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-map --json"
NEXT_BUNDLE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json"
HERMES_BRIDGE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json"
HERMES_BRIDGE_WRITE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json"
GEMMA_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-status --json"
GEMMA_DOCTOR_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json"
GEMMA_QUALITY_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json"
DIRECT_WRITE_COMMAND = "python 03_scripts/ghoti_repo_knowledge_map.py --write --json"

LATEST_CLEAN_MILESTONE = "N+5.9B - Gemma Readiness / Local Quality Plan landed on main"
CURRENT_MILESTONE = "N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation"
NEXT_RECOMMENDED_MILESTONE = "N+6.1A - Local Model Routing + Real Worker Task Integration"

READINESS_PERCENT = 55
GRAPHIFY_RUNTIME = "roadmap_only_not_wired"
EXTERNAL_REPO_RUNTIME = "not_wired"

TASK_BUNDLES = [
    "audit-main",
    "dashboard",
    "local-memory",
    "local-model-worker",
    "hermes",
    "content-workflow",
    "safety",
    "next-milestone",
]

OUTPUT_FILES = {
    "repo_knowledge_map.json": "knowledge_map_json",
    "repo_knowledge_map.md": "knowledge_map_markdown",
    "latest_reports_index.md": "latest_reports_index",
    "subsystem_index.md": "subsystem_index",
    "task_bundle_audit_main.md": "bundle_audit_main",
    "task_bundle_dashboard.md": "bundle_dashboard",
    "task_bundle_local_memory.md": "bundle_local_memory",
    "task_bundle_local_model_worker.md": "bundle_local_model_worker",
    "task_bundle_hermes.md": "bundle_hermes",
    "task_bundle_content_workflow.md": "bundle_content_workflow",
    "task_bundle_safety.md": "bundle_safety",
    "task_bundle_next_milestone.md": "bundle_next_milestone",
    "codex_next_prompt_graph_context.md": "codex_prompt",
    "chatgpt_repo_context_summary.md": "chatgpt_summary",
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

SAFETY_BOUNDARIES = [
    "no live APIs",
    "no provider setup or token flows",
    "no posting or account actions",
    "no money, trading, or legal actions",
    "no bot, captcha, or cloak bypass",
    "no external repo runtime wiring",
    "no network",
    "UI-TARS observation-only",
    "Hermes setup, provider config, Telegram, and tokens remain manual later",
]

SAFE_SCAN_NOTES = [
    "Selected repo-local allowlist only.",
    "Skips git internals, worktrees, dependency folders, caches, browser profiles, archives, binaries, and generated heavy runtime folders.",
    "Reads small text snippets from known product files and milestone reports.",
    "Never reads environment files, browser sessions, cookies, or credentials.",
]

IMPORTANT_FILE_CATALOG = [
    {
        "path": "README.md",
        "subsystem": "docs/operator guides",
        "description": "Public product overview, quickstart, local-first architecture, and safety model.",
        "why": "First file Ivan or GitHub visitors read before running Ghoti.",
    },
    {
        "path": "03_scripts/ghoti_product_launcher.py",
        "subsystem": "launcher",
        "description": "One-command launcher, smoke runner, context-pack shortcut, and local worker shortcut.",
        "why": "Daily operator entry point and safest command surface.",
    },
    {
        "path": "03_scripts/ghoti_context_pack_builder.py",
        "subsystem": "local memory/context packs",
        "description": "Builds compact Ghoti context packs for Codex, ChatGPT, Claude, and Obsidian.",
        "why": "Main token-saving continuity tool.",
    },
    {
        "path": "03_scripts/local_memory_compression_bridge.py",
        "subsystem": "local memory/context packs",
        "description": "Reports local compact memory bridge status and fallback truth.",
        "why": "Keeps durable memory visible without live providers.",
    },
    {
        "path": "03_scripts/local_model_worker_lane.py",
        "subsystem": "local model/easy worker",
        "description": "Detects Ollama/Gemma truth and writes deterministic local worker demo outputs.",
        "why": "Current credit-saving worker lane with local_demo fallback.",
    },
    {
        "path": "03_scripts/gemma_model_readiness.py",
        "subsystem": "local model/easy worker",
        "description": "Detects Gemma availability, writes manual install decision files, and prepares local task quality evaluation.",
        "why": "N+6.0A preflight and local model evaluation layer without provider setup or production routing.",
    },
    {
        "path": "03_scripts/hermes_local_bootstrap.py",
        "subsystem": "Hermes/WSL",
        "description": "Safe Hermes WSL status probes and bootstrap truth.",
        "why": "Hermes is a planned local agent layer, but setup/provider actions remain manual.",
    },
    {
        "path": "03_scripts/hermes_agent_workflow_bridge.py",
        "subsystem": "Hermes/WSL",
        "description": "Hermes manual bridge readiness, skills index, and generated setup packet.",
        "why": "Makes Hermes useful and inspectable while keeping provider setup, Telegram, tokens, and browser automation manual later.",
    },
    {
        "path": "03_scripts/ui_tars_observation_adapter.py",
        "subsystem": "UI-TARS/computer-use",
        "description": "Observation-only UI-TARS dry-run lane.",
        "why": "Preserves computer-use research without click/type control.",
    },
    {
        "path": "03_scripts/approved_adapter_runner.py",
        "subsystem": "adapter/external sandbox",
        "description": "Approval-gated local adapter runner.",
        "why": "Keeps integrations dry-run/local unless explicitly approved.",
    },
    {
        "path": "03_scripts/external_tool_sandbox_manager.py",
        "subsystem": "adapter/external sandbox",
        "description": "Static external tool intake and sandbox status.",
        "why": "Prevents uncontrolled external repo runtime wiring.",
    },
    {
        "path": "03_scripts/public_repo_security_audit.py",
        "subsystem": "public/security audit",
        "description": "Public readiness and security audit gate.",
        "why": "Finds blockers before public polish or main pushes.",
    },
    {
        "path": "03_scripts/model_council_tool_intake.py",
        "subsystem": "public/security audit",
        "description": "Local model/tool council scan.",
        "why": "Tracks provider/tool readiness without enabling unsafe automation.",
    },
    {
        "path": "03_scripts/supervised_content_mvp_runner.py",
        "subsystem": "supervised content demo",
        "description": "Local-only content workflow demo with 8 agents, titles, thumbnails, and previews.",
        "why": "Demonstrates supervised content workflow without posting.",
    },
    {
        "path": "01_projects/dashboard_mvp/server.js",
        "subsystem": "dashboard",
        "description": "Local dashboard HTTP server and fixed-argv product endpoints.",
        "why": "Backend for the Product Control Center and operator cards.",
    },
    {
        "path": "01_projects/dashboard_mvp/public/index.html",
        "subsystem": "dashboard",
        "description": "Dashboard UI structure and operator cards.",
        "why": "First-screen truth surface for daily use.",
    },
    {
        "path": "01_projects/dashboard_mvp/public/app.js",
        "subsystem": "dashboard",
        "description": "Dashboard client handlers for status cards and local actions.",
        "why": "Connects UI cards to local-only status endpoints.",
    },
    {
        "path": "01_projects/dashboard_mvp/public/styles.css",
        "subsystem": "dashboard",
        "description": "Dashboard styling.",
        "why": "Keeps the operator console usable and scannable.",
    },
    {
        "path": "docs/DAILY_OPERATOR_GUIDE.md",
        "subsystem": "docs/operator guides",
        "description": "Daily operator usage, troubleshooting, and cleanup guide.",
        "why": "Turns milestone work into repeatable human workflow.",
    },
    {
        "path": "docs/CODEX_ONLY_WORKFLOW.md",
        "subsystem": "docs/operator guides",
        "description": "Codex-only worktree, branch, audit, and safety workflow.",
        "why": "Keeps future Codex work isolated and auditable.",
    },
    {
        "path": "docs/LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md",
        "subsystem": "local memory/context packs",
        "description": "Guide for generating and using compact context packs.",
        "why": "Explains token-saving context handoff.",
    },
    {
        "path": "docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md",
        "subsystem": "local model/easy worker",
        "description": "Manual Ollama/Gemma setup truth and commands.",
        "why": "Shows how to unlock real local model work later without auto-downloads.",
    },
    {
        "path": "docs/GEMMA_MODEL_INSTALL_DECISION.md",
        "subsystem": "local model/easy worker",
        "description": "Gemma model install decision, manual commands, and no-auto-download policy.",
        "why": "Helps Ivan choose 4B, 1B, 270M, or stay local_demo.",
    },
    {
        "path": "docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md",
        "subsystem": "local model/easy worker",
        "description": "Human-approved gemma3:4b install scope and generated run locations.",
        "why": "Keeps the one-model approval separate from future routing or provider setup.",
    },
    {
        "path": "docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md",
        "subsystem": "local model/easy worker",
        "description": "Local model quality rubric and evaluation workflow.",
        "why": "Keeps real Gemma quality separate from local_demo fallback plumbing.",
    },
    {
        "path": "docs/EASY_WORKER_LANE_GUIDE.md",
        "subsystem": "local model/easy worker",
        "description": "Easy worker lane usage and fallback guide.",
        "why": "Documents safe credit-saving local tasks.",
    },
    {
        "path": "docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md",
        "subsystem": "Hermes/WSL",
        "description": "Hermes WSL install truth and provider plan.",
        "why": "Important next human/manual milestone context.",
    },
    {
        "path": "docs/HERMES_AGENT_WORKFLOW_GUIDE.md",
        "subsystem": "Hermes/WSL",
        "description": "Hermes Agent workflow and manual bridge guide.",
        "why": "Explains safe probes, generated readiness files, and manual later boundaries.",
    },
    {
        "path": "docs/HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md",
        "subsystem": "Hermes/WSL",
        "description": "Human checklist for later provider setup.",
        "why": "Keeps provider setup out of Codex automation and behind explicit approval.",
    },
    {
        "path": "docs/COMPUTER_USE_ROADMAP.md",
        "subsystem": "UI-TARS/computer-use",
        "description": "Future computer-use roadmap and safety gates.",
        "why": "Keeps click/type/autonomy future-gated.",
    },
    {
        "path": "docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md",
        "subsystem": "future Graphify roadmap",
        "description": "Token-efficiency, local models, memory, and Graphify planning.",
        "why": "Connects repo knowledge with the broader token-saving roadmap.",
    },
    {
        "path": "docs/BLOCKED_UNSAFE_AUTOMATION.md",
        "subsystem": "public/security audit",
        "description": "Unsafe automation policy.",
        "why": "Canonical list of blocked automation categories.",
    },
    {
        "path": "14_context/compact_memory/generated/ghoti_current_context_pack.md",
        "subsystem": "local memory/context packs",
        "description": "Latest generated context pack.",
        "why": "Short current-state handoff source.",
    },
    {
        "path": "14_context/local_worker/generated/local_worker_status.md",
        "subsystem": "local model/easy worker",
        "description": "Latest local worker status file.",
        "why": "Shows Ollama/Gemma/local_demo readiness.",
    },
    {
        "path": "14_context/hermes_workflow/generated/hermes_workflow_status.md",
        "subsystem": "Hermes/WSL",
        "description": "Latest Hermes manual bridge readiness status file.",
        "why": "Shows Hermes installed/version/skills truth and manual later boundaries.",
    },
    {
        "path": "01_projects/runtime_mvp/tests/test_n5_6a_local_model_easy_worker_lane.py",
        "subsystem": "tests",
        "description": "N+5.6 local worker lane tests.",
        "why": "Best current pattern for JSON script, launcher, docs, and dashboard checks.",
    },
]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, timeout=timeout, shell=False)


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


def _read_text(path: pathlib.Path, limit: int = 2500) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def _report_rank(name: str) -> List[int]:
    match = re.search(r"codex_n(\d+)_([0-9]+)([a-z]?)", name.lower())
    if not match:
        return [0, 0, 0]
    suffix = match.group(3)
    suffix_rank = (ord(suffix) - ord("a") + 1) if suffix else 0
    return [int(match.group(1)), int(match.group(2)), suffix_rank]


def _detect_report_kind(name: str) -> str:
    lowered = name.lower()
    if "final_main" in lowered or "main_merge" in lowered:
        return "main"
    if "audit" in lowered:
        return "audit"
    if "product" in lowered or "usability" in lowered:
        return "product"
    return "report"


def _verdict_hint(path: pathlib.Path) -> str:
    body = _read_text(path, limit=1600)
    for line in body.splitlines():
        cleaned = line.strip().replace("#", "").strip()
        lowered = cleaned.lower()
        if lowered in {"verdict", "final verdict"}:
            continue
        if "clean pass" in lowered or lowered.startswith("final verdict") or lowered.startswith("verdict"):
            return cleaned[:240]
    return "verdict not detected"


def discover_recent_reports(limit: int = 10) -> List[Dict[str, object]]:
    context_dir = REPO_ROOT / "14_context"
    try:
        candidates = [path for path in context_dir.glob("codex_*.md") if path.is_file()]
    except Exception:
        candidates = []
    reports: List[Dict[str, object]] = []
    for path in candidates:
        try:
            stat = path.stat()
        except OSError:
            continue
        reports.append({
            "path": _repo_rel(path),
            "name": path.name,
            "kind": _detect_report_kind(path.name),
            "rank": _report_rank(path.name),
            "modified_unix": int(stat.st_mtime),
            "verdict_hint": _verdict_hint(path),
        })
    reports.sort(key=lambda item: (item["rank"], item["modified_unix"], item["name"]), reverse=True)
    return reports[:limit]


def _file_summary(record: Dict[str, str]) -> Dict[str, object]:
    path = REPO_ROOT / record["path"]
    exists = path.exists() and path.is_file()
    size = path.stat().st_size if exists else 0
    snippet = _read_text(path, limit=600) if exists and size <= 250000 else ""
    return {
        "path": record["path"],
        "subsystem": record["subsystem"],
        "description": record["description"],
        "why_it_matters": record["why"],
        "exists": bool(exists),
        "size_bytes": int(size),
        "snippet_hint": _snippet_hint(snippet),
    }


def _snippet_hint(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#!"):
            return cleaned[:180]
    return "not read or empty"


def _important_files(reports: List[Dict[str, object]]) -> List[Dict[str, object]]:
    files = [_file_summary(item) for item in IMPORTANT_FILE_CATALOG]
    for report in reports:
        files.append({
            "path": str(report["path"]),
            "subsystem": "reports/14_context",
            "description": f"{report['kind']} milestone report",
            "why_it_matters": str(report["verdict_hint"]),
            "exists": True,
            "size_bytes": int((REPO_ROOT / str(report["path"])).stat().st_size)
            if (REPO_ROOT / str(report["path"])).exists() else 0,
            "snippet_hint": str(report["verdict_hint"]),
        })
    seen = set()
    unique = []
    for item in files:
        path = item["path"]
        if path in seen:
            continue
        seen.add(path)
        unique.append(item)
    return unique


def _subsystem_index(important_files: List[Dict[str, object]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for item in important_files:
        grouped.setdefault(str(item["subsystem"]), []).append(str(item["path"]))
    return {key: sorted(value) for key, value in sorted(grouped.items())}


def _output_paths(output_dir: pathlib.Path) -> Dict[str, str]:
    return {filename: _repo_rel(output_dir / filename) for filename in OUTPUT_FILES}


def _bundle_paths(output_dir: pathlib.Path) -> Dict[str, str]:
    return {
        bundle: _repo_rel(output_dir / f"task_bundle_{bundle.replace('-', '_')}.md")
        for bundle in TASK_BUNDLES
    }


def _status_line() -> str:
    return (
        "Repo knowledge readiness: 55%. Local file map and task bundles are available. "
        "Graphify runtime: roadmap only/not wired; no external repo runtime; no network."
    )


def build_map(generated_at: str | None = None, output_dir: pathlib.Path | None = None) -> Dict[str, object]:
    out_dir = output_dir or GENERATED_DIR
    reports = discover_recent_reports(limit=10)
    files = _important_files(reports)
    subsystems = _subsystem_index(files)
    return {
        "ok": True,
        "lane": "repo_knowledge_graphify_lane",
        "milestone": CURRENT_MILESTONE,
        "latest_clean_milestone": LATEST_CLEAN_MILESTONE,
        "next_recommended_milestone": NEXT_RECOMMENDED_MILESTONE,
        "local_only": True,
        "external_api_used": False,
        "live_api_used": False,
        "network_used": False,
        "external_repos_used": False,
        "external_repo_runtime": EXTERNAL_REPO_RUNTIME,
        "graphify_runtime": GRAPHIFY_RUNTIME,
        "readiness_percent": READINESS_PERCENT,
        "status_line": _status_line(),
        "generated_at": generated_at or _utc_now(),
        "main_hash": _current_main_hash(),
        "launcher_command": LAUNCHER_COMMAND,
        "dashboard_url": DASHBOARD_URL,
        "context_pack_command": CONTEXT_PACK_COMMAND,
        "local_worker_command": LOCAL_WORKER_COMMAND,
        "gemma_status_command": GEMMA_STATUS_COMMAND,
        "gemma_doctor_command": GEMMA_DOCTOR_COMMAND,
        "gemma_quality_command": GEMMA_QUALITY_COMMAND,
        "gemma_readiness": {
            "status": "manual_install_decision_ready",
            "generated_dir": "14_context/local_model_readiness/generated",
            "status_path": "14_context/local_model_readiness/generated/gemma_readiness_status.md",
            "install_decision_path": "14_context/local_model_readiness/generated/gemma_install_decision.md",
            "quality_plan_path": "14_context/local_model_readiness/generated/local_task_quality_plan.md",
            "evaluation_runs_dir": "14_context/local_model_evaluation/runs",
            "production_routing": "disabled",
            "manual_download": "manual approval required before model download",
        },
        "repo_map_command": REPO_MAP_COMMAND,
        "next_bundle_command": NEXT_BUNDLE_COMMAND,
        "hermes_bridge_command": HERMES_BRIDGE_COMMAND,
        "hermes_bridge_write_command": HERMES_BRIDGE_WRITE_COMMAND,
        "output_dir": _repo_rel(out_dir),
        "output_paths": _output_paths(out_dir),
        "task_bundles": TASK_BUNDLES,
        "task_bundle_paths": _bundle_paths(out_dir),
        "latest_reports": reports,
        "important_files": files,
        "subsystems": subsystems,
        "scan_rules": SAFE_SCAN_NOTES,
        "safety_boundaries": SAFETY_BOUNDARIES,
        "safety": {
            "no_live_apis": True,
            "no_network": True,
            "no_external_repos": True,
            "no_provider_setup": True,
            "no_posting": True,
            "ui_tars_observation_only": True,
        },
        "confidence": "medium",
        "freshness_notes": [
            "Generated from local repo files and current git metadata.",
            "Latest reports are ranked by milestone-like filename and modified time.",
            "External Graphify runtime is planned but not wired.",
        ],
    }


def status_payload(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    payload = build_map(generated_at=generated_at, output_dir=output_dir)
    payload["exists"] = (output_dir / "repo_knowledge_map.json").exists()
    payload["latest_map_path"] = _repo_rel(output_dir / "repo_knowledge_map.md")
    payload["latest_report_index_path"] = _repo_rel(output_dir / "latest_reports_index.md")
    return payload


def _strip(text: str) -> str:
    cleaned = textwrap.dedent(text)
    cleaned = re.sub(r"^ {8}", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip() + "\n"


def _latest_reports_index(reports: Iterable[Dict[str, object]]) -> str:
    rows = []
    for report in reports:
        rows.append(f"- `{report['path']}` ({report['kind']}): {report['verdict_hint']}")
    report_lines = "\n".join(rows) if rows else "- No milestone reports found."
    return _strip(f"""
        # Latest Report Index

        This latest report index is local-only and generated from `14_context/codex_*.md`.

        {report_lines}
    """)


def _subsystem_markdown(subsystems: Dict[str, List[str]]) -> str:
    sections = ["# Subsystem Index", "", "Local repo knowledge grouped by subsystem.", ""]
    for name, paths in subsystems.items():
        sections.append(f"## {name}")
        sections.extend(f"- `{path}`" for path in paths)
        sections.append("")
    return "\n".join(sections).strip() + "\n"


def _map_markdown(map_data: Dict[str, object]) -> str:
    files = "\n".join(
        f"- `{item['path']}` [{item['subsystem']}]: {item['why_it_matters']}"
        for item in map_data["important_files"]
        if item.get("exists")
    )
    bundles = "\n".join(
        f"- `{name}` -> `{path}`"
        for name, path in map_data["task_bundle_paths"].items()
    )
    safety = "\n".join(f"- {item}" for item in SAFETY_BOUNDARIES)
    return _strip(f"""
        # Ghoti Repo Knowledge Map

        Generated: `{map_data['generated_at']}`

        {map_data['status_line']}

        - Main hash: `{map_data['main_hash']}`
        - Latest clean milestone: {map_data['latest_clean_milestone']}
        - Current milestone: {map_data['milestone']}
        - Next recommended milestone: {map_data['next_recommended_milestone']}
        - Launcher: `{LAUNCHER_COMMAND}`
        - Dashboard: `{DASHBOARD_URL}`
        - Repo map command: `{REPO_MAP_COMMAND}`
        - Hermes bridge command: `{HERMES_BRIDGE_COMMAND}`
        - Gemma status command: `{GEMMA_STATUS_COMMAND}`
        - Gemma quality command: `{GEMMA_QUALITY_COMMAND}`
        - Gemma readiness files: `14_context/local_model_readiness/generated/`
        - Local model eval runs: `14_context/local_model_evaluation/runs/`
        - Gemma production routing: disabled
        - Graphify runtime: roadmap only/not wired
        - no external repo runtime
        - no network

        ## Important Files

        {files}

        ## Task Bundles

        {bundles}

        ## Safety Boundaries

        {safety}
    """)


def _bundle_definition(bundle: str) -> Dict[str, object]:
    definitions = {
        "audit-main": {
            "title": "Audit Current Main",
            "purpose": "Validate origin/main from a clean worktree and report blockers only.",
            "files": [
                "README.md",
                "03_scripts/public_repo_security_audit.py",
                "03_scripts/ghoti_product_launcher.py",
                "01_projects/runtime_mvp/tests",
                "14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md",
            ],
            "prompt": "Audit current origin/main from a clean repo-contained worktree. Run N+4/N+5 tests, product probes, public audit, and report blockers only.",
        },
        "dashboard": {
            "title": "Dashboard Work",
            "purpose": "Update the local Product Control Center without changing safety semantics.",
            "files": [
                "01_projects/dashboard_mvp/server.js",
                "01_projects/dashboard_mvp/public/index.html",
                "01_projects/dashboard_mvp/public/app.js",
                "01_projects/dashboard_mvp/public/styles.css",
                "03_scripts/ghoti_product_launcher.py",
            ],
            "prompt": "Improve the dashboard from a repo-contained worktree. Keep UI-TARS observation-only, use fixed argv endpoints, and verify local DOM labels.",
        },
        "local-memory": {
            "title": "Local Memory / Context Pack Work",
            "purpose": "Improve compact memory and copy-paste context without live providers.",
            "files": [
                "03_scripts/ghoti_context_pack_builder.py",
                "03_scripts/local_memory_compression_bridge.py",
                "docs/LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md",
                "14_context/compact_memory/generated/ghoti_current_context_pack.md",
            ],
            "prompt": "Build the next local memory improvement with compact outputs, source-linked truth, and no provider/token wiring.",
        },
        "local-model-worker": {
            "title": "Local Model / Easy Worker Work",
            "purpose": "Improve Ollama/Gemma truth, Gemma readiness, local_demo fallback tasks, and local model quality evaluation without provider setup.",
            "files": [
                "03_scripts/local_model_worker_lane.py",
                "03_scripts/gemma_model_readiness.py",
                "docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md",
                "docs/EASY_WORKER_LANE_GUIDE.md",
                "docs/GEMMA_MODEL_INSTALL_DECISION.md",
                "docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md",
                "docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md",
                "14_context/local_worker/generated/local_worker_status.md",
                "14_context/local_model_readiness/generated/gemma_readiness_status.md",
                "14_context/local_model_readiness/generated/local_task_quality_plan.md",
                "14_context/local_model_evaluation/runs/",
            ],
            "prompt": "Improve the local model worker lane and Gemma evaluation. Do not run new model pulls, live APIs, provider setup, or production routing without explicit approval.",
        },
        "hermes": {
            "title": "Hermes Agent / Manual Bridge Work",
            "purpose": "Inspect or improve the Hermes manual bridge without setup/token actions.",
            "files": [
                "03_scripts/hermes_agent_workflow_bridge.py",
                "03_scripts/hermes_local_bootstrap.py",
                "docs/HERMES_AGENT_WORKFLOW_GUIDE.md",
                "docs/HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md",
                "docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md",
                "docs/CODEX_ONLY_WORKFLOW.md",
                "14_context/hermes_workflow/generated/hermes_workflow_status.md",
                "14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md",
            ],
            "prompt": "Work on the Hermes Agent / Manual Bridge lane. Use safe probes only; no setup/provider config/Telegram/tokens/live APIs/browser automation.",
        },
        "content-workflow": {
            "title": "Supervised Content Workflow",
            "purpose": "Inspect or improve the local-only content demo without posting.",
            "files": [
                "03_scripts/supervised_content_mvp_runner.py",
                "14_context/content_workflows",
                "01_projects/dashboard_mvp/public/index.html",
                "README.md",
            ],
            "prompt": "Improve the supervised content workflow locally. Keep 8 agents / 100 titles / 100 thumbnails / local preview / no posting truthful.",
        },
        "safety": {
            "title": "Safety Audit",
            "purpose": "Keep unsafe automation blocked and public readiness truthful.",
            "files": [
                "docs/BLOCKED_UNSAFE_AUTOMATION.md",
                "03_scripts/public_repo_security_audit.py",
                "03_scripts/model_council_tool_intake.py",
                "README.md",
                "SECURITY.md",
            ],
            "prompt": "Run a safety audit for false autonomy, secrets, unsafe automation, live actions, and shell command regressions. Fix blockers only.",
        },
        "next-milestone": {
            "title": "Next Milestone",
            "purpose": "Prepare N+6.1A Local Model Routing + Real Worker Task Integration after a clean N+6.0A evaluation.",
            "files": [
                "03_scripts/local_model_worker_lane.py",
                "03_scripts/gemma_model_readiness.py",
                "docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md",
                "docs/EASY_WORKER_LANE_GUIDE.md",
                "docs/GEMMA_MODEL_INSTALL_DECISION.md",
                "docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md",
                "docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md",
                "14_context/local_worker/generated/local_worker_status.md",
                "14_context/local_model_readiness/generated/gemma_install_decision.md",
                "14_context/local_model_readiness/generated/local_task_quality_plan.md",
                "14_context/local_model_evaluation/runs/",
                "14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md",
            ],
            "prompt": "Plan N+6.1A Local Model Routing + Real Worker Task Integration only if N+6.0A installed and evaluated a real local model cleanly. No live APIs, provider setup, Telegram setup, or production routing without audit.",
        },
    }
    return definitions[bundle]


def build_bundle(bundle: str, map_data: Dict[str, object] | None = None) -> Dict[str, object]:
    normalized = bundle.strip().lower()
    if normalized not in TASK_BUNDLES:
        return {
            "ok": False,
            "local_only": True,
            "external_api_used": False,
            "bundle": bundle,
            "error": "unsupported bundle",
            "available_bundles": TASK_BUNDLES,
        }
    data = map_data or build_map()
    definition = _bundle_definition(normalized)
    files = "\n".join(f"- `{path}`" for path in definition["files"])
    safety = "\n".join(f"- {item}" for item in SAFETY_BOUNDARIES)
    validation = "\n".join(
        f"- `{cmd}`"
        for cmd in [
            "git diff --check",
            "git show --check --stat HEAD",
            'python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n4_*.py" -v',
            'python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n5_*.py" -v',
            "python 03_scripts/ghoti_product_launcher.py --smoke --json",
            DIRECT_WRITE_COMMAND,
            "python 03_scripts/public_repo_security_audit.py --run --json",
        ]
    )
    useful = "\n".join(
        f"- `{cmd}`"
        for cmd in [
            LAUNCHER_COMMAND,
            CONTEXT_PACK_COMMAND,
            LOCAL_WORKER_COMMAND,
            GEMMA_STATUS_COMMAND,
            GEMMA_DOCTOR_COMMAND,
            GEMMA_QUALITY_COMMAND,
            "python 03_scripts/ghoti_product_launcher.py --local-model-eval --json",
            REPO_MAP_COMMAND,
            HERMES_BRIDGE_COMMAND,
            f"python 03_scripts/ghoti_repo_knowledge_map.py --bundle {normalized} --json",
            NEXT_BUNDLE_COMMAND,
        ]
    )
    current_truth = "\n".join([
        f"- Main hash: `{data['main_hash']}`",
        f"- Latest clean milestone: {data['latest_clean_milestone']}",
        f"- Current milestone: {data['milestone']}",
        "- Previous Hermes bridge milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness.",
        "- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0; Hermes Agent / Manual Bridge files available; browser/Playwright degraded/not claimed.",
        "- Ollama available v0.24.0; Gemma is installed only if local `ollama list` proves it; local_demo fallback remains available.",
        "- Gemma / Local Model Quality files live under `14_context/local_model_readiness/generated/`; local eval runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.",
        "- UI-TARS observation-only; adapter runner approval-gated/local-only; external sandbox static inspection only.",
        "- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.",
    ])
    text = _strip(f"""
        # Task Bundle: {definition['title']}

        ## Purpose

        {definition['purpose']}

        ## Files To Inspect First

        {files}

        ## Current Truth

        {current_truth}

        ## Safety Boundaries

        {safety}

        ## Useful Commands

        {useful}

        ## Validation Commands

        {validation}

        ## Known Limitations

        - Graphify is a roadmap concept here; the external Graphify runtime is not wired.
        - This bundle is generated from a selected local file map, not a full graph database.
        - Browser/Playwright and Hermes provider support are not claimed.
        - Generated reports may need refresh after a new milestone.

        ## Next Recommended Prompt

        {definition['prompt']}
    """)
    return {
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "network_used": False,
        "bundle": normalized,
        "title": definition["title"],
        "text": text,
        "generated_at": data["generated_at"],
        "main_hash": data["main_hash"],
    }


def _codex_prompt(map_data: Dict[str, object]) -> str:
    return _strip(f"""
        Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

        Use only repo-contained worktrees under `.claude/worktrees`; keep the primary worktree read-only except inspection.
        Refresh compact context first with `{CONTEXT_PACK_COMMAND}` and repo knowledge with `{REPO_MAP_COMMAND}`.
        For the next milestone, inspect `{map_data['task_bundle_paths']['next-milestone']}`.

        Current truth:
        - Main hash: `{map_data['main_hash']}`
        - Latest clean milestone: {map_data['latest_clean_milestone']}
        - Current feature milestone: {map_data['milestone']}
        - Graphify runtime: roadmap only/not wired; no external repo runtime; no network.
        - Hermes setup/provider config/Telegram/tokens remain manual later.
        - Gemma local evaluation runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.
        - UI-TARS remains observation-only.

        Next recommended milestone:
        {NEXT_RECOMMENDED_MILESTONE}
    """)


def _chatgpt_summary(map_data: Dict[str, object]) -> str:
    return _strip(f"""
        # ChatGPT Repo Context Summary

        Ghoti now has a local repo knowledge lane. It generates a selected file map,
        latest report index, subsystem index, and compact task bundles so Ivan can
        paste focused context instead of a giant prompt.

        {map_data['status_line']}

        Use:

        - `{REPO_MAP_COMMAND}`
        - `{NEXT_BUNDLE_COMMAND}`
        - `{CONTEXT_PACK_COMMAND}`

        Graphify remains a roadmap layer. The current implementation is local JSON and
        Markdown only, with no external repo runtime and no network.
    """)


def build_files(map_data: Dict[str, object]) -> Dict[str, str]:
    bundle_payloads = {bundle: build_bundle(bundle, map_data=map_data) for bundle in TASK_BUNDLES}
    files = {
        "repo_knowledge_map.json": json.dumps(map_data, indent=2) + "\n",
        "repo_knowledge_map.md": _map_markdown(map_data),
        "latest_reports_index.md": _latest_reports_index(map_data["latest_reports"]),
        "subsystem_index.md": _subsystem_markdown(map_data["subsystems"]),
        "codex_next_prompt_graph_context.md": _codex_prompt(map_data),
        "chatgpt_repo_context_summary.md": _chatgpt_summary(map_data),
    }
    for bundle, payload in bundle_payloads.items():
        files[f"task_bundle_{bundle.replace('-', '_')}.md"] = payload["text"]
    return files


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated repo knowledge output matched forbidden secret pattern: {pattern.pattern}")


def write_outputs(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    map_data = build_map(generated_at=generated_at, output_dir=output_dir)
    files = build_files(map_data)
    _assert_secret_safe(files.values())
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write repo knowledge output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    payload = status_payload(output_dir=output_dir, generated_at=map_data["generated_at"])
    payload.update({
        "action": "write",
        "paths": paths,
        "generated_at": map_data["generated_at"],
    })
    return payload


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("status_line"):
        print(payload["status_line"])
    if payload.get("paths"):
        print("Generated repo knowledge files:")
        for filename, relpath in payload["paths"].items():
            print(f"  {filename}: {relpath}")
    elif payload.get("text"):
        print(payload["text"])
    else:
        print(json.dumps(payload, indent=2))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or inspect Ghoti's local repo knowledge map and task bundles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/ghoti_repo_knowledge_map.py --status --json\n"
            "  python 03_scripts/ghoti_repo_knowledge_map.py --write --json\n"
            "  python 03_scripts/ghoti_repo_knowledge_map.py --bundle next-milestone --json\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show repo knowledge map status")
    parser.add_argument("--scan", action="store_true", help="scan selected repo knowledge map without writing")
    parser.add_argument("--write", action="store_true", help="write repo knowledge map and task bundles")
    parser.add_argument("--bundle", choices=TASK_BUNDLES, help="emit one compact task-specific context bundle")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.bundle:
            payload = build_bundle(args.bundle, map_data=build_map(generated_at=args.generated_at, output_dir=output_dir))
        elif args.write:
            payload = write_outputs(output_dir=output_dir, generated_at=args.generated_at)
        elif args.scan:
            payload = build_map(generated_at=args.generated_at, output_dir=output_dir)
            payload["action"] = "scan"
        else:
            payload = status_payload(output_dir=output_dir, generated_at=args.generated_at)
            payload["action"] = "status"
    except Exception as exc:
        payload = {
            "ok": False,
            "local_only": True,
            "external_api_used": False,
            "network_used": False,
            "error": str(exc),
            "generated_at": _utc_now(),
        }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_human(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
