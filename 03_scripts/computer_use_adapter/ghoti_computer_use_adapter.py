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
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

MILESTONE = "N+6.29A"
ADAPTER_VERSION = "0.1.0"

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
        # file:// is always local
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


def _run_plan(plan_path: str) -> dict:
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

    return {
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
        "refused_live_actions": REFUSED_LIVE_ACTIONS,
        "real_launch_note": (
            "This adapter is dry-run only. No real OS action is performed. "
            "Real computer-use requires a future audited milestone with "
            "explicit human approval."
        ),
        "safety": _build_safety_block(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _run_check() -> dict:
    return {
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

    args = parser.parse_args()

    if args.check:
        result = _run_check()
    elif args.plan:
        result = _run_plan(args.plan)
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

    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    sys.exit(main())
