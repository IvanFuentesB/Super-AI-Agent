#!/usr/bin/env python3
"""Ghoti repo-backed controlled swarm launcher - DRY RUN ONLY (N+6.27A).

The first Ghoti-side swarm launcher. It reads a task spec (JSON), validates scope, assigns
roles, detects file-ownership overlap, proposes worktree paths (placeholders), and writes a
**dry-run execution plan** that an operator could approve later. It is repo-backed: the
design patterns are adapted from inspected swarm repos (see
14_context/swarm_launcher/repo_inspiration_manifest_n6_27a.json); no third-party code is
vendored.

Safe by construction - it launches NOTHING:

  * Python standard library only. It spawns no process: no subprocess, no shell, no
    os.system, no popen, no exec.
  * It does not spawn any process and does not start Claude/Codex/Hermes.
  * It does not create git worktrees - it only proposes placeholder paths.
  * It writes NO files; it parses the task JSON and prints the plan JSON to stdout.
  * No browser/computer-use, no MCP, no account/money/trading/mass-messaging, no
    auto-submit, no secret access.
  * live_launch_enabled is always false; approval_required and kill_switch_required are
    always true. Real launching is deferred to a later, audited, human-approved milestone.

CLI:
  --check                 emit a safety self-check JSON
  --task <path> --dry-run emit the dry-run execution plan for a task spec JSON
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

MILESTONE = "N+6.27A"

# 03_scripts/swarm_launcher/ghoti_swarm_launcher.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
INSPIRATION_MANIFEST = "14_context/swarm_launcher/repo_inspiration_manifest_n6_27a.json"

# Task roles that can be assigned to a task.
ROLES = ["planner", "builder", "auditor", "summarizer", "human_approver"]

# The default agent roster (one coordinator + role agents + the human approver).
DEFAULT_AGENTS = [
    {"id": "chatgpt_strategy", "name": "ChatGPT strategy", "role": "planner"},
    {"id": "claude_builder", "name": "Claude builder", "role": "builder"},
    {"id": "codex_auditor", "name": "Codex auditor", "role": "auditor"},
    {"id": "hermes_coordinator", "name": "Hermes coordinator", "role": "coordinator"},
    {"id": "local_summarizer", "name": "local model summarizer", "role": "summarizer"},
    {"id": "human_approver", "name": "Human approver", "role": "human_approver"},
]
ROLE_TO_AGENT = {a["role"]: a["id"] for a in DEFAULT_AGENTS}
AGENT_BY_ID = {a["id"]: a for a in DEFAULT_AGENTS}

DEFAULT_MAX_PARALLEL = 2

GATES = {
    "live_launch_enabled": False,
    "approval_required": True,
    "kill_switch_required": True,
    "human_approver_required": True,
    "main_merge": "codex_gate_only",
    "one_owner_per_path": True,
    "dry_run_first": True,
}

REFUSED_LIVE_ACTIONS = [
    "live agent launch",
    "process / subprocess / shell launch",
    "git worktree creation",
    "starting a Claude / Codex / Hermes process",
    "browser / computer-use",
    "MCP",
    "account login",
    "money / trading actions",
    "mass messaging",
    "auto-submit",
    "secret / token access",
]

SAFETY = {
    "milestone": MILESTONE,
    "dry_run_only": True,
    "live_launch_enabled": False,
    "approval_required": True,
    "kill_switch_required": True,
    "spawns_processes": False,
    "uses_subprocess": False,
    "uses_shell": False,
    "creates_worktrees": False,
    "writes_files": False,
    "reads_secret_values": False,
    "uses_browser_or_computer_use": False,
    "uses_mcp": False,
    "auto_submit": False,
}

REAL_LAUNCH_NOTE = (
    "Real launching is deferred to a later, audited, human-approved milestone. This output "
    "is a dry-run plan only; no process is spawned and no worktree is created."
)


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"__error__": str(exc)[:200]}


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")[:48] or "task"


def _path_within_scope(file_path, allowed):
    """A task file must be a repo-relative path, no drive, no absolute, no '..', and inside
    one of the allowed scope paths (if any are given)."""
    if not isinstance(file_path, str) or not file_path.strip():
        return False
    norm = file_path.replace("\\", "/").strip()
    if norm.startswith("/") or ".." in norm.split("/") or re.match(r"^[A-Za-z]:", norm):
        return False
    if allowed:
        return any(norm == a or norm.startswith(a.rstrip("/") + "/") for a in allowed)
    return True


def _validate_tasks(tasks):
    errors = []
    if not isinstance(tasks, list) or not tasks:
        return ["task spec has no 'tasks' list"]
    seen = set()
    for idx, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append("task #{0} is not an object".format(idx))
            continue
        tid = task.get("id")
        if not tid or not isinstance(tid, str):
            errors.append("task #{0} missing string 'id'".format(idx))
            continue
        if tid in seen:
            errors.append("duplicate task id: {0}".format(tid))
        seen.add(tid)
        if task.get("role") not in ROLES:
            errors.append("task {0} has invalid role {1!r}".format(tid, task.get("role")))
        if not isinstance(task.get("files", []), list):
            errors.append("task {0} 'files' must be a list".format(tid))
    return errors


def _scope_violations(tasks, allowed):
    violations = []
    for task in tasks:
        for fpath in task.get("files", []) or []:
            if not _path_within_scope(fpath, allowed):
                violations.append({"task_id": task.get("id"), "path": fpath})
    return violations


def _overlap_conflicts(tasks):
    owners = {}
    for task in tasks:
        for fpath in task.get("files", []) or []:
            owners.setdefault(fpath, [])
            if task.get("id") not in owners[fpath]:
                owners[fpath].append(task.get("id"))
    return [{"path": p, "claimed_by": sorted(ids)} for p, ids in owners.items() if len(ids) > 1]


def _dependency_errors(tasks):
    ids = {t.get("id") for t in tasks}
    errors = []
    for task in tasks:
        for dep in task.get("depends_on", []) or []:
            if dep not in ids:
                errors.append("task {0} depends on unknown task {1}".format(task.get("id"), dep))
            if dep == task.get("id"):
                errors.append("task {0} depends on itself".format(task.get("id")))
    return errors


def _build_waves(tasks, max_parallel):
    by_id = {t["id"]: t for t in tasks}
    done = set()
    remaining = set(by_id)
    waves = []
    guard = 0
    while remaining and guard < 10000:
        guard += 1
        ready = sorted(tid for tid in remaining
                       if all(dep in done for dep in by_id[tid].get("depends_on", []) or []))
        if not ready:
            return None  # cycle / unsatisfiable
        for i in range(0, len(ready), max(1, max_parallel)):
            waves.append(ready[i:i + max_parallel])
        done |= set(ready)
        remaining -= set(ready)
    return waves if not remaining else None


def _proposed_worktree(task_id):
    # Placeholder only - never a real local path; no worktree is created.
    return "<repo>/.claude/worktrees/{0}".format(_slug(task_id))


def _assignments(tasks, wave_of):
    rows = []
    for task in tasks:
        role = task.get("role")
        agent_id = task.get("agent") or ROLE_TO_AGENT.get(role)
        agent = AGENT_BY_ID.get(agent_id, {"id": agent_id, "name": agent_id, "role": role})
        worktree = _proposed_worktree(task["id"])
        rows.append({
            "task_id": task["id"],
            "role": role,
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "description": str(task.get("description", ""))[:200],
            "files": list(task.get("files", []) or []),
            "depends_on": list(task.get("depends_on", []) or []),
            "proposed_worktree": worktree,
            "wave": wave_of.get(task["id"]),
            "would_run": ("DRY-RUN (NOT executed): would create worktree '{0}' and run {1} "
                          "on this task after human approval.").format(worktree, agent["name"]),
            "executed": False,
        })
    return rows


def _arena_status(tasks):
    """A status block shaped for the Agent Arena to visualize later (simulation only)."""
    roles_used = {t.get("role") for t in tasks}
    agents = []
    for agent in DEFAULT_AGENTS:
        if agent["role"] == "coordinator":
            state = "coordinating"
        elif agent["role"] == "human_approver":
            state = "approval_pending"
        elif agent["role"] in roles_used:
            state = "queued"
        else:
            state = "idle"
        agents.append({"id": agent["id"], "name": agent["name"], "role": agent["role"],
                       "state": state, "branch": None, "worktree": None})
    return {
        "mode": "dry_run_plan",
        "simulation": True,
        "live_execution": False,
        "task_states": ["idle", "queued", "approval_pending", "coordinating", "done"],
        "agents": agents,
        "note": "Safe to visualize in the Agent Arena; nothing is launched.",
    }


def build_plan(task_path):
    raw = _read_json(task_path)
    if isinstance(raw, dict) and "__error__" in raw:
        return {"ok": False, "milestone": MILESTONE, "mode": "dry_run", "status": "error",
                "error": "could not read task spec", "detail": raw["__error__"],
                "safety": dict(SAFETY)}
    tasks = raw.get("tasks") if isinstance(raw, dict) else None
    allowed = (raw.get("scope", {}) or {}).get("allowed_paths", []) if isinstance(raw, dict) else []
    max_parallel = int((raw.get("constraints", {}) or {}).get("max_parallel", DEFAULT_MAX_PARALLEL)) \
        if isinstance(raw, dict) else DEFAULT_MAX_PARALLEL

    blocked_reasons = []
    task_errors = _validate_tasks(tasks)
    blocked_reasons.extend(task_errors)
    tasks = tasks if isinstance(tasks, list) else []

    scope_v = _scope_violations(tasks, allowed) if not task_errors else []
    if scope_v:
        blocked_reasons.append("{0} file(s) fall outside the allowed scope".format(len(scope_v)))
    overlaps = _overlap_conflicts(tasks) if not task_errors else []
    if overlaps:
        blocked_reasons.append("{0} file path(s) claimed by more than one task "
                               "(one owner per path)".format(len(overlaps)))
    dep_errors = _dependency_errors(tasks) if not task_errors else []
    blocked_reasons.extend(dep_errors)

    waves = None
    if not task_errors and not dep_errors:
        waves = _build_waves(tasks, max_parallel)
        if waves is None:
            blocked_reasons.append("dependency cycle or unsatisfiable order")

    wave_of = {}
    if waves:
        for wi, wave in enumerate(waves):
            for tid in wave:
                wave_of[tid] = wi

    status = "blocked" if blocked_reasons else "dry_run_ready"
    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "dry_run",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_title": str(raw.get("title", "")) if isinstance(raw, dict) else "",
        "status": status,
        "blocked_reasons": blocked_reasons,
        "roles": list(ROLES),
        "default_agents": [dict(a) for a in DEFAULT_AGENTS],
        "max_parallel": max_parallel,
        "assignments": _assignments(tasks, wave_of) if not task_errors else [],
        "waves": waves or [],
        "overlap": {"one_owner_per_path": not overlaps, "conflicts": overlaps},
        "scope": {"allowed_paths": list(allowed or []), "violations": scope_v},
        "dependency_errors": dep_errors,
        "gates": dict(GATES),
        "arena_status": _arena_status(tasks) if not task_errors else {},
        "refused_live_actions": list(REFUSED_LIVE_ACTIONS),
        "repo_inspiration": {"manifest": INSPIRATION_MANIFEST,
                             "note": "design patterns adapted from inspected repos; no third-party code vendored"},
        "real_launch_note": REAL_LAUNCH_NOTE,
        "safety": dict(SAFETY),
    }


def build_check():
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    no_subprocess = re.search(r"import\s+subprocess|subprocess\s*\.", src) is None
    no_shell = re.search(r"shell\s*=\s*True", src) is None
    no_os_exec = re.search(r"os\.system\s*\(|os\.popen|os\.exec|\bPopen\b|pty\.spawn", src) is None
    no_writes = re.search(r"\.write_text\s*\(|\.write_bytes\s*\(|\.mkdir\s*\(|open\s*\([^)]*[\"'][aw]", src) is None
    example_dir = REPO_ROOT / "14_context" / "swarm_launcher" / "examples"
    examples_present = example_dir.is_dir() and any(example_dir.glob("*.json"))
    manifest_present = (REPO_ROOT / INSPIRATION_MANIFEST).is_file()
    checks = {
        "ok": True,
        "milestone": MILESTONE,
        "tool": "ghoti_swarm_launcher",
        "script_exists": Path(__file__).is_file(),
        "no_subprocess": no_subprocess,
        "no_shell_true": no_shell,
        "no_os_exec_or_popen": no_os_exec,
        "no_process_spawn": no_subprocess and no_os_exec,
        "no_file_writes": no_writes,
        "no_worktree_creation": True,
        "examples_present": bool(examples_present),
        "inspiration_manifest_present": manifest_present,
        "roles_complete": ROLES == ["planner", "builder", "auditor", "summarizer", "human_approver"],
        "default_agents_count": len(DEFAULT_AGENTS),
        "live_launch_enabled": False,
        "approval_required": True,
        "kill_switch_required": True,
        "dry_run_only": True,
        "no_secrets": True,
        "safety": dict(SAFETY),
    }
    checks["ok"] = all([
        checks["script_exists"], checks["no_subprocess"], checks["no_shell_true"],
        checks["no_os_exec_or_popen"], checks["no_file_writes"], checks["roles_complete"],
        not checks["live_launch_enabled"], checks["approval_required"],
        checks["kill_switch_required"],
    ])
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ghoti repo-backed controlled swarm launcher (N+6.27A) - DRY RUN ONLY."
    )
    parser.add_argument("--check", action="store_true", help="Emit a safety self-check JSON.")
    parser.add_argument("--task", default=None, help="Path to a task spec JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Emit the dry-run plan (only mode).")
    parser.add_argument("--json", action="store_true", help="Force JSON output (default).")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.check:
        print(json.dumps(build_check(), indent=2))
        return 0
    if args.task:
        plan = build_plan(args.task)
        print(json.dumps(plan, indent=2))
        if not plan.get("ok"):
            return 2
        return 0
    # No live mode exists. Default to the safety self-check.
    print(json.dumps(build_check(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
