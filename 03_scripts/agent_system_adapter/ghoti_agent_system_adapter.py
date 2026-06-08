"""
ghoti_agent_system_adapter.py — N+6.36A first runnable plug-and-play agent system adapter.

Detects the safest external agent system available in the gitignored sandbox,
reads its package metadata and license, builds a no-op dry-run plan, and
validates the plan through the N+6.33A dual gate.

Selected system: claude_swarm (MOST_READY)
  - Pure Python ≥3.11, MIT, claude-agent-sdk-based
  - Has a native --dry-run flag (shows plan without executing)
  - No Docker, no MCP server, no hooks
  - Entry point: claude-swarm = "claude_swarm.cli:main"

This adapter does NOT install, import, or execute any code from claude_swarm.
It reads pyproject.toml / README.md / LICENSE as text files only.

Candidate external command (BLOCKED pending provider/API audit):
    claude-swarm --dry-run "task description"

Blocked command (NEVER in Ghoti environment):
    claude-swarm "task description"   # launches real agents

CLI flags:
  --check               Safety status (no sandbox required)
  --smoke               Metadata smoke + no-op plan (sandbox required)
  --sandbox <path>      Override sandbox root
  --json                Machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

MILESTONE = "N+6.36A"
SANDBOX_RELATIVE = "21_repos/third_party_runtime_sandbox"

# Primary target and fallback priority
_PRIMARY_TARGET = "claude_swarm"
_TARGET_PRIORITY = [
    "claude_swarm",      # MOST_READY metadata target; external invocation remains blocked
    "am_will_swarms",    # SECOND_READY: skills only, no-install
    "clawteam",          # CLI_ONLY: pip CLI (no MCP server)
]

# Capabilities that are globally blocked — the plan must never include these
_GLOBALLY_BLOCKED = frozenset({
    "hooks", "docker", "mcp", "live_computer_use", "auto_submit",
    "account_actions", "browser", "secrets", "shell_execution",
    "real_os_input", "mass_messaging", "telemetry_upload",
    "vm_launch", "live_launch", "live_agent_launch",
})

# Capabilities allowed in the no-op plan
_PLAN_CAPABILITIES = ["plan_render", "fixture_read", "repo_read", "local_policy_check"]

# Safety block present on every result
_SAFETY_BLOCK: dict[str, Any] = {
    "live_execution": False,
    "live_computer_use_enabled": False,
    "hooks_enabled": False,
    "docker_enabled": False,
    "mcp_enabled": False,
    "auto_submit": False,
    "simulation": True,
    "live_agent_launch": False,
    "third_party_code_executed": False,
    "third_party_code_imported": False,
    "secrets_committed": False,
    "real_os_paths_committed": False,
}

# What claude_swarm needs before a live run (human gate checklist)
_LIVE_APPROVAL_CHECKLIST = [
    "Separate Claude profile / isolated environment (not the Ghoti working profile)",
    "No Ghoti repo access from the trial environment",
    "API key approved for use in that environment only",
    "Sandbox-only target: no real accounts, no external services",
    "Separate audited milestone reviewed by human operator",
    "Dual-gate green (N+6.33A adapter + Rust mirror both allow the plan)",
    "Human approval recorded in milestone doc before any live run",
]

_EXTERNAL_DRY_RUN_WARNING = (
    "Blocked pending separate provider/API audit: claude-swarm --dry-run requires "
    "ANTHROPIC_API_KEY, calls the decomposition model, and writes a session record."
)

# Adapter selection rationale
_SELECTION_RATIONALE = {
    "claude_swarm": (
        "Selected as primary (MOST_READY): Python ≥3.11, MIT license, pure-pip install, no Docker, "
        "no MCP server, no hooks. Has a native --dry-run flag that shows a decomposed "
        "task plan without launching worker agents, but still requires a provider key/call "
        "and writes a session. External invocation remains blocked. Coordinator/worker plan "
        "shape maps cleanly onto the Ghoti policy checker's allowed capability set."
    ),
    "am_will_swarms": "Deferred: skills only, no license confirmed (do not copy code).",
    "clawteam": "Deferred: ships clawteam-mcp server — MCP must not be enabled in Ghoti.",
    "ruflo": "Deferred: MCP server + hooks daemon; install scripts require line-by-line review.",
    "ecc": "Deferred: ships hooks.json (PreToolUse/PreToolWrite) — hooks must never be installed.",
    "paperclip": "Deferred: requires Docker.",
    "hermes_paperclip_adapter": "Deferred: requires Hermes + Paperclip reviewed first.",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_sandbox(repo_root: Path) -> Path:
    return repo_root / SANDBOX_RELATIVE


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _sandbox_is_allowed(sandbox: Path, repo_root: Path) -> bool:
    allowed_root = _default_sandbox(repo_root).resolve()
    try:
        sandbox.resolve().relative_to(allowed_root)
    except ValueError:
        return False
    return True


def _detect_target(sandbox: Path) -> dict:
    for target_id in _TARGET_PRIORITY:
        repo_path = sandbox / target_id
        if not repo_path.exists():
            continue
        git_head = repo_path / ".git" / "HEAD"
        if not git_head.exists():
            continue
        commit = "unknown"
        ref = git_head.read_text().strip()
        if ref.startswith("ref: "):
            branch_ref = repo_path / ".git" / ref[5:]
            if branch_ref.exists():
                commit = branch_ref.read_text().strip()[:10]
        elif len(ref) >= 10:
            commit = ref[:10]
        return {
            "selected": target_id,
            "path": str(repo_path),
            "commit": commit,
            "present": True,
        }
    return {"selected": None, "path": None, "commit": None, "present": False}


def _read_pyproject_metadata(repo_path: Path) -> dict:
    pyproject = repo_path / "pyproject.toml"
    metadata: dict[str, Any] = {
        "name": "unknown",
        "version": "unknown",
        "license": "unknown",
        "requires_python": "unknown",
        "description": "",
        "entry_point": None,
        "dry_run_flag": None,
    }
    if not pyproject.exists():
        return metadata
    text = _read_text_file(pyproject)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("name =") and metadata["name"] == "unknown":
            metadata["name"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("version =") and metadata["version"] == "unknown":
            metadata["version"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("license =") and metadata["license"] == "unknown":
            metadata["license"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("requires-python =") and metadata["requires_python"] == "unknown":
            metadata["requires_python"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("description =") and not metadata["description"]:
            metadata["description"] = line.split("=", 1)[1].strip().strip('"')
        elif "claude-swarm" in line and "=" in line and "cli:main" in line:
            metadata["entry_point"] = "claude-swarm"
            metadata["dry_run_flag"] = "--dry-run"
    return metadata


def _read_license_type(repo_path: Path) -> str:
    license_file = repo_path / "LICENSE"
    if not license_file.exists():
        return "unknown"
    text = _read_text_file(license_file)
    first_line = text.splitlines()[0] if text.strip() else ""
    if "MIT" in first_line:
        return "MIT"
    if "Apache" in first_line:
        return "Apache-2.0"
    return first_line[:50]


def _read_readme_excerpt(repo_path: Path) -> str:
    readme = repo_path / "README.md"
    if not readme.exists():
        return ""
    lines = _read_text_file(readme).splitlines()
    for line in lines:
        stripped = line.strip().lstrip("#").strip()
        if stripped and not stripped.lower().startswith("badge") and len(stripped) > 10:
            return stripped[:120]
    return ""


def _count_source_files(repo_path: Path) -> int:
    count = 0
    src = repo_path / "src"
    if src.exists():
        for f in src.rglob("*.py"):
            count += 1
    return count


def _read_metadata(repo_path: Path, target_id: str) -> dict:
    pkg = _read_pyproject_metadata(repo_path)
    return {
        "target_id": target_id,
        "path": f"{SANDBOX_RELATIVE}/{target_id}",
        "package_name": pkg["name"],
        "version": pkg["version"],
        "license": _read_license_type(repo_path),
        "requires_python": pkg["requires_python"],
        "description": pkg.get("description", ""),
        "readme_excerpt": _read_readme_excerpt(repo_path),
        "entry_point": pkg.get("entry_point"),
        "dry_run_flag": pkg.get("dry_run_flag"),
        "source_file_count": _count_source_files(repo_path),
        "safe_command": None,
        "candidate_external_command": (
            f"{pkg['entry_point']} --dry-run \"describe task here\""
            if pkg.get("entry_point") and pkg.get("dry_run_flag")
            else None
        ),
        "candidate_external_command_approved": False,
        "candidate_external_command_warning": _EXTERNAL_DRY_RUN_WARNING,
        "external_dry_run_requires_api_key": True,
        "external_dry_run_calls_provider": True,
        "external_dry_run_writes_session": True,
        "blocked_command": (
            f"{pkg['entry_point']} \"describe task here\"  # launches real agents"
            if pkg.get("entry_point")
            else None
        ),
        "rationale": _SELECTION_RATIONALE.get(target_id, ""),
        "third_party_code_imported": False,
        "third_party_code_executed": False,
    }


def _build_noop_plan(metadata: dict) -> dict:
    target_id = metadata["target_id"]
    return {
        "plan_id": f"noop-{target_id}-N+6.36A",
        "engine": target_id,
        "engine_version": metadata.get("version", "unknown"),
        "description": "Ghoti-native no-op dry-run plan. Reads metadata only. Does not install or run third-party code.",
        "dry_run": True,
        "live_launch": False,
        "live_agent_launch": False,
        "requires_human_approval": True,
        "capabilities": _PLAN_CAPABILITIES,
        "actions": [
            {
                "step": 1,
                "action": "detect_sandbox_repo",
                "target": metadata.get("path", ""),
                "action_type": "repo_read",
                "dry_run": True,
            },
            {
                "step": 2,
                "action": "read_package_metadata",
                "target": "pyproject.toml",
                "action_type": "fixture_read",
                "dry_run": True,
            },
            {
                "step": 3,
                "action": "render_noop_swarm_plan",
                "target": target_id,
                "action_type": "plan_render",
                "dry_run": True,
                "candidate_external_command": metadata.get("candidate_external_command"),
                "note": "Local plan rendered from metadata only; external candidate command remains blocked.",
            },
            {
                "step": 4,
                "action": "validate_through_dual_gate",
                "target": "ghoti_computer_use_adapter --rust-bridge",
                "action_type": "local_policy_check",
                "dry_run": True,
            },
        ],
        "synthetic_swarm_config": {
            "swarm": {
                "name": f"ghoti-noop-{target_id}",
                "max_concurrent": 1,
                "budget_usd": 0.0,
                "note": "This is a Ghoti-native synthetic representation only. No real agents configured.",
            },
            "agents": {},
            "connections": [],
        },
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
    if plan.get("live_launch") or plan.get("live_agent_launch"):
        blocked.append("live_launch")

    if blocked:
        return {
            "gate": "ghoti_adapter_pre_filter",
            "allowed": False,
            "blocked_capabilities": list(set(blocked)),
            "reason": "globally_blocked_capability_or_live_launch",
        }

    adapter_dir = _repo_root() / "03_scripts" / "computer_use_adapter"
    if not (adapter_dir / "ghoti_computer_use_adapter.py").exists():
        return {
            "gate": "dual_gate",
            "allowed": False,
            "blocked_capabilities": [],
            "reason": "adapter_not_found_fail_closed",
            "adapter_available": False,
        }

    cu_plan = {
        "plan_id": plan.get("plan_id", "agent_system_adapter_noop"),
        "action_type": "plan_render",
        "target": "local_sandbox",
        "target_url": "",
        "value": "",
        "dry_run": True,
        "requires_human_approval": True,
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
        bridge_ready = bool(result.get("rust_policy_bridge_ready", False))
        rust_decision = result.get("rust_policy_decision", {})
        rust_allowed = bool(rust_decision.get("allowed", False))
        allowed = bool(result.get("ok", False)) and bridge_ready and rust_allowed
        return {
            "gate": "dual_gate",
            "allowed": allowed,
            "blocked_capabilities": result.get("blocked_capabilities", []),
            "reason": (
                result.get("reason", "")
                if allowed
                else "dual_gate_not_ready_or_denied"
            ),
            "rust_policy_bridge_ready": bridge_ready,
            "rust_policy_decision": rust_decision,
            "rust_allowed": rust_allowed,
            "accepted": result.get("accepted"),
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

def _run_check(sandbox: Path | None = None) -> dict:
    repo_root = _repo_root()
    if sandbox is None:
        sandbox = _default_sandbox(repo_root)
    if not _sandbox_is_allowed(sandbox, repo_root):
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "check",
            "error": "sandbox_outside_allowed_root",
            "reason": f"Sandbox must stay under {SANDBOX_RELATIVE}.",
            "safety_block": _SAFETY_BLOCK,
        }

    detection = _detect_target(sandbox)

    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "check",
        "sandbox_root": SANDBOX_RELATIVE,
        "selected_target": detection["selected"],
        "target_present": detection["present"],
        "globally_blocked_capabilities": sorted(_GLOBALLY_BLOCKED),
        "selection_rationale": {k: v for k, v in _SELECTION_RATIONALE.items()},
        "live_approval_checklist": _LIVE_APPROVAL_CHECKLIST,
        "safety_block": _SAFETY_BLOCK,
    }


def _run_smoke(sandbox: Path | None = None) -> dict:
    repo_root = _repo_root()
    if sandbox is None:
        sandbox = _default_sandbox(repo_root)
    if not _sandbox_is_allowed(sandbox, repo_root):
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "smoke",
            "error": "sandbox_outside_allowed_root",
            "reason": f"Sandbox must stay under {SANDBOX_RELATIVE}.",
            "safety_block": _SAFETY_BLOCK,
        }

    detection = _detect_target(sandbox)
    if not detection["present"]:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "smoke",
            "error": "no_target_detected",
            "reason": f"No supported agent repo found in sandbox: {sandbox}",
            "safety_block": _SAFETY_BLOCK,
        }

    repo_path = Path(detection["path"])
    if not _sandbox_is_allowed(repo_path, repo_root):
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "smoke",
            "error": "target_outside_allowed_sandbox",
            "reason": "Detected target resolves outside the approved runtime sandbox.",
            "safety_block": _SAFETY_BLOCK,
        }
    metadata = _read_metadata(repo_path, detection["selected"])
    metadata["commit"] = detection["commit"]

    plan = _build_noop_plan(metadata)
    validation = _validate_plan(plan)
    accepted = validation.get("allowed", False)

    return {
        "ok": accepted,
        "milestone": MILESTONE,
        "mode": "smoke",
        "selected_target": detection["selected"],
        "target_commit": detection["commit"],
        "accepted": accepted,
        "metadata": metadata,
        "noop_plan": plan,
        "validation": validation,
        "safe_command": metadata.get("safe_command"),
        "candidate_external_command": metadata.get("candidate_external_command"),
        "candidate_external_command_approved": metadata.get("candidate_external_command_approved"),
        "candidate_external_command_warning": metadata.get("candidate_external_command_warning"),
        "blocked_command": metadata.get("blocked_command"),
        "selection_rationale": _SELECTION_RATIONALE.get(detection["selected"], ""),
        "deferred_systems": {k: v for k, v in _SELECTION_RATIONALE.items()
                             if k != detection["selected"]},
        "live_approval_checklist": _LIVE_APPROVAL_CHECKLIST,
        "safety_block": _SAFETY_BLOCK,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Ghoti N+6.36A first runnable agent system adapter"
    )
    parser.add_argument("--check", action="store_true", help="Safety status check")
    parser.add_argument("--smoke", action="store_true", help="Metadata smoke + no-op plan")
    parser.add_argument("--sandbox", metavar="PATH", help="Override sandbox root path")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Machine-readable output")
    args = parser.parse_args(argv)

    sandbox = Path(args.sandbox) if args.sandbox else None

    if args.smoke:
        result = _run_smoke(sandbox=sandbox)
    else:
        result = _run_check(sandbox=sandbox)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] ok={ok} mode={result.get('mode')}")
        print(f"  selected_target={result.get('selected_target')}")
        sb = result.get("safety_block", {})
        print(f"  simulation={sb.get('simulation')} live_execution={sb.get('live_execution')}")
        if "safe_command" in result and result["safe_command"]:
            print(f"  safe_command:    {result['safe_command']}")
        if result.get("candidate_external_command"):
            print(f"  blocked_candidate_command: {result['candidate_external_command']}")
        if "blocked_command" in result and result["blocked_command"]:
            print(f"  blocked_command: {result['blocked_command']}")
        if not ok:
            print(f"  error={result.get('error')} reason={result.get('reason')}")


if __name__ == "__main__":
    _main()
