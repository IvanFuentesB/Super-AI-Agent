from __future__ import annotations

from datetime import datetime, timezone

from .operator_loop import (
    APPROVAL_INBOX_PATH,
    MANUAL_EXECUTION_QUEUE_PATH,
    OPERATOR_STATE_FILE,
    build_approval_inbox_summary,
    build_compact_timeline_summary,
    build_manual_queue_summary,
    get_operator_control_center_state,
    read_approval_inbox_state,
    read_manual_queue_state,
)


def _ts_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _determine_latest_stage(approval_item: dict, queue_item: dict | None) -> str:
    approval_status = str(approval_item.get("status", "") or "")
    if approval_status == "pending":
        return "approval_pending"
    if approval_status == "rejected":
        return "approval_rejected"
    if approval_status == "approved":
        if queue_item is None:
            return "approved_no_queue"
        qs = str(queue_item.get("status", "") or "")
        if qs == "reviewed_by_operator":
            return "reviewed_by_operator"
        if qs == "ready_for_manual_execution":
            return "ready_for_manual_execution"
    return "unknown"


def _best_timestamp(approval_item: dict, queue_item: dict | None) -> str:
    candidates = []
    if queue_item:
        if queue_item.get("reviewed_at_utc"):
            candidates.append(str(queue_item["reviewed_at_utc"]))
        if queue_item.get("created_at_utc"):
            candidates.append(str(queue_item["created_at_utc"]))
    if approval_item.get("resolved_at_utc"):
        candidates.append(str(approval_item["resolved_at_utc"]))
    if approval_item.get("timestamp_utc"):
        candidates.append(str(approval_item["timestamp_utc"]))
    return max(candidates) if candidates else ""


_VALID_STATUS_FILTERS = {"pending", "approved", "rejected", "ready", "reviewed"}


def get_pipeline_items_overview(status_filter: str | None = None) -> dict:
    """Return a compact per-item pipeline overview. Read-only. Nothing executes."""
    if status_filter and status_filter not in _VALID_STATUS_FILTERS:
        return {
            "status": "error",
            "reason": f"invalid_status_filter: {status_filter!r}. Allowed: {sorted(_VALID_STATUS_FILTERS)}",
            "items": [],
            "counts": {},
        }

    inbox = read_approval_inbox_state()
    if inbox.get("status") != "ok":
        return {
            "status": "error",
            "reason": inbox.get("reason", "approval_inbox_unavailable"),
            "generated_at_utc": _ts_now(),
            "items": [],
            "counts": {},
        }

    approval_items = inbox.get("items", [])
    queue_result = read_manual_queue_state()
    queue_ok = queue_result.get("status") == "ok"
    queue_items = queue_result.get("items", []) if queue_ok else []

    queue_by_approval: dict[str, dict] = {}
    for qi in queue_items:
        src = str(qi.get("source_approval_id", "") or "")
        if src:
            queue_by_approval[src] = qi

    rows: list[dict] = []
    for ai in approval_items:
        approval_id = str(ai.get("id", "") or "")
        qi = queue_by_approval.get(approval_id)
        latest_stage = _determine_latest_stage(ai, qi)
        latest_ts = _best_timestamp(ai, qi)

        if status_filter:
            include = (
                (status_filter == "pending" and latest_stage == "approval_pending")
                or (status_filter == "approved" and str(ai.get("status", "")) == "approved")
                or (status_filter == "rejected" and latest_stage == "approval_rejected")
                or (status_filter == "ready" and latest_stage == "ready_for_manual_execution")
                or (status_filter == "reviewed" and latest_stage == "reviewed_by_operator")
            )
            if not include:
                continue

        rows.append({
            "approval_id": approval_id,
            "proposed_action": str(ai.get("proposed_action", "") or ""),
            "operator_decision": str(ai.get("decision", "") or ""),
            "approval_status": str(ai.get("status", "") or ""),
            "queue_status": str(qi.get("status", "") or "") if qi else "",
            "reviewed": qi is not None and qi.get("status") == "reviewed_by_operator",
            "latest_stage": latest_stage,
            "latest_timestamp_utc": latest_ts,
            "latest_note": (
                str(qi.get("review_note", "") or "") if qi
                else str(ai.get("reason", "") or "")
            ),
            "has_explanation": False,
        })

    rows.sort(key=lambda r: str(r.get("latest_timestamp_utc", "") or ""), reverse=True)

    total = len(rows)
    pending_count = sum(1 for r in rows if r["approval_status"] == "pending")
    approved_count = sum(1 for r in rows if r["approval_status"] == "approved")
    rejected_count = sum(1 for r in rows if r["approval_status"] == "rejected")
    ready_count = sum(1 for r in rows if r["latest_stage"] == "ready_for_manual_execution")
    reviewed_count = sum(1 for r in rows if r["latest_stage"] == "reviewed_by_operator")

    return {
        "status": "partial" if not queue_ok else "ok",
        "generated_at_utc": _ts_now(),
        "items": rows,
        "counts": {
            "total_items": total,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "ready_count": ready_count,
            "reviewed_count": reviewed_count,
        },
    }


def _get_attention_summary(inbox_summary: dict, queue_summary: dict) -> dict:
    """Compute what the operator needs to act on right now. Read-only. Nothing executes."""
    pending_count = int(inbox_summary.get("pending_count") or 0)
    ready_count = int(queue_summary.get("ready_count") or 0)

    if pending_count > 0:
        level = "high"
        message = (
            f"{pending_count} pending approval(s) need your decision now."
        )
        action_items = ["Go to Approval Inbox — review and approve or reject pending items"]
    elif ready_count > 0:
        level = "medium"
        message = f"{ready_count} item(s) ready for manual execution in the queue."
        action_items = ["Go to Manual Queue — mark items reviewed after inspection"]
    else:
        level = "none"
        message = "No immediate operator action required."
        action_items = []

    return {
        "needs_attention": pending_count > 0 or ready_count > 0,
        "attention_level": level,
        "pending_approvals_count": pending_count,
        "ready_queue_count": ready_count,
        "primary_message": message,
        "action_items": action_items,
        "latest_pending_approval_id": inbox_summary.get("latest_pending_id"),
        "latest_ready_item_id": queue_summary.get("latest_ready_id"),
    }


def get_full_control_center_state() -> dict:
    """Unified read-only control center state including pipeline overview. Nothing executes."""
    base = get_operator_control_center_state()
    overview = get_pipeline_items_overview()

    counts = overview.get("counts", {})
    recent_items = overview.get("items", [])[:5]

    inbox_summary = base.get("approval_inbox_summary", {})
    queue_summary = base.get("manual_queue_summary", {})
    latest_state = base.get("latest_operator_state") or {}

    base["pipeline_overview_counts"] = counts
    base["recent_pipeline_items"] = recent_items
    base["latest_items"] = {
        "latest_operator_decision": str(latest_state.get("decision", "") or "") or None,
        "latest_pending_approval_id": inbox_summary.get("latest_pending_id"),
        "latest_approved_approval_id": inbox_summary.get("latest_approved_id"),
        "latest_rejected_approval_id": inbox_summary.get("latest_rejected_id"),
        "latest_ready_item_id": queue_summary.get("latest_ready_id"),
        "latest_reviewed_item_id": queue_summary.get("latest_reviewed_id"),
        "latest_proposed_action": base.get("latest_proposed_action"),
    }
    base["attention_summary"] = _get_attention_summary(inbox_summary, queue_summary)

    return base
