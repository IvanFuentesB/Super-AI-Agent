#!/usr/bin/env python3
"""Ghoti local model truth and easy worker lane.

N+5.6A adds a safe local worker lane that can inspect local Ollama/Gemma
readiness and create compact deterministic demo outputs. It never calls live
APIs, never downloads models, and never performs posting/account actions.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import subprocess
import sys
import textwrap
from typing import Dict, Iterable, List


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
GENERATED_DIR = REPO_ROOT / "14_context" / "local_worker" / "generated"
CONTEXT_PACK_DIR = REPO_ROOT / "14_context" / "compact_memory" / "generated"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
WORKER_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json"
WORKER_DEMO_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json"
DIRECT_STATUS_COMMAND = "python 03_scripts/local_model_worker_lane.py --status --json"
DIRECT_DEMO_COMMAND = "python 03_scripts/local_model_worker_lane.py --write-demo-output --json"
PREFERRED_GEMMA_MODEL = "gemma3:4b"
MANUAL_GEMMA_PULL_COMMAND = f"ollama pull {PREFERRED_GEMMA_MODEL}"
MODEL_LIST_COMMAND = "ollama list"

SAFE_DEMO_TASKS = [
    "summarize-latest-report",
    "status-paragraph",
    "classify-next-task",
    "codex-next-prompt",
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
        "so the local model lane can be enabled for audited local tasks. No live APIs, "
        "no auto-downloads."
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
    return textwrap.dedent(f"""\
        Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

        Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary worktree read-only except inspection.
        Refresh context first with `{CONTEXT_PACK_COMMAND}` and inspect latest reports under `14_context/`.

        Local worker truth:
        - Run `{WORKER_STATUS_COMMAND}` to check Ollama/Gemma/local_demo mode.
        - Run `{WORKER_DEMO_COMMAND}` to refresh compact deterministic demo outputs.
        - Do not run `ollama pull`, live APIs, providers, Telegram, posting, or account actions unless the human explicitly approves later.

        Context prompt excerpt:

        {prompt[:1800]}
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
            "\nManual Gemma command for later, not run by Ghoti automatically:\n"
            f"  {MANUAL_GEMMA_PULL_COMMAND}\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show local model worker readiness")
    parser.add_argument("--doctor", action="store_true", help="show detailed local model checks")
    parser.add_argument("--demo-task", choices=SAFE_DEMO_TASKS, help="run one deterministic safe demo task")
    parser.add_argument("--task-text", help="text to classify for --demo-task classify-next-task")
    parser.add_argument("--write-demo-output", action="store_true", help="write all demo output files")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.doctor:
            payload = build_doctor(generated_at=args.generated_at)
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
