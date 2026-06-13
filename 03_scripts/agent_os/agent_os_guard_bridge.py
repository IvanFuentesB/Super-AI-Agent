"""Read-only status bridge from the command center to the Rust Agent OS guard."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import local_worker_trial


def _decision_summary(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "allow": bool(decision.get("allow")),
        "decision": decision.get("decision", "denied"),
        "reasons": list(decision.get("reasons", [])),
        "denied_capabilities": list(decision.get("denied_capabilities", [])),
        "guard_version": decision.get("guard_version"),
        "default_deny": bool((decision.get("safety") or {}).get("default_deny")),
        "live_execution": bool((decision.get("safety") or {}).get("live_execution")),
    }


@lru_cache(maxsize=1)
def guard_status() -> dict[str, Any]:
    """Prove the safe allow path and dangerous deny path without live execution."""
    safe_request = local_worker_trial._guard_request(
        "coding-task-plan", "simulation", None
    )
    dangerous_request = local_worker_trial._guard_request(
        "coding-task-plan", "simulation", None
    )
    dangerous_request["requested_capabilities"] = ["repo_read", "browser"]

    safe = _decision_summary(local_worker_trial._invoke_guard(safe_request))
    dangerous = _decision_summary(local_worker_trial._invoke_guard(dangerous_request))
    available = bool(safe.get("guard_version") and dangerous.get("guard_version"))
    return {
        "ok": available and safe["allow"] and not dangerous["allow"],
        "available": available,
        "guard_version": safe.get("guard_version") or dangerous.get("guard_version"),
        "safe_suggestion_allowed": safe["allow"],
        "dangerous_capability_denied": not dangerous["allow"]
        and "browser" in dangerous["denied_capabilities"],
        "default_deny": safe["default_deny"] and dangerous["default_deny"],
        "live_execution": safe["live_execution"] or dangerous["live_execution"],
        "approved_local_execution_enabled": False,
        "approved_local_artifact_execution_enabled": True,
        "safe_decision": safe,
        "dangerous_decision": dangerous,
    }


def guard_check_records() -> list[dict[str, Any]]:
    """Return read-only self-check records for the integrated command center."""
    status = guard_status()
    return [
        {
            "name": "agent_os_guard_allows_safe_suggestion",
            "ok": status["safe_suggestion_allowed"],
            "details": status.get("guard_version") or "guard unavailable",
        },
        {
            "name": "agent_os_guard_denies_browser_capability",
            "ok": status["dangerous_capability_denied"],
            "details": ", ".join(
                status["dangerous_decision"]["denied_capabilities"]
            )
            or "no denied capabilities",
        },
    ]
