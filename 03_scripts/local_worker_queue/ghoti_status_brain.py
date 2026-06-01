#!/usr/bin/env python3
"""Ghoti Status Brain (N+6.15A).

Generate a useful, local, offline status packet for Ghoti. This is the first
genuinely day-to-day-useful local workflow: one command answers "where is the
project, what just happened, what is merged vs. pending, is the computer-use
sandbox ready, how is repo intake going, and what should I do next?".

Hard safety posture (all enforced by construction):
  * Local and offline. No internet, no GitHub CLI, no external API, no account.
  * Git is used read-only only (rev-parse / log / status / branch --show-current).
  * subprocess is always called with an argument list, never a shell string.
  * Optional summarization uses a *local* Ollama Gemma model only if it is already
    installed; otherwise a deterministic local summary is used. No repo contents
    are ever sent to an external API.
  * No live browser, no OS-level input, no Telegram control, no MCP, no auto-send.

This module is import-safe: ``build_status_packet`` can be imported and called by
the local worker queue without triggering any CLI behaviour.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MILESTONE = "N+6.15A"

# This module lives at 03_scripts/local_worker_queue/ghoti_status_brain.py, so the
# repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]

CONTEXT_DIR = REPO_ROOT / "14_context"
TESTS_DIR = REPO_ROOT / "01_projects" / "runtime_mvp" / "tests"
FLAGS_PATH = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"
HERMES_STATUS_PATH = (
    CONTEXT_DIR / "hermes_manual_bridge" / "generated"
    / "00_hermes_manual_bridge_status.json"
)
TELEGRAM_BOT_SCRIPT = (
    REPO_ROOT / "03_scripts" / "telegram_status_bot" / "ghoti_telegram_status_bot.py"
)
CONFINED_RUNNER = (
    REPO_ROOT / "03_scripts" / "computer_use_sandbox"
    / "confined_browser_sandbox_runner.py"
)
SANDBOX_TARGET = (
    CONTEXT_DIR / "computer_use" / "sandbox" / "sandbox_target.html"
)
TOOL_INTAKE_REPORTS = CONTEXT_DIR / "tool_intake" / "repo_intake_reports"
HANDOFF_PATH = (
    CONTEXT_DIR / "agent_handoff_vault" / "04_Logs" / "GHOTI_STATUS_BRAIN_LAST_RUN.md"
)

GEMMA_MODEL = "gemma3:4b"

# Maps each repo-intake candidate to the token that identifies its report file.
INTAKE_CANDIDATES = {
    "Ruflo": "ruflo",
    "TryCUA / CUA": "trycua",
    "Browser Harness": "browser_harness",
    "Vercel agent-browser": "vercel_agent_browser",
    "UI-TARS": "ui_tars",
}

_MILESTONE_RE = re.compile(r"_n(\d+)_(\d+)([a-z]?)", re.IGNORECASE)

# `ollama run` streams its answer with ANSI cursor-control escapes; strip them so
# the captured summary and handoff note stay clean text.
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _sanitize_text(text):
    text = _ANSI_RE.sub("", text)
    text = "".join(ch for ch in text if ch in ("\n", "\t") or " " <= ch < "\x7f")
    return text.strip()


def _run_git(args, timeout=15):
    """Run a read-only git command and return stripped stdout, or None on error."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _milestone_sort_key(path: Path):
    match = _MILESTONE_RE.search(path.name)
    if not match:
        return (-1, -1, -1)
    major = int(match.group(1))
    minor = int(match.group(2))
    letter = match.group(3).lower()
    return (major, minor, ord(letter) if letter else 0)


def _format_milestone(path: Path):
    match = _MILESTONE_RE.search(path.name)
    if not match:
        return None
    letter = match.group(3).upper()
    return f"N+{int(match.group(1))}.{int(match.group(2))}{letter}"


def _first_heading(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.stem
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return path.stem


def _latest_report(glob_pattern):
    """Return {path, title, milestone} for the highest-milestone matching report."""
    if not CONTEXT_DIR.is_dir():
        return None
    candidates = [
        p for p in CONTEXT_DIR.glob(glob_pattern)
        if p.is_file() and _MILESTONE_RE.search(p.name)
    ]
    if not candidates:
        return None
    best = max(candidates, key=_milestone_sort_key)
    return {
        "path": best.relative_to(REPO_ROOT).as_posix(),
        "title": _first_heading(best),
        "milestone": _format_milestone(best),
    }


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _n6_test_count():
    """Count test_n6_*.py test methods by static scan. None if no tests dir."""
    if not TESTS_DIR.is_dir():
        return None
    count = 0
    pattern = re.compile(r"^\s*def test_", re.MULTILINE)
    for path in TESTS_DIR.glob("test_n6_*.py"):
        try:
            count += len(pattern.findall(path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return count


def _computer_use_sandbox_status(include: bool):
    """Report confined-sandbox readiness. Dry-run only; never launches a browser."""
    status = {
        "available": CONFINED_RUNNER.is_file(),
        "mode": "dry_run_only",
        "runner_exists": CONFINED_RUNNER.is_file(),
        "dry_run_ok": None,
        "browser_launched": False,
        "dom_action_performed": False,
        "os_input_used": False,
        "live_website": False,
    }
    if not include or not status["runner_exists"] or not SANDBOX_TARGET.is_file():
        return status
    try:
        proc = subprocess.run(
            [sys.executable, str(CONFINED_RUNNER),
             "--target", str(SANDBOX_TARGET), "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        data = json.loads(proc.stdout)
        status["dry_run_ok"] = bool(data.get("ok")) and data.get("mode") == "dry_run"
        status["browser_launched"] = bool(data.get("browser_launched"))
        status["dom_action_performed"] = bool(data.get("dom_action_performed"))
        status["os_input_used"] = bool(data.get("os_input_used"))
        status["live_website"] = bool(data.get("live_website"))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        status["dry_run_ok"] = False
    return status


def _telegram_runtime_status():
    return (
        "inventory_only_not_running"
        if TELEGRAM_BOT_SCRIPT.is_file()
        else "absent_not_running"
    )


def _hermes_integration_status():
    data = _load_json(HERMES_STATUS_PATH)
    if not isinstance(data, dict):
        return "manual_bridge_documented"
    pct = data.get("readiness_percent")
    if isinstance(pct, (int, float)):
        return f"manual_bridge_only_readiness_{int(pct)}pct"
    return "manual_bridge_only"


def _tool_intake_summary():
    if not TOOL_INTAKE_REPORTS.is_dir():
        return None
    reports = sorted(p.name for p in TOOL_INTAKE_REPORTS.glob("*.md"))
    overview = TOOL_INTAKE_REPORTS / "n6_12a_overview.md"
    title = _first_heading(overview) if overview.is_file() else "computer-use repo intake"
    return {
        "path": TOOL_INTAKE_REPORTS.relative_to(REPO_ROOT).as_posix(),
        "title": title,
        "candidate_count": len(reports),
    }


def repo_intake_candidate_status(candidates):
    """For each candidate name, report whether a static intake report exists."""
    results = []
    available = []
    if TOOL_INTAKE_REPORTS.is_dir():
        available = [p.name.lower() for p in TOOL_INTAKE_REPORTS.glob("*.md")]
    for name in candidates:
        token = INTAKE_CANDIDATES.get(name)
        report = None
        if token:
            for fname in available:
                if token in fname:
                    report = (TOOL_INTAKE_REPORTS / fname).relative_to(REPO_ROOT).as_posix()
                    break
        results.append({
            "candidate": name,
            "statically_inspected": report is not None,
            "report": report,
        })
    return results


def _next_recommended_action(origin_main_short, branch, commits_ahead, latest_claude):
    milestone = latest_claude.get("milestone") if latest_claude else None
    head = f"latest local milestone {milestone}" if milestone else "local work"
    if commits_ahead and commits_ahead > 0:
        return (
            f"{head} is {commits_ahead} commit(s) ahead of origin/main "
            f"({origin_main_short}) on branch '{branch}'. Recommended: run the "
            "Codex audit on the pushed feature branch, then merge to main after a "
            "CLEAN PASS."
        )
    return (
        f"branch '{branch}' is in sync with origin/main ({origin_main_short}). "
        "Recommended: pick the next milestone from the handoff vault backlog."
    )


def _try_gemma(prompt, timeout=60):
    """Run a local Ollama Gemma model. Return summary text or None. Local only."""
    exe = shutil.which("ollama")
    if not exe:
        return None
    try:
        listed = subprocess.run(
            [exe, "list"], capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if listed.returncode != 0 or GEMMA_MODEL not in (listed.stdout or ""):
        return None
    try:
        run = subprocess.run(
            [exe, "run", GEMMA_MODEL, prompt],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if run.returncode != 0:
        return None
    text = _sanitize_text(run.stdout or "")
    return text or None


def _deterministic_summary(packet):
    claude = packet.get("latest_claude_report") or {}
    cus = packet.get("computer_use_sandbox_status") or {}
    lines = [
        f"Ghoti status: origin/main {packet.get('origin_main_short')}, "
        f"branch {packet.get('current_branch')}.",
        f"Latest milestone report: {claude.get('milestone') or 'n/a'} "
        f"({claude.get('title') or 'n/a'}).",
        f"n6 test methods: {packet.get('n6_test_count_known_or_null')}.",
        f"Computer-use sandbox: {'dry-run ready' if cus.get('available') else 'absent'} "
        "(no browser, no OS input).",
        f"Hermes: {packet.get('hermes_integration_status')}; "
        f"Telegram: {packet.get('telegram_runtime_status')}.",
        f"Next: {packet.get('next_recommended_action')}",
    ]
    return "\n".join(lines)


def _build_summary_text(packet, use_gemma_if_available):
    """Return (summary_text, gemma_used, fallback_summary_used)."""
    deterministic = _deterministic_summary(packet)
    if not use_gemma_if_available:
        return deterministic, False, True
    prompt = (
        "Summarize this local project status in 4 short bullet points. "
        "Do not invent facts. Status:\n" + deterministic
    )
    gemma_text = _try_gemma(prompt)
    if gemma_text:
        return gemma_text, True, False
    return deterministic, False, True


def _write_handoff(packet):
    cus = packet.get("computer_use_sandbox_status") or {}
    claude = packet.get("latest_claude_report") or {}
    codex = packet.get("latest_codex_report") or {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Ghoti Status Brain - Last Run",
        "",
        f"_Generated {now} by ghoti_status_brain.py (local, offline, read-only)._",
        "",
        "## Current status",
        "",
        f"- origin/main: `{packet.get('origin_main_short')}`",
        f"- current branch: `{packet.get('current_branch')}`",
        f"- commits ahead of main: {packet.get('commits_ahead_of_main')}",
        f"- n6 test methods: {packet.get('n6_test_count_known_or_null')}",
        f"- latest Claude report: {claude.get('milestone') or 'n/a'} - {claude.get('title') or 'n/a'}",
        f"- latest Codex report: {codex.get('milestone') or 'n/a'} - {codex.get('title') or 'n/a'}",
        "",
        "## Useful capabilities",
        "",
        "- One-command local status packet (this brain).",
        "- Local worker queue for safe read-only tasks.",
        f"- Confined computer-use sandbox: {'dry-run ready' if cus.get('available') else 'absent'} (no browser launch, no OS input).",
        "- Static repo-intake summary of computer-use candidates.",
        "",
        "## Pending branches",
        "",
        f"- {packet.get('next_recommended_action')}",
        "",
        "## Safety disabled",
        "",
        "- No live browser, no OS-level input, no Telegram control, no MCP, no auto-send, no external API.",
        "- Optional summarization is local Ollama Gemma only; otherwise deterministic fallback.",
        "",
        "## Next action",
        "",
        f"- {packet.get('next_recommended_action')}",
        "",
        f"_Summary source: {'local Gemma' if packet.get('gemma_used') else 'deterministic fallback'}._",
        "",
    ]
    HANDOFF_PATH.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_PATH.write_text("\n".join(lines), encoding="utf-8")
    return HANDOFF_PATH.relative_to(REPO_ROOT).as_posix()


def build_status_packet(*, include_computer_use_sandbox=False,
                        use_gemma_if_available=False, write_handoff=False):
    """Build the N+6.15A status packet. Pure local reads; safe to import + call."""
    origin_main_short = _run_git(["rev-parse", "--short", "origin/main"])
    branch = _run_git(["branch", "--show-current"]) or None

    log_ref = "origin/main" if origin_main_short else "HEAD"
    log_out = _run_git(["log", "-n", "5", "--pretty=format:%h %s", log_ref])
    latest_main_commits = log_out.splitlines() if log_out else []

    ahead_out = _run_git(["rev-list", "--count", "origin/main..HEAD"])
    try:
        commits_ahead = int(ahead_out) if ahead_out is not None else None
    except ValueError:
        commits_ahead = None

    latest_claude = _latest_report("claude_n*.md")
    latest_codex = _latest_report("codex_n*.md")

    packet = {
        "ok": True,
        "milestone": MILESTONE,
        "repo_root": str(REPO_ROOT),
        "origin_main_short": origin_main_short,
        "current_branch": branch,
        "commits_ahead_of_main": commits_ahead,
        "latest_main_commits": latest_main_commits,
        "n6_test_count_known_or_null": _n6_test_count(),
        "latest_codex_report": latest_codex,
        "latest_claude_report": latest_claude,
        "latest_tool_intake_summary": _tool_intake_summary(),
        "computer_use_sandbox_status": _computer_use_sandbox_status(include_computer_use_sandbox),
        "telegram_runtime_status": _telegram_runtime_status(),
        "hermes_integration_status": _hermes_integration_status(),
        "repo_visibility_unknown_or_public_private": "unknown",
        "next_recommended_action": _next_recommended_action(
            origin_main_short, branch, commits_ahead, latest_claude
        ),
        "handoff_written": False,
        "handoff_path": None,
        "gemma_used": False,
        "fallback_summary_used": True,
        "safety": {
            "live_browser_used": False,
            "os_input_used": False,
            "external_api_used": False,
            "telegram_control_used": False,
            "mcp_used": False,
            "auto_send_used": False,
            "network_used": False,
            "local_only": True,
        },
    }

    summary_text, gemma_used, fallback_used = _build_summary_text(
        packet, use_gemma_if_available
    )
    packet["summary_text"] = summary_text
    packet["gemma_used"] = gemma_used
    packet["fallback_summary_used"] = fallback_used

    if write_handoff:
        packet["handoff_path"] = _write_handoff(packet)
        packet["handoff_written"] = True

    return packet


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Status Brain (N+6.15A) - local, offline status packet."
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit the status packet as JSON.")
    parser.add_argument("--write-handoff", action="store_true",
                        help="Also write the Obsidian handoff note.")
    parser.add_argument("--include-computer-use-sandbox", action="store_true",
                        help="Run the confined sandbox dry-run (no browser launch).")
    parser.add_argument("--use-gemma-if-available", action="store_true",
                        help="Use a local Ollama Gemma model to summarize if present.")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    packet = build_status_packet(
        include_computer_use_sandbox=args.include_computer_use_sandbox,
        use_gemma_if_available=args.use_gemma_if_available,
        write_handoff=args.write_handoff,
    )
    if args.json:
        print(json.dumps(packet, indent=2))
    else:
        print(packet["summary_text"])
        if packet["handoff_written"]:
            print(f"\nHandoff written: {packet['handoff_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
