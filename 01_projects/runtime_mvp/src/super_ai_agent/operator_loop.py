from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .mcp_runtime import call_mcp_tool
from .storage import _write_text, get_project_root, runtime_data_lock

SMALL_REPO_FILE_THRESHOLD = 50
OPERATOR_STATE_FILE = get_project_root().parents[1] / "14_context" / "compact_memory" / "latest_operator_state.json"
APPROVAL_INBOX_PATH = get_project_root().parents[1] / "14_context" / "compact_memory" / "approval_inbox.json"
MANUAL_EXECUTION_QUEUE_PATH = get_project_root().parents[1] / "14_context" / "compact_memory" / "manual_execution_queue.json"


def _timestamp_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_proposed_next_action(decision: str) -> str:
    mapping = {
        "INIT_REQUIRED": "CREATE_INITIAL_STATE_SURFACE",
        "EXPAND_PROJECT": "EXPAND_VISIBLE_OPERATOR_CAPABILITIES",
        "STABLE": "REVIEW_NEXT_CONTROLLED_INTEGRATION",
    }
    return mapping.get(decision, "REVIEW_NEXT_CONTROLLED_INTEGRATION")


def _current_state_preview_info(payload: dict) -> dict:
    return {
        "exists": bool(payload.get("exists", False)),
        "preview": str(payload.get("preview", "") or ""),
        "source_path": "14_context/current_state.md",
    }


def _write_operator_state(payload: dict) -> None:
    OPERATOR_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    OPERATOR_STATE_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_approval_items_unlocked() -> list[dict]:
    if not APPROVAL_INBOX_PATH.exists():
        return []
    with APPROVAL_INBOX_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("approval_inbox_invalid_shape")
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("approval_inbox_invalid_item")
    return payload


def _write_approval_items_unlocked(items: list[dict]) -> None:
    APPROVAL_INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_text(APPROVAL_INBOX_PATH, json.dumps(items, indent=2) + "\n")


def _load_manual_queue_unlocked() -> list[dict]:
    if not MANUAL_EXECUTION_QUEUE_PATH.exists():
        return []
    with MANUAL_EXECUTION_QUEUE_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("manual_queue_invalid_shape")
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("manual_queue_invalid_item")
    return payload


def _write_manual_queue_unlocked(items: list[dict]) -> None:
    MANUAL_EXECUTION_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_text(MANUAL_EXECUTION_QUEUE_PATH, json.dumps(items, indent=2) + "\n")


def bridge_approval_to_manual_queue(approval_item: dict) -> dict:
    """Create a ready-for-manual-execution record from an approved inbox item. Does not execute anything."""
    approval_id = str(approval_item.get("id", "") or "")
    if not approval_id:
        return {
            "status": "error",
            "reason": "bridge_missing_approval_id",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    if approval_item.get("status") != "approved":
        return {
            "status": "skipped",
            "reason": "bridge_skipped_not_approved",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }

    try:
        with runtime_data_lock():
            existing = _load_manual_queue_unlocked()
            for record in existing:
                if record.get("source_approval_id") == approval_id:
                    return {
                        "status": "deduped",
                        "reason": "bridge_already_exists_for_approval_id",
                        "ready_item": record,
                        "path": str(MANUAL_EXECUTION_QUEUE_PATH),
                    }

            ready_item = {
                "id": f"ready-{uuid4().hex}",
                "source_approval_id": approval_id,
                "created_at_utc": _timestamp_utc(),
                "status": "ready_for_manual_execution",
                "proposed_action": str(approval_item.get("proposed_action", "") or ""),
                "approval_timestamp_utc": str(approval_item.get("resolved_at_utc", "") or ""),
                "operator_decision": str(approval_item.get("decision", "") or ""),
                "operator_snapshot": dict(approval_item.get("operator_snapshot", {}) or {}),
                "execution_mode": "manual_only",
                "notes": "",
            }
            existing.append(ready_item)
            _write_manual_queue_unlocked(existing)
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_write_failed: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_invalid_json: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }

    return {
        "status": "created",
        "ready_item": ready_item,
        "path": str(MANUAL_EXECUTION_QUEUE_PATH),
    }


def read_manual_queue_state() -> dict:
    try:
        with runtime_data_lock():
            items = _load_manual_queue_unlocked()
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_read_failed: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_invalid_json: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    return {
        "status": "ok",
        "items": items,
        "path": str(MANUAL_EXECUTION_QUEUE_PATH),
    }


def get_manual_queue_item(item_id: str) -> dict:
    queue = read_manual_queue_state()
    if queue.get("status") != "ok":
        return queue
    for item in queue.get("items", []):
        if item.get("id") == item_id:
            return {
                "status": "ok",
                "item": item,
                "path": queue["path"],
            }
    return {
        "status": "error",
        "reason": "manual_queue_item_not_found",
        "path": queue["path"],
    }


def explain_manual_queue_item(item_id: str) -> dict:
    """Return a read-only explanation of a queue item. Nothing executes."""
    result = get_manual_queue_item(item_id)
    if result.get("status") != "ok":
        return result
    item = result["item"]
    proposed_action = str(item.get("proposed_action", "") or "none")
    operator_decision = str(item.get("operator_decision", "") or "none")
    execution_mode = str(item.get("execution_mode", "") or "manual_only")
    status = str(item.get("status", "") or "unknown")
    review_note = str(item.get("review_note", "") or "")
    notes = str(item.get("notes", "") or "")

    execution_preview = (
        f"[NON-EXECUTING] Proposed action: {proposed_action}. "
        f"Operator decision: {operator_decision}. "
        f"Execution mode: {execution_mode}. "
        f"Current status: {status}. "
        f"Nothing will run automatically. "
        f"A human must initiate any follow-up action manually outside this system."
    )

    return {
        "status": "ok",
        "path": result["path"],
        "explanation": {
            "id": str(item.get("id", "")),
            "status": status,
            "proposed_action": proposed_action,
            "operator_decision": operator_decision,
            "execution_mode": execution_mode,
            "notes": notes,
            "review_note": review_note,
            "execution_preview": execution_preview,
        },
    }


def find_manual_queue_item_by_approval_id(approval_id: str) -> dict | None:
    queue = read_manual_queue_state()
    if queue.get("status") != "ok":
        return None
    for item in queue.get("items", []):
        if item.get("source_approval_id") == approval_id:
            return item
    return None


def find_latest_approved_approval_item() -> dict | None:
    inbox = read_approval_inbox_state()
    if inbox.get("status") != "ok":
        return None
    approved = [i for i in inbox.get("items", []) if i.get("status") == "approved"]
    if not approved:
        return None
    return max(approved, key=lambda i: str(i.get("resolved_at_utc", "") or ""))


def _build_audit_timeline(approval_item: dict, queue_item: dict | None) -> list[dict]:
    events: list[dict] = []
    if approval_item.get("timestamp_utc"):
        events.append({
            "event": "approval_created",
            "timestamp_utc": approval_item["timestamp_utc"],
            "source": "approval_inbox",
            "status": "pending",
        })
    if approval_item.get("resolved_at_utc"):
        events.append({
            "event": "approval_resolved",
            "timestamp_utc": approval_item["resolved_at_utc"],
            "source": "approval_inbox",
            "status": str(approval_item.get("status", "unknown")),
        })
    if queue_item:
        if queue_item.get("created_at_utc"):
            events.append({
                "event": "queue_item_created",
                "timestamp_utc": queue_item["created_at_utc"],
                "source": "manual_execution_queue",
                "status": "ready_for_manual_execution",
            })
        if queue_item.get("reviewed_at_utc"):
            events.append({
                "event": "queue_item_reviewed",
                "timestamp_utc": queue_item["reviewed_at_utc"],
                "source": "manual_execution_queue",
                "status": "reviewed_by_operator",
                "note": str(queue_item.get("review_note", "") or ""),
            })
    events.sort(key=lambda e: str(e.get("timestamp_utc", "") or ""))
    return events


def get_audit_trace(approval_id: str) -> dict:
    """Reconstruct the full supervised lifecycle for one approval id. Read-only."""
    approval_result = get_approval_item(approval_id)
    if approval_result.get("status") != "ok":
        return {
            "trace_status": "error",
            "reason": approval_result.get("reason", "approval_item_not_found"),
            "approval_id": approval_id,
            "path_summary": {
                "approval_inbox_path": str(APPROVAL_INBOX_PATH),
                "manual_execution_queue_path": str(MANUAL_EXECUTION_QUEUE_PATH),
                "latest_operator_state_path": str(OPERATOR_STATE_FILE),
            },
        }

    approval_item = approval_result["item"]
    approval_status = str(approval_item.get("status", "unknown"))

    latest_state = read_latest_operator_state()
    latest_state_ok = isinstance(latest_state, dict) and "decision" in latest_state

    queue_item = find_manual_queue_item_by_approval_id(approval_id)
    queue_status = str(queue_item.get("status", "")) if queue_item else ""

    explanation: dict | None = None
    if queue_item:
        exp = explain_manual_queue_item(str(queue_item.get("id", "")))
        if exp.get("status") == "ok":
            explanation = exp.get("explanation")

    lifecycle_flags = {
        "approval_found": True,
        "approval_pending": approval_status == "pending",
        "approval_approved": approval_status == "approved",
        "approval_rejected": approval_status == "rejected",
        "queue_item_found": queue_item is not None,
        "queue_ready": queue_status == "ready_for_manual_execution",
        "queue_reviewed": queue_status == "reviewed_by_operator",
        "explanation_available": explanation is not None,
    }

    if approval_status == "approved" and queue_item is not None:
        trace_status = "ok"
    else:
        trace_status = "partial"

    return {
        "trace_status": trace_status,
        "approval_id": approval_id,
        "approval_item": approval_item,
        "operator_snapshot_from_approval": dict(approval_item.get("operator_snapshot", {}) or {}),
        "latest_operator_state": latest_state if latest_state_ok else None,
        "manual_queue_item": queue_item,
        "manual_queue_explanation": explanation,
        "lifecycle_flags": lifecycle_flags,
        "timeline": _build_audit_timeline(approval_item, queue_item),
        "path_summary": {
            "approval_inbox_path": str(APPROVAL_INBOX_PATH),
            "manual_execution_queue_path": str(MANUAL_EXECUTION_QUEUE_PATH),
            "latest_operator_state_path": str(OPERATOR_STATE_FILE),
        },
    }


def update_manual_queue_item_review(item_id: str, note: str) -> dict:
    """Transition a ready_for_manual_execution item to reviewed_by_operator. Does not execute anything."""
    note = note.strip() if note else ""
    if not note:
        return {
            "status": "error",
            "reason": "review_note_required",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }

    try:
        with runtime_data_lock():
            items = _load_manual_queue_unlocked()
            target: dict | None = None
            for item in items:
                if item.get("id") == item_id:
                    target = item
                    break
            if target is None:
                return {
                    "status": "error",
                    "reason": "manual_queue_item_not_found",
                    "path": str(MANUAL_EXECUTION_QUEUE_PATH),
                }
            if target.get("status") != "ready_for_manual_execution":
                return {
                    "status": "error",
                    "reason": "manual_queue_item_not_ready_for_review",
                    "path": str(MANUAL_EXECUTION_QUEUE_PATH),
                    "item": target,
                }
            target["status"] = "reviewed_by_operator"
            target["review_note"] = note
            target["reviewed_at_utc"] = _timestamp_utc()
            _write_manual_queue_unlocked(items)
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_write_failed: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_invalid_json: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(MANUAL_EXECUTION_QUEUE_PATH),
        }

    return {
        "status": "ok",
        "item": target,
        "path": str(MANUAL_EXECUTION_QUEUE_PATH),
    }


def read_approval_inbox_state() -> dict:
    try:
        with runtime_data_lock():
            items = _load_approval_items_unlocked()
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_read_failed: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_invalid_json: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(APPROVAL_INBOX_PATH),
        }
    return {
        "status": "ok",
        "items": items,
        "path": str(APPROVAL_INBOX_PATH),
    }


def get_approval_item(approval_id: str) -> dict:
    inbox = read_approval_inbox_state()
    if inbox.get("status") != "ok":
        return inbox
    for item in inbox.get("items", []):
        if item.get("id") == approval_id:
            return {
                "status": "ok",
                "item": item,
                "path": inbox["path"],
            }
    return {
        "status": "error",
        "reason": "approval_item_not_found",
        "path": inbox["path"],
    }


def update_approval_item_status(approval_id: str, *, new_status: str, reason: str = "") -> dict:
    if new_status not in {"approved", "rejected"}:
        return {
            "status": "error",
            "reason": "approval_status_not_allowed",
            "path": str(APPROVAL_INBOX_PATH),
        }

    try:
        with runtime_data_lock():
            items = _load_approval_items_unlocked()
            target: dict | None = None
            for item in items:
                if item.get("id") == approval_id:
                    target = item
                    break
            if target is None:
                return {
                    "status": "error",
                    "reason": "approval_item_not_found",
                    "path": str(APPROVAL_INBOX_PATH),
                }
            if target.get("status") != "pending":
                return {
                    "status": "error",
                    "reason": "approval_item_not_pending",
                    "path": str(APPROVAL_INBOX_PATH),
                    "item": target,
                }
            target["status"] = new_status
            target["reason"] = reason if new_status == "rejected" else ""
            target["resolved_at_utc"] = _timestamp_utc()
            _write_approval_items_unlocked(items)
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_write_failed: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_invalid_json: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(APPROVAL_INBOX_PATH),
        }

    bridge_result: dict = {}
    bridge_attempted = new_status == "approved"
    bridge_succeeded: bool | None = None
    if bridge_attempted:
        bridge_result = bridge_approval_to_manual_queue(target)
        bridge_succeeded = bridge_result.get("status") in {"created", "deduped"}

    result_status = "ok"
    result_reason = ""
    if bridge_attempted and bridge_succeeded is False:
        result_status = "partial"
        result_reason = "approval_transition_succeeded_but_manual_queue_bridge_failed"

    result: dict = {
        "status": result_status,
        "item": target,
        "path": str(APPROVAL_INBOX_PATH),
        "transition_succeeded": True,
        "transition_status": new_status,
        "bridge_attempted": bridge_attempted,
        "bridge_succeeded": bridge_succeeded,
    }
    if bridge_result:
        result["bridge_result"] = bridge_result
    if result_reason:
        result["reason"] = result_reason
    return result


def create_operator_approval_item(operator_state: dict) -> dict:
    proposed_action = str(operator_state.get("proposed_next_action", "") or "").strip()
    if not proposed_action:
        return {
            "status": "skipped",
            "reason": "approval_item_not_created_without_proposed_action",
            "path": str(APPROVAL_INBOX_PATH),
        }

    try:
        with runtime_data_lock():
            items = _load_approval_items_unlocked()
            for item in items:
                if item.get("status") == "pending" and item.get("proposed_action") == proposed_action:
                    return {
                        "status": "deduped",
                        "approval_item": item,
                        "path": str(APPROVAL_INBOX_PATH),
                    }

            approval_item = {
                "id": f"approval-{uuid4().hex}",
                "timestamp_utc": _timestamp_utc(),
                "source": "operator",
                "decision": str(operator_state.get("decision", "") or ""),
                "proposed_action": proposed_action,
                "status": "pending",
                "reason": "",
                "operator_snapshot": dict(operator_state),
            }
            items.append(approval_item)
            _write_approval_items_unlocked(items)
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_write_failed: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"approval_inbox_invalid_json: {exc}",
            "path": str(APPROVAL_INBOX_PATH),
        }
    except ValueError as exc:
        return {
            "status": "error",
            "reason": str(exc),
            "path": str(APPROVAL_INBOX_PATH),
        }

    return {
        "status": "created",
        "approval_item": approval_item,
        "path": str(APPROVAL_INBOX_PATH),
    }


def read_latest_operator_state() -> dict:
    if not OPERATOR_STATE_FILE.exists():
        return {
            "status": "error",
            "reason": "operator_state_missing",
            "path": str(OPERATOR_STATE_FILE),
        }
    try:
        data = json.loads(OPERATOR_STATE_FILE.read_text(encoding="utf-8"))
    except OSError as exc:
        return {
            "status": "error",
            "reason": f"operator_state_read_failed: {exc}",
            "path": str(OPERATOR_STATE_FILE),
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"operator_state_invalid_json: {exc}",
            "path": str(OPERATOR_STATE_FILE),
        }
    if not isinstance(data, dict):
        return {
            "status": "error",
            "reason": "operator_state_invalid_shape",
            "path": str(OPERATOR_STATE_FILE),
        }
    return data


def build_approval_inbox_summary() -> dict:
    inbox = read_approval_inbox_state()
    if inbox.get("status") != "ok":
        return {"available": False, "reason": inbox.get("reason", "unavailable")}
    items = inbox.get("items", [])
    pending = [i for i in items if i.get("status") == "pending"]
    approved = [i for i in items if i.get("status") == "approved"]
    rejected = [i for i in items if i.get("status") == "rejected"]

    def _latest(lst: list[dict], key: str = "timestamp_utc") -> dict | None:
        if not lst:
            return None
        return max(lst, key=lambda i: str(i.get(key, "") or ""))

    latest_pending = _latest(pending)
    latest_approved = _latest(approved, "resolved_at_utc")
    latest_rejected = _latest(rejected, "resolved_at_utc")
    return {
        "available": True,
        "total_count": len(items),
        "pending_count": len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "latest_pending_id": str(latest_pending.get("id", "") or "") if latest_pending else None,
        "latest_approved_id": str(latest_approved.get("id", "") or "") if latest_approved else None,
        "latest_rejected_id": str(latest_rejected.get("id", "") or "") if latest_rejected else None,
    }


def build_manual_queue_summary() -> dict:
    queue = read_manual_queue_state()
    if queue.get("status") != "ok":
        return {"available": False, "reason": queue.get("reason", "unavailable")}
    items = queue.get("items", [])
    ready = [i for i in items if i.get("status") == "ready_for_manual_execution"]
    reviewed = [i for i in items if i.get("status") == "reviewed_by_operator"]

    def _latest(lst: list[dict], key: str = "created_at_utc") -> dict | None:
        if not lst:
            return None
        return max(lst, key=lambda i: str(i.get(key, "") or ""))

    latest_ready = _latest(ready)
    latest_reviewed = _latest(reviewed, "reviewed_at_utc")
    return {
        "available": True,
        "total_count": len(items),
        "ready_count": len(ready),
        "reviewed_count": len(reviewed),
        "latest_ready_id": str(latest_ready.get("id", "") or "") if latest_ready else None,
        "latest_reviewed_id": str(latest_reviewed.get("id", "") or "") if latest_reviewed else None,
    }


def build_compact_timeline_summary() -> list[dict]:
    events: list[dict] = []
    # Latest operator state timestamp
    state = read_latest_operator_state()
    if isinstance(state, dict) and state.get("timestamp_utc"):
        events.append({
            "event": "operator_tick",
            "timestamp_utc": state["timestamp_utc"],
            "source": "latest_operator_state",
            "note": str(state.get("decision", "") or ""),
        })
    # Latest inbox events
    inbox = read_approval_inbox_state()
    if inbox.get("status") == "ok":
        for item in inbox.get("items", []):
            if item.get("timestamp_utc"):
                events.append({
                    "event": "approval_created",
                    "timestamp_utc": item["timestamp_utc"],
                    "source": "approval_inbox",
                    "note": str(item.get("proposed_action", "") or ""),
                })
            if item.get("resolved_at_utc"):
                events.append({
                    "event": "approval_resolved",
                    "timestamp_utc": item["resolved_at_utc"],
                    "source": "approval_inbox",
                    "note": str(item.get("status", "") or ""),
                })
    # Latest queue events
    queue = read_manual_queue_state()
    if queue.get("status") == "ok":
        for item in queue.get("items", []):
            if item.get("created_at_utc"):
                events.append({
                    "event": "queue_item_created",
                    "timestamp_utc": item["created_at_utc"],
                    "source": "manual_execution_queue",
                    "note": str(item.get("proposed_action", "") or ""),
                })
            if item.get("reviewed_at_utc"):
                events.append({
                    "event": "queue_item_reviewed",
                    "timestamp_utc": item["reviewed_at_utc"],
                    "source": "manual_execution_queue",
                    "note": str(item.get("review_note", "") or ""),
                })
    events.sort(key=lambda e: str(e.get("timestamp_utc", "") or ""), reverse=True)
    return events[:10]


def get_operator_control_center_state() -> dict:
    """Build a unified read-only supervised pipeline status object. Nothing executes."""
    generated_at = _timestamp_utc()
    latest_state = read_latest_operator_state()
    latest_state_ok = isinstance(latest_state, dict) and "decision" in latest_state

    inbox_summary = build_approval_inbox_summary()
    queue_summary = build_manual_queue_summary()
    timeline = build_compact_timeline_summary()

    latest_proposed_action = ""
    latest_operator_decision = ""
    if latest_state_ok:
        latest_proposed_action = str(latest_state.get("proposed_next_action", "") or "")
        latest_operator_decision = str(latest_state.get("decision", "") or "")

    # Compact latest_items previews
    latest_items: dict = {
        "latest_operator_decision": latest_operator_decision or None,
        "latest_pending_approval_id": inbox_summary.get("latest_pending_id"),
        "latest_approved_approval_id": inbox_summary.get("latest_approved_id"),
        "latest_ready_item_id": queue_summary.get("latest_ready_id"),
        "latest_reviewed_item_id": queue_summary.get("latest_reviewed_id"),
    }

    lifecycle_health = {
        "operator_state_available": latest_state_ok,
        "approval_inbox_available": inbox_summary.get("available", False),
        "manual_queue_available": queue_summary.get("available", False),
        "has_pending_approvals": int(inbox_summary.get("pending_count", 0) or 0) > 0,
        "has_ready_items": int(queue_summary.get("ready_count", 0) or 0) > 0,
        "has_reviewed_items": int(queue_summary.get("reviewed_count", 0) or 0) > 0,
        "system_visible": True,
        "approval_gate_intact": True,
    }

    all_available = (
        lifecycle_health["operator_state_available"]
        and lifecycle_health["approval_inbox_available"]
        and lifecycle_health["manual_queue_available"]
    )
    status = "ok" if all_available else "partial"

    return {
        "status": status,
        "generated_at_utc": generated_at,
        "latest_operator_state": latest_state if latest_state_ok else None,
        "latest_proposed_action": latest_proposed_action or None,
        "approval_inbox_summary": inbox_summary,
        "manual_queue_summary": queue_summary,
        "latest_items": latest_items,
        "lifecycle_health": lifecycle_health,
        "compact_timeline_summary": timeline,
    }


def simple_operator_tick() -> dict:
    repo_summary = call_mcp_tool("read_repo_summary")
    current_state = call_mcp_tool("read_current_state")

    if not current_state.get("exists", False):
        decision = "INIT_REQUIRED"
    elif int(repo_summary.get("files", 0) or 0) < SMALL_REPO_FILE_THRESHOLD:
        decision = "EXPAND_PROJECT"
    else:
        decision = "STABLE"

    state = {
        "timestamp_utc": _timestamp_utc(),
        "repo_summary": repo_summary,
        "current_state_preview_info": _current_state_preview_info(current_state),
        "decision": decision,
        "proposed_next_action": build_proposed_next_action(decision),
        "approval_required": True,
        "status": "ok",
    }

    try:
        _write_operator_state(state)
    except OSError as exc:
        return {
            **state,
            "status": "error",
            "reason": f"operator_state_write_failed: {exc}",
            "operator_state_path": str(OPERATOR_STATE_FILE),
        }

    approval_result = create_operator_approval_item({
        **state,
        "operator_state_path": str(OPERATOR_STATE_FILE),
    })
    if approval_result.get("status") == "error":
        return {
            **state,
            "status": "error",
            "reason": approval_result.get("reason", "approval_inbox_write_failed"),
            "operator_state_path": str(OPERATOR_STATE_FILE),
            "approval_inbox_path": str(APPROVAL_INBOX_PATH),
        }

    approval_item = approval_result.get("approval_item") or {}
    return {
        **state,
        "operator_state_path": str(OPERATOR_STATE_FILE),
        "approval_inbox_path": approval_result.get("path", str(APPROVAL_INBOX_PATH)),
        "approval_item_status": approval_result.get("status", "skipped"),
        "approval_item_id": str(approval_item.get("id", "") or ""),
    }
