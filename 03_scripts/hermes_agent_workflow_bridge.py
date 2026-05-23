#!/usr/bin/env python3
"""Safe Hermes Agent manual bridge readiness lane.

N+5.8A makes Hermes understandable and inspectable without doing live setup.
This script only runs safe local WSL probes, writes local JSON/Markdown
readiness files, and keeps provider setup, Telegram, tokens, live APIs, and
browser automation out of scope.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap
from typing import Dict, Iterable, List


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
GENERATED_DIR = REPO_ROOT / "14_context" / "hermes_workflow" / "generated"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"
HERMES_BRIDGE_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json"
HERMES_BRIDGE_WRITE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json"
DIRECT_STATUS_COMMAND = "python 03_scripts/hermes_agent_workflow_bridge.py --status --json"
DIRECT_WRITE_COMMAND = "python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json"
HERMES_LOCAL_BOOTSTRAP_COMMAND = "python 03_scripts/hermes_local_bootstrap.py --status --json"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
REPO_BUNDLE_HERMES_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-bundle hermes --json"

EXPECTED_HERMES_PATH = "/home/ai_sandbox/.local/bin/hermes"
EXPECTED_HERMES_VERSION_HINT = "v0.14.0"
READINESS_WITH_CORE_AND_SKILLS = 58
READINESS_WITH_CORE_ONLY = 50
READINESS_WITH_WSL_ONLY = 25
READINESS_UNAVAILABLE = 15

SAFE_COMMANDS = [
    'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"',
    'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"',
    'wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"',
    HERMES_LOCAL_BOOTSTRAP_COMMAND,
    DIRECT_STATUS_COMMAND,
    DIRECT_WRITE_COMMAND,
]

BLOCKED_COMMANDS = [
    "hermes setup",
    "hermes login",
    "hermes auth",
    "hermes pairing",
    "provider config",
    "Telegram setup",
    "token commands",
    "live provider API calls",
    "browser automation",
]

TRACKED_SKILLS = [
    {
        "name": "codex",
        "category": "coding/audit",
        "future_use": "Possible Hermes Codex provider/operator skill after manual provider verification.",
        "status_now": "manual later - Codex provider pending/not proven",
    },
    {
        "name": "claude-code",
        "category": "coding",
        "future_use": "Implementation lane when Claude Code credits/tooling are available.",
        "status_now": "manual later",
    },
    {
        "name": "hermes-agent",
        "category": "Hermes core",
        "future_use": "Local Hermes agent workflow layer.",
        "status_now": "safe to inspect only",
    },
    {
        "name": "mcp",
        "category": "tool protocol",
        "future_use": "Future provider/tool bridge through audited MCP workflows.",
        "status_now": "planning only",
    },
    {
        "name": "memory",
        "category": "memory",
        "future_use": "Compact memory and Obsidian-like workflow support.",
        "status_now": "safe to plan; repo memory remains file-based",
    },
    {
        "name": "obsidian",
        "category": "memory",
        "future_use": "Obsidian-style local memory workflows.",
        "status_now": "safe to plan; no external API",
    },
    {
        "name": "github",
        "category": "repo workflow",
        "future_use": "GitHub workflow assistance after explicit approval gates.",
        "status_now": "planning/local docs only",
    },
    {
        "name": "plan",
        "category": "planning",
        "future_use": "Structured planning and handoff workflows.",
        "status_now": "safe to inspect",
    },
    {
        "name": "test-driven-development",
        "category": "engineering",
        "future_use": "Test-first development pattern support.",
        "status_now": "safe to inspect",
    },
    {
        "name": "browser",
        "category": "computer-use",
        "future_use": "Future browser/computer-use research after remediation.",
        "status_now": "manual later - browser/Playwright degraded/not claimed",
    },
    {
        "name": "computer-use",
        "category": "computer-use",
        "future_use": "Future audited observe/click/type work.",
        "status_now": "blocked for control; observation-only in Ghoti",
    },
    {
        "name": "youtube",
        "category": "content",
        "future_use": "Content workflow planning after approvals.",
        "status_now": "planning only - no posting",
    },
]

OUTPUT_FILES = {
    "hermes_workflow_status.json": "status_json",
    "hermes_workflow_status.md": "status_markdown",
    "hermes_skills_index.json": "skills_json",
    "hermes_skills_index.md": "skills_markdown",
    "hermes_manual_setup_checklist.md": "manual_setup_checklist",
    "hermes_safe_next_steps.md": "safe_next_steps",
    "hermes_codex_provider_plan.md": "codex_provider_plan",
    "hermes_telegram_manual_plan.md": "telegram_manual_plan",
    "hermes_browser_playwright_remediation_plan.md": "browser_playwright_remediation_plan",
    "hermes_operator_bridge_packet.md": "operator_bridge_packet",
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
    if not shutil.which("wsl"):
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "wsl executable not found",
            "command": command,
        }
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
    ubuntu = _wsl_probe("true", timeout=8)
    if not ubuntu["ok"]:
        return {
            "wsl_available": bool(shutil.which("wsl")),
            "ubuntu_available": False,
            "path_probe": "",
            "version_probe": "",
            "skills_probe": "",
            "probe_error": ubuntu["stderr"] or "Ubuntu WSL unavailable",
        }
    path_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true", timeout=10)
    version_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true", timeout=10)
    skills_probe = _wsl_probe("source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true", timeout=20)
    return {
        "wsl_available": True,
        "ubuntu_available": True,
        "path_probe": path_probe["stdout"].strip(),
        "version_probe": (version_probe["stdout"] or version_probe["stderr"]).strip(),
        "skills_probe": (skills_probe["stdout"] or skills_probe["stderr"]).strip(),
        "probe_error": "",
    }


def _parse_skills(raw: str) -> List[Dict[str, object]]:
    skills: List[Dict[str, object]] = []
    seen = set()
    for line in raw.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if "│" in cleaned:
            columns = [part.strip() for part in cleaned.split("│") if part.strip()]
            if not columns:
                continue
            if columns[0].lower() in {"name", "installed"}:
                continue
            name = columns[0].strip("`:,|")
            if not name or not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$", name):
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            skills.append({
                "name": name,
                "line": cleaned[:240],
            })
            continue
        lowered = cleaned.lower()
        if "available skills" in lowered or lowered.startswith("name ") or lowered.startswith("---"):
            continue
        cleaned = cleaned.lstrip("-* ").strip()
        name = cleaned.split()[0].strip("`:,|")
        if name.lower() in {"installed", "name"}:
            continue
        if not name or not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$", name):
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        skills.append({
            "name": name,
            "line": cleaned[:240],
        })
    return skills


def _classify_important_skills(skills: List[Dict[str, object]]) -> List[Dict[str, object]]:
    haystack = "\n".join(f"{item['name']} {item.get('line', '')}" for item in skills).lower()
    indexed = []
    for tracked in TRACKED_SKILLS:
        name = tracked["name"]
        detected = name.lower() in haystack
        indexed.append({
            **tracked,
            "detected": detected,
            "safe_now": tracked["status_now"] in {"safe to inspect only", "safe to inspect"},
        })
    return indexed


def build_skills_index(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    probes = _safe_wsl_probes()
    raw = str(probes.get("skills_probe") or "")
    skills = _parse_skills(raw)
    important = _classify_important_skills(skills)
    status = "visible" if skills else "unavailable"
    return {
        "ok": True,
        "action": "skills-index",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "skills_status": status,
        "skills_count": len(skills),
        "skills": skills,
        "important_skill_names": [item["name"] for item in important],
        "important_skills": important,
        "raw_line_count": len(raw.splitlines()),
        "generated_at": created,
    }


def build_status(generated_at: str | None = None) -> Dict[str, object]:
    created = generated_at or _utc_now()
    probes = _safe_wsl_probes()
    path = (str(probes.get("path_probe") or "").splitlines() or [""])[0].strip()
    version = (str(probes.get("version_probe") or "").splitlines() or [""])[0].strip()
    installed = bool(path)
    skills = _parse_skills(str(probes.get("skills_probe") or ""))
    if installed and skills:
        readiness = READINESS_WITH_CORE_AND_SKILLS
    elif installed:
        readiness = READINESS_WITH_CORE_ONLY
    elif probes.get("ubuntu_available"):
        readiness = READINESS_WITH_WSL_ONLY
    else:
        readiness = READINESS_UNAVAILABLE
    status_line = (
        f"Hermes workflow readiness: {readiness}%. Hermes core is installed and skills are "
        "visible. Provider setup, Telegram, browser/Playwright, and Codex provider verification "
        "remain manual/unproven. Ghoti exposes status, skills index, manual setup plan, and "
        "future bridge packet with safe probes only and no live provider setup."
        if installed and skills else
        f"Hermes workflow readiness: {readiness}%. Hermes core status is "
        f"{'installed' if installed else 'not fully available'}; skills are "
        f"{'visible' if skills else 'not visible'}. Provider setup, Telegram, browser/Playwright, "
        "and Codex provider verification remain manual/unproven. Safe probes only."
    )
    return {
        "ok": True,
        "action": "status",
        "lane": "hermes_agent_manual_bridge",
        "milestone": "N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness",
        "local_only": True,
        "network_required": False,
        "live_api_used": False,
        "external_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "browser_automation_run": False,
        "setup_commands_run": False,
        "installed": installed,
        "wsl_available": bool(probes.get("wsl_available")),
        "ubuntu_available": bool(probes.get("ubuntu_available")),
        "path": path or "not found",
        "expected_path": EXPECTED_HERMES_PATH,
        "version": version or "not found",
        "expected_version_hint": EXPECTED_HERMES_VERSION_HINT,
        "skills_status": "visible" if skills else "unavailable",
        "skills_count": len(skills),
        "important_skills_detected": [item["name"] for item in _classify_important_skills(skills) if item["detected"]],
        "readiness_percent": readiness,
        "status_line": status_line,
        "codex_provider_status": "pending/not proven",
        "telegram_status": "manual later/no token",
        "browser_playwright_status": "degraded/not claimed",
        "provider_setup_status": "manual later",
        "no_vps": True,
        "safe_commands": SAFE_COMMANDS,
        "blocked_commands": BLOCKED_COMMANDS,
        "next_human_steps": _manual_steps(),
        "output_paths": {filename: _repo_rel(GENERATED_DIR / filename) for filename in OUTPUT_FILES},
        "confidence": "medium" if installed else "low",
        "generated_at": created,
        "probe_error": probes.get("probe_error") or "",
        "safety": _safety_flags(),
    }


def _manual_steps() -> List[str]:
    return [
        "Run the Hermes bridge status command and review generated files.",
        "Review the Hermes skills index to understand what is visible locally.",
        "Only after human-approved setup, decide whether to verify provider support.",
        "Keep Codex provider verification manual until a safe Hermes command proves support.",
        "Keep Telegram setup manual later; do not place tokens in git.",
        "Treat browser/Playwright as degraded/not claimed until a later remediation milestone verifies it.",
    ]


def _safety_flags() -> Dict[str, bool]:
    return {
        "no_live_apis": True,
        "no_provider_setup": True,
        "no_telegram_setup": True,
        "no_tokens_read": True,
        "no_browser_automation": True,
        "no_vps": True,
        "safe_probes_only": True,
    }


def build_doctor(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    checks = [
        {
            "name": "WSL executable",
            "ok": bool(status["wsl_available"]),
            "detail": "available" if status["wsl_available"] else "not found",
        },
        {
            "name": "Ubuntu distro",
            "ok": bool(status["ubuntu_available"]),
            "detail": "available" if status["ubuntu_available"] else "not available",
        },
        {
            "name": "Hermes command",
            "ok": bool(status["installed"]),
            "detail": status["path"],
        },
        {
            "name": "Hermes version",
            "ok": status["version"] != "not found",
            "detail": status["version"],
        },
        {
            "name": "Skills list",
            "ok": status["skills_count"] > 0,
            "detail": f"{status['skills_count']} skill line(s) visible",
        },
        {
            "name": "Safety",
            "ok": True,
            "detail": "safe probes only; no provider setup, no Telegram setup, no tokens, no live APIs",
        },
    ]
    status.update({
        "action": "doctor",
        "checks": checks,
        "manual_next_commands": [
            HERMES_BRIDGE_STATUS_COMMAND,
            HERMES_BRIDGE_WRITE_COMMAND,
            DIRECT_STATUS_COMMAND,
            DIRECT_WRITE_COMMAND,
        ],
        "troubleshooting": [
            "If WSL is missing, install/enable WSL manually before using the Hermes lane.",
            "If Ubuntu is missing, install the Ubuntu distro manually and rerun status.",
            "If Hermes is missing, review the installer plan first; do not ask Codex to run setup.",
            "If skills are unavailable, keep Hermes as manual bridge pending and use context packs/repo bundles.",
            "If browser/Playwright fails, keep it not claimed until a remediation milestone verifies it.",
        ],
    })
    return status


def build_manual_plan(generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    return {
        "ok": True,
        "action": "manual-plan",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "readiness_percent": status["readiness_percent"],
        "manual_steps": _manual_steps(),
        "blocked_until_later": [
            "provider setup",
            "Codex provider verification",
            "Telegram setup",
            "token entry",
            "browser/Playwright automation",
            "live provider API calls",
        ],
        "safe_now": [
            "Run safe WSL Hermes probes.",
            "Generate Hermes readiness files.",
            "Use repo knowledge Hermes bundle.",
            "Paste generated setup checklist into a human planning chat.",
        ],
        "generated_at": status["generated_at"],
        "safety": _safety_flags(),
    }


def _strip(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def _status_markdown(status: Dict[str, object]) -> str:
    return _strip(f"""
        # Hermes Agent / Manual Bridge Status

        {status['status_line']}

        - Launcher: `{LAUNCHER_COMMAND}`
        - Dashboard: `{DASHBOARD_URL}`
        - Hermes bridge status: `{HERMES_BRIDGE_STATUS_COMMAND}`
        - Hermes bridge write: `{HERMES_BRIDGE_WRITE_COMMAND}`
        - Direct status: `{DIRECT_STATUS_COMMAND}`
        - Direct write: `{DIRECT_WRITE_COMMAND}`
        - Installed: `{status['installed']}`
        - WSL path: `{status['path']}`
        - Version: `{status['version']}`
        - Skills detected: `{status['skills_count']}`
        - Readiness percentage: `{status['readiness_percent']}%`
        - Codex provider pending/not proven
        - Telegram manual later/no token
        - browser/Playwright degraded/not claimed
        - No VPS: `{status['no_vps']}`

        Safety: safe probes only, no live provider setup, no provider config,
        no Telegram setup, no tokens, no browser automation, no live APIs.
    """)


def _skills_markdown(skills_payload: Dict[str, object]) -> str:
    rows = []
    for item in skills_payload["important_skills"]:
        rows.append(
            f"- `{item['name']}` [{item['category']}]: detected={item['detected']}; "
            f"now={item['status_now']}; later={item['future_use']}"
        )
    skill_lines = "\n".join(rows) or "- No important skills could be classified."
    raw_skills = "\n".join(f"- `{item['name']}`: {item['line']}" for item in skills_payload["skills"][:80])
    if not raw_skills:
        raw_skills = "- Hermes skills list unavailable; keep this lane manual/pending."
    return _strip(f"""
        # Hermes Skills Index

        - Status: `{skills_payload['skills_status']}`
        - Skills count: `{skills_payload['skills_count']}`
        - Local only: `{skills_payload['local_only']}`
        - Safe probes only: true

        ## Important Ghoti Skills

        {skill_lines}

        ## Visible Skill Lines

        {raw_skills}
    """)


def _manual_setup_checklist(plan: Dict[str, object]) -> str:
    steps = "\n".join(f"- {item}" for item in plan["manual_steps"])
    blocked = "\n".join(f"- {item}" for item in plan["blocked_until_later"])
    safe_now = "\n".join(f"- {item}" for item in plan["safe_now"])
    return _strip(f"""
        # Hermes Manual Provider Setup Checklist

        This is a human checklist for later. Codex did not run Hermes setup,
        provider config, Telegram setup, token commands, live APIs, or browser
        automation.

        ## Safe Now

        {safe_now}

        ## Manual Later

        {steps}

        ## Blocked Until Later

        {blocked}
    """)


def _safe_next_steps(status: Dict[str, object]) -> str:
    steps = "\n".join(f"- {item}" for item in status["next_human_steps"])
    safe = "\n".join(f"- `{item}`" for item in SAFE_COMMANDS)
    blocked = "\n".join(f"- `{item}`" for item in BLOCKED_COMMANDS)
    return _strip(f"""
        # Hermes Safe Next Steps

        Hermes workflow readiness: {status['readiness_percent']}%.

        ## Safe probes only

        {safe}

        ## Human next steps

        {steps}

        ## Blocked commands

        {blocked}
    """)


def _codex_provider_plan(status: Dict[str, object]) -> str:
    return _strip(f"""
        # Hermes Codex Provider Plan

        Codex provider pending/not proven.

        Do not claim Codex provider support because the presence of a Hermes
        `codex` skill does not prove provider support. A later human-approved
        milestone can inspect safe Hermes docs/commands and then decide whether
        to configure a provider.

        Current bridge status:

        - Hermes installed: `{status['installed']}`
        - Hermes path: `{status['path']}`
        - Hermes version: `{status['version']}`
        - Skills count: `{status['skills_count']}`
        - Readiness: `{status['readiness_percent']}%`

        No live provider setup was run.
    """)


def _telegram_plan() -> str:
    return _strip("""
        # Hermes Telegram Manual Plan

        Telegram manual later/no token.

        A later human-approved setup can create a bot token and chat ID outside
        git. Codex must not generate, request, store, or commit tokens. No
        Telegram setup command was run in this milestone.
    """)


def _browser_plan() -> str:
    return _strip("""
        # Hermes Browser / Playwright Remediation Plan

        browser/Playwright degraded/not claimed.

        This milestone does not run browser automation. A later remediation
        milestone can verify local dependencies, inspect error output, and prove
        browser support with a safe local-only check. Until then, Hermes browser
        automation remains not claimed.
    """)


def _operator_packet(status: Dict[str, object], skills: Dict[str, object]) -> str:
    return _strip(f"""
        # Hermes Operator Bridge Packet

        Use this compact packet when planning the Hermes lane with ChatGPT,
        Codex, or Claude.

        - Status: {status['status_line']}
        - Launcher: `{LAUNCHER_COMMAND}`
        - Dashboard: `{DASHBOARD_URL}`
        - Context pack: `{CONTEXT_PACK_COMMAND}`
        - Repo Hermes bundle: `{REPO_BUNDLE_HERMES_COMMAND}`
        - Hermes bridge status: `{HERMES_BRIDGE_STATUS_COMMAND}`
        - Hermes bridge write: `{HERMES_BRIDGE_WRITE_COMMAND}`
        - Skills visible: `{skills['skills_count']}`
        - Codex provider pending/not proven
        - Telegram manual later/no token
        - browser/Playwright degraded/not claimed
        - No VPS

        Safety: safe probes only; no live provider setup; no provider config;
        no Telegram setup; no tokens; no browser automation; no live APIs.
    """)


def _build_files(status: Dict[str, object], skills: Dict[str, object], plan: Dict[str, object]) -> Dict[str, str]:
    return {
        "hermes_workflow_status.json": json.dumps(status, indent=2) + "\n",
        "hermes_workflow_status.md": _status_markdown(status),
        "hermes_skills_index.json": json.dumps(skills, indent=2) + "\n",
        "hermes_skills_index.md": _skills_markdown(skills),
        "hermes_manual_setup_checklist.md": _manual_setup_checklist(plan),
        "hermes_safe_next_steps.md": _safe_next_steps(status),
        "hermes_codex_provider_plan.md": _codex_provider_plan(status),
        "hermes_telegram_manual_plan.md": _telegram_plan(),
        "hermes_browser_playwright_remediation_plan.md": _browser_plan(),
        "hermes_operator_bridge_packet.md": _operator_packet(status, skills),
    }


def _assert_secret_safe(contents: Iterable[str]) -> None:
    combined = "\n".join(contents)
    for pattern in FORBIDDEN_SECRET_PATTERNS:
        if pattern.search(combined):
            raise ValueError(f"generated Hermes bridge output matched forbidden secret pattern: {pattern.pattern}")


def write_readiness(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    skills = build_skills_index(generated_at=status["generated_at"])
    plan = build_manual_plan(generated_at=status["generated_at"])
    files = _build_files(status, skills, plan)
    _assert_secret_safe(files.values())
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}
    for filename, content in files.items():
        dest = output_dir / filename
        if not _is_inside_repo(dest):
            raise ValueError("refusing to write Hermes bridge output outside repo root")
        dest.write_text(content, encoding="utf-8")
        paths[filename] = _repo_rel(dest)
    return {
        "ok": True,
        "action": "write-readiness",
        "local_only": True,
        "live_api_used": False,
        "provider_setup_run": False,
        "telegram_setup_run": False,
        "tokens_read": False,
        "readiness_percent": status["readiness_percent"],
        "status_line": status["status_line"],
        "skills_count": skills["skills_count"],
        "paths": paths,
        "generated_at": status["generated_at"],
    }


def status_payload(output_dir: pathlib.Path, generated_at: str | None = None) -> Dict[str, object]:
    status = build_status(generated_at=generated_at)
    status["exists"] = (output_dir / "hermes_workflow_status.json").exists()
    status["latest_status_path"] = _repo_rel(output_dir / "hermes_workflow_status.md")
    status["latest_skills_index_path"] = _repo_rel(output_dir / "hermes_skills_index.md")
    status["latest_bridge_packet_path"] = _repo_rel(output_dir / "hermes_operator_bridge_packet.md")
    return status


def _print_human(payload: Dict[str, object]) -> None:
    if payload.get("status_line"):
        print(payload["status_line"])
    if payload.get("paths"):
        print("Generated Hermes workflow files:")
        for filename, relpath in payload["paths"].items():
            print(f"  {filename}: {relpath}")
    elif payload.get("checks"):
        print("Hermes doctor checks:")
        for check in payload["checks"]:
            print(f"  - {check['name']}: {check['ok']} ({check['detail']})")
    elif payload.get("manual_steps"):
        print("Hermes manual plan:")
        for step in payload["manual_steps"]:
            print(f"  - {step}")
    else:
        print(json.dumps(payload, indent=2))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Hermes Agent workflow readiness without running live setup.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common commands:\n"
            "  python 03_scripts/hermes_agent_workflow_bridge.py --status --json\n"
            "  python 03_scripts/hermes_agent_workflow_bridge.py --doctor --json\n"
            "  python 03_scripts/hermes_agent_workflow_bridge.py --skills-index --json\n"
            "  python 03_scripts/hermes_agent_workflow_bridge.py --manual-plan --json\n"
            "  python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show Hermes manual bridge status")
    parser.add_argument("--doctor", action="store_true", help="show detailed safe checks")
    parser.add_argument("--skills-index", action="store_true", help="show classified Hermes skills index")
    parser.add_argument("--manual-plan", action="store_true", help="show future manual setup plan")
    parser.add_argument("--write-readiness", action="store_true", help="write Hermes readiness files")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output-dir", help="repo-local output directory override")
    parser.add_argument("--generated-at", help="override generated timestamp for deterministic tests")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
        if args.doctor:
            payload = build_doctor(generated_at=args.generated_at)
        elif args.skills_index:
            payload = build_skills_index(generated_at=args.generated_at)
        elif args.manual_plan:
            payload = build_manual_plan(generated_at=args.generated_at)
        elif args.write_readiness:
            payload = write_readiness(output_dir=output_dir, generated_at=args.generated_at)
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
