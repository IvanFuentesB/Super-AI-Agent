#!/usr/bin/env python3
"""Ghoti local model truth and easy worker lane.

N+5.6A adds a safe local worker lane that can inspect local Ollama/Gemma
readiness and create compact deterministic demo outputs. It never calls live
APIs, never downloads models, and never performs posting/account actions.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
GENERATED_DIR = REPO_ROOT / "14_context" / "local_worker" / "generated"
ROUTING_RUNS_DIR = REPO_ROOT / "14_context" / "local_worker" / "routing_runs"
CONTEXT_PACK_DIR = REPO_ROOT / "14_context" / "compact_memory" / "generated"
REPO_KNOWLEDGE_DIR = REPO_ROOT / "14_context" / "repo_knowledge" / "generated"
OUTPUT_GUARD_SCRIPT = REPO_ROOT / "03_scripts" / "local_model_output_guard.py"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
WORKER_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json"
WORKER_DEMO_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json"
DIRECT_STATUS_COMMAND = "python 03_scripts/local_model_worker_lane.py --status --json"
DIRECT_DEMO_COMMAND = "python 03_scripts/local_model_worker_lane.py --write-demo-output --json"
DIRECT_ROUTING_STATUS_COMMAND = "python 03_scripts/local_model_worker_lane.py --routing-status --json"
DIRECT_ROUTE_TASK_COMMAND = "python 03_scripts/local_model_worker_lane.py --route-task status-paragraph --json"
DIRECT_ROUTING_DEMO_COMMAND = "python 03_scripts/local_model_worker_lane.py --write-routing-demo --json"
PREFERRED_GEMMA_MODEL = "gemma3:4b"
MANUAL_GEMMA_PULL_COMMAND = f"ollama pull {PREFERRED_GEMMA_MODEL}"
MODEL_LIST_COMMAND = "ollama list"

SAFE_DEMO_TASKS = [
    "summarize-latest-report",
    "status-paragraph",
    "classify-next-task",
    "codex-next-prompt",
]

SAFE_ROUTED_TASKS = [
    "summarize-latest-report",
    "status-paragraph",
    "codex-next-prompt",
    "safety-classification",
    "context-bundle-summary",
    "next-milestone-outline",
    "report-to-bullets",
]

BLOCKED_ROUTED_TASKS = [
    "code editing",
    "shell commands",
    "browser actions",
    "API actions",
    "posting",
    "money/trading/legal decisions",
    "credential/session handling",
    "unsupported file claims",
    "live account operations",
]

DEFAULT_ROUTING_DEMO_TASKS = [
    "status-paragraph",
    "context-bundle-summary",
    "safety-classification",
]

OUTPUT_FILES = {
    "local_worker_status.json": "status_json",
    "local_worker_status.md": "status_markdown",
    "latest_report_summary.md": "latest_report_summary",
    "status_paragraph.md": "status_paragraph",
    "codex_next_prompt_from_context.md": "codex_next_prompt",
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


def _run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    if cmd == ["ollama", "--version"]:
        if os.environ.get("GHOTI_LOCAL_WORKER_FAKE_OLLAMA_MISSING") == "1":
            raise FileNotFoundError("ollama")
        fake = os.environ.get("GHOTI_LOCAL_WORKER_FAKE_OLLAMA_VERSION")
        if fake is not None:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=fake, stderr="")
    if cmd == ["ollama", "list"]:
        fake = os.environ.get("GHOTI_LOCAL_WORKER_FAKE_OLLAMA_LIST")
        if fake is not None:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=fake, stderr="")
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


def _parse_ollama_models(stdout: str) -> List[str]:
    models: List[str] = []
    for line in stdout.splitlines():
        columns = line.split()
        if not columns:
            continue
        name = columns[0].strip()
        if name.lower() == "name":
            continue
        models.append(name)
    return models


def probe_ollama() -> Dict[str, object]:
    result: Dict[str, object] = {
        "available": False,
        "version": "not_found",
        "models": [],
        "list_ok": False,
        "probe_error": "",
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
    result["available"] = True
    result["version"] = (version.stdout or "").strip() or "available"

    try:
        listed = _run(["ollama", "list"], timeout=10)
    except FileNotFoundError:
        result["probe_error"] = "ollama list executable lookup failed"
        return result
    except subprocess.TimeoutExpired:
        result["probe_error"] = "ollama list timed out"
        return result
    except OSError as exc:
        result["probe_error"] = f"ollama list failed: {exc}"
        return result
    if listed.returncode != 0:
        result["probe_error"] = (listed.stderr or listed.stdout or "ollama list failed").strip()[:300]
        return result
    result["list_ok"] = True
    result["models"] = _parse_ollama_models(listed.stdout or "")
    return result


def _gemma_truth(models: Iterable[str]) -> Dict[str, object]:
    model_names = list(models)
    preferred = [
        name for name in model_names
        if name.lower() == PREFERRED_GEMMA_MODEL.lower()
    ]
    any_gemma = [name for name in model_names if "gemma" in name.lower()]
    installed = bool(preferred or any_gemma)
    model_name = (preferred or any_gemma or [None])[0]
    return {
        "installed": installed,
        "preferred_model": PREFERRED_GEMMA_MODEL,
        "model_name": model_name,
        "status": "installed" if installed else "missing",
        "manual_install_command": MANUAL_GEMMA_PULL_COMMAND,
        "manual_check_command": MODEL_LIST_COMMAND,
    }


def build_status(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    ollama = probe_ollama()
    gemma = _gemma_truth(ollama.get("models") or [])
    active_mode = "ollama_gemma" if gemma["installed"] else "local_demo"
    readiness = 25
    if ollama["available"]:
        readiness = 45
    if gemma["installed"]:
        readiness = 75
    status_line = (
        "Local worker readiness: %s%%. Ollama is installed (%s), Gemma is installed, "
        "so real local evaluation is possible. Production routing remains gated. "
        "No live APIs, no auto-downloads."
        % (readiness, ollama["version"])
        if gemma["installed"]
        else "Local worker readiness: %s%%. Ollama is %s, Gemma is missing, so Ghoti is using "
        "local_demo fallback. Context packs and deterministic summaries work now; run the "
        "documented manual Gemma command later to unlock real local worker tasks. No live APIs, "
        "no auto-downloads."
        % (readiness, "installed (%s)" % ollama["version"] if ollama["available"] else "not detected")
    )
    return {
        "ok": True,
        "lane": "local_model_easy_worker_lane",
        "milestone": "N+5.6A",
        "local_only": True,
        "network_required": False,
        "live_api_used": False,
        "external_api_used": False,
        "auto_downloads_enabled": False,
        "ollama_pull_run": False,
        "model_downloaded": False,
        "posting_enabled": False,
        "account_actions_enabled": False,
        "launcher_command": LAUNCHER_COMMAND,
        "dashboard_url": DASHBOARD_URL,
        "context_pack_command": CONTEXT_PACK_COMMAND,
        "local_worker_status_command": WORKER_STATUS_COMMAND,
        "local_worker_demo_command": WORKER_DEMO_COMMAND,
        "direct_status_command": DIRECT_STATUS_COMMAND,
        "direct_demo_command": DIRECT_DEMO_COMMAND,
        "main_hash": _current_main_hash(),
        "ollama": ollama,
        "gemma": gemma,
        "active_mode": active_mode,
        "fallback_available": True,
        "readiness_percent": readiness,
        "readiness_label": "real_local_model_available" if gemma["installed"] else "local_demo_fallback_active",
        "status_line": status_line,
        "safe_demo_tasks": SAFE_DEMO_TASKS,
        "manual_next_commands": [
            MODEL_LIST_COMMAND,
            MANUAL_GEMMA_PULL_COMMAND,
            DIRECT_STATUS_COMMAND,
            DIRECT_DEMO_COMMAND,
        ],
        "output_paths": {filename: _repo_rel(GENERATED_DIR / filename) for filename in OUTPUT_FILES},
        "safety": {
            "no_live_apis": True,
            "no_auto_downloads": True,
            "no_posting": True,
            "no_account_actions": True,
            "no_money_trading_legal": True,
            "no_bot_captcha_cloak_bypass": True,
        },
        "generated_at": created,
    }


def build_doctor(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    checks = [
        {
            "name": "Ollama executable",
            "ok": bool(status["ollama"]["available"]),
            "detail": status["ollama"]["version"] if status["ollama"]["available"] else status["ollama"].get("probe_error") or "not found",
        },
        {
            "name": "Ollama model list",
            "ok": bool(status["ollama"].get("list_ok")),
            "detail": "%s model(s) visible" % len(status["ollama"].get("models") or [])
            if status["ollama"].get("list_ok") else status["ollama"].get("probe_error") or "not listed",
        },
        {
            "name": "Gemma model",
            "ok": bool(status["gemma"]["installed"]),
            "detail": status["gemma"]["model_name"] or "missing; local_demo fallback active",
        },
        {
            "name": "Safety",
            "ok": True,
            "detail": "no live APIs, no auto-downloads, no posting, no account actions",
        },
    ]
    status.update({
        "action": "doctor",
        "checks": checks,
        "troubleshooting": [
            "If Ollama is missing, install it manually before using local model tasks.",
            "If Ollama is installed but not responding, start the local Ollama service and rerun --doctor.",
            "If Gemma is missing, run the documented manual command later; Ghoti will not run ollama pull automatically.",
            "If output files are stale, run --write-demo-output again and refresh the dashboard.",
        ],
    })
    return status


def discover_latest_report() -> pathlib.Path | None:
    context_dir = REPO_ROOT / "14_context"
    try:
        reports = [path for path in context_dir.glob("codex_*.md") if path.is_file()]
    except Exception:
        reports = []
    if not reports:
        return None
    return max(reports, key=lambda path: (path.stat().st_mtime, path.name))


def _read_text(path: pathlib.Path, limit: int = 6000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def _latest_report_summary() -> Dict[str, object]:
    report = discover_latest_report()
    if report is None:
        text = (
            "# Latest Report Summary\n\n"
            "No `14_context/codex_*.md` report was found. Generate or audit the next milestone, "
            "then rerun the local worker lane.\n"
        )
        return {"path": None, "text": text}
    body = _read_text(report)
    interesting: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if (
            "clean pass" in lowered
            or "blocked" in lowered
            or "final verdict" in lowered
            or "origin/main" in lowered
            or "feature branch" in lowered
            or "audit branch" in lowered
            or "launcher command" in lowered
            or "dashboard url" in lowered
            or "public audit" in lowered
            or "tests" in lowered
        ):
            interesting.append(stripped)
        if len(interesting) >= 10:
            break
    if not interesting:
        interesting = body.splitlines()[:8]
    text = "# Latest Report Summary\n\n"
    text += f"Source: `{_repo_rel(report)}`\n\n"
    text += "\n".join(f"- {item}" for item in interesting if item.strip())
    text += "\n\nThis is a deterministic local_demo summary. No live APIs were used.\n"
    return {"path": _repo_rel(report), "text": text}


def _status_markdown(status: Dict[str, object]) -> str:
    models = status["ollama"].get("models") or []
    model_lines = "\n".join(f"- `{name}`" for name in models[:12]) or "- none visible"
    return textwrap.dedent(f"""\
        # Local Model / Easy Worker Lane Status

        {status['status_line']}

        - Launcher: `{LAUNCHER_COMMAND}`
        - Dashboard: `{DASHBOARD_URL}`
        - Context pack: `{CONTEXT_PACK_COMMAND}`
        - Local worker status: `{WORKER_STATUS_COMMAND}`
        - Local worker demo: `{WORKER_DEMO_COMMAND}`
        - Active mode: `{status['active_mode']}`
        - Ollama available: `{status['ollama']['available']}`
        - Ollama version: `{status['ollama']['version']}`
        - Gemma installed: `{status['gemma']['installed']}`
        - Gemma model: `{status['gemma']['model_name'] or 'missing'}`
        - Manual check command: `{MODEL_LIST_COMMAND}`
        - Manual install command: `{MANUAL_GEMMA_PULL_COMMAND}`

        ## Visible Local Models

        {model_lines}

        Safety: no live APIs, no auto-downloads, no posting, no account actions.
    """)


def _status_paragraph(status: Dict[str, object]) -> str:
    return (
        f"{status['status_line']} Launch with `{LAUNCHER_COMMAND}`. Refresh memory with "
        f"`{CONTEXT_PACK_COMMAND}`. Check the worker with `{WORKER_STATUS_COMMAND}` or write "
        f"demo outputs with `{WORKER_DEMO_COMMAND}`. Safe tasks now: "
        f"{', '.join(SAFE_DEMO_TASKS)}. This lane is local-only with no live APIs and no auto-downloads."
    )


def _classify_next_task(text: str | None = None) -> str:
    source = (text or "N+5.7A Graphify / Repo Knowledge Map + Better Context Retrieval").lower()
    labels: List[str] = []
    for label, needles in [
        ("coding", ["script", "dashboard", "endpoint", "test", "implementation", "worker"]),
        ("docs", ["doc", "guide", "readme", "playbook"]),
        ("audit", ["audit", "validate", "merge gate", "security"]),
        ("content", ["content", "thumbnail", "title", "preview"]),
        ("research", ["graphify", "knowledge", "retrieval", "roadmap", "research"]),
    ]:
        if any(needle in source for needle in needles):
            labels.append(label)
    if not labels:
        labels.append("research")
    return (
        "# Next Task Classification\n\n"
        f"Input: `{text or 'N+5.7A Graphify / Repo Knowledge Map + Better Context Retrieval'}`\n\n"
        f"Classification: {', '.join(labels)}.\n\n"
        "Recommended handling: create a repo-contained worktree, write focused tests first, "
        "avoid live APIs, and keep any external tool intake static until approved.\n"
    )


def _codex_next_prompt() -> str:
    prompt_path = CONTEXT_PACK_DIR / "ghoti_codex_next_prompt.md"
    prompt = _read_text(prompt_path, limit=3000).strip()
    if not prompt:
        prompt = "Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary worktree read-only except inspection."
    excerpt = prompt
    if len(excerpt) > 1800:
        excerpt = excerpt[:1800].rsplit("\n", 1)[0].rstrip()
        excerpt += "\n\n[excerpt truncated; run the context-pack command for the full prompt.]"
    return textwrap.dedent(f"""\
        Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

        Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary worktree read-only except inspection.
        Refresh context first with `{CONTEXT_PACK_COMMAND}` and inspect latest reports under `14_context/`.

        Local worker truth:
        - Run `{WORKER_STATUS_COMMAND}` to check Ollama/Gemma/local_demo mode.
        - Run `{WORKER_DEMO_COMMAND}` to refresh compact deterministic demo outputs.
        - Do not run `ollama pull`, live APIs, providers, Telegram, posting, or account actions unless the human explicitly approves later.

        Context prompt excerpt:

        {excerpt}
    """)


def run_demo_task(task: str, generated_at: str | None = None, task_text: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    normalized = task.strip().lower()
    if normalized not in SAFE_DEMO_TASKS:
        return {
            "ok": False,
            "local_only": True,
            "external_api_used": False,
            "task": task,
            "error": "unsupported demo task",
            "safe_demo_tasks": SAFE_DEMO_TASKS,
            "generated_at": status["generated_at"],
        }
    if normalized == "summarize-latest-report":
        summary = _latest_report_summary()
        text = summary["text"]
        extra = {"source_report": summary["path"]}
    elif normalized == "status-paragraph":
        text = _status_paragraph(status)
        extra = {}
    elif normalized == "classify-next-task":
        text = _classify_next_task(task_text)
        extra = {}
    else:
        text = _codex_next_prompt()
        extra = {"source_context_prompt": _repo_rel(CONTEXT_PACK_DIR / "ghoti_codex_next_prompt.md")}
    payload = {
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "live_api_used": False,
        "auto_downloads_enabled": False,
        "ollama_pull_run": False,
        "task": normalized,
        "active_mode": status["active_mode"],
        "readiness_percent": status["readiness_percent"],
        "text": text,
        "generated_at": status["generated_at"],
    }
    payload.update(extra)
    return payload


def _load_output_guard():
    spec = importlib.util.spec_from_file_location("local_model_output_guard", OUTPUT_GUARD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("local_model_output_guard.py is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _call_ollama_generate(model: str, prompt: str, timeout: int = 60) -> Dict[str, object]:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return {"ok": False, "model": model, "text": "", "latency_seconds": round(time.time() - started, 3), "error": str(exc)}
    except TimeoutError:
        return {"ok": False, "model": model, "text": "", "latency_seconds": round(time.time() - started, 3), "error": "ollama generate timed out"}
    try:
        data = json.loads(raw)
    except Exception as exc:
        return {"ok": False, "model": model, "text": "", "latency_seconds": round(time.time() - started, 3), "error": f"invalid Ollama JSON: {exc}"}
    text = str(data.get("response") or "").strip()
    return {
        "ok": bool(text),
        "model": model,
        "text": text,
        "latency_seconds": round(time.time() - started, 3),
        "error": "" if text else "empty response",
    }


def _latest_routing_manifest() -> pathlib.Path | None:
    try:
        manifests = [path for path in ROUTING_RUNS_DIR.glob("*/00_routing_manifest.json") if path.is_file()]
    except Exception:
        manifests = []
    if not manifests:
        return None
    return max(manifests, key=lambda path: (path.stat().st_mtime, path.as_posix()))


def _task_bundle_path(bundle_id: str) -> str:
    normalized = bundle_id.replace("-", "_")
    return f"14_context/repo_knowledge/generated/task_bundle_{normalized}.md"


def _source_metadata_for_task(task: str) -> Dict[str, object]:
    latest_report = discover_latest_report()
    latest_report_path = _repo_rel(latest_report) if latest_report else "14_context/repo_knowledge/generated/latest_reports_index.md"
    mapping = {
        "summarize-latest-report": {
            "bundle_ids": ["audit-main", "next-milestone"],
            "file_paths": [latest_report_path, _task_bundle_path("next-milestone")],
        },
        "status-paragraph": {
            "bundle_ids": ["next-milestone", "local-model-worker"],
            "file_paths": [_task_bundle_path("next-milestone"), "03_scripts/local_model_worker_lane.py"],
        },
        "codex-next-prompt": {
            "bundle_ids": ["next-milestone", "local-model-worker"],
            "file_paths": [
                "14_context/compact_memory/generated/ghoti_codex_next_prompt.md",
                _task_bundle_path("next-milestone"),
            ],
        },
        "safety-classification": {
            "bundle_ids": ["safety", "next-milestone"],
            "file_paths": [_task_bundle_path("safety"), "docs/BLOCKED_UNSAFE_AUTOMATION.md"],
        },
        "context-bundle-summary": {
            "bundle_ids": ["next-milestone", "local-model-worker", "local-model-routing"],
            "file_paths": [_task_bundle_path("next-milestone"), _task_bundle_path("local-model-worker"), _task_bundle_path("local-model-routing")],
        },
        "next-milestone-outline": {
            "bundle_ids": ["next-milestone", "hermes"],
            "file_paths": [_task_bundle_path("next-milestone"), _task_bundle_path("hermes")],
        },
        "report-to-bullets": {
            "bundle_ids": ["audit-main", "next-milestone"],
            "file_paths": [latest_report_path, _task_bundle_path("next-milestone")],
        },
    }
    metadata = dict(mapping.get(task, mapping["status-paragraph"]))
    metadata["local_only"] = True
    metadata["live_api_used"] = False
    return metadata


def _json_task_output(answer: str, task: str) -> str:
    return json.dumps({
        "answer": answer.strip(),
        "source_metadata": _source_metadata_for_task(task),
    }, indent=2)


def _extract_answer(text: str) -> str:
    try:
        parsed = json.loads(text)
    except Exception:
        return text.strip()
    if isinstance(parsed, dict):
        return str(parsed.get("answer") or parsed.get("summary") or parsed.get("text") or "").strip()
    return text.strip()


def _local_demo_routed_output(task: str, status: Dict[str, object]) -> str:
    if task == "summarize-latest-report":
        summary = _latest_report_summary()
        answer = (
            "Latest report summary from local files only:\n"
            + "\n".join(line for line in summary["text"].splitlines() if line.strip())[:1600]
        )
    elif task == "status-paragraph":
        answer = _status_paragraph(status)
    elif task == "codex-next-prompt":
        answer = _codex_next_prompt()[:2200]
    elif task == "safety-classification":
        answer = (
            "Safe classification: local-only summary or planning task. Blocked if it requests code execution, "
            "browser clicks/typing, live APIs, posting, money/trading/legal actions, credentials, sessions, "
            "bot/captcha/cloak bypass, or unsupported repo/file claims."
        )
    elif task == "context-bundle-summary":
        bundle = _read_text(REPO_KNOWLEDGE_DIR / "task_bundle_next_milestone.md", limit=2400)
        answer = (
            "Use known bundle `next-milestone` for N+6.1A and `local-model-worker` for routing code. "
            "Do not invent bundle IDs or external repositories.\n\n" + bundle[:1400]
        )
    elif task == "next-milestone-outline":
        answer = (
            "Next milestone order: finish N+6.1A guarded local routing, then N+6.2A Hermes manual bridge "
            "verification, then N+6.3A safe computer-use observation harness. Keep no live APIs, no provider "
            "tokens, no Telegram setup, and no autonomous click/type."
        )
    elif task == "report-to-bullets":
        summary = _latest_report_summary()
        bullets = [line.strip("- ").strip() for line in summary["text"].splitlines() if line.strip().startswith("-")]
        answer = "\n".join(f"- {item}" for item in bullets[:10]) or "- No latest report bullets available."
    else:
        answer = "Unsupported routed task."
    return _json_task_output(answer, task)


def _route_prompt(task: str, status: Dict[str, object]) -> str:
    metadata = _source_metadata_for_task(task)
    source_text = ""
    for relpath in metadata["file_paths"]:
        source_text += f"\n\n# Source: {relpath}\n"
        source_text += _read_text(REPO_ROOT / relpath, limit=2200)
    return textwrap.dedent(f"""\
        You are Ghoti's local offline worker. Return ONLY valid JSON with:
        {{
          "answer": "short useful answer",
          "source_metadata": {{
            "bundle_ids": {json.dumps(metadata['bundle_ids'])},
            "file_paths": {json.dumps(metadata['file_paths'])},
            "local_only": true,
            "live_api_used": false
          }}
        }}

        Task: {task}

        Hard constraints:
        - Use only the listed bundle_ids and file_paths.
        - Do not invent repo bundles, external repositories, URLs, files, providers, browser abilities, or setup status.
        - Do not write shell commands to execute, edit files, click/type, post, use accounts, or call live APIs.
        - If unsure, say uncertainty in the answer while keeping the exact source_metadata.

        Current worker status: {status['status_line']}

        Sources:
        {source_text[:5200]}
    """)


def routing_status_payload(output_root: pathlib.Path | None = None, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    latest_manifest = _latest_routing_manifest()
    output_root = output_root or ROUTING_RUNS_DIR
    return {
        "ok": True,
        "action": "routing-status",
        "milestone": "N+6.1A",
        "local_only": True,
        "live_api_used": False,
        "external_api_used": False,
        "auto_downloads_enabled": False,
        "ollama_pull_run": False,
        "provider_setup_performed": False,
        "telegram_setup_performed": False,
        "browser_automation_performed": False,
        "production_routing_enabled": False,
        "guard_enabled": True,
        "source_metadata_required": True,
        "known_bundle_allowlist_source": "14_context/repo_knowledge/generated/repo_knowledge_map.json",
        "routing_enabled_for_safe_tasks": bool(status["gemma"]["installed"]),
        "active_model": status["gemma"]["model_name"] or "local_demo",
        "active_route_preference": "ollama_gemma_guarded" if status["gemma"]["installed"] else "local_demo_fallback",
        "fallback_available": True,
        "safe_routed_tasks": SAFE_ROUTED_TASKS,
        "blocked_routed_tasks": BLOCKED_ROUTED_TASKS,
        "readiness_percent": 82 if status["gemma"]["installed"] else 55,
        "status_line": (
            "Local model routing readiness: 82%. Gemma is installed, guarded safe-task routing is available, "
            "and repo-bundle hallucination guard is enabled. Production routing remains limited to offline safe tasks."
            if status["gemma"]["installed"]
            else "Local model routing readiness: 55%. Gemma is missing, so routing uses local_demo fallback with the same guard shape."
        ),
        "latest_routing_run_path": _repo_rel(latest_manifest.parent) if latest_manifest else _repo_rel(output_root),
        "output_dir": _repo_rel(output_root),
        "generated_at": status["generated_at"],
    }


def route_task(task: str, generated_at: str | None = None) -> Dict[str, object]:
    normalized = task.strip().lower()
    if normalized not in SAFE_ROUTED_TASKS:
        return {
            "ok": False,
            "action": "route-task",
            "local_only": True,
            "live_api_used": False,
            "task": normalized,
            "error": "unsupported routed task",
            "safe_routed_tasks": SAFE_ROUTED_TASKS,
            "blocked_routed_tasks": BLOCKED_ROUTED_TASKS,
            "generated_at": generated_at or _utc_now(),
        }
    status = build_status(generated_at=generated_at)
    guard = _load_output_guard()
    gemma_installed = bool(status["gemma"]["installed"])
    model_name = str(status["gemma"]["model_name"] or PREFERRED_GEMMA_MODEL)
    gemma_generation = {"ok": False, "model": model_name, "text": "", "latency_seconds": None, "error": "gemma not attempted"}
    rejected_model_text = ""
    guard_result: Dict[str, object]
    final_json: str
    active_route = "local_demo_fallback"

    if gemma_installed:
        prompt = _route_prompt(normalized, status)
        gemma_generation = _call_ollama_generate(model_name, prompt, timeout=60)
        if gemma_generation.get("ok"):
            raw_text = str(gemma_generation.get("text") or "")
            validation = guard.validate_model_output(raw_text, task=normalized)
            if validation["status"] in ("pass", "warn"):
                final_json = raw_text
                guard_result = validation
                active_route = "ollama_gemma"
            else:
                rejected_model_text = raw_text
                final_json = _local_demo_routed_output(normalized, status)
                guard_result = guard.fallback_guard_result(validation, "Gemma output rejected; local_demo fallback used.")
        else:
            final_json = _local_demo_routed_output(normalized, status)
            validation = {
                "ok": False,
                "status": "reject",
                "task": normalized,
                "local_only": True,
                "live_api_used": False,
                "bundle_ids": [],
                "file_paths": [],
                "known_bundle_count": 0,
                "known_file_count": 0,
                "reasons": [gemma_generation.get("error") or "Gemma generation failed"],
                "warnings": [],
                "requires_fallback": True,
            }
            guard_result = guard.fallback_guard_result(validation, "Gemma generation failed; local_demo fallback used.")
    else:
        final_json = _local_demo_routed_output(normalized, status)
        guard_result = guard.validate_model_output(final_json, task=normalized)

    return {
        "ok": True,
        "action": "route-task",
        "milestone": "N+6.1A",
        "local_only": True,
        "live_api_used": False,
        "external_api_used": False,
        "auto_downloads_enabled": False,
        "ollama_pull_run": False,
        "provider_setup_performed": False,
        "telegram_setup_performed": False,
        "browser_automation_performed": False,
        "production_routing_enabled": False,
        "task": normalized,
        "safe_routed_tasks": SAFE_ROUTED_TASKS,
        "active_route": active_route,
        "active_model": model_name if active_route == "ollama_gemma" else "local_demo",
        "gemma_attempted": gemma_installed,
        "gemma_generation": gemma_generation,
        "guard_enabled": True,
        "guard_result": guard_result,
        "fallback_available": True,
        "fallback_used": active_route == "local_demo_fallback",
        "text": _extract_answer(final_json),
        "final_output_json": final_json,
        "rejected_model_text": rejected_model_text,
        "generated_at": status["generated_at"],
    }


def _routing_run_dir(output_root: pathlib.Path, generated_at: str | None = None) -> pathlib.Path:
    stamp = re.sub(r"[^0-9A-Za-z]+", "", generated_at or _utc_now()) or "timestamp"
    return output_root / f"{stamp}_guarded_routing_demo"


def write_routing_demo(output_root: pathlib.Path | None = None, generated_at: str | None = None) -> Dict[str, object]:
    root = output_root or ROUTING_RUNS_DIR
    if not _is_inside_repo(root):
        raise ValueError("routing output directory must stay inside repo root")
    created = generated_at or _utc_now()
    run_dir = _routing_run_dir(root, generated_at=created)
    tasks = DEFAULT_ROUTING_DEMO_TASKS
    results = [route_task(task, generated_at=created) for task in tasks]
    manifest = routing_status_payload(output_root=root, generated_at=created)
    manifest.update({
        "action": "write-routing-demo",
        "run_dir": _repo_rel(run_dir),
        "tasks": tasks,
        "guard_statuses": [result["guard_result"]["status"] for result in results],
        "fallback_used": any(result["fallback_used"] for result in results),
    })
    task_inputs = [{"task": task, "source_metadata": _source_metadata_for_task(task)} for task in tasks]
    gemma_outputs = "\n\n".join(
        f"## {result['task']}\n\n{result['gemma_generation'].get('text') or result['gemma_generation'].get('error') or 'not attempted'}"
        for result in results
    )
    guard_results = {
        "ok": True,
        "local_only": True,
        "live_api_used": False,
        "results": [result["guard_result"] for result in results],
    }
    fallback_outputs = "\n\n".join(
        f"## {result['task']}\n\n{result['text']}" for result in results if result["fallback_used"]
    ) or "No fallback was needed in this routing demo.\n"
    final_outputs = "\n\n".join(f"## {result['task']}\n\n{result['text']}" for result in results)
    quality_review = textwrap.dedent(f"""\
        # Guarded Local Routing Quality Review

        - Tasks routed: {len(results)}
        - Guard enabled: true
        - Fallback used: {str(manifest['fallback_used']).lower()}
        - Live APIs used: false
        - Commands executed from model output: false
        - Files edited from model output: false

        N+6.0A hallucination fix: Gemma previously invented a `StableLM-DanceDiffusion`
        bundle and cited an external GitHub URL. N+6.1A now rejects invented bundle IDs,
        unknown source files, URLs, and missing source metadata before a routed answer can
        be accepted.
    """)
    next_steps = textwrap.dedent("""\
        # Next Steps

        Keep N+6.1A limited to offline safe tasks. N+6.2A should verify the Hermes manual
        bridge without tokens or provider setup. N+6.3A should prepare observation-only
        computer-use tests with human approval for every future click/type.
    """)
    files = {
        "00_routing_manifest.json": json.dumps(manifest, indent=2) + "\n",
        "01_task_inputs.json": json.dumps(task_inputs, indent=2) + "\n",
        "02_gemma_outputs.md": gemma_outputs + "\n",
        "03_guard_results.json": json.dumps(guard_results, indent=2) + "\n",
        "04_fallback_outputs.md": fallback_outputs,
        "05_final_outputs.md": final_outputs + "\n",
        "06_quality_review.md": quality_review,
        "07_next_steps.md": next_steps,
    }
    _assert_secret_safe(files.values())
    run_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = run_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write routing demo output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "action": "write-routing-demo",
        "local_only": True,
        "live_api_used": False,
        "guard_enabled": True,
        "safe_routed_tasks": SAFE_ROUTED_TASKS,
        "run_dir": _repo_rel(run_dir),
        "paths": paths,
        "fallback_used": manifest["fallback_used"],
        "guard_statuses": manifest["guard_statuses"],
        "generated_at": created,
    }


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated local worker output matched forbidden secret pattern: {pattern.pattern}")


def write_demo_output(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    report = run_demo_task("summarize-latest-report", generated_at=status["generated_at"])
    status_paragraph = run_demo_task("status-paragraph", generated_at=status["generated_at"])
    codex_prompt = run_demo_task("codex-next-prompt", generated_at=status["generated_at"])
    files = {
        "local_worker_status.json": json.dumps(status, indent=2) + "\n",
        "local_worker_status.md": _status_markdown(status),
        "latest_report_summary.md": report["text"],
        "status_paragraph.md": status_paragraph["text"] + "\n",
        "codex_next_prompt_from_context.md": codex_prompt["text"],
    }
    _assert_secret_safe(files.values())
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write local worker output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "local_only": True,
        "external_api_used": False,
        "live_api_used": False,
        "auto_downloads_enabled": False,
        "ollama_pull_run": False,
        "active_mode": status["active_mode"],
        "readiness_percent": status["readiness_percent"],
        "status_line": status["status_line"],
        "paths": paths,
        "generated_at": status["generated_at"],
    }


def status_payload(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    status["exists"] = (output_dir / "local_worker_status.json").exists()
    status["latest_status_path"] = _repo_rel(output_dir / "local_worker_status.json")
    status["latest_status_markdown_path"] = _repo_rel(output_dir / "local_worker_status.md")
    return status


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("status_line"):
        print(payload["status_line"])
    if payload.get("paths"):
        print("Generated local worker files:")
        for filename, relpath in payload["paths"].items():
            print(f"  {filename}: {relpath}")
    elif payload.get("checks"):
        print("Doctor checks:")
        for check in payload["checks"]:
            print(f"  - {check['name']}: {check['ok']} ({check['detail']})")
    elif payload.get("text"):
        print(payload["text"])
    else:
        print(json.dumps(payload, indent=2))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Ghoti local model readiness and generate safe local worker demo outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/local_model_worker_lane.py --status --json\n"
            "  python 03_scripts/local_model_worker_lane.py --doctor --json\n"
            "  python 03_scripts/local_model_worker_lane.py --demo-task status-paragraph --json\n"
            "  python 03_scripts/local_model_worker_lane.py --write-demo-output --json\n"
            "  python 03_scripts/local_model_worker_lane.py --routing-status --json\n"
            "  python 03_scripts/local_model_worker_lane.py --route-task status-paragraph --json\n"
            "  python 03_scripts/local_model_worker_lane.py --write-routing-demo --json\n"
            "\nManual Gemma command for later, not run by Ghoti automatically:\n"
            f"  {MANUAL_GEMMA_PULL_COMMAND}\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show local model worker readiness")
    parser.add_argument("--doctor", action="store_true", help="show detailed local model checks")
    parser.add_argument("--demo-task", choices=SAFE_DEMO_TASKS, help="run one deterministic safe demo task")
    parser.add_argument("--task-text", help="text to classify for --demo-task classify-next-task")
    parser.add_argument("--write-demo-output", action="store_true", help="write all demo output files")
    parser.add_argument("--routing-status", action="store_true", help="show guarded local model routing status")
    parser.add_argument("--route-task", choices=SAFE_ROUTED_TASKS, help="route one allowlisted local worker task through guard/fallback")
    parser.add_argument("--write-routing-demo", action="store_true", help="write a guarded routing demo run")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.doctor:
            payload = build_doctor(generated_at=args.generated_at)
        elif args.routing_status:
            payload = routing_status_payload(output_root=ROUTING_RUNS_DIR, generated_at=args.generated_at)
        elif args.route_task:
            payload = route_task(args.route_task, generated_at=args.generated_at)
        elif args.write_routing_demo:
            payload = write_routing_demo(output_root=ROUTING_RUNS_DIR, generated_at=args.generated_at)
        elif args.demo_task:
            payload = run_demo_task(args.demo_task, generated_at=args.generated_at, task_text=args.task_text)
        elif args.write_demo_output:
            payload = write_demo_output(output_dir=output_dir, generated_at=args.generated_at)
        else:
            payload = status_payload(output_dir=output_dir, generated_at=args.generated_at)
    except Exception as exc:
        payload = {"ok": False, "local_only": True, "external_api_used": False, "error": str(exc), "generated_at": _utc_now()}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_human(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
