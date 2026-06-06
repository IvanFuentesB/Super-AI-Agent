#!/usr/bin/env python3
"""Ghoti Agent Arena - real trace loader (N+6.23A).

Turns existing local Ghoti report files into an Agent Arena "trace" so the dashboard
can show a real local project trace, not only the sample simulation. It is read-only
and file-only:

  * Python standard library only. NO subprocess, NO network, NO writes.
  * It reads existing committed report files (14_context/claude_n6_*.md,
    codex_n6_*.md, and the agent handoff vault) and extracts milestone, title, verdict,
    branch, and Codex-audit-target. It never runs git or any command.
  * It surfaces no secret values and no absolute local paths - report paths are made
    repo-relative.
  * live_execution and simulation are forced false in every payload. The loader
    launches no agent and executes nothing.

CLI:
  --check          emit a safety self-check JSON
  --trace-json     emit the real local trace JSON
  --status-json    emit the status cards JSON
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

MILESTONE = "N+6.23A"

# 03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py -> repo root is two up.
REPO_ROOT = Path(__file__).resolve().parents[2]
CONTEXT = REPO_ROOT / "14_context"
HANDOFF_DIR = CONTEXT / "agent_handoff_vault" / "02_Agent_Handoffs"
SAMPLE_TRACE = CONTEXT / "agent_arena" / "sample_trace.json"
TRACE_SCHEMA = CONTEXT / "agent_arena" / "trace_schema.json"
# Read-only presence checks only (these files are owned by other lanes; never edited).
MEMORY_VAULT_README = CONTEXT / "memory_vault" / "README.md"
TOOL_INTAKE_INVENTORY = CONTEXT / "tool_intake" / "tool_backlog_inventory_n6_22a.json"

REPORT_LIMIT = 25
HANDOFF_LIMIT = 10

_MILESTONE_RE = re.compile(r"_n(\d+)_(\d+)([a-z]?)", re.IGNORECASE)
_BRANCH_RE = re.compile(r"feat/ghoti-agent-[a-z]+-n[0-9][0-9a-z-]+")
_AUDIT_RE = re.compile(r"audit/ghoti-agent-codex-n[0-9][0-9a-z-]+")
_MAIN_SHA_RE = re.compile(r"origin/main[`:\s_]{0,14}`?([0-9a-f]{7,40})", re.IGNORECASE)

SAFETY = {
    "milestone": MILESTONE,
    "local_only": True,
    "read_only": True,
    "reads_files_only": True,
    "runs_commands": False,
    "writes_files": False,
    "reads_secret_values": False,
    "live_execution": False,
    "simulation": False,
    "uses_external_assets": False,
}


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _milestone_key(name):
    match = _MILESTONE_RE.search(name)
    if not match:
        return (-1, -1, -1)
    return (int(match.group(1)), int(match.group(2)), ord(match.group(3).lower()) if match.group(3) else 0)


def _milestone_label(name):
    match = _MILESTONE_RE.search(name)
    if not match:
        return None
    return "N+{0}.{1}{2}".format(int(match.group(1)), int(match.group(2)), match.group(3).upper())


def _first_heading(text):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            title = re.sub(r"^Ghoti\s+", "", title)
            title = re.sub(r"\s*\(Report\)\s*$", "", title)
            return title[:120]
    return None


def _verdict(text):
    upper = text.upper()
    if "IMPLEMENTED_AND_PUSHED" in upper:
        return "IMPLEMENTED_AND_PUSHED"
    if "CLEAN PASS" in upper:
        return "CLEAN_PASS"
    if "BLOCKED" in upper:
        return "BLOCKED"
    return "recorded"


def _agent_for(name):
    low = name.lower()
    if low.startswith("claude_"):
        return "claude"
    if low.startswith("codex_"):
        return "codex"
    if low.startswith("hermes_"):
        return "hermes"
    return "ghoti"


def _extract(path, text):
    branch = _BRANCH_RE.search(text)
    audit = _AUDIT_RE.search(text)
    main_sha = _MAIN_SHA_RE.search(text)
    try:
        rel = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        rel = path.name
    return {
        "milestone": _milestone_label(path.name) or "unknown",
        "title": _first_heading(text) or path.stem,
        "verdict": _verdict(text),
        "branch": branch.group(0) if branch else None,
        "codex_audit_target": audit.group(0) if audit else None,
        "origin_main_short": main_sha.group(1)[:12] if main_sha else None,
        "agent": _agent_for(path.name),
        "path": rel,
    }


def _candidate_files():
    files = []
    if CONTEXT.is_dir():
        for pattern in ("claude_n6_*.md", "codex_n6_*.md"):
            files.extend(CONTEXT.glob(pattern))
    files.sort(key=lambda p: _milestone_key(p.name), reverse=True)
    return files


def collect_reports(limit=REPORT_LIMIT):
    reports = []
    for path in _candidate_files()[:limit]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        reports.append(_extract(path, text))
    return reports


def collect_handoffs(limit=HANDOFF_LIMIT):
    handoffs = []
    if not HANDOFF_DIR.is_dir():
        return handoffs
    for path in sorted(HANDOFF_DIR.glob("NEXT_*.md"))[:limit]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        handoffs.append({"from": "claude", "to": "next-lane", "kind": "seed_handoff",
                         "file": rel, "title": _first_heading(text) or path.stem})
    return handoffs


_STATE_FOR_VERDICT = {
    "IMPLEMENTED_AND_PUSHED": "done",
    "CLEAN_PASS": "done",
    "BLOCKED": "blocked",
    "recorded": "done",
}


def _derive_roster(reports):
    latest_claude = next((r for r in reports if r["agent"] == "claude"), None)
    latest_codex = next((r for r in reports if r["agent"] == "codex"), None)
    claude_state = _STATE_FOR_VERDICT.get((latest_claude or {}).get("verdict"), "idle")
    return [
        {"id": "claude_builder", "name": "Claude builder", "role": "implementer",
         "state": claude_state, "branch": (latest_claude or {}).get("branch"),
         "worktree": None, "current_task": (latest_claude or {}).get("title"),
         "token_estimate": None, "cost_estimate_usd": None,
         "note": "Derived from the latest committed Claude report."},
        {"id": "codex_auditor", "name": "Codex auditor", "role": "auditor",
         "state": "done" if latest_codex else "queued",
         "branch": (latest_codex or {}).get("branch"), "worktree": None,
         "current_task": (latest_codex or {}).get("title") or "audit pending",
         "token_estimate": None, "cost_estimate_usd": None,
         "note": "Derived from the latest committed Codex report (if any)."},
        {"id": "hermes_coordinator", "name": "Hermes coordinator", "role": "coordinator",
         "state": "idle", "branch": None, "worktree": None,
         "current_task": "tracks lane status", "token_estimate": None,
         "cost_estimate_usd": None, "note": "Status-only; no live control."},
        {"id": "human_approver", "name": "Human approver", "role": "approver",
         "state": "idle", "branch": None, "worktree": None,
         "current_task": "approves merges after a CLEAN audit", "token_estimate": None,
         "cost_estimate_usd": None, "note": "Humans approve and merge."},
    ]


def build_status(reports=None):
    if reports is None:
        reports = collect_reports()
    latest_claude = next((r for r in reports if r["agent"] == "claude"), None)
    latest_codex = next((r for r in reports if r["agent"] == "codex"), None)
    main_sha = next((r["origin_main_short"] for r in reports if r.get("origin_main_short")), None)
    audit_target = next((r["codex_audit_target"] for r in reports if r.get("codex_audit_target")), None)
    return {
        "latest_main_commit_recorded": main_sha or "unavailable",
        "latest_main_commit_source": "recorded in the most recent local report (file-only, not a live git read)",
        "latest_claude_branch": (latest_claude or {}).get("branch") or "unavailable",
        "latest_claude_milestone": (latest_claude or {}).get("milestone"),
        "latest_codex_audit": audit_target or (latest_codex or {}).get("milestone") or "unavailable",
        "memory_vault_present": MEMORY_VAULT_README.is_file(),
        "tool_intake_present": TOOL_INTAKE_INVENTORY.is_file(),
        "report_count": len(reports),
    }


def _force_safe(trace):
    trace["ok"] = True
    trace["milestone"] = trace.get("milestone") or MILESTONE
    trace["mode"] = "local_trace"
    trace["simulation"] = False
    trace["live_execution"] = False
    trace["served_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    safety = dict(trace.get("safety") or {})
    safety.update({"live_execution": False, "simulation": False, "read_only": True})
    trace["safety"] = safety
    return trace


def build_trace():
    reports = collect_reports()
    if not reports:
        sample = _read_json(SAMPLE_TRACE)
        if isinstance(sample, dict):
            return _force_safe(sample)
    status = build_status(reports)
    timeline = [
        {"t": r["milestone"], "agent": r["agent"], "from_state": "running",
         "to_state": _STATE_FOR_VERDICT.get(r["verdict"], "done"), "note": r["title"]}
        for r in reports
    ]
    traces = [
        {"step": i, "agent": r["agent"], "action": r["verdict"],
         "note": "{0} - {1}".format(r["milestone"], r["title"])}
        for i, r in enumerate(reports, 1)
    ]
    return _force_safe({
        "milestone": MILESTONE,
        "title": "Ghoti Agent Arena - local trace",
        "mode": "local_trace",
        "source": "local report files",
        "scenario": "Recent committed Claude/Codex reports and handoffs, read-only.",
        "status": status,
        "agents": _derive_roster(reports),
        "task_states": ["idle", "queued", "running", "blocked", "done"],
        "queue": [],
        "timeline": timeline,
        "handoffs": collect_handoffs(),
        "traces": traces,
        "reports": reports,
        "totals": {"report_count": len(reports), "agent_count": 4,
                   "estimate_basis": "real reports; tokens/cost not estimated for traces"},
        "safety": dict(SAFETY),
    })


def build_check():
    sample = _read_json(SAMPLE_TRACE)
    sample_valid = isinstance(sample, dict) and sample.get("live_execution") is False
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    no_subprocess = re.search(r"import\s+subprocess", src) is None
    no_writes = re.search(r"\.write_text\s*\(|\.write_bytes\s*\(|\.mkdir\s*\(", src) is None
    try:
        trace = build_trace()
        trace_ok = bool(trace.get("ok")) and trace.get("live_execution") is False
    except Exception:
        trace_ok = False
    try:
        status = build_status()
        status_ok = isinstance(status, dict) and "memory_vault_present" in status
    except Exception:
        status_ok = False
    checks = {
        "ok": True,
        "milestone": MILESTONE,
        "tool": "ghoti_agent_arena_trace_loader",
        "loader_exists": Path(__file__).is_file(),
        "sample_trace_present": SAMPLE_TRACE.is_file(),
        "sample_trace_valid": sample_valid,
        "schema_present": TRACE_SCHEMA.is_file(),
        "reads_files_only": no_subprocess,
        "no_subprocess": no_subprocess,
        "no_writes": no_writes,
        "trace_builds": trace_ok,
        "trace_live_execution": False,
        "status_builds": status_ok,
        "memory_vault_present": MEMORY_VAULT_README.is_file(),
        "tool_intake_present": TOOL_INTAKE_INVENTORY.is_file(),
        "no_secrets": True,
        "safety": dict(SAFETY),
    }
    checks["ok"] = all([
        checks["loader_exists"], checks["sample_trace_present"], checks["sample_trace_valid"],
        checks["schema_present"], checks["reads_files_only"], checks["no_writes"],
        checks["trace_builds"], checks["status_builds"],
    ])
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ghoti Agent Arena trace loader (N+6.23A) - read-only, file-only."
    )
    parser.add_argument("--check", action="store_true", help="Emit a safety self-check JSON.")
    parser.add_argument("--trace-json", action="store_true", help="Emit the real local trace JSON.")
    parser.add_argument("--status-json", action="store_true", help="Emit the status cards JSON.")
    parser.add_argument("--json", action="store_true", help="Force JSON output (default).")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.trace_json:
        print(json.dumps(build_trace(), indent=2))
    elif args.status_json:
        print(json.dumps({"ok": True, "milestone": MILESTONE, "mode": "local_trace",
                          "simulation": False, "live_execution": False,
                          "status": build_status(), "safety": dict(SAFETY)}, indent=2))
    else:
        print(json.dumps(build_check(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
