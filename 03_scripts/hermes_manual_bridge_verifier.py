#!/usr/bin/env python3
"""Hermes manual bridge verifier and WSL usage guide.

N+6.2A turns the Hermes lane into a practical manual bridge without running
provider setup, Telegram setup, token flows, live APIs, browser automation, or
computer-use control. It only runs safe WSL probes and writes local guide files.
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
GENERATED_DIR = REPO_ROOT / "14_context" / "hermes_manual_bridge" / "generated"

WINDOWS_REPO_PATH = r"C:\Users\ai_sandbox\Documents\AI_Managed_Only"
WSL_REPO_PATH = "/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only"
WSL_PROMPT_EXAMPLE = "ai_sandbox@Ivan-G14:/mnt/c/Users/ai_sandbox$"
EXPECTED_HERMES_PATH = "/home/ai_sandbox/.local/bin/hermes"
EXPECTED_HERMES_VERSION_HINT = "v0.14.0"
LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
MANUAL_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json"
WSL_GUIDE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json"
SAFE_COMMANDS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json"
DIRECT_WRITE_COMMAND = "python 03_scripts/hermes_manual_bridge_verifier.py --write-guide --json"

SAFE_COMMANDS = [
    {
        "label": "show WSL working directory",
        "command": 'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; pwd"',
        "why": "Confirms Ubuntu WSL opens and shows the current Linux path.",
    },
    {
        "label": "find Hermes",
        "command": 'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"',
        "why": "Read-only command lookup; no setup or login.",
    },
    {
        "label": "print Hermes version",
        "command": 'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"',
        "why": "Read-only version check.",
    },
    {
        "label": "list visible Hermes skills",
        "command": 'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"',
        "why": "Read-only skills view capped at 120 lines.",
    },
    {
        "label": "show Hermes help",
        "command": 'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --help | head -120 || true"',
        "why": "Read-only command surface overview capped at 120 lines.",
    },
    {
        "label": "Ghoti manual bridge status",
        "command": MANUAL_STATUS_COMMAND,
        "why": "Repo-local JSON status wrapper for daily use.",
    },
]

BLOCKED_COMMANDS = [
    {"command": "hermes setup", "reason": "provider/setup flow must be human-approved later"},
    {"command": "hermes login", "reason": "auth flow may request credentials or tokens"},
    {"command": "hermes auth", "reason": "auth/token flow is out of scope"},
    {"command": "hermes auth add", "reason": "token/provider configuration is out of scope"},
    {"command": "hermes provider", "reason": "provider setup is pending/not proven"},
    {"command": "hermes telegram", "reason": "Telegram is manual later/no token"},
    {"command": "hermes whatsapp", "reason": "live account messaging is out of scope"},
    {"command": "hermes browser", "reason": "browser/Playwright is degraded/not claimed"},
    {"command": "hermes computer-use", "reason": "click/type/control is future-gated"},
    {"command": "hermes gateway install", "reason": "external install/runtime wiring needs separate approval"},
    {"command": "hermes mcp install", "reason": "external install/runtime wiring needs separate approval"},
]

IMPORTANT_SKILL_HINTS = [
    "codex",
    "claude-code",
    "hermes-agent",
    "mcp",
    "memory",
    "obsidian",
    "github",
    "plan",
    "test-driven-development",
    "browser",
    "computer-use",
    "youtube",
]

OUTPUT_FILES = [
    "00_hermes_manual_bridge_status.json",
    "01_wsl_usage_guide.md",
    "02_hermes_safe_commands.md",
    "03_hermes_blocked_commands.md",
    "04_hermes_skills_summary.md",
    "05_hermes_agent_bridge_next_steps.md",
    "06_computer_use_roadmap_note.md",
    "07_apple_comparison_manual_bridge_plan.md",
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


def _run(cmd: List[str], timeout: int = 12) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _wsl_probe(command: str, timeout: int = 12) -> Dict[str, object]:
    completed = _run(["wsl", "-d", "Ubuntu", "--", "bash", "-lc", command], timeout=timeout)
    if completed is None:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "probe failed or timed out",
            "command": command,
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "")[:12000],
        "stderr": (completed.stderr or "")[:12000],
        "command": command,
    }


def _safe_wsl_probes() -> Dict[str, object]:
    pwd_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; pwd", timeout=8)
    path_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true", timeout=10)
    version_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true", timeout=10)
    skills_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true", timeout=20)
    help_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; hermes --help | head -120 || true", timeout=12)
    return {
        "wsl_available": bool(pwd_probe["ok"] or path_probe["ok"] or version_probe["ok"] or skills_probe["ok"]),
        "ubuntu_available": bool(pwd_probe["ok"] or path_probe["ok"] or version_probe["ok"] or skills_probe["ok"]),
        "pwd_probe": (pwd_probe["stdout"] or pwd_probe["stderr"]).strip(),
        "path_probe": (path_probe["stdout"] or path_probe["stderr"]).strip(),
        "version_probe": (version_probe["stdout"] or version_probe["stderr"]).strip(),
        "skills_probe": (skills_probe["stdout"] or skills_probe["stderr"]).strip(),
        "help_probe": (help_probe["stdout"] or help_probe["stderr"]).strip(),
        "probe_errors": [
            str(item.get("stderr") or "").strip()
            for item in [pwd_probe, path_probe, version_probe, skills_probe, help_probe]
            if item.get("stderr")
        ],
    }


def _parse_skills(raw: str) -> List[Dict[str, object]]:
    skills: List[Dict[str, object]] = []
    seen = set()
    for line in raw.splitlines():
        cleaned = line.strip().strip("|")
        if not cleaned:
            continue
        if "│" in cleaned:
            parts = [part.strip() for part in cleaned.split("│") if part.strip()]
            cleaned = parts[0] if parts else cleaned
        cleaned = cleaned.lstrip("-* ").strip()
        if not cleaned or cleaned.lower().startswith(("name", "usage", "available")):
            continue
        name = cleaned.split()[0].strip("`:,|")
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$", name or ""):
            continue
        lowered = name.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        skills.append({"name": name, "line": line.strip()[:240]})
    return skills


def _important_skills(skills: List[Dict[str, object]]) -> List[Dict[str, object]]:
    haystack = "\n".join(f"{item['name']} {item.get('line', '')}" for item in skills).lower()
    rows = []
    for hint in IMPORTANT_SKILL_HINTS:
        detected = hint.lower() in haystack
        status = "safe to inspect now" if detected and hint not in {"browser", "computer-use"} else "manual later or blocked"
        if hint in {"browser", "computer-use"}:
            status = "future-gated; no click/type/control now"
        rows.append({
            "name": hint,
            "detected": detected,
            "status_now": status,
        })
    return rows


def _safety_flags() -> Dict[str, bool]:
    return {
        "no_live_apis": True,
        "no_provider_setup": True,
        "no_telegram_setup": True,
        "no_tokens_read": True,
        "no_browser_automation": True,
        "no_computer_use": True,
        "no_vps": True,
        "safe_probes_only": True,
    }


def build_wsl_explain(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    return {
        "ok": True,
        "action": "wsl-explain",
        "local_only": True,
        "live_api_used": False,
        "windows_repo_path": WINDOWS_REPO_PATH,
        "wsl_repo_path": WSL_REPO_PATH,
        "prompt_example": WSL_PROMPT_EXAMPLE,
        "meaning": (
            "From Windows PowerShell, `wsl -d Ubuntu` opens Ubuntu. In WSL, "
            "`/mnt/c/...` is the Linux path for the Windows C: drive. "
            "The prompt shows user@machine:current-linux-directory$."
        ),
        "how_to_open": "wsl -d Ubuntu",
        "how_to_exit": "exit",
        "generated_at": created,
    }


def build_safe_commands(generated_at: str | None = None) -> Dict[str, object]:
    return {
        "ok": True,
        "action": "safe-commands",
        "local_only": True,
        "live_api_used": False,
        "safe_probes_only": True,
        "safe_commands": SAFE_COMMANDS,
        "generated_at": generated_at or _utc_now(),
    }


def build_blocked_commands(generated_at: str | None = None) -> Dict[str, object]:
    return {
        "ok": True,
        "action": "blocked-commands",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_blocked": True,
        "telegram_setup_blocked": True,
        "browser_automation_blocked": True,
        "computer_use_blocked": True,
        "blocked_commands": BLOCKED_COMMANDS,
        "generated_at": generated_at or _utc_now(),
    }


def build_skills_summary(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    probes = _safe_wsl_probes()
    skills = _parse_skills(str(probes.get("skills_probe") or ""))
    return {
        "ok": True,
        "action": "skills-summary",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "skills_count": len(skills),
        "skills_status": "visible" if skills else "unavailable",
        "skills": skills,
        "important_skills": _important_skills(skills),
        "wsl_footer_enabled_builtins": "84 reported previously; not re-proven by this parser unless visible in command output",
        "generated_at": created,
    }


def build_status(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    probes = _safe_wsl_probes()
    skills = _parse_skills(str(probes.get("skills_probe") or ""))
    path = (str(probes.get("path_probe") or "").splitlines() or [""])[0].strip()
    version = (str(probes.get("version_probe") or "").splitlines() or [""])[0].strip()
    installed = bool(path and "not found" not in path.lower() and "failed" not in path.lower())
    if installed and version and skills:
        readiness = 64
    elif installed and version:
        readiness = 58
    elif probes.get("ubuntu_available"):
        readiness = 35
    else:
        readiness = 18
    status_line = (
        f"Hermes manual bridge readiness: {readiness}%. WSL/Hermes can be safely inspected. "
        "Provider setup, Codex provider verification, Telegram, browser/Playwright, and "
        "computer-use control remain manual/unproven or blocked."
    )
    paths = {filename: _repo_rel(GENERATED_DIR / filename) for filename in OUTPUT_FILES}
    return {
        "ok": True,
        "action": "status",
        "lane": "hermes_manual_bridge_wsl_guide",
        "milestone": "N+6.2A - Hermes Agent Manual Bridge Verification + WSL Usage Guide",
        "local_only": True,
        "network_required": False,
        "live_api_used": False,
        "external_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "browser_automation_run": False,
        "computer_use_run": False,
        "setup_commands_run": False,
        "installed": installed,
        "wsl_available": bool(probes.get("wsl_available")),
        "ubuntu_available": bool(probes.get("ubuntu_available")),
        "path": path or "not found",
        "expected_path": EXPECTED_HERMES_PATH,
        "version": version or "not found",
        "expected_version_hint": EXPECTED_HERMES_VERSION_HINT,
        "skills_count": len(skills),
        "important_skills": _important_skills(skills),
        "readiness_percent": readiness,
        "status_line": status_line,
        "codex_provider_status": "pending/not proven",
        "telegram_status": "manual later/no token",
        "browser_playwright_status": "degraded/not claimed",
        "provider_setup_status": "manual later",
        "no_vps": True,
        "wsl_explanation": build_wsl_explain(generated_at=created),
        "safe_commands": SAFE_COMMANDS,
        "blocked_commands": BLOCKED_COMMANDS,
        "next_human_steps": [
            "Use the dashboard Hermes Manual Bridge / WSL Guide card.",
            "Run the safe WSL path/version/skills probes.",
            "Read generated WSL usage and safe/blocked command files.",
            "Keep provider setup, Telegram, tokens, browser automation, and click/type for later audited milestones.",
            "Use Gemma guarded routing for small local text tasks while Hermes remains manual bridge only.",
        ],
        "paths": paths,
        "latest_status_path": paths["00_hermes_manual_bridge_status.json"],
        "wsl_usage_guide_path": paths["01_wsl_usage_guide.md"],
        "safe_commands_path": paths["02_hermes_safe_commands.md"],
        "blocked_commands_path": paths["03_hermes_blocked_commands.md"],
        "apple_plan_path": paths["07_apple_comparison_manual_bridge_plan.md"],
        "confidence": "medium" if installed else "low",
        "generated_at": created,
        "safety": _safety_flags(),
    }


def build_doctor(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    checks = [
        {"name": "WSL Ubuntu", "ok": status["ubuntu_available"], "detail": "available" if status["ubuntu_available"] else "not available"},
        {"name": "Hermes command", "ok": status["installed"], "detail": status["path"]},
        {"name": "Hermes version", "ok": status["version"] != "not found", "detail": status["version"]},
        {"name": "Hermes skills", "ok": status["skills_count"] > 0, "detail": f"{status['skills_count']} parsed skill line(s)"},
        {"name": "Safety", "ok": True, "detail": "safe probes only; no setup/auth/token/Telegram/browser/computer-use"},
    ]
    status.update({
        "action": "doctor",
        "checks": checks,
        "troubleshooting": [
            "If `wsl -d Ubuntu` fails, open Windows Features/WSL manually and retry later.",
            "If Hermes is not found, use the install/provider plan doc; do not run setup from Codex.",
            "If skills are not visible, keep Hermes as manual bridge pending.",
            "If browser/Playwright is needed, wait for the N+6.3A observation harness milestone.",
        ],
    })
    return status


def _strip(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def _md_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _safe_commands_md(payload: Dict[str, object]) -> str:
    rows = "\n".join(f"- `{item['command']}` - {item['why']}" for item in payload["safe_commands"])
    return _strip(f"""
        # Hermes Safe Commands

        These commands are safe now because they are read-only probes or local Ghoti
        status commands. They do not run setup, auth, Telegram, provider config,
        live APIs, browser automation, or computer-use control.

        {rows}

        Safety: safe probes only, no live provider setup.
    """)


def _blocked_commands_md(payload: Dict[str, object]) -> str:
    rows = "\n".join(f"- `{item['command']}` - {item['reason']}" for item in payload["blocked_commands"])
    return _strip(f"""
        # Hermes Blocked Commands

        These commands stay blocked/manual later in N+6.2A.

        {rows}

        Do not run provider setup, auth, Telegram setup, token commands, live
        APIs, browser automation, computer-use click/type, or account actions.
    """)


def _wsl_usage_md(status: Dict[str, object]) -> str:
    explain = status["wsl_explanation"]
    return _strip(f"""
        # WSL Usage Guide For Ghoti

        WSL lets Windows run Ubuntu. From Windows PowerShell, run:

        ```powershell
        wsl -d Ubuntu
        ```

        To leave Ubuntu, type:

        ```bash
        exit
        ```

        ## Path Mapping

        - Windows repo path: `{explain['windows_repo_path']}`
        - WSL repo path: `{explain['wsl_repo_path']}`
        - Prompt example: `{explain['prompt_example']}`

        The `/mnt/c` prefix means the Windows `C:\\` drive from inside Ubuntu.
        A prompt like `{WSL_PROMPT_EXAMPLE}` means user `ai_sandbox`, machine
        `Ivan-G14`, current Linux directory `/mnt/c/Users/ai_sandbox`.

        ## Hermes Truth

        - Hermes path: `{status['path']}`
        - Hermes version: `{status['version']}`
        - Skills detected: `{status['skills_count']}`
        - Readiness: `{status['readiness_percent']}%`

        Safety: safe probes only, no live provider setup, no provider config,
        no Telegram setup, no tokens, no browser automation, no computer-use
        click/type, and no live APIs.
    """)


def _skills_summary_md(payload: Dict[str, object]) -> str:
    important = "\n".join(
        f"- `{item['name']}`: detected={item['detected']}; {item['status_now']}"
        for item in payload["important_skills"]
    )
    visible = "\n".join(f"- `{item['name']}`: {item['line']}" for item in payload["skills"][:80])
    if not visible:
        visible = "- Skills unavailable; keep Hermes manual bridge pending."
    return _strip(f"""
        # Hermes Skills Summary

        - Skills status: `{payload['skills_status']}`
        - Skills count: `{payload['skills_count']}`
        - WSL footer note: `{payload['wsl_footer_enabled_builtins']}`

        ## Important Skills

        {important}

        ## Visible Skills

        {visible}

        Browser/computer-use skills, if visible, are not enabled for control.
        They remain future-gated until a separate audited milestone.
    """)


def _next_steps_md(status: Dict[str, object]) -> str:
    return _strip(f"""
        # Hermes Agent Bridge Next Steps

        {_md_list(status['next_human_steps'])}

        Current status: {status['status_line']}

        Use Gemma guarded routing for small local text tasks. Use Hermes as a
        manual bridge only until provider setup, Codex provider verification,
        Telegram, browser/Playwright, and computer-use are explicitly approved
        and audited.
    """)


def _computer_use_note_md() -> str:
    return _strip("""
        # Hermes To Computer-Use Roadmap Note

        N+6.2A does not run live browser automation or computer-use control.
        The future path is:

        - Keep UI-TARS observation-only.
        - Use Gemma to summarize visible text only after an observation harness exists.
        - Use Hermes as a manual bridge until provider/tool support is proven.
        - Add Browser Harness or Vercel agent-browser only in a later audited milestone.
        - Require human approval for every future click/type/live-account action.

        No bot, CAPTCHA, cloak, cookie, login, purchase, cart, account, posting,
        money, trading, or legal workflow is enabled.
    """)


def _apple_plan_md() -> str:
    return _strip("""
        # Apple Comparison Manual Bridge Plan

        Do not execute this plan now. It is a future N+6.3A+ observation/manual
        approval test design only.

        Goal: open Chrome in Incognito mode, go to the Apple website, navigate
        to Mac, find the newest Mac laptop option, compare it with Mac mini,
        and create a local markdown decision packet.

        Rules:

        - observation-only first
        - manual approval required for every future click and type action
        - no login
        - no purchase
        - no cart
        - no account actions
        - no cookie, CAPTCHA, bot, or cloak bypass
        - no fake user behavior
        - no live APIs
        - no autonomous browser control in N+6.2A
        - no data scraping beyond visible page notes

        Future output packet:

        - product names observed
        - source URL
        - visible specs/prices if available
        - uncertainty notes
        - recommended next human action

        Gemma may summarize visible page text later. Hermes, UI-TARS, Browser
        Harness, or Vercel agent-browser may only orchestrate after a separate
        audited future milestone.
    """)


def _status_json_md(status: Dict[str, object]) -> str:
    return json.dumps(status, indent=2) + "\n"


def _build_files(status: Dict[str, object], skills: Dict[str, object]) -> Dict[str, str]:
    safe = build_safe_commands(generated_at=status["generated_at"])
    blocked = build_blocked_commands(generated_at=status["generated_at"])
    return {
        "00_hermes_manual_bridge_status.json": _status_json_md(status),
        "01_wsl_usage_guide.md": _wsl_usage_md(status),
        "02_hermes_safe_commands.md": _safe_commands_md(safe),
        "03_hermes_blocked_commands.md": _blocked_commands_md(blocked),
        "04_hermes_skills_summary.md": _skills_summary_md(skills),
        "05_hermes_agent_bridge_next_steps.md": _next_steps_md(status),
        "06_computer_use_roadmap_note.md": _computer_use_note_md(),
        "07_apple_comparison_manual_bridge_plan.md": _apple_plan_md(),
    }


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated Hermes manual bridge output matched forbidden secret pattern: {pattern.pattern}")


def write_guide(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    skills = build_skills_summary(generated_at=status["generated_at"])
    files = _build_files(status, skills)
    _assert_secret_safe(files.values())
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write Hermes manual bridge output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "action": "write-guide",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "readiness_percent": status["readiness_percent"],
        "skills_count": skills["skills_count"],
        "status_line": status["status_line"],
        "paths": paths,
        "generated_at": status["generated_at"],
    }


def status_payload(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    payload = build_status(generated_at=generated_at)
    payload["exists"] = (output_dir / "00_hermes_manual_bridge_status.json").exists()
    payload["latest_wsl_usage_guide_path"] = _repo_rel(output_dir / "01_wsl_usage_guide.md")
    payload["latest_safe_commands_path"] = _repo_rel(output_dir / "02_hermes_safe_commands.md")
    payload["latest_blocked_commands_path"] = _repo_rel(output_dir / "03_hermes_blocked_commands.md")
    payload["latest_apple_plan_path"] = _repo_rel(output_dir / "07_apple_comparison_manual_bridge_plan.md")
    return payload


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("status_line"):
        print(payload["status_line"])
    elif payload.get("meaning"):
        print(payload["meaning"])
    else:
        print(json.dumps(payload, indent=2))
    if payload.get("paths"):
        for filename, relpath in payload["paths"].items():
            print(f"{filename}: {relpath}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify Hermes manual bridge and WSL guide with safe probes only.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --status --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --doctor --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --wsl-explain --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --safe-commands --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --blocked-commands --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --skills-summary --json\n"
            "  python 03_scripts/hermes_manual_bridge_verifier.py --write-guide --json\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show Hermes manual bridge status")
    parser.add_argument("--doctor", action="store_true", help="show safe diagnostic checks")
    parser.add_argument("--wsl-explain", action="store_true", help="explain Windows to WSL path mapping")
    parser.add_argument("--safe-commands", action="store_true", help="list safe Hermes/WSL probe commands")
    parser.add_argument("--blocked-commands", action="store_true", help="list blocked/manual-later commands")
    parser.add_argument("--skills-summary", action="store_true", help="summarize visible Hermes skills")
    parser.add_argument("--write-guide", action="store_true", help="write Hermes manual bridge guide files")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.doctor:
            payload = build_doctor(generated_at=args.generated_at)
        elif args.wsl_explain:
            payload = build_wsl_explain(generated_at=args.generated_at)
        elif args.safe_commands:
            payload = build_safe_commands(generated_at=args.generated_at)
        elif args.blocked_commands:
            payload = build_blocked_commands(generated_at=args.generated_at)
        elif args.skills_summary:
            payload = build_skills_summary(generated_at=args.generated_at)
        elif args.write_guide:
            payload = write_guide(output_dir=output_dir, generated_at=args.generated_at)
        else:
            payload = status_payload(output_dir=output_dir, generated_at=args.generated_at)
    except Exception as exc:
        payload = {
            "ok": False,
            "local_only": True,
            "live_api_used": False,
            "provider_setup_run": False,
            "telegram_setup_run": False,
            "tokens_read": False,
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
