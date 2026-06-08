"""
ghoti_agent_systems_trial.py — N+6.35A dry-run trial planner for plug-and-play agent systems.

Reads a JSON task spec, selects a candidate engine, outputs a dry-run execution plan,
routes to the correct model tier, and validates through the N+6.33A dual gate.

Never launches third-party code. Refuses live hooks, MCP servers, Docker, and any
live computer-use action.

CLI flags:
  --check               Safety status (no task required)
  --task <path>         Path to task-spec JSON
  --sandbox <path>      Path to third-party sandbox root (default: 21_repos/third_party_runtime_sandbox)
  --inventory <path>    Path to repo inventory JSON
  --json                Machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

MILESTONE = "N+6.35A"
SANDBOX_RELATIVE = "21_repos/third_party_runtime_sandbox"
INVENTORY_RELATIVE = "14_context/agent_systems_trial/agent_systems_inventory_n6_35a.json"

# Engines allowed for live trial planning (others are inspect-only)
_TRIAL_READY_VERDICTS = {"MOST_READY", "SECOND_READY", "CLI_ONLY"}

# Capabilities that are globally blocked — no plan may include these
_GLOBALLY_BLOCKED = frozenset({
    "hooks", "docker", "mcp", "live_computer_use", "auto_submit",
    "account_actions", "browser", "secrets", "shell_execution",
    "real_os_input", "mass_messaging", "telemetry_upload",
    "vm_launch", "live_launch",
})

# Task-type → preferred engine ID (deterministic selection)
_TASK_TYPE_ENGINE = {
    "swarm_coordination": "claude_swarm",
    "parallel_tasks": "am_will_swarms",
    "agent_launch": "claude_swarm",
    "skill_execution": "am_will_swarms",
    "cli_batch": "clawteam",
    "code_fix": "claude_swarm",
    "merge_gate": "claude_swarm",
    "summary": "am_will_swarms",
    "coordination": "claude_swarm",
}

# Model routing table (N+6.35A spec)
_MODEL_ROUTING: dict[str, dict[str, str]] = {
    "complex_integration": {
        "model": "claude-opus-max",
        "tier": "Claude Opus Max",
        "reason": "High-stakes synthesis, multi-repo integration, final decisions",
    },
    "small_fix": {
        "model": "claude-sonnet-max",
        "tier": "Claude Sonnet Max",
        "reason": "Small focused changes, low-risk edits",
    },
    "merge_gate": {
        "model": "codex-extra-high",
        "tier": "Codex Extra High",
        "reason": "Merge-gate checks, code audit, formal verification",
    },
    "coordination": {
        "model": "hermes-gpt-5-5-medium",
        "tier": "Hermes GPT-5.5 Medium",
        "reason": "Multi-agent coordination, task dispatch, plan rendering",
    },
    "summary": {
        "model": "deepseek-v4",
        "tier": "DeepSeek",
        "reason": "Cheap long-context background summaries (non-sensitive, repo-local only)",
        "guards": "No secrets, no private content. Future only — no live calls in N+6.35A.",
    },
}

# Safety block present on every result
_SAFETY_BLOCK: dict[str, Any] = {
    "live_execution": False,
    "live_computer_use_enabled": False,
    "hooks_enabled": False,
    "docker_enabled": False,
    "mcp_enabled": False,
    "auto_submit": False,
    "simulation": True,
    "third_party_code_executed": False,
    "third_party_code_imported": False,
    "secrets_committed": False,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_sandbox(repo_root: Path) -> Path:
    return repo_root / SANDBOX_RELATIVE


def _default_inventory(repo_root: Path) -> Path:
    return repo_root / INVENTORY_RELATIVE


def _load_inventory(inventory_path: Path) -> list[dict]:
    if not inventory_path.exists():
        return []
    with inventory_path.open() as fh:
        data = json.load(fh)
    return data.get("repos", [])


def _detect_repo(sandbox: Path, repo_id: str) -> dict:
    repo_path = sandbox / repo_id
    present = repo_path.exists() and (repo_path / ".git").exists()
    commit = "unknown"
    if present:
        head_file = repo_path / ".git" / "HEAD"
        if head_file.exists():
            ref = head_file.read_text().strip()
            if ref.startswith("ref: "):
                branch_ref = repo_path / ".git" / ref[5:]
                if branch_ref.exists():
                    commit = branch_ref.read_text().strip()[:10]
            elif len(ref) >= 10:
                commit = ref[:10]
    return {"id": repo_id, "present": present, "commit": commit, "path": str(repo_path)}


def _select_engine(task_spec: dict, inventory: list[dict]) -> dict:
    task_type = task_spec.get("task_type", "")
    complexity = task_spec.get("complexity", "medium")

    ready_ids = {r["id"] for r in inventory if r.get("verdict") in _TRIAL_READY_VERDICTS}

    preferred = _TASK_TYPE_ENGINE.get(task_type)
    if preferred and preferred in ready_ids:
        engine_entry = next((r for r in inventory if r["id"] == preferred), None)
        if engine_entry:
            return {
                "selected": preferred,
                "reason": f"task_type={task_type!r} maps to preferred engine",
                "complexity": complexity,
                "entry": engine_entry,
            }

    # Fallback: pick by trial_order among ready engines
    ready = sorted(
        [r for r in inventory if r.get("verdict") in _TRIAL_READY_VERDICTS],
        key=lambda r: r.get("trial_order", 99),
    )
    if ready:
        entry = ready[0]
        return {
            "selected": entry["id"],
            "reason": "fallback: lowest trial_order among ready engines",
            "complexity": complexity,
            "entry": entry,
        }

    return {"selected": None, "reason": "no_ready_engine_found", "complexity": complexity, "entry": None}


def _route_model(task_spec: dict, engine_selection: dict) -> dict:
    task_type = task_spec.get("task_type", "")
    complexity = task_spec.get("complexity", "medium")

    if task_type == "merge_gate":
        key = "merge_gate"
    elif task_type == "summary":
        key = "summary"
    elif task_spec.get("requires_coordination"):
        key = "coordination"
    elif complexity == "high":
        key = "complex_integration"
    elif complexity == "low":
        key = "small_fix"
    else:
        key = "coordination"

    return {"routing_key": key, **_MODEL_ROUTING[key]}


def _check_hooks_blocked(task_spec: dict) -> bool:
    caps = task_spec.get("capabilities", [])
    actions = task_spec.get("actions", [])
    hook_markers = {"hooks", "install_hooks", "enable_hooks", "PreToolUse", "PreToolWrite"}
    return bool(hook_markers.intersection(set(caps) | set(actions)))


def _requested_blocked_capabilities(task_spec: dict) -> list[str]:
    requested = {
        value
        for field in ("capabilities", "actions")
        for value in task_spec.get(field, [])
        if isinstance(value, str)
    }
    return sorted(requested & _GLOBALLY_BLOCKED)


def _build_execution_plan(task_spec: dict, engine_selection: dict, model_route: dict) -> dict:
    engine_id = engine_selection.get("selected")
    entry = engine_selection.get("entry") or {}

    actions = [
        {
            "step": 1,
            "action": "read_inventory",
            "target": "14_context/agent_systems_trial/agent_systems_inventory_n6_35a.json",
            "action_type": "fixture_read",
            "dry_run": True,
        },
        {
            "step": 2,
            "action": "detect_sandbox_repo",
            "target": entry.get("sandbox_path", f"21_repos/third_party_runtime_sandbox/{engine_id}"),
            "action_type": "repo_read",
            "dry_run": True,
        },
        {
            "step": 3,
            "action": "render_coordinator_plan",
            "target": engine_id,
            "action_type": "plan_render",
            "dry_run": True,
            "model": model_route.get("model"),
        },
        {
            "step": 4,
            "action": "validate_through_dual_gate",
            "target": "ghoti_computer_use_adapter --rust-bridge",
            "action_type": "local_policy_check",
            "dry_run": True,
        },
    ]

    return {
        "plan_id": task_spec.get("task_id", "unset"),
        "engine": engine_id,
        "engine_verdict": entry.get("verdict"),
        "model_routing": model_route,
        "dry_run": True,
        "live_launch": False,
        "requires_human_approval": True,
        "capabilities": ["fixture_read", "repo_read", "plan_render", "local_policy_check"],
        "actions": actions,
    }


def _validate_plan(plan: dict) -> dict:
    import tempfile

    blocked = []

    for cap in plan.get("capabilities", []):
        if cap in _GLOBALLY_BLOCKED:
            blocked.append(cap)

    for action in plan.get("actions", []):
        if action.get("action_type") in _GLOBALLY_BLOCKED:
            blocked.append(action.get("action_type"))

    if plan.get("live_launch"):
        blocked.append("live_launch")

    if blocked:
        return {
            "gate": "ghoti_agent_systems_trial_pre_filter",
            "allowed": False,
            "blocked_capabilities": list(set(blocked)),
            "reason": "globally_blocked_capability_or_live_launch",
        }

    # Run through the N+6.33A dual gate adapter via its file-based entry point
    adapter_dir = _repo_root() / "03_scripts" / "computer_use_adapter"
    if not (adapter_dir / "ghoti_computer_use_adapter.py").exists():
        return {
            "gate": "dual_gate",
            "allowed": False,
            "blocked_capabilities": [],
            "reason": "adapter_not_found_fail_closed",
            "adapter_available": False,
        }

    # Build a minimal CU-adapter-compatible plan from the first action
    first_action = plan["actions"][0] if plan.get("actions") else {}
    cu_plan = {
        "plan_id": plan.get("plan_id", "agent_systems_trial"),
        "action_type": first_action.get("action_type", "fixture_read"),
        "target": "local_sandbox",
        "target_url": "",
        "value": "",
        "dry_run": True,
        "requires_human_approval": plan.get("requires_human_approval", True),
        "capabilities": [],
    }

    sys.path.insert(0, str(adapter_dir))
    try:
        import ghoti_computer_use_adapter as _bridge  # type: ignore[import]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            json.dump(cu_plan, tf)
            tmp_path = tf.name
        try:
            result = _bridge._run_plan(tmp_path, rust_bridge=True)
        finally:
            os.unlink(tmp_path)
        allowed = result.get("ok", False)
        return {
            "gate": "dual_gate",
            "allowed": allowed,
            "blocked_capabilities": result.get("blocked_capabilities", []),
            "reason": result.get("reason", ""),
            "rust_policy_bridge": result.get("rust_policy_bridge", {}),
            "adapter_available": True,
        }
    except Exception as exc:
        return {
            "gate": "dual_gate",
            "allowed": False,
            "blocked_capabilities": [],
            "reason": f"adapter_import_error_fail_closed: {exc}",
            "adapter_available": False,
        }
    finally:
        if str(adapter_dir) in sys.path:
            sys.path.remove(str(adapter_dir))


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def _run_check(sandbox: Path | None = None, inventory_path: Path | None = None) -> dict:
    repo_root = _repo_root()
    if sandbox is None:
        sandbox = _default_sandbox(repo_root)
    if inventory_path is None:
        inventory_path = _default_inventory(repo_root)

    inventory = _load_inventory(inventory_path)
    repo_detections = [_detect_repo(sandbox, r["id"]) for r in inventory]
    present_count = sum(1 for r in repo_detections if r["present"])

    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "check",
        "sandbox_root": str(sandbox),
        "inventory_path": str(inventory_path),
        "inventory_loaded": bool(inventory),
        "repos_in_inventory": len(inventory),
        "repos_present_in_sandbox": present_count,
        "safety_block": _SAFETY_BLOCK,
        "globally_blocked_capabilities": sorted(_GLOBALLY_BLOCKED),
        "trial_ready_verdicts": sorted(_TRIAL_READY_VERDICTS),
    }


def _run_trial(task_spec_path: Path, sandbox: Path | None = None,
               inventory_path: Path | None = None) -> dict:
    repo_root = _repo_root()
    if sandbox is None:
        sandbox = _default_sandbox(repo_root)
    if inventory_path is None:
        inventory_path = _default_inventory(repo_root)

    with task_spec_path.open() as fh:
        task_spec = json.load(fh)

    if _check_hooks_blocked(task_spec):
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "trial",
            "task_id": task_spec.get("task_id"),
            "error": "hooks_requested",
            "reason": "Live hooks (PreToolUse, PreToolWrite, enable_hooks) are permanently blocked in the Ghoti environment.",
            "safety_block": _SAFETY_BLOCK,
        }

    blocked_requests = _requested_blocked_capabilities(task_spec)
    if blocked_requests:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "trial",
            "task_id": task_spec.get("task_id"),
            "error": "globally_blocked_request",
            "reason": "Task requested globally blocked capabilities or actions.",
            "blocked_capabilities": blocked_requests,
            "safety_block": _SAFETY_BLOCK,
        }

    inventory = _load_inventory(inventory_path)
    engine_selection = _select_engine(task_spec, inventory)

    if engine_selection["selected"] is None:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "trial",
            "task_id": task_spec.get("task_id"),
            "error": "no_ready_engine",
            "reason": engine_selection["reason"],
            "safety_block": _SAFETY_BLOCK,
        }

    model_route = _route_model(task_spec, engine_selection)
    plan = _build_execution_plan(task_spec, engine_selection, model_route)
    validation = _validate_plan(plan)

    accepted = validation.get("allowed", False)

    return {
        "ok": accepted,
        "milestone": MILESTONE,
        "mode": "trial",
        "task_id": task_spec.get("task_id"),
        "accepted": accepted,
        "engine_selection": {
            "selected": engine_selection["selected"],
            "reason": engine_selection["reason"],
            "verdict": engine_selection.get("entry", {}).get("verdict"),
        },
        "model_routing": model_route,
        "execution_plan": plan,
        "validation": validation,
        "safety_block": _SAFETY_BLOCK,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ghoti N+6.35A plug-and-play agent systems trial planner")
    parser.add_argument("--check", action="store_true", help="Safety status check (no task required)")
    parser.add_argument("--task", metavar="PATH", help="Path to task-spec JSON")
    parser.add_argument("--sandbox", metavar="PATH", help="Override sandbox root path")
    parser.add_argument("--inventory", metavar="PATH", help="Override inventory JSON path")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Machine-readable output")
    args = parser.parse_args(argv)

    sandbox = Path(args.sandbox) if args.sandbox else None
    inventory_path = Path(args.inventory) if args.inventory else None

    if args.check or not args.task:
        result = _run_check(sandbox=sandbox, inventory_path=inventory_path)
    else:
        result = _run_trial(Path(args.task), sandbox=sandbox, inventory_path=inventory_path)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] ok={ok} milestone={MILESTONE}")
        if "accepted" in result:
            print(f"  accepted={result['accepted']} engine={result.get('engine_selection', {}).get('selected')}")
            mr = result.get("model_routing", {})
            print(f"  model_routing={mr.get('tier')} ({mr.get('routing_key')})")
        sb = result.get("safety_block", {})
        print(f"  simulation={sb.get('simulation')} live_execution={sb.get('live_execution')}")
        if not ok:
            print(f"  error={result.get('error')} reason={result.get('reason')}")


if __name__ == "__main__":
    _main()
