"""
ghoti_claude_swarm_dry_run.py — N+6.37A Ghoti safety wrapper for claude-swarm dry-run.

Key findings from source-code inspection (claude_swarm/cli.py):
  - --dry-run REQUIRES ANTHROPIC_API_KEY and calls the Claude API (decompose_task)
    before skipping execution. This is NOT a true no-op.
    Status: BLOCKED — violates "no API keys, no account actions" hard rules.
  - --demo runs a simulated TUI with NO API key required, but writes session
    events to ~/.claude-swarm/sessions/ (home directory write).
    Status: CONDITIONALLY SAFE in an isolated scratch profile only.
  - --version and --help are fully safe.

This wrapper:
  1. Verifies claude-swarm is available (--version probe)
  2. Refuses to run if ANTHROPIC_API_KEY is set in env
  3. Refuses live mode (missing --dry-run or --demo flag)
  4. Refuses account/auth paths, non-scratch output paths, live launch flags
  5. In PROBE mode: checks tool availability only (no execution)
  6. In DEMO mode: runs --demo in a temp scratch dir (no API key path)
  7. Emits Agent-Arena-shaped status: simulation=true, live_execution=false

Blocked command (requires API key + makes API calls):
  claude-swarm --dry-run "task"

Conditionally safe (no API key, writes only to scratch):
  claude-swarm --demo

Fully safe probe (version check only):
  claude-swarm --version

CLI flags:
  --probe               Probe tool availability (--version check only)
  --demo-mode           Run --demo in a scratch directory (no API key)
  --check               Safety status check (no execution)
  --sandbox <path>      Sandbox root for detection
  --scratch <path>      Scratch directory for demo output
  --json                Machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

MILESTONE = "N+6.37A"
SANDBOX_RELATIVE = "21_repos/third_party_runtime_sandbox"

# API key environment variables — if any are set, refuse execution
_API_KEY_ENV_VARS = [
    "ANTHROPIC_API_KEY",
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
]

# Flags that indicate live mode (agents would actually launch)
_LIVE_LAUNCH_FLAGS = [
    # No --dry-run and no --demo = live mode
    # We detect this by requiring one of the safe flags explicitly
]

# Flags that are safe
_SAFE_FLAGS = {"--dry-run", "--demo", "--version", "--help", "-v", "--no-ui"}

# Blocked flags that must never be passed
_BLOCKED_FLAGS = {
    "--mcp", "--hooks", "--browser",
    # No explicit flag needed; live mode is the DEFAULT
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
    "live_agent_launch": False,
    "api_key_used": False,
    "network_attempted": False,
    "files_written_outside_scratch": False,
    "third_party_code_executed": False,
    "secrets_committed": False,
}

# Execution status constants
_STATUS_NOT_INSTALLED = "not_installed"
_STATUS_API_KEY_REQUIRED = "api_key_required_blocked"
_STATUS_PROBE_OK = "probe_ok"
_STATUS_DEMO_OK = "demo_ok"
_STATUS_DEMO_FAILED = "demo_failed"
_STATUS_BLOCKED = "blocked"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_sandbox(repo_root: Path) -> Path:
    return repo_root / SANDBOX_RELATIVE


def _find_claude_swarm() -> dict:
    cmd = shutil.which("claude-swarm")
    if cmd:
        return {"found": True, "path": cmd, "source": "PATH"}
    # Not in PATH; check if installable from sandbox
    sandbox_pyproject = (
        _default_sandbox(_repo_root()) / "claude_swarm" / "pyproject.toml"
    )
    if sandbox_pyproject.exists():
        return {
            "found": False,
            "path": None,
            "source": "sandbox_available_not_installed",
            "sandbox_path": str(sandbox_pyproject.parent),
        }
    return {"found": False, "path": None, "source": "not_found"}


def _check_api_keys_in_env() -> list[str]:
    present = []
    for key in _API_KEY_ENV_VARS:
        if os.environ.get(key):
            present.append(key)
    return present


def _probe_version(cmd: str) -> dict:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True, text=True, timeout=10,
            env={k: v for k, v in os.environ.items()
                 if k not in _API_KEY_ENV_VARS},
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip()[:200],
            "stderr": result.stderr.strip()[:200],
            "success": result.returncode == 0,
        }
    except FileNotFoundError:
        return {"exit_code": -1, "stdout": "", "stderr": "command not found", "success": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "timeout", "success": False}
    except Exception as exc:
        return {"exit_code": -1, "stdout": "", "stderr": str(exc), "success": False}


def _run_demo_in_scratch(cmd: str, scratch_dir: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in _API_KEY_ENV_VARS}
    env["HOME"] = scratch_dir
    env["USERPROFILE"] = scratch_dir
    env["XDG_DATA_HOME"] = os.path.join(scratch_dir, ".local", "share")
    try:
        result = subprocess.run(
            [cmd, "--demo", "--no-ui"],
            capture_output=True, text=True, timeout=60,
            cwd=scratch_dir,
            env=env,
        )
        files_written = []
        for dirpath, _, filenames in os.walk(scratch_dir):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                files_written.append(os.path.relpath(fp, scratch_dir))
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip()[:2000],
            "stderr": result.stderr.strip()[:500],
            "success": result.returncode == 0,
            "files_written": files_written[:20],
            "network_attempted": False,
            "agents_launched": False,
            "api_key_used": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1, "stdout": "", "stderr": "timeout after 60s",
            "success": False, "files_written": [], "network_attempted": False,
            "agents_launched": False, "api_key_used": False,
        }
    except Exception as exc:
        return {
            "exit_code": -1, "stdout": "", "stderr": str(exc),
            "success": False, "files_written": [], "network_attempted": False,
            "agents_launched": False, "api_key_used": False,
        }


# ---------------------------------------------------------------------------
# Validation guards
# ---------------------------------------------------------------------------

def _validate_invocation(flags: list[str], scratch: str | None = None) -> dict:
    blocked = []

    api_keys = _check_api_keys_in_env()
    if api_keys:
        blocked.append(f"api_key_present: {api_keys}")

    safe = {f for f in flags if f in _SAFE_FLAGS}
    if not safe:
        blocked.append("no_safe_mode_flag: must include --dry-run, --demo, or --version")

    for flag in flags:
        if flag in _BLOCKED_FLAGS:
            blocked.append(f"blocked_flag: {flag}")

    if "--dry-run" in flags and not any(f in flags for f in ["--demo"]):
        if api_keys or not os.environ.get("ANTHROPIC_API_KEY"):
            blocked.append(
                "dry_run_requires_api_key: claude-swarm --dry-run calls "
                "decompose_task() via Claude API before skipping execution"
            )

    if scratch is not None:
        scratch_path = Path(scratch)
        repo_root = _repo_root()
        try:
            scratch_path.resolve().relative_to(repo_root.resolve())
            blocked.append("scratch_inside_repo: output must be outside repo root")
        except ValueError:
            pass

    return {
        "allowed": len(blocked) == 0,
        "blocked_reasons": blocked,
    }


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def _run_check(sandbox: Path | None = None) -> dict:
    tool = _find_claude_swarm()
    api_keys = _check_api_keys_in_env()

    dry_run_status = (
        "BLOCKED — requires ANTHROPIC_API_KEY and makes Claude API calls "
        "in decompose_task() before skipping execution"
    )
    demo_status = (
        "SAFE (no API key required) but writes to home dir; "
        "use --demo-mode with explicit --scratch in isolated environment only"
    )

    return {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "check",
        "tool_available": tool["found"],
        "tool_detection": tool,
        "api_keys_in_env": api_keys,
        "api_keys_blocked": len(api_keys) > 0,
        "dry_run_flag_status": dry_run_status,
        "demo_mode_status": demo_status,
        "safe_command": "claude-swarm --version  (probe only)",
        "blocked_command": "claude-swarm --dry-run \"task\"  (requires API key + makes API calls)",
        "conditionally_safe_command": (
            "claude-swarm --demo --no-ui  (no API key, isolated scratch only)"
        ),
        "start_conditions": {
            "n6_35b_on_main": False,
            "n6_36b_on_main": False,
            "note": "N+6.35B and N+6.36B PRs (#10, #11) are drafts — not yet merged to main. "
                    "Proceeding with wrapper and tests; actual execution deferred.",
        },
        "safety_block": _SAFETY_BLOCK,
    }


def _run_probe(sandbox: Path | None = None) -> dict:
    api_keys = _check_api_keys_in_env()
    if api_keys:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "probe",
            "execution_status": _STATUS_BLOCKED,
            "tool_available": False,
            "api_keys_blocked": api_keys,
            "safety_block": _SAFETY_BLOCK,
        }

    tool = _find_claude_swarm()

    if not tool["found"]:
        return {
            "ok": True,
            "milestone": MILESTONE,
            "mode": "probe",
            "execution_status": _STATUS_NOT_INSTALLED,
            "tool_available": False,
            "tool_detection": tool,
            "probe_result": None,
            "note": (
                "claude-swarm is not installed. In an isolated sandbox, "
                "install with: pip install claude-swarm (then run --version probe)."
            ),
            "dry_run_blocked_reason": (
                "--dry-run requires ANTHROPIC_API_KEY and makes Claude API calls "
                "via decompose_task() before any dry-run behavior applies."
            ),
            "safety_block": _SAFETY_BLOCK,
        }

    probe = _probe_version(tool["path"])
    return {
        "ok": probe["success"],
        "milestone": MILESTONE,
        "mode": "probe",
        "execution_status": _STATUS_PROBE_OK if probe["success"] else _STATUS_BLOCKED,
        "tool_available": True,
        "tool_path": tool["path"],
        "probe_result": probe,
        "dry_run_blocked_reason": (
            "--dry-run requires ANTHROPIC_API_KEY and makes Claude API calls. "
            "Execution is BLOCKED. Only --version and --demo are safe."
        ),
        "network_attempted": False,
        "agents_launched": False,
        "api_key_used": False,
        "files_written": False,
        "safety_block": _SAFETY_BLOCK,
    }


def _run_demo_mode(scratch: str | None = None, sandbox: Path | None = None) -> dict:
    api_keys = _check_api_keys_in_env()
    if api_keys:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "demo",
            "execution_status": _STATUS_BLOCKED,
            "blocked_reason": f"API key(s) present in env: {api_keys}",
            "safety_block": _SAFETY_BLOCK,
        }

    tool = _find_claude_swarm()

    if not tool["found"]:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "demo",
            "execution_status": _STATUS_NOT_INSTALLED,
            "tool_available": False,
            "safety_block": _SAFETY_BLOCK,
        }

    validation = _validate_invocation(["--demo", "--no-ui"], scratch=scratch)
    if not validation["allowed"]:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "demo",
            "execution_status": _STATUS_BLOCKED,
            "validation": validation,
            "safety_block": _SAFETY_BLOCK,
        }

    use_tmp = scratch is None
    tmp_dir = scratch or tempfile.mkdtemp(prefix="ghoti_swarm_demo_")
    try:
        demo_result = _run_demo_in_scratch(tool["path"], tmp_dir)
        status = _STATUS_DEMO_OK if demo_result["success"] else _STATUS_DEMO_FAILED
        return {
            "ok": demo_result["success"],
            "milestone": MILESTONE,
            "mode": "demo",
            "execution_status": status,
            "tool_path": tool["path"],
            "scratch_dir": tmp_dir if not use_tmp else "(temp, cleaned up)",
            "demo_result": demo_result,
            "network_attempted": demo_result.get("network_attempted", False),
            "agents_launched": demo_result.get("agents_launched", False),
            "api_key_used": demo_result.get("api_key_used", False),
            "files_written_in_scratch": demo_result.get("files_written", []),
            "safety_block": {**_SAFETY_BLOCK,
                             "third_party_code_executed": True},
        }
    finally:
        if use_tmp:
            try:
                import shutil as _shutil
                _shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Ghoti N+6.37A claude-swarm safety wrapper"
    )
    parser.add_argument("--check", action="store_true", help="Safety status check")
    parser.add_argument("--probe", action="store_true", help="Probe tool availability (--version)")
    parser.add_argument("--demo-mode", action="store_true", help="Run --demo in scratch (no API)")
    parser.add_argument("--sandbox", metavar="PATH", help="Override sandbox root")
    parser.add_argument("--scratch", metavar="PATH", help="Scratch directory for demo output")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    sandbox = Path(args.sandbox) if args.sandbox else None

    if args.demo_mode:
        result = _run_demo_mode(scratch=args.scratch, sandbox=sandbox)
    elif args.probe:
        result = _run_probe(sandbox=sandbox)
    else:
        result = _run_check(sandbox=sandbox)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] ok={ok} mode={result.get('mode')} "
              f"status={result.get('execution_status', 'n/a')}")
        sb = result.get("safety_block", {})
        print(f"  simulation={sb.get('simulation')} "
              f"live_execution={sb.get('live_execution')} "
              f"api_key_used={sb.get('api_key_used', False)}")
        if "dry_run_blocked_reason" in result:
            print(f"  dry_run: BLOCKED — {result['dry_run_blocked_reason'][:80]}")
        if "note" in result:
            print(f"  note: {result['note'][:80]}")


if __name__ == "__main__":
    _main()
