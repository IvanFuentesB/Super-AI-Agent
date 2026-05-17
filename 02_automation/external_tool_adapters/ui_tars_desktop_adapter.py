#!/usr/bin/env python3
"""UI-TARS Desktop adapter stub (N+4.8A) — SAFE STUB ONLY.

Ghoti-local adapter stub for UI-TARS Desktop (bytedance/UI-TARS-desktop).

This stub does NOT import or run any external repo code, does NOT execute
desktop actions, and does NOT call any external API. It only describes the
tool and the safety gates that must pass before any real runtime wiring.
Real runtime wiring requires explicit human approval.
"""

TOOL_KEY = 'ui_tars_desktop'
TOOL_NAME = 'UI-TARS Desktop'
TOOL_SLUG = 'bytedance/UI-TARS-desktop'
REQUIRES_HUMAN_APPROVAL = True


def status() -> dict:
    """Adapter status. The adapter is a stub: not wired, local-only."""
    return {
        "tool": TOOL_NAME,
        "tool_key": TOOL_KEY,
        "slug": TOOL_SLUG,
        "adapter_kind": "safe_stub",
        "wired": False,
        "runtime_wiring": "not_wired",
        "local_only": True,
        "external_code_imported": False,
        "external_code_executed": False,
        "desktop_control_enabled": False,
        "live_api_enabled": False,
        "requires_human_approval": REQUIRES_HUMAN_APPROVAL,
    }


def capabilities() -> list:
    """Capabilities the tool WOULD provide once approved and wired."""
    return [
        "desktop GUI automation (screenshot + click/type)",
        "visual grounding of on-screen UI elements",
        "task execution against the local desktop",
    ]


def safety_gates() -> list:
    """Gates that must all pass, with human approval, before wiring."""
    return [
        "human_approval_required",
        "sandbox_static_scan_reviewed",
        "no_external_code_execution",
        "no_dependency_install_without_approval",
        "no_desktop_control_without_approval",
        "no_live_api_calls_without_approval",
        "no_live_account_actions",
    ]


if __name__ == "__main__":
    import json
    print(json.dumps({
        "status": status(),
        "capabilities": capabilities(),
        "safety_gates": safety_gates(),
    }, indent=2))
