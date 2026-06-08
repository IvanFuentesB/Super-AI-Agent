#!/usr/bin/env python3
"""
ghoti_computer_use_adapter.py - N+6.29A Computer-Use Repo-Backed Adapter Dry-Run

Dry-run adapter contract for proposed computer-use action plans.
Reads a plan, validates target/actions, rejects unsafe patterns,
outputs a dry-run status payload for Agent Arena. No real OS control.

Repo-backed design (all statically inspected in N+6.12A; no code copied):
  - TryCUA/CUA Driver (MIT)          : action-intent + sandbox isolation patterns
  - UI-TARS (Apache-2.0)             : observation-only mode, structured action contract
  - Browser Harness (MIT)            : local fixture + CDP isolation patterns
  - Vercel agent-browser (Apache-2.0): capability declaration + approval gate patterns
  - Ruflo (MIT)                      : coordinator/worker + declared-skill pattern

Attribution: 14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json

Hard limits (enforced, not configurable):
  - No real OS click / keyboard input
  - No live browser control
  - No external website navigation
  - No account login / session
  - No secrets / tokens / cookies / auth files
  - No auto-submit
  - No Docker
  - No MCP setup
  - No shell command execution
  - No remote API calls
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

MILESTONE = "N+6.29A"
ADAPTER_VERSION = "0.1.0"

# N+6.33A — Rust policy bridge. The bridge is OPT-IN (default off) so the
# baseline N+6.29A dry-run contract is unchanged. When engaged, every dry-run
# plan must clear a SECOND, independent gate: the ghoti_policy_checker decision
# (mirrored deterministically in Python, optionally cross-checked via cargo).
RUST_BRIDGE_MILESTONE = "N+6.33A"
RUST_POLICY_MANIFEST = "rust/ghoti_policy_checker/Cargo.toml"
REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_RUST_POLICY_MANIFEST = (REPO_ROOT / RUST_POLICY_MANIFEST).resolve()

# ------------------------------------------------------------------
# Policy constants
# ------------------------------------------------------------------

ALLOWED_TARGETS = frozenset({"local_sandbox", "approved_window"})

ALLOWED_ACTION_TYPES = frozenset({
    "read_fixture",
    "check_state",
    "dry_run_inspect",
    "dry_run_click",
    "dry_run_type",
    "generate_report",
    "inspect_window",
})

BLOCKED_ACTION_TYPES = frozenset({
    "real_click",
    "real_type",
    "real_key_press",
    "real_mouse_move",
    "real_screenshot_upload",
    "login",
    "submit_form",
    "auto_submit",
    "purchase",
    "transfer_money",
    "open_browser",
    "launch_docker",
    "mcp_setup",
    "install_package",
    "run_shell_command",
    "write_env_file",
    "access_keychain",
    "copy_token",
    "read_secret_file",
    "navigate_url",
    "execute_script",
})

SECRET_FIELD_NAMES = frozenset({
    "password", "secret", "token", "api_key", "cookie", "auth",
    "credential", "private_key", "access_key", "bearer", "passwd",
    "login_code", "otp", "pin", "session_id", "refresh_token",
})

SECRET_VALUE_PATTERN = re.compile(
    r"(password|secret|token|api_key|cookie|auth|credential|bearer|passwd"
    r"|private_key|access_key|login_code|otp|session_id|refresh_token)",
    re.IGNORECASE,
)

BLOCKED_CAPABILITIES = frozenset({
    "live_browser",
    "real_os_input",
    "account_login",
    "external_web",
    "docker",
    "mcp",
    "shell",
    "secrets",
    "auto_submit",
    "purchase",
    "money_transfer",
    "mass_messaging",
    "file_system_write_outside_sandbox",
})

ALLOWED_LOCAL_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1"})

REFUSED_LIVE_ACTIONS = [
    "real OS click or mouse move",
    "real OS keyboard input",
    "live web browser launch or control",
    "account login or session management",
    "external website navigation",
    "secrets / tokens / cookies / auth files",
    "auto-submit / auto-post / auto-paste",
    "purchase / payment / money transfer",
    "Docker container launch",
    "MCP server setup or activation",
    "package installation",
    "shell command execution",
    "keychain or credential store access",
    "remote API call",
    "screenshot upload to external service",
    "mass messaging",
    "file system writes outside sandbox",
]


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------

def _check_target(plan: dict) -> list[str]:
    reasons: list[str] = []
    target = plan.get("target", "")
    if target not in ALLOWED_TARGETS:
        reasons.append(
            f"target '{target}' not in allowed set {sorted(ALLOWED_TARGETS)}"
        )
    return reasons


def _check_url(plan: dict) -> list[str]:
    reasons: list[str] = []
    url = plan.get("target_url", "")
    if not url:
        return reasons

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        # Only hostless local file URLs are allowed: file:///path/to/fixture
        # file://hostname/path has a non-empty authority and must be blocked.
        netloc = parsed.netloc
        if netloc:
            reasons.append(
                f"target_url '{url}' uses file:// with a non-empty authority '{netloc}'; "
                f"only hostless local file URLs are allowed (e.g. file:///path/to/fixture)"
            )
        return reasons

    if scheme in ("http", "https"):
        hostname = (parsed.hostname or "").lower()
        if hostname not in ALLOWED_LOCAL_HOSTNAMES:
            reasons.append(
                f"target_url '{url}' hostname '{hostname}' is not a local hostname "
                f"(allowed: {sorted(ALLOWED_LOCAL_HOSTNAMES)})"
            )
        return reasons

    reasons.append(
        f"target_url '{url}' scheme '{scheme}' is not allowed "
        f"(allowed schemes: file, http/https with local hostname only)"
    )
    return reasons


def _check_auto_submit(plan: dict) -> list[str]:
    if plan.get("auto_submit", False):
        return ["auto_submit is true — not allowed"]
    return []


def _check_human_approval(plan: dict) -> list[str]:
    if not plan.get("requires_human_approval", False):
        return ["requires_human_approval must be true"]
    return []


def _check_capabilities(plan: dict) -> list[str]:
    reasons: list[str] = []
    caps = plan.get("capabilities_required", [])
    for cap in caps:
        if cap in BLOCKED_CAPABILITIES:
            reasons.append(f"capability '{cap}' is blocked")
    return reasons


def _check_actions(plan: dict) -> tuple[list[str], list[dict]]:
    """Returns (blocked_reasons, dry_run_action_list)."""
    reasons: list[str] = []
    dry_run_actions: list[dict] = []

    actions = plan.get("actions", [])
    for i, action in enumerate(actions):
        action_id = action.get("action_id", f"action_{i}")
        atype = action.get("type", "")

        if atype in BLOCKED_ACTION_TYPES:
            reasons.append(
                f"action '{action_id}': type '{atype}' is blocked"
            )
            continue

        if atype not in ALLOWED_ACTION_TYPES:
            reasons.append(
                f"action '{action_id}': type '{atype}' is unknown; "
                f"allowed types: {sorted(ALLOWED_ACTION_TYPES)}"
            )
            continue

        # Check value for secret keywords
        value = action.get("value", "")
        if isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
            reasons.append(
                f"action '{action_id}': value appears to contain a secret or token"
            )
            continue

        # Check field names inside action for secret names
        secret_fields = [
            k for k in action
            if k.lower() in SECRET_FIELD_NAMES
        ]
        if secret_fields:
            reasons.append(
                f"action '{action_id}': contains secret field(s): {secret_fields}"
            )
            continue

        dry_run_actions.append({
            "action_id": action_id,
            "type": atype,
            "target_element": action.get("target_element"),
            "would_perform": (
                f"DRY-RUN {atype} on '{action.get('target_element', 'N/A')}'"
                f" — NOT executed"
            ),
            "real_action_performed": False,
            "real_click_performed": False,
            "real_type_performed": False,
            "os_input_used": False,
        })

    return reasons, dry_run_actions


def _validate_plan(plan: dict) -> tuple[str, list[str], list[dict]]:
    """Returns (status, blocked_reasons, dry_run_actions)."""
    blocked: list[str] = []
    blocked += _check_target(plan)
    blocked += _check_url(plan)
    blocked += _check_auto_submit(plan)
    blocked += _check_human_approval(plan)
    blocked += _check_capabilities(plan)
    action_blocked, dry_run_actions = _check_actions(plan)
    blocked += action_blocked

    status = "blocked" if blocked else "allowed"
    return status, blocked, dry_run_actions


# ------------------------------------------------------------------
# N+6.33A — Rust policy bridge (mirror + optional cargo cross-check)
# ------------------------------------------------------------------
#
# The bridge is a SECOND gate. A dry-run plan is only "accepted" when BOTH the
# Python adapter (above) AND the policy checker agree to allow it. The mirror
# below reimplements rust/ghoti_policy_checker/src/main.rs `evaluate()` exactly,
# so the decision is deterministic and needs no toolchain. Passing
# rust_bridge=True with a manifest also cross-checks against the real cargo
# binary; the mirror remains authoritative for the accept decision.

# Must match ghoti_policy_checker ALLOWED_CAPABILITIES / BLOCKED_CAPABILITIES.
_RUST_ALLOWED_CAPABILITIES = frozenset({
    "fixture_read",
    "local_policy_check",
    "plan_render",
    "repo_read",
    "status_read",
})

_RUST_BLOCKED_CAPABILITIES = frozenset({
    "account",
    "browser",
    "computer_use",
    "mass_message",
    "mcp",
    "money",
    "secrets",
})

# Computer-use capability vocabulary -> policy-checker vocabulary. Anything not
# mapped (e.g. docker, shell, auto_submit) stays as-is and lands in the
# checker's "unknown" bucket, which is also a deny — default-deny holds.
_CU_CAPABILITY_TO_RUST = {
    "live_browser": "browser",
    "external_web": "browser",
    "real_os_input": "computer_use",
    "account_login": "account",
    "mcp": "mcp",
    "secrets": "secrets",
    "purchase": "money",
    "money_transfer": "money",
    "mass_messaging": "mass_message",
}

# Blocked computer-use action types -> policy-checker capability they imply.
_BLOCKED_ACTION_TO_RUST_CAP = {
    "real_click": "computer_use",
    "real_type": "computer_use",
    "real_key_press": "computer_use",
    "real_mouse_move": "computer_use",
    "real_screenshot_upload": "computer_use",
    "login": "account",
    "purchase": "money",
    "transfer_money": "money",
    "open_browser": "browser",
    "mcp_setup": "mcp",
    "write_env_file": "secrets",
    "access_keychain": "secrets",
    "copy_token": "secrets",
    "read_secret_file": "secrets",
    "navigate_url": "browser",
}


def _normalize_capability(value: str) -> str:
    """Mirror of normalize_capability() in the Rust checker."""
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _plan_to_swarm_plan(plan: dict) -> dict:
    """Map a computer-use dry-run plan into the policy checker's plan shape.

    Capabilities, blocked action types, an unsafe target_url, and secret-bearing
    actions all surface as policy-checker capabilities / a live_launch request,
    so the checker independently rejects the same plans the adapter rejects.
    """
    capabilities: set[str] = set()
    live_launch = False

    for cap in plan.get("capabilities_required", []):
        capabilities.add(_CU_CAPABILITY_TO_RUST.get(cap, cap))
        if cap in ("live_browser", "external_web", "real_os_input", "account_login"):
            live_launch = True

    # Tie the URL guard into the second gate: any URL the adapter would reject
    # becomes a browser capability + live launch for the policy checker.
    if _check_url(plan):
        capabilities.add("browser")
        live_launch = True

    for action in plan.get("actions", []):
        atype = action.get("type", "")
        if atype in BLOCKED_ACTION_TYPES:
            live_launch = True
            mapped = _BLOCKED_ACTION_TO_RUST_CAP.get(atype)
            if mapped:
                capabilities.add(mapped)
        value = action.get("value", "")
        if isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
            capabilities.add("secrets")
        if any(k.lower() in SECRET_FIELD_NAMES for k in action):
            capabilities.add("secrets")

    return {
        "plan_id": plan.get("plan_id", "unknown"),
        "dry_run": True,  # this adapter is dry-run only
        "live_launch": live_launch,
        "requires_human_approval": bool(plan.get("requires_human_approval", False)),
        "capabilities": sorted(capabilities),
    }


def _mirror_rust_policy_decision(swarm_plan: dict) -> dict:
    """Deterministic Python mirror of ghoti_policy_checker `evaluate()`.

    Returns the same shape the Rust binary emits (subset used by the bridge),
    with source="python_mirror".
    """
    reasons: list[str] = []
    blocked_caps: list[str] = []
    unknown_caps: list[str] = []

    dry_run = bool(swarm_plan.get("dry_run", False))
    live_launch = bool(swarm_plan.get("live_launch", False))
    requires_human_approval = bool(swarm_plan.get("requires_human_approval", False))

    if not dry_run:
        reasons.append("dry_run_required")
    if live_launch:
        reasons.append("live_launch_requested")
    if not requires_human_approval:
        reasons.append("human_approval_not_required_by_plan")

    for capability in swarm_plan.get("capabilities", []):
        normalized = _normalize_capability(capability)
        if normalized in _RUST_BLOCKED_CAPABILITIES:
            blocked_caps.append(normalized)
        elif normalized not in _RUST_ALLOWED_CAPABILITIES:
            unknown_caps.append(normalized)

    blocked_caps = sorted(set(blocked_caps))
    unknown_caps = sorted(set(unknown_caps))

    if blocked_caps:
        reasons.append("blocked_capability_requested")
    if unknown_caps:
        reasons.append("unknown_capability_requested")

    allowed = not reasons
    return {
        "ok": True,
        "checker": "ghoti_policy_checker",
        "policy_version": "n6.28a-prototype-v1",
        "source": "python_mirror",
        "plan_id": swarm_plan.get("plan_id", "unknown"),
        "allowed": allowed,
        "decision": "allow" if allowed else "deny",
        "dry_run": dry_run,
        "live_launch": live_launch,
        "requires_human_approval": requires_human_approval,
        "reasons": reasons,
        "blocked_capabilities": blocked_caps,
        "unknown_capabilities": unknown_caps,
    }


def _invoke_rust_policy_checker(swarm_plan: dict, manifest: str) -> dict:
    """Optionally cross-check via the approved local Rust policy checker.

    Writes the swarm plan to a temp file and runs
    `cargo run --locked --offline --manifest-path <approved> -- --input <tmp>`.
    Cargo build artifacts stay in a temporary target directory. Never raises:
    on any failure (unapproved manifest, no toolchain, build error, timeout)
    returns an available=False stub so the mirror stays authoritative.
    """
    if manifest == RUST_POLICY_MANIFEST:
        resolved_manifest = APPROVED_RUST_POLICY_MANIFEST
    else:
        try:
            resolved_manifest = Path(manifest).resolve()
        except OSError as exc:
            return {
                "available": False,
                "source": "rust_cli",
                "note": f"cargo policy checker manifest could not be resolved: {exc}",
            }
    if resolved_manifest != APPROVED_RUST_POLICY_MANIFEST:
        return {
            "available": False,
            "source": "rust_cli",
            "note": "cargo policy checker manifest is not the approved Ghoti manifest",
        }
    if not resolved_manifest.is_file():
        return {
            "available": False,
            "source": "rust_cli",
            "note": "approved Ghoti cargo policy checker manifest is missing",
        }

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(swarm_plan, fh)
            tmp_path = fh.name
        cargo_env = os.environ.copy()
        cargo_env.setdefault(
            "CARGO_TARGET_DIR",
            str(Path(tempfile.gettempdir()) / "ghoti_rust_target"),
        )
        proc = subprocess.run(
            [
                "cargo", "run", "--quiet", "--locked", "--offline",
                "--manifest-path", str(resolved_manifest),
                "--", "--input", tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            cwd=str(REPO_ROOT),
            env=cargo_env,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {
                "available": False,
                "source": "rust_cli",
                "note": "cargo policy checker unavailable or returned no decision",
                "returncode": proc.returncode,
            }
        decision = json.loads(proc.stdout)
        decision["available"] = True
        decision["source"] = "rust_cli"
        return decision
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return {
            "available": False,
            "source": "rust_cli",
            "note": f"cargo policy checker not invoked: {exc}",
        }
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass


def _bridge_fields(plan: dict, adapter_status: str, *, run_cargo: bool,
                   manifest: str) -> dict:
    """Build the N+6.33A bridge result fragment for a validated plan."""
    swarm_plan = _plan_to_swarm_plan(plan)
    mirror = _mirror_rust_policy_decision(swarm_plan)
    adapter_allowed = adapter_status == "allowed"
    accepted = adapter_allowed and mirror["allowed"]

    fields = {
        "rust_policy_bridge_ready": True,
        "rust_bridge_milestone": RUST_BRIDGE_MILESTONE,
        "rust_policy_bridge_note": (
            "Dual-gate dry-run: a plan is accepted only when the Python adapter "
            "AND the ghoti_policy_checker decision both allow it. Mirror is "
            "authoritative; the approved local cargo cross-check is optional, "
            "locked, and offline."
        ),
        "rust_swarm_plan_input": swarm_plan,
        "rust_policy_decision": mirror,
        "adapter_allowed": adapter_allowed,
        "rust_allowed": mirror["allowed"],
        "accepted": accepted,
    }
    if run_cargo:
        fields["rust_policy_decision_cli"] = _invoke_rust_policy_checker(
            swarm_plan, manifest
        )
    return fields


# ------------------------------------------------------------------
# Result builders
# ------------------------------------------------------------------

def _build_arena_status(status: str, plan: dict) -> dict:
    return {
        "simulation": True,
        "live_execution": False,
        "live_computer_use_enabled": False,
        "plan_id": plan.get("plan_id", "unknown"),
        "target": plan.get("target", "unknown"),
        "status": status,
        "real_action_performed": False,
        "approved": False,
        "approval_pending": True,
    }


def _build_safety_block() -> dict:
    return {
        "no_real_os_input": True,
        "no_live_browser": True,
        "no_external_url": True,
        "no_account_login": True,
        "no_secrets_accessed": True,
        "no_auto_submit": True,
        "no_docker": True,
        "no_mcp": True,
        "no_shell_commands": True,
        "no_remote_api_calls": True,
        "dry_run_only": True,
        "real_action_performed": False,
        "real_click_performed": False,
        "real_type_performed": False,
        "os_input_used": False,
        "secrets_accessed": False,
    }


def _run_plan(plan_path: str, *, rust_bridge: bool = False,
              run_cargo: bool = False,
              rust_manifest: str = RUST_POLICY_MANIFEST) -> dict:
    try:
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "milestone": MILESTONE,
            "mode": "dry_run",
            "status": "error",
            "error": str(exc),
            "safety": _build_safety_block(),
        }

    status, blocked_reasons, dry_run_actions = _validate_plan(plan)

    result = {
        "ok": status == "allowed",
        "milestone": MILESTONE,
        "adapter_version": ADAPTER_VERSION,
        "mode": "dry_run",
        "status": status,
        "plan_id": plan.get("plan_id", "unknown"),
        "target": plan.get("target"),
        "target_url": plan.get("target_url"),
        "target_verified": status == "allowed",
        "blocked_reasons": blocked_reasons,
        "dry_run_actions": dry_run_actions,
        "real_action_performed": False,
        "real_click_performed": False,
        "real_type_performed": False,
        "os_input_used": False,
        "secrets_accessed": False,
        "auto_submit_performed": False,
        "requires_human_approval": plan.get("requires_human_approval", False),
        "approval_token": None,
        "rust_policy_bridge_ready": False,
        "rust_policy_bridge_note": (
            "N+6.28B Rust policy checker is merged; "
            "bridge wiring deferred to next milestone."
        ),
        "arena_status": _build_arena_status(status, plan),
        # placeholder; replaced below when the N+6.33A bridge is engaged
        "refused_live_actions": REFUSED_LIVE_ACTIONS,
        "real_launch_note": (
            "This adapter is dry-run only. No real OS action is performed. "
            "Real computer-use requires a future audited milestone with "
            "explicit human approval."
        ),
        "safety": _build_safety_block(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if rust_bridge:
        bridge = _bridge_fields(
            plan, status, run_cargo=run_cargo, manifest=rust_manifest
        )
        result.update(bridge)
        # When the second gate is engaged, ok reflects the combined decision.
        result["ok"] = bridge["accepted"]

    return result


def _run_check(*, rust_bridge: bool = False, run_cargo: bool = False,
               rust_manifest: str = RUST_POLICY_MANIFEST) -> dict:
    result = {
        "ok": True,
        "milestone": MILESTONE,
        "adapter_version": ADAPTER_VERSION,
        "check": "system_ready",
        "mode": "dry_run",
        "computer_use_enabled": False,
        "live_browser_enabled": False,
        "real_os_input_enabled": False,
        "auto_submit_enabled": False,
        "docker_enabled": False,
        "mcp_enabled": False,
        "secrets_access_enabled": False,
        "rust_policy_bridge_ready": False,
        "rust_policy_bridge_note": (
            "N+6.28B Rust policy checker is merged; "
            "bridge wiring deferred to next milestone."
        ),
        "n6_27a_dependency": "merged (N+6.27B on main) — swarm_launcher files untouched by this branch",
        "n6_28b_dependency": "merged (N+6.28B on main) — rust/ghoti_policy_checker files untouched by this branch",
        "allowed_targets": sorted(ALLOWED_TARGETS),
        "allowed_action_types": sorted(ALLOWED_ACTION_TYPES),
        "blocked_action_types": sorted(BLOCKED_ACTION_TYPES),
        "blocked_capabilities": sorted(BLOCKED_CAPABILITIES),
        "refused_live_actions": REFUSED_LIVE_ACTIONS,
        "repo_inspiration": "14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json",
        "safety": _build_safety_block(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if rust_bridge:
        # Demonstrate the second gate on the built-in default-deny plan: an
        # empty plan must be DENIED by the policy checker (default-deny holds).
        default_swarm_plan = {
            "plan_id": "built-in-default-deny-check",
            "dry_run": False,
            "live_launch": False,
            "requires_human_approval": False,
            "capabilities": [],
        }
        result["rust_policy_bridge_ready"] = True
        result["rust_bridge_milestone"] = RUST_BRIDGE_MILESTONE
        result["rust_policy_bridge_note"] = (
            "Dual-gate bridge active: ghoti_policy_checker validates every "
            "dry-run plan as a second gate (mirror authoritative; cargo "
            "cross-check optional, approved-manifest-only, locked, and offline)."
        )
        result["rust_default_deny_decision"] = _mirror_rust_policy_decision(
            default_swarm_plan
        )
        if run_cargo:
            result["rust_default_deny_decision_cli"] = _invoke_rust_policy_checker(
                default_swarm_plan, rust_manifest
            )

    return result


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ghoti N+6.29A Computer-Use Repo-Backed Adapter (dry-run only)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run system readiness check",
    )
    parser.add_argument(
        "--plan",
        metavar="FILE",
        help="Path to action plan JSON file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry-run mode (always true; real execution not supported)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON",
    )
    parser.add_argument(
        "--rust-bridge",
        action="store_true",
        help="Engage the N+6.33A second gate (ghoti_policy_checker decision)",
    )
    parser.add_argument(
        "--rust-cargo",
        action="store_true",
        help="Cross-check via the approved local Cargo manifest (locked/offline)",
    )
    parser.add_argument(
        "--rust-manifest",
        metavar="PATH",
        default=RUST_POLICY_MANIFEST,
        help=(
            "Policy checker Cargo.toml; only the approved Ghoti manifest is "
            f"accepted (default: {RUST_POLICY_MANIFEST})"
        ),
    )

    args = parser.parse_args()

    if args.check:
        result = _run_check(
            rust_bridge=args.rust_bridge,
            run_cargo=args.rust_cargo,
            rust_manifest=args.rust_manifest,
        )
    elif args.plan:
        result = _run_plan(
            args.plan,
            rust_bridge=args.rust_bridge,
            run_cargo=args.rust_cargo,
            rust_manifest=args.rust_manifest,
        )
    else:
        parser.print_help()
        return 1

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", result.get("check", "unknown"))
        ok = result.get("ok", False)
        print(f"[{MILESTONE}] adapter status: {status} | ok: {ok}")
        if result.get("blocked_reasons"):
            for r in result["blocked_reasons"]:
                print(f"  BLOCKED: {r}")
        if result.get("dry_run_actions"):
            print(f"  dry_run_actions: {len(result['dry_run_actions'])}")
        if result.get("rust_policy_bridge_ready") and "rust_policy_decision" in result:
            rd = result["rust_policy_decision"]
            print(
                f"  [{RUST_BRIDGE_MILESTONE}] rust gate: {rd['decision']} "
                f"| accepted (both gates): {result.get('accepted')}"
            )
            for r in rd.get("reasons", []):
                print(f"    RUST: {r}")

    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    sys.exit(main())
