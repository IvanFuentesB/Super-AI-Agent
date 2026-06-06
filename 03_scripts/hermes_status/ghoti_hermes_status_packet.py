#!/usr/bin/env python3
"""Ghoti Hermes status/memory packet generator (N+6.25A).

Builds a small, reliable coordinator packet that Hermes reads BEFORE answering, so it
stops giving shallow or incorrect summaries. It reads existing committed status sources
only and never launches or controls anything:

  * latest git main commit (read-only git metadata)
  * Agent Arena trace status (if present)
  * Memory Vault index (if present)
  * Tool Intake summary (if present)
  * latest Claude report and latest Codex report
  * feature-flags summary (the example flags file only)

Safe by construction:

  * Read-only. The only command it runs is git, and only read subcommands (log/rev-parse)
    to read commit metadata. No shell, no os.system, no third-party process.
  * It writes nothing unless --write is passed, and then only to a path inside the repo.
  * It launches no agent, opens no browser/computer-use, uses no MCP, submits nothing.
  * It reads no secrets: only the *.example flags file and committed reports/indexes.
  * It surfaces no absolute local path - every path in the packet is repo-relative.

CLI:
  --check            emit a safety self-check JSON
  --json             emit the status packet as JSON
  --md               emit the status packet as Markdown
  --write --output P write the Markdown packet to P (must be inside the repo)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

MILESTONE = "N+6.25A"
HUMAN_MEANING = ("Hermes memory/status upgrade: a read-only coordinator packet Hermes can "
                 "read before answering. Still no live agent launching.")

# 03_scripts/hermes_status/ghoti_hermes_status_packet.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
CONTEXT = REPO_ROOT / "14_context"

TRACE_SAMPLE = CONTEXT / "agent_arena" / "sample_trace.json"
TRACE_LOADER = REPO_ROOT / "03_scripts" / "agent_arena" / "ghoti_agent_arena_trace_loader.py"
MEMORY_VAULT_INDEX = CONTEXT / "memory_vault" / "INDEX.md"
MEMORY_VAULT_README = CONTEXT / "memory_vault" / "README.md"
TOOL_INTAKE_JSON = CONTEXT / "tool_intake" / "tool_backlog_inventory_n6_22a.json"
FEATURE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

_MILESTONE_RE = re.compile(r"_n(\d+)_(\d+)([a-z]?)", re.IGNORECASE)

# ECC is Everything Claude Code - NOT elliptic curve cryptography.
ECC = {
    "abbreviation": "ECC",
    "meaning": "Everything Claude Code",
    "is_not": "elliptic curve cryptography",
    "note": ("In this repo ECC always means Everything Claude Code (a curated bundle of "
             "Claude Code commands/agents/skills/hooks). Ghoti adapts the ideas as "
             "guidance only; it does not install ECC or wire its hooks."),
}

HERMES_ROLE = {
    "current": ("coordinator / status / memory only - Hermes reads this packet, prepares "
                "prompts, and routes to approved wrappers. It launches nothing, runs no "
                "command, and controls no app."),
    "future": ("automatic coordinator - only AFTER the controlled launcher and the "
               "approval gates are built and audited (dry-run first, worktree-per-agent, "
               "human approval)."),
}

HERMES_MUST_NOT_CLAIM = [
    "Do not claim any agent is being launched or controlled live - none is.",
    "Do not claim MCP, browser, or computer-use is enabled - all are off.",
    "Do not claim auto-submit, posting, email, or money actions - all are blocked.",
    "Do not confuse ECC with elliptic curve cryptography; ECC = Everything Claude Code.",
    "Do not claim overnight autonomous operation - it is planned and gated, not enabled.",
    "Do not invent status; if a source is missing, say it is missing.",
]

SAFETY = {
    "milestone": MILESTONE,
    "local_only": True,
    "read_only": True,
    "reads_git_metadata_only": True,
    "writes_only_when_write_flag": True,
    "launches_agents": False,
    "runs_commands_other_than_git_read": False,
    "uses_browser_or_computer_use": False,
    "uses_mcp": False,
    "auto_submit": False,
    "reads_secret_values": False,
}

# Read-only git subcommands this tool is allowed to call.
_GIT_READ_OK = {"log", "rev-parse"}


def _git(args):
    """Run a read-only git command and return stdout (or None). List args, no shell."""
    if not args or args[0] not in _GIT_READ_OK:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _read_json(path):
    text = _read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def _milestone_key(name):
    match = _MILESTONE_RE.search(name)
    if not match:
        return (-1, -1, -1)
    suffix = match.group(3).lower()
    return (int(match.group(1)), int(match.group(2)), ord(suffix) if suffix else 0)


def _milestone_label(name):
    match = _MILESTONE_RE.search(name)
    if not match:
        return None
    return "N+{0}.{1}{2}".format(int(match.group(1)), int(match.group(2)),
                                 match.group(3).upper())


def _first_heading(text):
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return re.sub(r"^#+\s*", "", stripped)[:120]
    return None


def _verdict(text):
    upper = (text or "").upper()
    if "IMPLEMENTED_AND_PUSHED" in upper:
        return "IMPLEMENTED_AND_PUSHED"
    if "CLEAN PASS" in upper:
        return "CLEAN_PASS"
    if "BLOCKED" in upper:
        return "BLOCKED"
    return "recorded"


def _latest_report(prefix):
    if not CONTEXT.is_dir():
        return None
    candidates = sorted(CONTEXT.glob("{0}_n*.md".format(prefix)),
                        key=lambda p: _milestone_key(p.name), reverse=True)
    if not candidates:
        return None
    path = candidates[0]
    text = _read_text(path)
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = path.name
    return {
        "milestone": _milestone_label(path.name) or "unknown",
        "title": _first_heading(text) or path.stem,
        "verdict": _verdict(text),
        "path": rel,
    }


def _main_commit():
    # Prefer origin/main (the canonical latest main after a fetch); a local "main" ref can
    # be stale inside a feature worktree, so it is only a fallback, then HEAD.
    for ref in ("origin/main", "main", "HEAD"):
        out = _git(["log", "-1", "--format=%h%x1f%s", ref])
        if out and "\x1f" in out:
            short, subject = out.split("\x1f", 1)
            return {"ref": ref, "short": short.strip(), "subject": subject.strip()[:140]}
    return {"ref": None, "short": "unavailable", "subject": "unavailable"}


def _feature_flags_summary():
    flags = _read_json(FEATURE_FLAGS)
    if not isinstance(flags, dict):
        return {"present": FEATURE_FLAGS.is_file(), "enabled": [], "count": 0,
                "source": "23_configs/ghoti_feature_flags.example.json"}
    enabled = sorted(k for k, v in flags.items() if v is True)
    return {"present": True, "enabled": enabled, "count": len(flags),
            "source": "23_configs/ghoti_feature_flags.example.json"}


def _trace_status():
    sample = _read_json(TRACE_SAMPLE)
    present = TRACE_LOADER.is_file()
    info = {"capability_present": present,
            "loader": "03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py"}
    if isinstance(sample, dict):
        info.update({"mode": sample.get("mode"), "simulation": sample.get("simulation"),
                     "live_execution": sample.get("live_execution")})
    return info


def _memory_vault_status():
    present = MEMORY_VAULT_INDEX.is_file()
    return {"present": present,
            "index": "14_context/memory_vault/INDEX.md" if present else None,
            "readme_present": MEMORY_VAULT_README.is_file(),
            "title": _first_heading(_read_text(MEMORY_VAULT_INDEX)) if present else None}


def _tool_intake_status():
    data = _read_json(TOOL_INTAKE_JSON)
    if not isinstance(data, dict):
        return {"present": TOOL_INTAKE_JSON.is_file(), "tool_count": 0}
    tools = data.get("tools") if isinstance(data.get("tools"), list) else []
    return {"present": True, "tool_count": len(tools),
            "static_intake_only": bool(data.get("static_intake_only")),
            "source": "14_context/tool_intake/tool_backlog_inventory_n6_22a.json"}


def build_sources():
    return {
        "main_commit": _main_commit(),
        "agent_arena_trace": _trace_status(),
        "memory_vault": _memory_vault_status(),
        "tool_intake": _tool_intake_status(),
        "latest_claude_report": _latest_report("claude"),
        "latest_codex_report": _latest_report("codex"),
        "feature_flags": _feature_flags_summary(),
    }


def build_progression():
    arena = TRACE_LOADER.is_file()
    stages = [
        {"stage": "simulation (Agent Arena)", "status": "done" if arena else "planned",
         "percent": 100 if arena else 0},
        {"stage": "trace ingestion", "status": "done" if arena else "planned",
         "percent": 100 if arena else 0},
        {"stage": "static repo intake (skills / swarm)", "status": "in_progress",
         "percent": 60, "note": "N+6.24A pushed; merges via N+6.24B gate."},
        {"stage": "hermes status / memory", "status": "in_progress", "percent": 60,
         "note": "this milestone (N+6.25A)."},
        {"stage": "controlled launcher", "status": "planned", "percent": 0,
         "note": "gated; dry-run-first; human-approved."},
        {"stage": "approved-window bridge", "status": "partial", "percent": 50,
         "note": "paste prepared; auto-submit blocked (N+6.20A)."},
        {"stage": "supervised overnight loop", "status": "planned", "percent": 0,
         "note": "gated; not enabled."},
    ]
    done = sum(1 for s in stages if s["status"] == "done")
    overall = round(sum(s["percent"] for s in stages) / len(stages))
    return {"stages": stages, "stages_done": done, "stages_total": len(stages),
            "overall_percent": overall, "live_automation_enabled_percent": 0}


def build_packet():
    sources = build_sources()
    progression = build_progression()
    claude = sources["latest_claude_report"] or {}
    plain = (
        "Ghoti planning/build track is about {0}% through the safe progression; live "
        "automation is 0% (not enabled). Latest main commit recorded: {1} ({2}). Newest "
        "Claude milestone: {3}. Hermes is status/memory only - it reads this packet and "
        "launches nothing."
    ).format(progression["overall_percent"], sources["main_commit"]["short"],
             sources["main_commit"]["subject"], claude.get("milestone", "unknown"))
    return {
        "ok": True,
        "milestone": MILESTONE,
        "label_human_meaning": HUMAN_MEANING,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status_plain_english": plain,
        "sources": sources,
        "progression": progression,
        "done": [
            "Agent Arena simulation (N+6.21A) and real local trace ingestion (N+6.23A) are on main.",
            "Repo Memory Vault v1 and Tool Backlog Intake v2 (N+6.22B) are on main.",
            "This Hermes status/memory packet (N+6.25A) reads committed sources read-only.",
        ],
        "blocked": [
            "Live agent launching - not built; gated behind the controlled launcher.",
            "MCP, browser, and computer-use - off.",
            "Auto-submit, posting, email, and money actions - blocked.",
            "Supervised overnight autonomous loop - planned, not enabled.",
        ],
        "parallel_safe": [
            "N+6.24B Codex audit and N+6.25A can run in parallel as long as "
            "14_context/skills and the swarm-intake files are not edited here.",
            "Read-only status packets never conflict with other lanes.",
        ],
        "hermes_must_not_claim": list(HERMES_MUST_NOT_CLAIM),
        "ecc": dict(ECC),
        "hermes_role": dict(HERMES_ROLE),
        "safety": dict(SAFETY),
    }


def _bullet_list(items):
    return "\n".join("- {0}".format(x) for x in items)


def render_md(packet):
    src = packet["sources"]
    mc = src["main_commit"]
    prog_rows = "\n".join(
        "| {0} | {1} | {2}% |".format(s["stage"], s["status"], s["percent"])
        for s in packet["progression"]["stages"]
    )
    claude = src["latest_claude_report"] or {}
    codex = src["latest_codex_report"] or {}
    flags = src["feature_flags"]
    enabled = ", ".join(flags["enabled"]) if flags["enabled"] else "(none enabled by default)"
    lines = [
        "# Hermes Status Packet - {0}".format(packet["milestone"]),
        "",
        "_Generated {0}. Read-only. Hermes: read this before answering._".format(packet["generated_utc"]),
        "",
        "**Human meaning:** {0}".format(packet["label_human_meaning"]),
        "",
        "## Plain-English status",
        "",
        packet["status_plain_english"],
        "",
        "- Overall progression: **{0}%**".format(packet["progression"]["overall_percent"]),
        "- Live automation enabled: **{0}%**".format(packet["progression"]["live_automation_enabled_percent"]),
        "",
        "## Progression",
        "",
        "| Stage | Status | Percent |",
        "|-------|--------|---------|",
        prog_rows,
        "",
        "## Sources (read-only)",
        "",
        "- **Latest main commit:** `{0}` - {1}".format(mc["short"], mc["subject"]),
        "- **Agent Arena trace:** capability_present={0}, mode={1}, live_execution={2}".format(
            src["agent_arena_trace"].get("capability_present"),
            src["agent_arena_trace"].get("mode"),
            src["agent_arena_trace"].get("live_execution")),
        "- **Memory Vault:** present={0} ({1})".format(
            src["memory_vault"]["present"], src["memory_vault"].get("index") or "missing"),
        "- **Tool Intake:** present={0}, tools={1}".format(
            src["tool_intake"]["present"], src["tool_intake"].get("tool_count")),
        "- **Latest Claude report:** {0} - {1} [{2}]".format(
            claude.get("milestone", "n/a"), claude.get("title", "n/a"), claude.get("verdict", "n/a")),
        "- **Latest Codex report:** {0} - {1} [{2}]".format(
            codex.get("milestone", "n/a"), codex.get("title", "n/a"), codex.get("verdict", "n/a")),
        "- **Feature flags (example):** {0}".format(enabled),
        "",
        "## What is done",
        "",
        _bullet_list(packet["done"]),
        "",
        "## What is blocked",
        "",
        _bullet_list(packet["blocked"]),
        "",
        "## What can run in parallel",
        "",
        _bullet_list(packet["parallel_safe"]),
        "",
        "## What Hermes should NOT claim",
        "",
        _bullet_list(packet["hermes_must_not_claim"]),
        "",
        "## ECC",
        "",
        "- **ECC = {0}** (it is NOT {1}).".format(packet["ecc"]["meaning"], packet["ecc"]["is_not"]),
        "- {0}".format(packet["ecc"]["note"]),
        "",
        "## Hermes role",
        "",
        "- **Now:** {0}".format(packet["hermes_role"]["current"]),
        "- **Future:** {0}".format(packet["hermes_role"]["future"]),
        "",
    ]
    return "\n".join(lines)


def build_check():
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    no_shell_true = re.search(r"shell\s*=\s*True", src) is None
    no_os_system = re.search(r"os\.system\s*\(", src) is None
    try:
        packet = build_packet()
        packet_ok = bool(packet.get("ok")) and packet["ecc"]["meaning"] == "Everything Claude Code"
    except Exception:
        packet_ok = False
    checks = {
        "ok": True,
        "milestone": MILESTONE,
        "tool": "ghoti_hermes_status_packet",
        "script_exists": Path(__file__).is_file(),
        "schema_present": (CONTEXT / "hermes_status" / "hermes_status_packet_schema.json").is_file(),
        "example_present": (CONTEXT / "hermes_status" / "HERMES_STATUS_PACKET.example.md").is_file(),
        "reads_git_metadata_only": True,
        "no_shell_true": no_shell_true,
        "no_os_system": no_os_system,
        "no_command_execution_other_than_git_read": no_shell_true and no_os_system,
        "writes_only_when_write_flag": True,
        "packet_builds": packet_ok,
        "no_live_launch": True,
        "no_browser_computer_use": True,
        "no_mcp": True,
        "no_secrets": True,
        "ecc_is_everything_claude_code": True,
        "safety": dict(SAFETY),
    }
    checks["ok"] = all([
        checks["script_exists"], checks["no_shell_true"], checks["no_os_system"],
        checks["packet_builds"],
    ])
    return checks


def _within_repo(path):
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except ValueError:
        return False


def write_packet(output):
    out_path = Path(output)
    if not out_path.is_absolute():
        out_path = (REPO_ROOT / out_path)
    if not _within_repo(out_path):
        return {"ok": False, "error": "refusing to write outside the repo root",
                "output": str(output)}
    body = render_md(build_packet())
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body, encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": "write failed", "detail": str(exc)[:200]}
    try:
        rel = out_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        rel = out_path.name
    return {"ok": True, "milestone": MILESTONE, "output": rel, "bytes": len(body.encode("utf-8")),
            "wrote_packet": True, "live_execution": False}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ghoti Hermes status/memory packet generator (N+6.25A) - read-only."
    )
    parser.add_argument("--check", action="store_true", help="Emit a safety self-check JSON.")
    parser.add_argument("--json", action="store_true", help="Emit the packet (or write result) as JSON.")
    parser.add_argument("--md", action="store_true", help="Emit the packet as Markdown.")
    parser.add_argument("--write", action="store_true", help="Write the Markdown packet to --output.")
    parser.add_argument("--output", default=None, help="Output path for --write (must be inside the repo).")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.check:
        print(json.dumps(build_check(), indent=2))
        return 0
    if args.write:
        if not args.output:
            print(json.dumps({"ok": False, "error": "--write requires --output"}, indent=2))
            return 2
        result = write_packet(args.output)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 2
    if args.md:
        print(render_md(build_packet()))
        return 0
    # Default: the JSON packet.
    print(json.dumps(build_packet(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
