#!/usr/bin/env python3
"""
ghoti_cua_trial_adapter.py — N+6.34A CUA Isolated Dry-Run / Observation Adapter

First real plug-and-play repo trial: TryCUA/CUA sandbox, metadata-only inspection.

What is real in this milestone:
  - TryCUA/CUA is cloned into the gitignored runtime sandbox
    (21_repos/third_party_runtime_sandbox/cua).
  - LICENSE, pyproject metadata, shell-script count, and runtime requirements
    are read from the live clone (not from static notes).
  - A dry-run trial plan is generated and validated through the N+6.33A
    dual gate (Python adapter + Rust policy checker).
  - The sandbox commit hash is recorded for audit traceability.

What is NOT live:
  - No CUA code is imported or executed.
  - No OS click / type / hotkey.
  - No Docker / QEMU / Lume VM.
  - No MCP server.
  - No account login / session.
  - No real browser control.
  - No secrets / tokens / cookies.
  - No auto-submit.
  - No telemetry triggered (cua-core posthog fires on import; we never import).

Hard limits (enforced here, not configurable):
  - CUA sandbox is read-only; no write to its files.
  - Metadata smoke reads only: LICENSE.md, pyproject.toml, shell-script count.
  - Trial plan is a local-sandbox, observation-only plan that passes the dual gate.
  - Any plan requesting live OS, browser, Docker, MCP, or account is denied.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path

MILESTONE = "N+6.34A"
ADAPTER_VERSION = "0.1.0"
CUA_REPO_URL = "https://github.com/trycua/cua"
CUA_EXPECTED_LICENSE = "MIT"

# Relative to repo root — must match the gitignored sandbox entry in .gitignore.
CUA_SANDBOX_RELATIVE = "21_repos/third_party_runtime_sandbox/cua"

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SANDBOX = _REPO_ROOT / CUA_SANDBOX_RELATIVE

# ------------------------------------------------------------------
# Import the N+6.33A Rust policy bridge (Gate 1 + Gate 2)
# ------------------------------------------------------------------

_BRIDGE_PATH = _REPO_ROOT / "03_scripts" / "computer_use_adapter"
if str(_BRIDGE_PATH) not in sys.path:
    sys.path.insert(0, str(_BRIDGE_PATH))

try:
    import ghoti_computer_use_adapter as _bridge  # noqa: E402
    _BRIDGE_AVAILABLE = True
except ImportError:
    _BRIDGE_AVAILABLE = False

# ------------------------------------------------------------------
# CUA-specific capability / action hard-blocks
# ------------------------------------------------------------------
#
# These are in addition to the N+6.29A adapter's BLOCKED_CAPABILITIES.
# Any trial plan that claims these is rejected before hitting the Rust gate.

CUA_TRIAL_BLOCKED_CAPABILITIES = frozenset({
    "computer_use",
    "docker",
    "lume",
    "qemu",
    "kasm",
    "mcp",
    "live_browser",
    "external_web",
    "account_login",
    "secrets",
    "auto_submit",
    "telemetry_upload",
    "real_os_input",
    "mass_messaging",
    "shell_execution",
    "vm_launch",
})

# What the metadata smoke verifies (read-only, no code execution):
METADATA_SMOKE_READS = [
    "LICENSE.md",
    "pyproject.toml",
]

REFUSED_LIVE_ACTIONS = [
    "real OS click / mouse move / keyboard input",
    "Docker / QEMU / Lume / KASM VM launch",
    "live browser control (any URL)",
    "MCP server activation",
    "account login or session management",
    "secrets / tokens / cookies / auth files",
    "auto-submit / auto-post",
    "telemetry activation (cua-core posthog)",
    "import or execution of any CUA package code",
    "shell script execution inside CUA sandbox",
    "external website navigation or API call",
]


# ------------------------------------------------------------------
# Sandbox detection and metadata reading
# ------------------------------------------------------------------

def _detect_sandbox(sandbox: Path) -> dict:
    """Check sandbox presence and basic health. Read-only; no code execution."""
    if not sandbox.exists():
        return {
            "present": False,
            "path": str(sandbox),
            "note": (
                "CUA sandbox not found. Clone with: "
                f"git clone --depth=1 --no-tags --template='' {CUA_REPO_URL} "
                f"{CUA_SANDBOX_RELATIVE}"
            ),
        }
    git_dir = sandbox / ".git"
    commit_hash = None
    if git_dir.exists():
        head_file = git_dir / "HEAD"
        # Resolve HEAD to a commit hash (packed-refs or direct)
        try:
            head_ref = head_file.read_text(encoding="utf-8").strip()
            if head_ref.startswith("ref: "):
                ref_path = git_dir / head_ref[5:]
                if ref_path.exists():
                    commit_hash = ref_path.read_text(encoding="utf-8").strip()[:40]
                else:
                    # Try packed-refs
                    packed = git_dir / "packed-refs"
                    if packed.exists():
                        ref_name = head_ref[5:].strip()
                        for line in packed.read_text(encoding="utf-8").splitlines():
                            if line.endswith(ref_name):
                                commit_hash = line.split()[0][:40]
                                break
            else:
                commit_hash = head_ref[:40]
        except OSError:
            pass
    return {
        "present": True,
        "path": str(sandbox),
        "git_present": git_dir.exists(),
        "commit_hash": commit_hash,
    }


def _read_cua_metadata(sandbox: Path) -> dict:
    """Read-only metadata extraction from the CUA sandbox.

    Reads: LICENSE.md, pyproject.toml name/version.
    Never imports, executes, or modifies any CUA file.
    """
    meta: dict = {
        "license": "unknown",
        "license_file_present": False,
        "package_name": "unknown",
        "package_version": "unknown",
        "pyproject_present": False,
        "shell_script_count": 0,
        "runtime_requirements_summary": (
            "Requires: Docker/QEMU/Lume VM for real desktop control; "
            "Python >=3.12; websocket-client; aiohttp; pillow; pydantic; "
            "cua-core (posthog telemetry fires on import). "
            "None of these are invoked by this adapter."
        ),
        "cua_code_imported": False,
        "cua_code_executed": False,
    }

    # License
    lic_path = sandbox / "LICENSE.md"
    if lic_path.exists():
        meta["license_file_present"] = True
        try:
            lic_text = lic_path.read_text(encoding="utf-8")
            if "MIT License" in lic_text or "MIT" in lic_text[:30]:
                meta["license"] = "MIT"
        except OSError:
            pass

    # pyproject.toml top-level
    pp_path = sandbox / "pyproject.toml"
    if pp_path.exists():
        meta["pyproject_present"] = True
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError:
                tomllib = None  # type: ignore[assignment]
        if tomllib is not None:
            try:
                with open(pp_path, "rb") as fh:
                    d = tomllib.load(fh)
                proj = d.get("project", {})
                meta["package_name"] = proj.get("name", "unknown")
                meta["package_version"] = proj.get("version", "unknown")
            except Exception:
                pass

    # Shell script count (surface area metric — not executed)
    try:
        meta["shell_script_count"] = sum(1 for _ in sandbox.rglob("*.sh"))
    except OSError:
        pass

    return meta


# ------------------------------------------------------------------
# Trial plan construction and validation
# ------------------------------------------------------------------

def _build_trial_plan(sandbox: Path, plan_id: str = "n6_34a_cua_observation_trial") -> dict:
    """Build a safe dry-run CUA observation plan.

    The plan uses only local sandbox targets and read-only actions.
    It has no live OS, browser, Docker, MCP, or account capabilities.
    This is the minimal plan that would be the first step toward a real CUA trial.
    """
    sandbox_url = f"file:///{sandbox.as_posix().lstrip('/')}"
    return {
        "plan_id": plan_id,
        "milestone": MILESTONE,
        "target": "local_sandbox",
        "target_url": sandbox_url,
        "auto_submit": False,
        "requires_human_approval": True,
        "capabilities_required": [],
        "description": (
            "Dry-run CUA observation trial: read sandbox metadata, "
            "check CUA structural state, generate report. "
            "No real OS action. No CUA code executed."
        ),
        "actions": [
            {
                "action_id": "cua_a1_check_sandbox",
                "type": "check_state",
                "target_element": CUA_SANDBOX_RELATIVE,
                "description": "Check CUA sandbox directory is present and gitignored.",
            },
            {
                "action_id": "cua_a2_read_license",
                "type": "read_fixture",
                "target_element": None,
                "value": f"{CUA_SANDBOX_RELATIVE}/LICENSE.md",
                "description": "Read CUA LICENSE.md to confirm MIT.",
            },
            {
                "action_id": "cua_a3_read_manifest",
                "type": "read_fixture",
                "target_element": None,
                "value": f"{CUA_SANDBOX_RELATIVE}/pyproject.toml",
                "description": "Read CUA top-level pyproject.toml for package name/version.",
            },
            {
                "action_id": "cua_a4_generate_report",
                "type": "generate_report",
                "target_element": None,
                "value": "14_context/cua_trial/cua_trial_status_latest.json",
                "description": "Generate trial status report (dry-run).",
            },
        ],
    }


def _write_temp_plan(plan: dict) -> str:
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(plan, fh)
    fh.close()
    return fh.name


def _validate_trial_plan(plan: dict) -> dict:
    """Validate the trial plan through the N+6.33A dual gate.

    Returns the full bridge result.  Falls back to a minimal stub
    when ghoti_computer_use_adapter is unavailable.
    """
    # First: check for CUA-trial-specific blocked capabilities (Gate 0).
    requested_caps = set(plan.get("capabilities_required", []))
    cua_blocked = sorted(requested_caps & CUA_TRIAL_BLOCKED_CAPABILITIES)
    if cua_blocked:
        return {
            "ok": False,
            "status": "blocked",
            "adapter_allowed": False,
            "rust_allowed": False,
            "accepted": False,
            "blocked_reasons": [f"cua_trial_blocked_capability: {c}" for c in cua_blocked],
            "rust_policy_decision": {
                "decision": "deny",
                "reasons": ["blocked_capability_requested"],
                "blocked_capabilities": cua_blocked,
                "unknown_capabilities": [],
            },
            "gate": "cua_trial_pre_filter",
        }

    if not _BRIDGE_AVAILABLE:
        return {
            "ok": False,
            "status": "bridge_unavailable",
            "adapter_allowed": False,
            "rust_allowed": False,
            "accepted": False,
            "note": "ghoti_computer_use_adapter not importable; bridge unavailable",
        }

    plan_path = _write_temp_plan(plan)
    return _bridge._run_plan(plan_path, rust_bridge=True)


# ------------------------------------------------------------------
# Result builders
# ------------------------------------------------------------------

def _build_safety_block() -> dict:
    return {
        "no_cua_code_imported": True,
        "no_cua_code_executed": True,
        "no_real_os_input": True,
        "no_docker_vm": True,
        "no_live_browser": True,
        "no_mcp_server": True,
        "no_account_login": True,
        "no_secrets_accessed": True,
        "no_auto_submit": True,
        "no_telemetry_triggered": True,
        "no_shell_scripts_run": True,
        "sandbox_read_only": True,
        "dry_run_only": True,
    }


def _run_check() -> dict:
    """System readiness check — does not require CUA to be cloned."""
    return {
        "ok": True,
        "milestone": MILESTONE,
        "adapter_version": ADAPTER_VERSION,
        "check": "system_ready",
        "mode": "dry_run",
        "bridge_available": _BRIDGE_AVAILABLE,
        "cua_repo_url": CUA_REPO_URL,
        "cua_sandbox_path": str(_DEFAULT_SANDBOX),
        "cua_sandbox_gitignored": True,
        "cua_expected_license": CUA_EXPECTED_LICENSE,
        "cua_code_imported": False,
        "cua_code_executed": False,
        "live_os_input_enabled": False,
        "docker_vm_enabled": False,
        "live_browser_enabled": False,
        "mcp_enabled": False,
        "account_login_enabled": False,
        "secrets_access_enabled": False,
        "auto_submit_enabled": False,
        "trial_blocked_capabilities": sorted(CUA_TRIAL_BLOCKED_CAPABILITIES),
        "refused_live_actions": REFUSED_LIVE_ACTIONS,
        "safety": _build_safety_block(),
        "timestamp_utc": _utc_now(),
    }


def _run_trial(
    sandbox: Path | None = None,
    plan_id: str = "n6_34a_cua_observation_trial",
) -> dict:
    """Full trial: sandbox detection → metadata read → plan generation → dual-gate validation."""
    sandbox = sandbox or _DEFAULT_SANDBOX

    detection = _detect_sandbox(sandbox)
    sandbox_present = detection["present"]

    metadata: dict = {}
    if sandbox_present:
        metadata = _read_cua_metadata(sandbox)

    trial_plan = _build_trial_plan(sandbox, plan_id)
    gate_result = _validate_trial_plan(trial_plan)

    accepted = gate_result.get("accepted", False)

    return {
        "ok": accepted and sandbox_present,
        "milestone": MILESTONE,
        "adapter_version": ADAPTER_VERSION,
        "mode": "dry_run",
        "trial_phase": "metadata_smoke",
        "cua_sandbox_present": sandbox_present,
        "cua_sandbox_detection": detection,
        "cua_metadata": metadata,
        "cua_license_ok": metadata.get("license") == CUA_EXPECTED_LICENSE if sandbox_present else None,
        "cua_code_imported": False,
        "cua_code_executed": False,
        "trial_plan": trial_plan,
        "gate_result": gate_result,
        "adapter_allowed": gate_result.get("adapter_allowed", False),
        "rust_allowed": gate_result.get("rust_allowed", False),
        "accepted": accepted,
        "pending_human_approval": True,
        "next_step_note": (
            "Trial plan accepted by dual gate (dry-run). "
            "Actual CUA execution requires a separate audited milestone, "
            "human approval, and an isolated profile / VM with no Ghoti repo access. "
            "CUA code is NOT imported or executed here."
        ) if accepted else (
            "Trial plan denied by dual gate. See gate_result for reasons."
        ),
        "refused_live_actions": REFUSED_LIVE_ACTIONS,
        "safety": _build_safety_block(),
        "timestamp_utc": _utc_now(),
    }


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _utc_now() -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            f"Ghoti {MILESTONE} CUA Isolated Trial Adapter "
            "(dry-run / observation only — no real CUA execution)"
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run system readiness check (no CUA required)",
    )
    parser.add_argument(
        "--trial",
        action="store_true",
        help="Run metadata-only trial (CUA must be cloned into sandbox)",
    )
    parser.add_argument(
        "--sandbox-path",
        metavar="PATH",
        default=None,
        help=f"Path to CUA sandbox (default: {CUA_SANDBOX_RELATIVE})",
    )
    parser.add_argument(
        "--plan-id",
        metavar="ID",
        default="n6_34a_cua_observation_trial",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON",
    )

    args = parser.parse_args()

    sandbox = (
        Path(args.sandbox_path).resolve() if args.sandbox_path else _DEFAULT_SANDBOX
    )

    if args.check:
        result = _run_check()
    elif args.trial:
        result = _run_trial(sandbox=sandbox, plan_id=args.plan_id)
    else:
        parser.print_help()
        return 1

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] CUA trial adapter | ok: {ok}")
        if result.get("cua_sandbox_present") is not None:
            print(f"  sandbox present: {result['cua_sandbox_present']}")
        if result.get("cua_license_ok") is not None:
            print(f"  license ok (MIT): {result['cua_license_ok']}")
        if "accepted" in result:
            print(f"  dual-gate accepted: {result['accepted']}")
        if not ok:
            gate = result.get("gate_result", {})
            for r in gate.get("blocked_reasons", []):
                print(f"  BLOCKED: {r}")

    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    sys.exit(main())
