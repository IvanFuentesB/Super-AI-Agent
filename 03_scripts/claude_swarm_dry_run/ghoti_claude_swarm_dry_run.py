"""
ghoti_claude_swarm_dry_run.py  --  N+6.37A Ghoti STATIC-ONLY wrapper for claude-swarm.

HARDENED (N+6.37A fix): This wrapper is now fully static-only. It never executes
the third-party claude-swarm CLI, never spawns a process, never imports the
`subprocess` module, and never opens a shell. Every mode (--check, --probe,
--demo-mode) only inspects static metadata/known file paths and produces a safe
plan/report.

Key findings from source-code inspection (claude_swarm/cli.py), text-read only:
  - --dry-run REQUIRES ANTHROPIC_API_KEY and calls the Claude API (decompose_task)
    before skipping execution. This is NOT a true no-op.
    Status: BLOCKED  --  violates "no API keys, no provider calls" hard rules.
  - --demo runs a simulated TUI with NO API key required, but it still spawns the
    real third-party CLI process. Executing it here would violate the static-only
    audit gate, so demo output is SIMULATED STATICALLY in this wrapper instead.
  - --version/--help do not call a provider, but invoking them still spawns the
    external CLI, which this wrapper refuses. Tool presence is reported via a
    non-executing PATH lookup only.

This wrapper:
  1. Detects whether claude-swarm is present (PATH lookup + sandbox metadata)  --
     NO execution.
  2. Refuses to run if any provider API key is set in env.
  3. Refuses live mode (missing a safe flag), blocked flags, in-repo scratch, and
     the --dry-run flag (documented as provider-gated).
  4. PROBE mode: static metadata inspection only; reports external CLI is blocked.
  5. DEMO mode: emits a STATIC simulated plan from hardcoded safe metadata.
  6. CHECK mode: scans this wrapper's own source AND the PowerShell checker for
     execution primitives and proves none are present.
  7. Emits Agent-Arena-shaped status with explicit:
       external_cli_executed=false, subprocess_used=false, provider_called=false,
       api_key_used=false, agents_launched=false, live_execution=false,
       simulation=true.

The honest truth (preserved):
  claude-swarm --dry-run remains BLOCKED because source inspection showed a
  provider key check + model decomposition (decompose_task) BEFORE the dry-run
  skip. The safe next path is provider-free fixture replay (N+6.38A) and, only
  after audit, an isolated --demo --no-ui run in a separate profile.

CLI flags:
  --probe               Static probe (metadata/PATH inspection only, no execution)
  --demo-mode           Emit a static simulated demo plan (no execution)
  --check               Safety status + source scan (no execution)
  --sandbox <path>      Sandbox root for detection
  --scratch <path>      Advisory scratch path (validated, never written)
  --json                Machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

MILESTONE = "N+6.37A"
SANDBOX_RELATIVE = "21_repos/third_party_runtime_sandbox"

# API key environment variables  --  if any are set, refuse execution
_API_KEY_ENV_VARS = [
    "ANTHROPIC_API_KEY",
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
]

# Flags that are safe (mode selectors only  --  never executed by this wrapper)
_SAFE_FLAGS = {"--dry-run", "--demo", "--version", "--help", "-v", "--no-ui"}

# Blocked flags that must never be passed
_BLOCKED_FLAGS = {
    "--mcp", "--hooks", "--browser",
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
    "external_cli_executed": False,
    "subprocess_used": False,
    "provider_called": False,
    "agents_launched": False,
    "secrets_committed": False,
}

# Execution status constants
_STATUS_NOT_INSTALLED = "not_installed"
_STATUS_API_KEY_REQUIRED = "api_key_required_blocked"
_STATUS_PROBE_OK = "probe_ok"
_STATUS_DEMO_OK = "demo_ok"
_STATUS_DEMO_FAILED = "demo_failed"
_STATUS_BLOCKED = "blocked"

# Static simulated demo plan  --  hardcoded, provider-free, no execution.
_STATIC_DEMO_PLAN: dict[str, Any] = {
    "swarm": "ghoti-static-demo",
    "source": "static_simulation",
    "dry_run": True,
    "simulation": True,
    "live_execution": False,
    "tasks": [
        {
            "id": "demo-1",
            "agent_type": "coder",
            "description": "Sample: scaffold a module (simulated, not executed)",
            "dependencies": [],
        },
        {
            "id": "demo-2",
            "agent_type": "tester",
            "description": "Sample: write unit tests (simulated, not executed)",
            "dependencies": ["demo-1"],
        },
        {
            "id": "demo-3",
            "agent_type": "reviewer",
            "description": "Sample: review output (simulated, not executed)",
            "dependencies": ["demo-1", "demo-2"],
        },
    ],
}

# Execution-primitive needles, assembled from fragments so the contiguous
# literal NEVER appears in this file (this lets the scan inspect this very file
# without flagging its own pattern list).
_PY_EXEC_NEEDLES = [
    "subprocess" + ".run",
    "subprocess" + ".Popen",
    "subprocess" + ".call",
    "subprocess" + ".check_output",
    "subprocess" + ".check_call",
    "Popen" + "(",
    "os" + ".system",
    "os" + ".popen",
    "os" + ".execv",
    "os" + ".execvp",
    "os" + ".spawn",
    "pty" + ".spawn",
]
_PY_IMPORT_NEEDLES = [
    "import " + "subprocess",
    "import " + "pty",
]
_PS_EXEC_NEEDLES = [
    "Invoke" + "-Expression",
    "Start" + "-Process",
    "iex " + "(",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_sandbox(repo_root: Path) -> Path:
    return repo_root / SANDBOX_RELATIVE


def _wrapper_source_path() -> Path:
    return Path(__file__).resolve()


def _ps1_checker_path() -> Path:
    return _wrapper_source_path().parent / "check_claude_swarm_dry_run.ps1"


def _static_only_fields() -> dict:
    """Explicit machine-readable proof fields stamped on every result."""
    return {
        "external_cli_executed": False,
        "subprocess_used": False,
        "provider_called": False,
        "api_key_used": False,
        "agents_launched": False,
        "live_execution": False,
        "simulation": True,
    }


def _find_claude_swarm() -> dict:
    """Detect claude-swarm via a NON-executing PATH lookup + sandbox metadata.

    shutil.which only scans PATH directories for a matching filename; it does
    not spawn or execute anything.
    """
    cmd = shutil.which("claude-swarm")
    if cmd:
        return {"found": True, "path": cmd, "source": "PATH"}
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


def _extract_toml_value(text: str, key: str) -> str | None:
    """Tiny text-only TOML scalar extractor (name/version). No execution."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
            if "=" in stripped:
                val = stripped.split("=", 1)[1].strip()
                return val.strip().strip('"').strip("'")
    return None


def _read_static_metadata() -> dict:
    """Read claude-swarm package metadata as TEXT only (no import, no execution)."""
    pyproject = _default_sandbox(_repo_root()) / "claude_swarm" / "pyproject.toml"
    if not pyproject.exists():
        return {"available": False, "source": "not_present"}
    try:
        text = pyproject.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - defensive
        return {"available": False, "source": "read_error", "error": str(exc)[:120]}
    return {
        "available": True,
        "source": "static_pyproject_text",
        "name": _extract_toml_value(text, "name"),
        "version": _extract_toml_value(text, "version"),
    }


def _scan_source_for_exec_patterns() -> dict:
    """Scan THIS wrapper and the PowerShell checker for execution primitives.

    Proves the wrapper contains no process-spawning calls (the subprocess
    module, Popen, or os-level system/exec helpers) and the checker contains no
    dynamic expression invocation or process-launch cmdlets. The needle list is
    assembled from fragments so the contiguous literals never appear here.
    """
    findings: dict[str, Any] = {"wrapper": [], "ps1": [], "clean": True}

    wp = _wrapper_source_path()
    if wp.exists():
        wtext = wp.read_text(encoding="utf-8", errors="replace")
        for needle in _PY_EXEC_NEEDLES + _PY_IMPORT_NEEDLES:
            if needle in wtext:
                findings["wrapper"].append(needle)

    ps = _ps1_checker_path()
    if ps.exists():
        ptext = ps.read_text(encoding="utf-8", errors="replace")
        for needle in _PS_EXEC_NEEDLES:
            if needle in ptext:
                findings["ps1"].append(needle)

    findings["clean"] = not findings["wrapper"] and not findings["ps1"]
    return findings


# ---------------------------------------------------------------------------
# Validation guards (pure logic  --  never execute anything)
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
# Public entry points (all static-only)
# ---------------------------------------------------------------------------

def _run_check(sandbox: Path | None = None) -> dict:
    tool = _find_claude_swarm()
    api_keys = _check_api_keys_in_env()
    source_scan = _scan_source_for_exec_patterns()

    dry_run_status = (
        "BLOCKED  --  requires ANTHROPIC_API_KEY and makes Claude API calls "
        "in decompose_task() before skipping execution"
    )
    demo_status = (
        "SIMULATED STATICALLY  --  this wrapper emits a hardcoded demo plan and "
        "never spawns the external claude-swarm CLI"
    )

    result = {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "check",
        "static_only": True,
        "tool_available": tool["found"],
        "tool_detection": tool,
        "static_metadata": _read_static_metadata(),
        "api_keys_in_env": api_keys,
        "api_keys_blocked": len(api_keys) > 0,
        "dry_run_flag_status": dry_run_status,
        "demo_mode_status": demo_status,
        "source_scan": source_scan,
        "source_scan_clean": source_scan["clean"],
        "safe_command": "(static metadata inspection only  --  no CLI execution)",
        "blocked_command": "claude-swarm --dry-run \"task\"  (requires API key + makes API calls)",
        "conditionally_safe_command": (
            "claude-swarm --demo --no-ui  (NOT executed here; isolated audited profile only)"
        ),
        "next_safe_path": (
            "Provider-free fixture replay (N+6.38A); isolated --demo --no-ui only "
            "after a separate audited milestone."
        ),
        "start_conditions": {
            "n6_35b_on_main": True,
            "n6_36b_on_main": True,
            "note": "N+6.35B and N+6.36B are merged to main. This N+6.37A fix "
                    "hardens the wrapper to static-only before N+6.37B re-audit.",
        },
        "safety_block": _SAFETY_BLOCK,
    }
    result.update(_static_only_fields())
    # source_scan_clean must hold for ok to be true
    result["ok"] = bool(source_scan["clean"])
    return result


def _run_probe(sandbox: Path | None = None) -> dict:
    api_keys = _check_api_keys_in_env()
    if api_keys:
        result = {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "probe",
            "static_only": True,
            "execution_status": _STATUS_BLOCKED,
            "tool_available": False,
            "api_keys_blocked": api_keys,
            "safety_block": _SAFETY_BLOCK,
        }
        result.update(_static_only_fields())
        return result

    tool = _find_claude_swarm()
    metadata = _read_static_metadata()

    status = _STATUS_PROBE_OK if tool["found"] else _STATUS_NOT_INSTALLED
    note = (
        "Static probe: tool presence determined via PATH lookup and sandbox "
        "metadata only. The external claude-swarm CLI is NOT executed."
    )
    if not tool["found"]:
        note = (
            "claude-swarm is not installed on PATH. Detection is static (PATH "
            "lookup + sandbox metadata). The external CLI is never executed."
        )

    result = {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "probe",
        "static_only": True,
        "execution_status": status,
        "tool_available": tool["found"],
        "tool_detection": tool,
        "static_metadata": metadata,
        "probe_result": None,
        "note": note,
        "dry_run_blocked_reason": (
            "--dry-run requires ANTHROPIC_API_KEY and makes Claude API calls "
            "via decompose_task() before any dry-run behavior applies. The "
            "external CLI is never executed by this wrapper."
        ),
        "files_written": False,
        "safety_block": _SAFETY_BLOCK,
    }
    result.update(_static_only_fields())
    return result


def _run_demo_mode(scratch: str | None = None, sandbox: Path | None = None) -> dict:
    api_keys = _check_api_keys_in_env()
    if api_keys:
        result = {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "demo",
            "static_only": True,
            "execution_status": _STATUS_BLOCKED,
            "blocked_reason": f"API key(s) present in env: {api_keys}",
            "safety_block": _SAFETY_BLOCK,
        }
        result.update(_static_only_fields())
        return result

    # Advisory validation: keep refusing in-repo scratch even though nothing
    # is written (defense in depth). Demo output is entirely static.
    validation = _validate_invocation(["--demo", "--no-ui"], scratch=scratch)
    if not validation["allowed"]:
        result = {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "demo",
            "static_only": True,
            "execution_status": _STATUS_BLOCKED,
            "validation": validation,
            "safety_block": _SAFETY_BLOCK,
        }
        result.update(_static_only_fields())
        return result

    tool = _find_claude_swarm()

    result = {
        "ok": True,
        "milestone": MILESTONE,
        "mode": "demo",
        "static_only": True,
        "execution_status": _STATUS_DEMO_OK,
        "tool_available": tool["found"],
        "tool_detection": tool,
        "demo_plan": _STATIC_DEMO_PLAN,
        "demo_source": "static_simulation",
        "note": (
            "Demo plan is a hardcoded static simulation. The external "
            "claude-swarm CLI is NOT spawned or executed."
        ),
        "files_written_in_scratch": [],
        "safety_block": _SAFETY_BLOCK,
    }
    result.update(_static_only_fields())
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Ghoti N+6.37A claude-swarm STATIC-ONLY wrapper"
    )
    parser.add_argument("--check", action="store_true", help="Safety status + source scan")
    parser.add_argument("--probe", action="store_true", help="Static probe (no execution)")
    parser.add_argument("--demo-mode", action="store_true", help="Static simulated demo plan")
    parser.add_argument("--sandbox", metavar="PATH", help="Override sandbox root")
    parser.add_argument("--scratch", metavar="PATH", help="Advisory scratch path (never written)")
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
              f"external_cli_executed={result.get('external_cli_executed')} "
              f"subprocess_used={result.get('subprocess_used')}")
        if "source_scan_clean" in result:
            print(f"  source_scan_clean={result['source_scan_clean']}")
        if "dry_run_blocked_reason" in result:
            print(f"  dry_run: BLOCKED  --  {result['dry_run_blocked_reason'][:70]}")
        if "note" in result:
            print(f"  note: {result['note'][:80]}")


if __name__ == "__main__":
    _main()
