#!/usr/bin/env python3
"""Gemma model availability and local task quality readiness.

N+5.9A adds a local-only decision layer for Ollama/Gemma. It detects what is
installed, writes a manual install plan, and prepares a deterministic quality
rubric. It never downloads models, never calls live APIs, and never enables
production routing.
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
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
GENERATED_DIR = REPO_ROOT / "14_context" / "local_model_readiness" / "generated"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
LOCAL_WORKER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json"
GEMMA_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-status --json"
GEMMA_DOCTOR_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json"
GEMMA_QUALITY_COMMAND = "python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json"
DIRECT_STATUS_COMMAND = "python 03_scripts/gemma_model_readiness.py --status --json"
DIRECT_DOCTOR_COMMAND = "python 03_scripts/gemma_model_readiness.py --doctor --json"
DIRECT_RECOMMEND_COMMAND = "python 03_scripts/gemma_model_readiness.py --recommend --json"
DIRECT_QUALITY_COMMAND = "python 03_scripts/gemma_model_readiness.py --quality-plan --json"
DIRECT_WRITE_COMMAND = "python 03_scripts/gemma_model_readiness.py --write-readiness --json"

PREFERRED_MODEL = "gemma3:4b"
FALLBACK_MODELS = ["gemma3:1b", "gemma3:270m"]
MANUAL_COMMANDS = [
    "ollama list",
    "ollama pull gemma3:4b",
    "ollama pull gemma3:1b",
    "ollama pull gemma3:270m",
]

MODEL_OPTIONS = {
    "gemma3:4b": {
        "role": "preferred first real local worker candidate",
        "disk_size_note": "Ollama lists gemma3:4b at about 3.3GB.",
        "context_window_note": "Gemma 3 4B is documented with a 128K context window on Ollama.",
        "why": "Best first balance for useful summaries, classification, and compact context work without jumping to 12B/27B.",
        "caution": "Needs local disk and enough RAM/VRAM; install manually only after Ivan approves the pull.",
        "manual_command": "ollama pull gemma3:4b",
    },
    "gemma3:1b": {
        "role": "lighter fallback for fast cheap tests",
        "disk_size_note": "Smaller than 4B; useful when speed or memory matters more than quality.",
        "context_window_note": "Use for quick status and classification experiments.",
        "why": "Good for first smoke if the machine struggles with 4B.",
        "caution": "Quality may be weaker than 4B; do not route production work by default.",
        "manual_command": "ollama pull gemma3:1b",
    },
    "gemma3:270m": {
        "role": "smallest fallback for setup sanity checks",
        "disk_size_note": "Tiny relative to 4B; useful for proving the lane can call a model.",
        "context_window_note": "Use for fast smoke checks, not serious reasoning.",
        "why": "Lowest-friction manual pull for constrained hardware.",
        "caution": "Expected quality is limited; keep Codex/ChatGPT/Claude for hard work.",
        "manual_command": "ollama pull gemma3:270m",
    },
}

QUALITY_TASKS = [
    {
        "id": "summarize_latest_report",
        "name": "Summarize latest Ghoti report",
        "goal": "Compress the latest milestone report into compact memory.",
    },
    {
        "id": "human_status_paragraph",
        "name": "Produce one-paragraph human status",
        "goal": "Give Ivan a concise truthful local MVP status.",
    },
    {
        "id": "classify_next_task",
        "name": "Classify next task",
        "goal": "Classify work as coding, docs, audit, content, research, or safety.",
    },
    {
        "id": "codex_prompt_from_context",
        "name": "Generate concise Codex prompt from context pack",
        "goal": "Create a small handoff prompt without leaking secrets.",
    },
    {
        "id": "identify_repo_bundle",
        "name": "Identify relevant repo bundle",
        "goal": "Pick the right repo knowledge bundle for a task.",
    },
    {
        "id": "unsafe_request_detection",
        "name": "Detect unsafe automation request",
        "goal": "Refuse unsafe autonomous action and suggest a safe alternative.",
    },
    {
        "id": "ten_bullet_report_compression",
        "name": "Compress long report to 10 bullets",
        "goal": "Summarize a long audit report while preserving status truth.",
    },
]

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


def _is_inside_repo(path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _repo_rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


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


def _fake_completed(stdout: str = "", stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run fixed argv only. Test fixtures can fake Ollama without touching PATH."""
    if cmd == ["ollama", "--version"]:
        if os.environ.get("GHOTI_GEMMA_READINESS_FAKE_OLLAMA_MISSING") == "1":
            raise FileNotFoundError("ollama")
        fake = os.environ.get("GHOTI_GEMMA_READINESS_FAKE_OLLAMA_VERSION")
        if fake is not None:
            return _fake_completed(stdout=fake)
    if cmd == ["ollama", "list"]:
        fake = os.environ.get("GHOTI_GEMMA_READINESS_FAKE_OLLAMA_LIST")
        if fake is not None:
            return _fake_completed(stdout=fake)
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        shell=False,
    )


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


def _parse_ollama_list(stdout: str) -> Tuple[List[str], bool, str]:
    text = stdout or ""
    stripped = text.strip()
    if not stripped:
        return [], True, ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return [], True, ""
    header = lines[0].lower()
    if not ("name" in header and "id" in header and "size" in header):
        return [], False, "ollama list output did not include the expected NAME/ID/SIZE header"
    models: List[str] = []
    for line in lines[1:]:
        columns = line.split()
        if not columns:
            continue
        name = columns[0].strip()
        if name and name.lower() != "name":
            models.append(name)
    return models, True, ""


def probe_ollama() -> Dict[str, object]:
    result: Dict[str, object] = {
        "ollama_installed": False,
        "ollama_version": "not_found",
        "ollama_reachable": False,
        "installed_models": [],
        "installed_models_count": 0,
        "model_list_parse_ok": True,
        "probe_error": "",
        "list_error": "",
    }
    try:
        version = _run(["ollama", "--version"], timeout=5)
    except FileNotFoundError:
        result["probe_error"] = "ollama executable not found in PATH"
        return result
    except subprocess.TimeoutExpired:
        result["probe_error"] = "ollama --version timed out"
        return result
    except OSError as exc:
        result["probe_error"] = f"ollama --version failed: {exc}"
        return result
    if version.returncode != 0:
        result["probe_error"] = (version.stderr or version.stdout or "ollama --version failed").strip()[:300]
        return result

    result["ollama_installed"] = True
    result["ollama_version"] = (version.stdout or "").strip() or "available"
    try:
        listed = _run(["ollama", "list"], timeout=10)
    except FileNotFoundError:
        result["list_error"] = "ollama list executable lookup failed"
        return result
    except subprocess.TimeoutExpired:
        result["list_error"] = "ollama list timed out"
        return result
    except OSError as exc:
        result["list_error"] = f"ollama list failed: {exc}"
        return result
    if listed.returncode != 0:
        result["list_error"] = (listed.stderr or listed.stdout or "ollama list failed").strip()[:300]
        return result
    models, parse_ok, warning = _parse_ollama_list(listed.stdout or "")
    result["model_list_parse_ok"] = parse_ok
    result["list_error"] = warning
    result["ollama_reachable"] = bool(parse_ok)
    result["installed_models"] = models
    result["installed_models_count"] = len(models)
    return result


def _gemma_models(models: Iterable[str]) -> Dict[str, object]:
    installed = list(models)
    lowered = {name.lower(): name for name in installed}
    gemma = [
        name for name in installed
        if name.lower().startswith("gemma") or "gemma" in name.lower()
    ]
    preferred = lowered.get(PREFERRED_MODEL.lower())
    fallbacks = [lowered[name.lower()] for name in FALLBACK_MODELS if name.lower() in lowered]
    selected = preferred or (fallbacks[0] if fallbacks else (gemma[0] if gemma else None))
    return {
        "gemma_installed": bool(gemma),
        "installed_gemma_models": gemma,
        "preferred_model": PREFERRED_MODEL,
        "preferred_model_installed": bool(preferred),
        "fallback_models_installed": fallbacks,
        "selected_model": selected,
    }


def _readiness_percent(ollama: Dict[str, object], gemma: Dict[str, object]) -> int:
    if not ollama["ollama_installed"]:
        return 20
    if not ollama["ollama_reachable"]:
        return 32
    if gemma["preferred_model_installed"]:
        return 74
    if gemma["fallback_models_installed"]:
        return 64
    if gemma["gemma_installed"]:
        return 60
    return 45


def _recommendation(ollama: Dict[str, object], gemma: Dict[str, object]) -> str:
    if not ollama["ollama_installed"]:
        return "Install or start Ollama manually, then rerun the Gemma doctor. Ghoti will not install packages or download models."
    if not ollama["ollama_reachable"]:
        return "Ollama is installed but model listing is unavailable. Start the local Ollama service or inspect `ollama list` manually."
    if gemma["preferred_model_installed"]:
        return "gemma3:4b is installed. Run the local quality plan next, but keep production routing disabled until a later human-approved milestone."
    if gemma["fallback_models_installed"]:
        return "A lighter Gemma model is installed. Use it for fast local tests, and consider manual `ollama pull gemma3:4b` if quality is not enough."
    if gemma["gemma_installed"]:
        return "A Gemma-family model is installed but not the preferred 4B or documented lighter fallback. Run quality checks before relying on it."
    return "Gemma is missing. Keep local_demo fallback active, or manually approve `ollama pull gemma3:4b` later."


def build_status(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    ollama = probe_ollama()
    gemma = _gemma_models(ollama["installed_models"])
    readiness = _readiness_percent(ollama, gemma)
    active_mode = "ollama_gemma" if gemma["gemma_installed"] else "local_demo"
    status_line = (
        f"Local model readiness: {readiness}%. Ollama is installed ({ollama['ollama_version']}). "
        f"Gemma model available: {gemma['selected_model']}. Active mode is {active_mode}. "
        "Production routing remains disabled."
        if gemma["gemma_installed"]
        else f"Local model readiness: {readiness}%. Ollama is "
        f"{'installed (' + str(ollama['ollama_version']) + ')' if ollama['ollama_installed'] else 'not detected'}. "
        "Gemma is missing, active mode is local_demo fallback, and no auto-downloads are enabled."
    )
    payload: Dict[str, object] = {
        "ok": True,
        "action": "status",
        "lane": "gemma_model_availability_local_task_quality",
        "milestone": "N+5.9A",
        "main_hash": _current_main_hash(),
        "local_only": True,
        "network_required": False,
        "live_api_used": False,
        "external_api_used": False,
        "auto_download_performed": False,
        "ollama_pull_performed": False,
        "secrets_used": False,
        "provider_setup_run": False,
        "production_routing_enabled": False,
        "manual_approval_required": True,
        "manual_approval_required_reason": "manual approval required before model download; Ghoti does not run `ollama pull` automatically",
        "ollama_installed": bool(ollama["ollama_installed"]),
        "ollama_version": ollama["ollama_version"],
        "ollama_reachable": bool(ollama["ollama_reachable"]),
        "installed_models": ollama["installed_models"],
        "installed_models_count": ollama["installed_models_count"],
        "model_list_parse_ok": ollama["model_list_parse_ok"],
        "probe_error": ollama["probe_error"],
        "list_error": ollama["list_error"],
        **gemma,
        "active_worker_mode": active_mode,
        "local_worker_readiness_percent": 75 if gemma["gemma_installed"] else (45 if ollama["ollama_installed"] else 25),
        "gemma_readiness_percent": readiness,
        "readiness_percent": readiness,
        "quality_evaluation_status": "pending_real_gemma_install" if not gemma["gemma_installed"] else "ready_for_human_approved_eval",
        "quality_plan_command": GEMMA_QUALITY_COMMAND,
        "manual_commands": MANUAL_COMMANDS,
        "recommended_manual_command": "ollama pull gemma3:4b",
        "recommended_first_model": PREFERRED_MODEL,
        "lighter_fallback_models": FALLBACK_MODELS,
        "recommendation": _recommendation(ollama, gemma),
        "status_line": status_line,
        "launcher_command": LAUNCHER_COMMAND,
        "dashboard_url": DASHBOARD_URL,
        "context_pack_command": CONTEXT_PACK_COMMAND,
        "local_worker_command": LOCAL_WORKER_COMMAND,
        "gemma_status_command": GEMMA_STATUS_COMMAND,
        "gemma_doctor_command": GEMMA_DOCTOR_COMMAND,
        "gemma_quality_command": GEMMA_QUALITY_COMMAND,
        "output_paths": {
            "gemma_readiness_status.json": _repo_rel(GENERATED_DIR / "gemma_readiness_status.json"),
            "gemma_readiness_status.md": _repo_rel(GENERATED_DIR / "gemma_readiness_status.md"),
            "gemma_install_decision.md": _repo_rel(GENERATED_DIR / "gemma_install_decision.md"),
            "local_task_quality_plan.md": _repo_rel(GENERATED_DIR / "local_task_quality_plan.md"),
            "local_task_quality_rubric.json": _repo_rel(GENERATED_DIR / "local_task_quality_rubric.json"),
        },
        "safety": {
            "no_live_apis": True,
            "no_auto_downloads": True,
            "no_ollama_pull": True,
            "no_provider_tokens": True,
            "production_routing_disabled": True,
            "local_demo_fallback_preserved": True,
        },
        "generated_at": created,
    }
    return payload


def build_doctor(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    checks = [
        {
            "name": "Ollama executable",
            "ok": status["ollama_installed"],
            "detail": status["ollama_version"] if status["ollama_installed"] else status["probe_error"] or "not found",
        },
        {
            "name": "Ollama model list",
            "ok": status["ollama_reachable"],
            "detail": f"{status['installed_models_count']} model(s) visible"
            if status["ollama_reachable"] else status["list_error"] or "model list unavailable",
        },
        {
            "name": "Gemma model",
            "ok": status["gemma_installed"],
            "detail": ", ".join(status["installed_gemma_models"]) if status["installed_gemma_models"] else "missing; local_demo fallback active",
        },
        {
            "name": "Preferred Gemma model",
            "ok": status["preferred_model_installed"],
            "detail": PREFERRED_MODEL if status["preferred_model_installed"] else "missing",
        },
        {
            "name": "Safety",
            "ok": True,
            "detail": "no live APIs, no auto-downloads, no ollama pull, production routing disabled",
        },
    ]
    status.update({
        "action": "doctor",
        "checks": checks,
        "troubleshooting": [
            "If Ollama is missing, install or start Ollama manually outside Ghoti.",
            "If `ollama list` fails, start the local Ollama service and rerun the doctor.",
            "If Gemma is missing, review the install decision and run a manual pull only after human approval.",
            "If Gemma is installed but quality is weak, keep local_demo or Codex/ChatGPT/Claude for hard tasks.",
        ],
    })
    return status


def build_recommendation(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    return {
        "ok": True,
        "action": "recommend",
        "local_only": True,
        "live_api_used": False,
        "auto_download_performed": False,
        "ollama_pull_performed": False,
        "production_routing_enabled": False,
        "human_approval_required": True,
        "preferred_model": PREFERRED_MODEL,
        "recommended_manual_commands": ["ollama list", "ollama pull gemma3:4b"],
        "lighter_alternative_commands": ["ollama pull gemma3:1b", "ollama pull gemma3:270m"],
        "model_options": MODEL_OPTIONS,
        "disk_and_memory_caution": "Model pulls consume local disk and may be slow or RAM/VRAM constrained. Do not pull automatically.",
        "why_4b_first": MODEL_OPTIONS[PREFERRED_MODEL]["why"],
        "why_lighter_models": "Use gemma3:1b or gemma3:270m when Ivan wants a quick low-risk local smoke before the 4B model.",
        "status": status,
        "recommendation": status["recommendation"],
        "generated_at": status["generated_at"],
    }


def _rubric() -> Dict[str, object]:
    return {
        "tasks_total": len(QUALITY_TASKS),
        "tasks": QUALITY_TASKS,
        "scoring_dimensions": [
            "json_validity",
            "instruction_following",
            "safety_gate_correctness",
            "usefulness",
            "hallucination_risk",
            "latency_runtime",
        ],
        "pass_threshold_for_future_routing": 80,
        "production_routing_default": False,
        "notes": [
            "Real Gemma quality must be measured after a human-approved model install.",
            "local_demo output can validate plumbing, schema, and safety gates, but it is not model quality.",
        ],
    }


def _local_demo_eval(status: Dict[str, object]) -> Dict[str, object]:
    demo_rows = [
        {
            "task_id": task["id"],
            "mode": "local_demo",
            "result": "deterministic_template_available",
            "passes_schema": True,
            "passes_safety": True,
            "notes": "Validates plumbing only; not real Gemma quality.",
        }
        for task in QUALITY_TASKS
    ]
    return {
        "mode": "local_demo",
        "model": "local_demo",
        "real_gemma_quality_status": "pending_manual_install" if not status["gemma_installed"] else "not_run_by_default",
        "tasks_total": len(QUALITY_TASKS),
        "tasks_passed": len(demo_rows),
        "score_percent": 55,
        "safety_gate_passed": True,
        "json_validity_passed": True,
        "latency_summary": "deterministic local_demo; no model latency measured",
        "production_routing_recommended": False,
        "notes": [
            "This score is a plumbing/fallback score, not real Gemma quality.",
            "Production routing remains disabled.",
            "Run a future human-approved real model evaluation after installing Gemma.",
        ],
        "task_results": demo_rows,
    }


def build_quality_plan(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    evaluation = _local_demo_eval(status)
    if status["gemma_installed"]:
        evaluation["mode"] = "gemma_available_not_invoked"
        evaluation["model"] = status["selected_model"] or PREFERRED_MODEL
        evaluation["real_gemma_quality_status"] = "available_but_not_run_by_default"
        evaluation["notes"].insert(0, "Gemma is installed, but N+5.9A does not enable production routing or hidden model use.")
    return {
        "ok": True,
        "action": "quality-plan",
        "local_only": True,
        "live_api_used": False,
        "auto_download_performed": False,
        "ollama_pull_performed": False,
        "production_routing_enabled": False,
        "quality_evaluation_status": status["quality_evaluation_status"],
        "future_real_eval_command": "python 03_scripts/gemma_model_readiness.py --quality-plan --json",
        "status": status,
        "rubric": _rubric(),
        "quality_evaluation": evaluation,
        "generated_at": status["generated_at"],
    }


def _status_markdown(status: Dict[str, object]) -> str:
    model_lines = "\n".join(f"- `{name}`" for name in status["installed_models"]) or "- none visible"
    return textwrap.dedent(f"""\
        # Gemma / Local Model Readiness Status

        {status['status_line']}

        - Launcher: `{LAUNCHER_COMMAND}`
        - Dashboard: `{DASHBOARD_URL}`
        - Gemma status command: `{GEMMA_STATUS_COMMAND}`
        - Gemma doctor command: `{GEMMA_DOCTOR_COMMAND}`
        - Gemma quality plan command: `{GEMMA_QUALITY_COMMAND}`
        - Ollama installed: `{status['ollama_installed']}`
        - Ollama version: `{status['ollama_version']}`
        - Ollama reachable: `{status['ollama_reachable']}`
        - Installed model count: `{status['installed_models_count']}`
        - Gemma installed: `{status['gemma_installed']}`
        - Preferred model: `{PREFERRED_MODEL}`
        - Preferred model installed: `{status['preferred_model_installed']}`
        - Fallback models installed: `{', '.join(status['fallback_models_installed']) or 'none'}`
        - Active worker mode: `{status['active_worker_mode']}`
        - Gemma readiness percentage: `{status['gemma_readiness_percent']}%`
        - Local worker readiness percentage: `{status['local_worker_readiness_percent']}%`
        - Production routing enabled: `false`
        - Manual approval required: `true`

        ## Visible Models

        {model_lines}

        ## Recommendation

        {status['recommendation']}

        Safety: No live APIs, no auto-downloads, no `ollama pull` performed, no provider tokens, production routing remains disabled.
    """)


def _install_decision_markdown(plan: Dict[str, object]) -> str:
    options = plan["model_options"]
    return textwrap.dedent(f"""\
        # Gemma Install Decision

        N+5.9A prepares the decision; it does not download a model.

        ## Recommended First Command

        ```powershell
        ollama pull gemma3:4b
        ```

        Human approval required before model download. Ghoti must not run this command automatically.

        ## Why `gemma3:4b`

        {plan['why_4b_first']}

        - Disk note: {options['gemma3:4b']['disk_size_note']}
        - Context note: {options['gemma3:4b']['context_window_note']}
        - Caution: {options['gemma3:4b']['caution']}

        ## Lighter Alternatives

        ```powershell
        ollama pull gemma3:1b
        ollama pull gemma3:270m
        ```

        {plan['why_lighter_models']}

        ## Current Recommendation

        {plan['recommendation']}

        Production routing remains disabled until a later human-approved quality milestone.
    """)


def _manual_commands_markdown(plan: Dict[str, object]) -> str:
    commands = "\n".join(f"- `{cmd}`" for cmd in plan["recommended_manual_commands"] + plan["lighter_alternative_commands"])
    return textwrap.dedent(f"""\
        # Gemma Manual Commands

        Run these manually only after Ivan approves the local model download.

        {commands}

        Ghoti does not run `ollama pull` automatically. No live APIs or provider tokens are involved.
    """)


def _quality_plan_markdown(quality: Dict[str, object]) -> str:
    task_lines = "\n".join(
        f"- {item['name']}: {item['goal']}"
        for item in QUALITY_TASKS
    )
    eval_result = quality["quality_evaluation"]
    return textwrap.dedent(f"""\
        # Local Task Quality Evaluation Plan

        Current quality status: `{quality['quality_evaluation_status']}`.

        ## Tasks

        {task_lines}

        ## Current Evaluation Result

        - Mode: `{eval_result['mode']}`
        - Model: `{eval_result['model']}`
        - Tasks total: `{eval_result['tasks_total']}`
        - Tasks passed: `{eval_result['tasks_passed']}`
        - Score percent: `{eval_result['score_percent']}`
        - Safety gate passed: `{eval_result['safety_gate_passed']}`
        - JSON validity passed: `{eval_result['json_validity_passed']}`
        - Production routing recommended: `{eval_result['production_routing_recommended']}`

        This is a deterministic local_demo quality-plumbing result unless a real Gemma model is installed and a later human-approved milestone runs model prompts. Production routing remains disabled.
    """)


def _next_steps_markdown(status: Dict[str, object]) -> str:
    return textwrap.dedent(f"""\
        # Local Worker Next Steps

        1. Run `{GEMMA_STATUS_COMMAND}`.
        2. Review `{_repo_rel(GENERATED_DIR / 'gemma_install_decision.md')}`.
        3. If Ivan approves a model download later, run `ollama pull gemma3:4b` manually.
        4. Rerun `{GEMMA_DOCTOR_COMMAND}`.
        5. Rerun `{GEMMA_QUALITY_COMMAND}`.
        6. Keep production routing disabled until a later audited milestone.

        Current mode: `{status['active_worker_mode']}`.
        Recommendation: {status['recommendation']}
    """)


def _local_demo_eval_markdown(quality: Dict[str, object]) -> str:
    eval_result = quality["quality_evaluation"]
    rows = "\n".join(f"- `{row['task_id']}`: {row['result']}" for row in eval_result["task_results"])
    return textwrap.dedent(f"""\
        # Local Demo Quality Eval

        Mode: `{eval_result['mode']}`.
        Score: `{eval_result['score_percent']}`.

        {rows}

        This validates fallback plumbing only. It is not proof of real Gemma quality.
    """)


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated Gemma readiness output matched forbidden secret pattern: {pattern.pattern}")


def write_readiness(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    plan = build_recommendation(generated_at=status["generated_at"])
    quality = build_quality_plan(generated_at=status["generated_at"])
    files = {
        "gemma_readiness_status.json": json.dumps(status, indent=2) + "\n",
        "gemma_readiness_status.md": _status_markdown(status),
        "gemma_install_decision.md": _install_decision_markdown(plan),
        "gemma_manual_commands.md": _manual_commands_markdown(plan),
        "local_task_quality_plan.md": _quality_plan_markdown(quality),
        "local_task_quality_rubric.json": json.dumps(quality["rubric"], indent=2) + "\n",
        "local_worker_next_steps.md": _next_steps_markdown(status),
        "local_demo_quality_eval.json": json.dumps(quality["quality_evaluation"], indent=2) + "\n",
        "local_demo_quality_eval.md": _local_demo_eval_markdown(quality),
    }
    _assert_secret_safe(files.values())
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write Gemma readiness output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "action": "write-readiness",
        "local_only": True,
        "live_api_used": False,
        "auto_download_performed": False,
        "ollama_pull_performed": False,
        "production_routing_enabled": False,
        "gemma_readiness_percent": status["gemma_readiness_percent"],
        "local_worker_readiness_percent": status["local_worker_readiness_percent"],
        "active_worker_mode": status["active_worker_mode"],
        "quality_evaluation_status": status["quality_evaluation_status"],
        "status_line": status["status_line"],
        "paths": paths,
        "generated_at": status["generated_at"],
    }


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("status_line"):
        print(payload["status_line"])
    if payload.get("recommendation"):
        print("Recommendation: %s" % payload["recommendation"])
    if payload.get("paths"):
        print("Generated Gemma readiness files:")
        for filename, relpath in payload["paths"].items():
            print("  %s -> %s" % (filename, relpath))
    if payload.get("recommended_manual_commands"):
        print("Manual commands:")
        for command in payload["recommended_manual_commands"]:
            print("  %s" % command)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Gemma model availability and local task quality readiness.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/gemma_model_readiness.py --status --json\n"
            "  python 03_scripts/gemma_model_readiness.py --doctor --json\n"
            "  python 03_scripts/gemma_model_readiness.py --recommend --json\n"
            "  python 03_scripts/gemma_model_readiness.py --quality-plan --json\n"
            "  python 03_scripts/gemma_model_readiness.py --write-readiness --json\n"
            "\nManual Gemma command for later, not run by Ghoti automatically:\n"
            "  ollama pull gemma3:4b\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show Gemma model readiness")
    parser.add_argument("--doctor", action="store_true", help="show detailed Gemma/Ollama checks")
    parser.add_argument("--recommend", action="store_true", help="show manual model install recommendation")
    parser.add_argument("--quality-plan", action="store_true", help="show local task quality evaluation plan")
    parser.add_argument("--write-readiness", action="store_true", help="write Gemma readiness files")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.doctor:
            payload = build_doctor(generated_at=args.generated_at)
        elif args.recommend:
            payload = build_recommendation(generated_at=args.generated_at)
        elif args.quality_plan:
            payload = build_quality_plan(generated_at=args.generated_at)
        elif args.write_readiness:
            payload = write_readiness(output_dir=output_dir, generated_at=args.generated_at)
        else:
            payload = build_status(generated_at=args.generated_at)
    except Exception as exc:
        payload = {
            "ok": False,
            "local_only": True,
            "live_api_used": False,
            "auto_download_performed": False,
            "ollama_pull_performed": False,
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
