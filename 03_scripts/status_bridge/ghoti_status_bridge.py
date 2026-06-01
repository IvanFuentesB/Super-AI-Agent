#!/usr/bin/env python3
"""Ghoti Status Bridge (N+6.16A).

One local, read-only entry point that turns the N+6.15A status brain into the
shapes the places the user actually opens can consume:

  * --json                  the full status packet (brain packet + a source tag)
  * --markdown              the same status rendered as Markdown (Obsidian/Hermes)
  * --telegram-safe-json    a short, sanitized, length-bounded text safe to post in
                            a Telegram reply, wrapped in a small JSON envelope
  * --write-hermes-handoff  also write a Hermes-readable handoff note so Hermes can
                            read one status source instead of repeating generic
                            summaries (only with this explicit flag)

How it stays safe:

  * It calls the local status brain (03_scripts/local_worker_queue/
    ghoti_status_brain.py) as a read-only subprocess using an argument list only -
    never a shell string, never Invoke-Expression. There is a timeout, and if the
    brain is missing or fails the bridge returns a deterministic local fallback.
  * It needs no Telegram token and no chat id, opens no network connection, calls no
    external API, launches no agent, and controls no browser/desktop.
  * Gemma is off by default. The local Gemma summary only runs when the caller
    passes --use-gemma-if-available, which is forwarded to the brain; otherwise the
    brain uses its deterministic fallback summary.
  * Output is scrubbed for secret-shaped substrings and stripped of non-printable
    characters before it is ever shaped for Telegram.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

MILESTONE = "N+6.16A"

# 03_scripts/status_bridge/ghoti_status_bridge.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_BRAIN = (
    REPO_ROOT / "03_scripts" / "local_worker_queue" / "ghoti_status_brain.py"
)
HERMES_HANDOFF_PATH = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "04_Logs"
    / "HERMES_STATUS_BRIDGE_LAST_RUN.md"
)

DEFAULT_TIMEOUT = 20
TELEGRAM_TEXT_LIMIT = 3500

# Belt-and-suspenders: the status brain emits no secrets, but the bridge still
# scrubs secret-shaped "key: value" substrings before shaping any text for Telegram.
_SECRET_RE = re.compile(
    r"(?i)\b(token|secret|api[_-]?key|password|passwd|bearer|authorization)\b"
    r"\s*[:=]\s*\S+"
)
_NONPRINTABLE_OK = ("\n", "\t")

SAFETY = {
    "live_browser_used": False,
    "os_input_used": False,
    "external_api_used": False,
    "telegram_control_used": False,
    "mcp_used": False,
    "auto_send_used": False,
    "agent_launch_used": False,
    "network_used": False,
    "secrets_read": False,
    "local_only": True,
}


def _scrub_secrets(text):
    return _SECRET_RE.sub(lambda m: "{0}: [redacted]".format(m.group(1)), text)


def _strip_nonprintable(text):
    return "".join(
        ch for ch in text if ch in _NONPRINTABLE_OK or " " <= ch < "\x7f"
    )


def _sanitize(text, limit=TELEGRAM_TEXT_LIMIT):
    text = _strip_nonprintable(_scrub_secrets(text)).strip()
    if len(text) > limit:
        text = text[: limit - 15].rstrip() + "\n... (truncated)"
    return text


def _run_status_brain(use_gemma_if_available, timeout):
    """Call the local status brain read-only and return its parsed packet.

    Returns (packet_dict, None) on success or (None, reason) on any failure. The
    call is an argument list only; there is no shell string and no Invoke-Expression.
    """
    if not STATUS_BRAIN.is_file():
        return None, "status brain script not found"
    args = [sys.executable, str(STATUS_BRAIN), "--json"]
    if use_gemma_if_available:
        args.append("--use-gemma-if-available")
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "status brain call failed: {0}".format(exc.__class__.__name__)
    if proc.returncode != 0:
        return None, "status brain returned exit code {0}".format(proc.returncode)
    try:
        return json.loads(proc.stdout), None
    except ValueError:
        return None, "status brain produced no parseable JSON"


def _fallback_packet(reason):
    """Deterministic local fallback when the status brain is unavailable. Carries no
    git lookup of its own so the bridge's only subprocess is the brain call."""
    return {
        "ok": True,
        "source": "fallback",
        "milestone": MILESTONE,
        "fallback_reason": reason,
        "repo_root": str(REPO_ROOT),
        "origin_main_short": "unavailable",
        "current_branch": "unavailable",
        "n6_test_count_known_or_null": None,
        "latest_claude_report": None,
        "latest_codex_report": None,
        "computer_use_sandbox_status": {"mode": "dry_run_only", "available": None},
        "telegram_runtime_status": "inventory_only_not_running",
        "hermes_integration_status": "manual_bridge_only",
        "next_recommended_action": (
            "Run the local status brain "
            "(03_scripts/local_worker_queue/ghoti_status_brain.py --json) for a full "
            "status packet."
        ),
        "gemma_used": False,
        "fallback_summary_used": True,
        "safety": dict(SAFETY),
    }


def build_packet(use_gemma_if_available=False, timeout=DEFAULT_TIMEOUT):
    """Return (packet, source). source is 'status_brain' or 'fallback'."""
    packet, reason = _run_status_brain(use_gemma_if_available, timeout)
    if packet is None:
        return _fallback_packet(reason), "fallback"
    packet["source"] = "status_brain"
    # The bridge never opens the network or reads secrets; record that plainly.
    packet.setdefault("safety", {})
    packet["safety"].setdefault("network_used", False)
    packet["safety"].setdefault("secrets_read", False)
    packet["safety"].setdefault("local_only", True)
    return packet, "status_brain"


def _report_line(label, report):
    if not isinstance(report, dict):
        return "{0}: (none)".format(label)
    milestone = report.get("milestone") or "?"
    title = report.get("title") or report.get("path") or "(unknown)"
    return "{0}: {1} - {2}".format(label, milestone, title)


def _safe_status_lines(packet):
    """Status lines that are always safe to show anywhere, including Telegram."""
    return [
        "Ghoti status ({0})".format(packet.get("source", "unknown")),
        "origin_main: {0}".format(packet.get("origin_main_short", "unavailable")),
        "branch: {0}".format(packet.get("current_branch", "unavailable")),
        "n6_tests: {0}".format(packet.get("n6_test_count_known_or_null")),
        _report_line("latest_claude", packet.get("latest_claude_report")),
        _report_line("latest_codex", packet.get("latest_codex_report")),
        "telegram_runtime: {0}".format(packet.get("telegram_runtime_status", "unknown")),
        "hermes: {0}".format(packet.get("hermes_integration_status", "unknown")),
        "next: {0}".format(packet.get("next_recommended_action", "(none)")),
        "live_launch_enabled: false",
        "telegram_control_enabled: false",
        "mcp_enabled: false",
        "browser_computer_use_enabled: false",
        "auto_send_enabled: false",
    ]


def to_telegram_safe_text(packet):
    """A short, sanitized, length-bounded status text safe for a Telegram reply."""
    return _sanitize("\n".join(_safe_status_lines(packet)))


def to_markdown(packet):
    """Render the packet as Markdown for Obsidian / a Hermes-readable note."""
    generated = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Ghoti Status Bridge ({0})".format(MILESTONE),
        "",
        "Generated: {0}".format(generated),
        "Source: {0}".format(packet.get("source", "unknown")),
        "",
        "## Status",
        "",
        "- origin/main: `{0}`".format(packet.get("origin_main_short", "unavailable")),
        "- branch: `{0}`".format(packet.get("current_branch", "unavailable")),
        "- n6 tests: `{0}`".format(packet.get("n6_test_count_known_or_null")),
        "- {0}".format(_report_line("latest Claude report", packet.get("latest_claude_report"))),
        "- {0}".format(_report_line("latest Codex report", packet.get("latest_codex_report"))),
        "- Telegram runtime: `{0}`".format(packet.get("telegram_runtime_status", "unknown")),
        "- Hermes integration: `{0}`".format(packet.get("hermes_integration_status", "unknown")),
        "",
        "## Next recommended action",
        "",
        packet.get("next_recommended_action", "(none)"),
        "",
        "## Safety",
        "",
        "- local_only, read-only; no Telegram control, no agent launch, no MCP, no",
        "  live browser/computer-use, no email/WhatsApp, no auto-send, no external API.",
        "- Telegram stays status-only. There is no /run and no live control.",
        "",
    ]
    return _sanitize("\n".join(lines), limit=20000)


def telegram_safe_status_text(use_gemma_if_available=False, timeout=DEFAULT_TIMEOUT):
    """Convenience for the status-only Telegram bot: return a sanitized status text,
    or None if nothing could be built. Performs no network or secret access here; the
    only subprocess is the local read-only status-brain call inside build_packet."""
    try:
        packet, _source = build_packet(
            use_gemma_if_available=use_gemma_if_available, timeout=timeout
        )
        text = to_telegram_safe_text(packet)
        return text or None
    except Exception:
        return None


def write_hermes_handoff(packet):
    """Write the Hermes-readable handoff note. Returns the repo-relative path."""
    HERMES_HANDOFF_PATH.parent.mkdir(parents=True, exist_ok=True)
    HERMES_HANDOFF_PATH.write_text(to_markdown(packet), encoding="utf-8")
    return HERMES_HANDOFF_PATH.relative_to(REPO_ROOT).as_posix()


def build_result(*, mode, use_gemma_if_available=False, write_hermes_handoff_flag=False,
                 timeout=DEFAULT_TIMEOUT):
    packet, source = build_packet(
        use_gemma_if_available=use_gemma_if_available, timeout=timeout
    )
    handoff_path = None
    if write_hermes_handoff_flag:
        handoff_path = write_hermes_handoff(packet)
    if mode == "telegram-safe-json":
        return {
            "ok": True,
            "milestone": MILESTONE,
            "source": source,
            "telegram_safe_text": to_telegram_safe_text(packet),
            "secrets_present": False,
            "hermes_handoff_written": bool(handoff_path),
            "hermes_handoff_path": handoff_path,
            "safety": dict(SAFETY),
        }
    # json / markdown modes both carry the full packet; markdown adds a rendering.
    result = {
        "ok": True,
        "milestone": MILESTONE,
        "source": source,
        "hermes_handoff_written": bool(handoff_path),
        "hermes_handoff_path": handoff_path,
        "packet": packet,
        "safety": dict(SAFETY),
    }
    if mode == "markdown":
        result["markdown"] = to_markdown(packet)
    return result


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Status Bridge (N+6.16A) - local read-only status for "
                    "Telegram, Hermes, Obsidian, and PowerShell."
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit the full status packet as JSON.")
    parser.add_argument("--markdown", action="store_true",
                        help="Emit the status rendered as Markdown.")
    parser.add_argument("--telegram-safe-json", action="store_true",
                        help="Emit a short sanitized Telegram-safe text in JSON.")
    parser.add_argument("--write-hermes-handoff", action="store_true",
                        help="Also write the Hermes-readable handoff note.")
    parser.add_argument("--use-gemma-if-available", action="store_true",
                        help="Forward the local-Gemma flag to the status brain "
                             "(off by default; deterministic fallback otherwise).")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="Status-brain subprocess timeout in seconds.")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.telegram_safe_json:
        mode = "telegram-safe-json"
    elif args.markdown:
        mode = "markdown"
    else:
        mode = "json"
    result = build_result(
        mode=mode,
        use_gemma_if_available=args.use_gemma_if_available,
        write_hermes_handoff_flag=args.write_hermes_handoff,
        timeout=args.timeout,
    )
    if mode == "markdown" and not args.json:
        # Plain Markdown to stdout unless --json was also asked for.
        print(result["markdown"])
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
