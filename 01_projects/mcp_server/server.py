#!/usr/bin/env python3
"""
Ghoti MCP Server - minimal read-only tool server for the Ghoti operator system.

Transport: stdio (newline-delimited JSON-RPC 2.0)
Tools: ghoti_status, relay_status, read_compact_memory, read_next_actions

Safety: no shell, no writes, no network, no env access. Read-only within repo.
"""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# Resolve paths relative to this file so the server works from any cwd.
_SERVER_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SERVER_DIR.parent.parent
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"
NEXT_ACTIONS_FILE = REPO_ROOT / "14_context" / "next_actions.md"
RELAY_STATE_FILE = COMPACT_MEMORY_DIR / "current_loop_state.md"
CURRENT_STATE_FILE = REPO_ROOT / "14_context" / "current_state.md"
OPERATOR_STATE_FILE = COMPACT_MEMORY_DIR / "latest_operator_state.json"
MANUAL_EXECUTION_QUEUE_FILE = COMPACT_MEMORY_DIR / "manual_execution_queue.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_read(path):
    """Return file text or None - never raises."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, PermissionError):
        return None


def _parse_md_kv(text):
    """Parse simple `- key: value` markdown list into a dict."""
    result = {}
    for line in text.splitlines():
        line = line.strip().lstrip("- ")
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip().strip("`")
    return result


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def ghoti_status():
    return {
        "status": "ok",
        "system": "ghoti-mcp",
        "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def read_repo_summary():
    files = 0
    folders = 0
    for item in REPO_ROOT.iterdir():
        if item.is_file():
            files += 1
        elif item.is_dir():
            folders += 1
            try:
                for child in item.iterdir():
                    if child.is_file():
                        files += 1
                    elif child.is_dir():
                        folders += 1
            except OSError:
                continue
    return {
        "files": files,
        "folders": folders,
        "has_runtime": (REPO_ROOT / "01_projects" / "runtime_mvp").is_dir(),
        "has_mcp": (REPO_ROOT / "01_projects" / "mcp_server").is_dir(),
    }


def read_current_state():
    content = _safe_read(CURRENT_STATE_FILE)
    if content is None:
        return {"exists": False, "preview": ""}
    preview = " ".join(content[:300].split())
    return {"exists": True, "preview": preview}


def read_latest_operator_state():
    content = _safe_read(OPERATOR_STATE_FILE)
    if content is None:
        return {
            "status": "error",
            "reason": "operator_state_missing",
            "path": str(OPERATOR_STATE_FILE),
        }
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"operator_state_invalid_json: {exc}",
            "path": str(OPERATOR_STATE_FILE),
        }
    if not isinstance(payload, dict):
        return {
            "status": "error",
            "reason": "operator_state_invalid_shape",
            "path": str(OPERATOR_STATE_FILE),
        }
    return payload


def relay_status():
    text = _safe_read(RELAY_STATE_FILE)
    if text is None:
        return {"error": "relay state file not found", "expected_path": str(RELAY_STATE_FILE)}
    parsed = _parse_md_kv(text)
    return parsed if parsed else {"raw": text}


def read_compact_memory(filename):
    # Reject anything with path separators or traversal sequences.
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        return {"error": "invalid filename - bare filename required, no path components"}

    target = COMPACT_MEMORY_DIR / filename
    # Second check: resolved path must still sit inside compact_memory.
    try:
        target.resolve().relative_to(COMPACT_MEMORY_DIR.resolve())
    except ValueError:
        return {"error": "path traversal rejected"}

    content = _safe_read(target)
    if content is None:
        available = (
            sorted(f.name for f in COMPACT_MEMORY_DIR.iterdir() if f.is_file())
            if COMPACT_MEMORY_DIR.is_dir()
            else []
        )
        return {"error": "file not found", "filename": filename, "available_files": available}

    return {"filename": filename, "content": content}


def read_manual_execution_queue():
    content = _safe_read(MANUAL_EXECUTION_QUEUE_FILE)
    if content is None:
        return {
            "status": "ok",
            "items": [],
            "item_count": 0,
            "path": str(MANUAL_EXECUTION_QUEUE_FILE),
        }
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": f"manual_queue_invalid_json: {exc}",
            "path": str(MANUAL_EXECUTION_QUEUE_FILE),
        }
    if not isinstance(payload, list):
        return {
            "status": "error",
            "reason": "manual_queue_invalid_shape",
            "path": str(MANUAL_EXECUTION_QUEUE_FILE),
        }
    return {
        "status": "ok",
        "items": payload,
        "item_count": len(payload),
        "path": str(MANUAL_EXECUTION_QUEUE_FILE),
    }


def read_pipeline_items_overview(status_filter=None):
    valid_filters = {"pending", "approved", "rejected", "ready", "reviewed"}
    if status_filter and status_filter not in valid_filters:
        return {"error": f"invalid_status_filter: {status_filter!r}. Allowed: {sorted(valid_filters)}"}

    approval_inbox = COMPACT_MEMORY_DIR / "approval_inbox.json"
    manual_queue = COMPACT_MEMORY_DIR / "manual_execution_queue.json"

    def _load_json(path):
        text = _safe_read(path)
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    inbox_items = _load_json(approval_inbox)
    if not isinstance(inbox_items, list):
        return {"error": "approval_inbox_invalid_or_missing", "items": [], "counts": {}}

    queue_items = _load_json(manual_queue)
    queue_ok = isinstance(queue_items, list)
    queue_items = queue_items if queue_ok else []

    queue_by_approval = {}
    for qi in queue_items:
        if isinstance(qi, dict):
            src = str(qi.get("source_approval_id", "") or "")
            if src:
                queue_by_approval[src] = qi

    def _stage(ai, qi):
        s = str(ai.get("status", "") or "")
        if s == "pending":
            return "approval_pending"
        if s == "rejected":
            return "approval_rejected"
        if s == "approved":
            if qi is None:
                return "approved_no_queue"
            qs = str(qi.get("status", "") or "")
            if qs == "reviewed_by_operator":
                return "reviewed_by_operator"
            if qs == "ready_for_manual_execution":
                return "ready_for_manual_execution"
        return "unknown"

    def _best_ts(ai, qi):
        cands = []
        if qi:
            if qi.get("reviewed_at_utc"):
                cands.append(str(qi["reviewed_at_utc"]))
            if qi.get("created_at_utc"):
                cands.append(str(qi["created_at_utc"]))
        if ai.get("resolved_at_utc"):
            cands.append(str(ai["resolved_at_utc"]))
        if ai.get("timestamp_utc"):
            cands.append(str(ai["timestamp_utc"]))
        return max(cands) if cands else ""

    rows = []
    for ai in inbox_items:
        if not isinstance(ai, dict):
            continue
        aid = str(ai.get("id", "") or "")
        qi = queue_by_approval.get(aid)
        stage = _stage(ai, qi)

        if status_filter:
            include = (
                (status_filter == "pending" and stage == "approval_pending")
                or (status_filter == "approved" and str(ai.get("status", "")) == "approved")
                or (status_filter == "rejected" and stage == "approval_rejected")
                or (status_filter == "ready" and stage == "ready_for_manual_execution")
                or (status_filter == "reviewed" and stage == "reviewed_by_operator")
            )
            if not include:
                continue

        rows.append({
            "approval_id": aid,
            "proposed_action": str(ai.get("proposed_action", "") or ""),
            "operator_decision": str(ai.get("decision", "") or ""),
            "approval_status": str(ai.get("status", "") or ""),
            "queue_status": str(qi.get("status", "") or "") if qi else "",
            "reviewed": qi is not None and qi.get("status") == "reviewed_by_operator",
            "latest_stage": stage,
            "latest_timestamp_utc": _best_ts(ai, qi),
            "latest_note": str(qi.get("review_note", "") or "") if qi else str(ai.get("reason", "") or ""),
            "has_explanation": False,
        })

    rows.sort(key=lambda r: str(r.get("latest_timestamp_utc", "") or ""), reverse=True)
    total = len(rows)
    return {
        "status": "partial" if not queue_ok else "ok",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "items": rows,
        "counts": {
            "total_items": total,
            "pending_count": sum(1 for r in rows if r["approval_status"] == "pending"),
            "approved_count": sum(1 for r in rows if r["approval_status"] == "approved"),
            "rejected_count": sum(1 for r in rows if r["approval_status"] == "rejected"),
            "ready_count": sum(1 for r in rows if r["latest_stage"] == "ready_for_manual_execution"),
            "reviewed_count": sum(1 for r in rows if r["latest_stage"] == "reviewed_by_operator"),
        },
    }


def read_control_center_state():
    def _load_json(path):
        text = _safe_read(path)
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    approval_inbox = COMPACT_MEMORY_DIR / "approval_inbox.json"
    manual_queue = COMPACT_MEMORY_DIR / "manual_execution_queue.json"

    inbox_items = _load_json(approval_inbox) or []
    queue_items = _load_json(manual_queue) or []
    latest_state = _load_json(OPERATOR_STATE_FILE)

    inbox_ok = isinstance(inbox_items, list)
    queue_ok = isinstance(queue_items, list)
    state_ok = isinstance(latest_state, dict) and "decision" in latest_state

    if not inbox_ok:
        inbox_items = []
    if not queue_ok:
        queue_items = []

    pending = [i for i in inbox_items if isinstance(i, dict) and i.get("status") == "pending"]
    approved = [i for i in inbox_items if isinstance(i, dict) and i.get("status") == "approved"]
    rejected = [i for i in inbox_items if isinstance(i, dict) and i.get("status") == "rejected"]
    ready = [i for i in queue_items if isinstance(i, dict) and i.get("status") == "ready_for_manual_execution"]
    reviewed = [i for i in queue_items if isinstance(i, dict) and i.get("status") == "reviewed_by_operator"]

    def _latest_id(lst, key="timestamp_utc"):
        if not lst:
            return None
        best = max(lst, key=lambda i: str(i.get(key, "") or ""))
        return best.get("id")

    status = "ok" if (state_ok and inbox_ok and queue_ok) else "partial"
    return {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "latest_operator_state": latest_state if state_ok else None,
        "latest_proposed_action": (latest_state or {}).get("proposed_next_action") if state_ok else None,
        "approval_inbox_summary": {
            "available": inbox_ok,
            "total_count": len(inbox_items),
            "pending_count": len(pending),
            "approved_count": len(approved),
            "rejected_count": len(rejected),
            "latest_pending_id": _latest_id(pending),
            "latest_approved_id": _latest_id(approved, "resolved_at_utc"),
        },
        "manual_queue_summary": {
            "available": queue_ok,
            "total_count": len(queue_items),
            "ready_count": len(ready),
            "reviewed_count": len(reviewed),
            "latest_ready_id": _latest_id(ready),
            "latest_reviewed_id": _latest_id(reviewed, "reviewed_at_utc"),
        },
        "lifecycle_health": {
            "operator_state_available": state_ok,
            "approval_inbox_available": inbox_ok,
            "manual_queue_available": queue_ok,
            "has_pending_approvals": len(pending) > 0,
            "has_ready_items": len(ready) > 0,
            "has_reviewed_items": len(reviewed) > 0,
            "system_visible": True,
            "approval_gate_intact": True,
        },
    }


def read_audit_trace(approval_id):
    if not approval_id or not isinstance(approval_id, str):
        return {"error": "approval_id_required"}
    # Inline trace build — server has no import of operator_loop; replicate minimally.
    approval_inbox = COMPACT_MEMORY_DIR / "approval_inbox.json"
    manual_queue = COMPACT_MEMORY_DIR / "manual_execution_queue.json"

    def _load_json(path):
        text = _safe_read(path)
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    inbox_items = _load_json(approval_inbox)
    if not isinstance(inbox_items, list):
        return {"error": "approval_inbox_invalid_or_missing", "approval_id": approval_id}

    approval_item = next((i for i in inbox_items if isinstance(i, dict) and i.get("id") == approval_id), None)
    if approval_item is None:
        return {"error": "approval_item_not_found", "approval_id": approval_id}

    queue_items = _load_json(manual_queue)
    queue_item = None
    if isinstance(queue_items, list):
        queue_item = next((i for i in queue_items if isinstance(i, dict) and i.get("source_approval_id") == approval_id), None)

    approval_status = str(approval_item.get("status", "unknown"))
    queue_status = str(queue_item.get("status", "")) if queue_item else ""

    latest_state = _load_json(OPERATOR_STATE_FILE)

    timeline = []
    if approval_item.get("timestamp_utc"):
        timeline.append({"event": "approval_created", "timestamp_utc": approval_item["timestamp_utc"], "source": "approval_inbox", "status": "pending"})
    if approval_item.get("resolved_at_utc"):
        timeline.append({"event": "approval_resolved", "timestamp_utc": approval_item["resolved_at_utc"], "source": "approval_inbox", "status": approval_status})
    if queue_item and queue_item.get("created_at_utc"):
        timeline.append({"event": "queue_item_created", "timestamp_utc": queue_item["created_at_utc"], "source": "manual_execution_queue", "status": "ready_for_manual_execution"})
    if queue_item and queue_item.get("reviewed_at_utc"):
        timeline.append({"event": "queue_item_reviewed", "timestamp_utc": queue_item["reviewed_at_utc"], "source": "manual_execution_queue", "status": "reviewed_by_operator", "note": str(queue_item.get("review_note", "") or "")})
    timeline.sort(key=lambda e: str(e.get("timestamp_utc", "") or ""))

    trace_status = "ok" if approval_status == "approved" and queue_item is not None else "partial"

    return {
        "trace_status": trace_status,
        "approval_id": approval_id,
        "approval_item": approval_item,
        "latest_operator_state": latest_state,
        "manual_queue_item": queue_item,
        "lifecycle_flags": {
            "approval_found": True,
            "approval_approved": approval_status == "approved",
            "approval_rejected": approval_status == "rejected",
            "approval_pending": approval_status == "pending",
            "queue_item_found": queue_item is not None,
            "queue_ready": queue_status == "ready_for_manual_execution",
            "queue_reviewed": queue_status == "reviewed_by_operator",
        },
        "timeline": timeline,
        "path_summary": {
            "approval_inbox_path": str(approval_inbox),
            "manual_execution_queue_path": str(manual_queue),
            "latest_operator_state_path": str(OPERATOR_STATE_FILE),
        },
    }


APPROVAL_INBOX_FILE = COMPACT_MEMORY_DIR / "approval_inbox.json"


def read_approval_inbox():
    content = _safe_read(APPROVAL_INBOX_FILE)
    if content is None:
        return {"status": "ok", "items": [], "item_count": 0, "path": str(APPROVAL_INBOX_FILE)}
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        return {"status": "error", "reason": f"approval_inbox_invalid_json: {exc}", "path": str(APPROVAL_INBOX_FILE)}
    if not isinstance(payload, list):
        return {"status": "error", "reason": "approval_inbox_invalid_shape", "path": str(APPROVAL_INBOX_FILE)}
    pending = [i for i in payload if isinstance(i, dict) and i.get("status") == "pending"]
    return {
        "status": "ok",
        "items": payload,
        "item_count": len(payload),
        "pending_count": len(pending),
        "path": str(APPROVAL_INBOX_FILE),
    }


def read_approval_item(approval_id):
    if not approval_id or not isinstance(approval_id, str):
        return {"error": "approval_id_required"}
    content = _safe_read(APPROVAL_INBOX_FILE)
    if content is None:
        return {"error": "approval_inbox_missing", "approval_id": approval_id}
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "approval_inbox_invalid_json", "approval_id": approval_id}
    if not isinstance(payload, list):
        return {"error": "approval_inbox_invalid_shape", "approval_id": approval_id}
    item = next((i for i in payload if isinstance(i, dict) and i.get("id") == approval_id), None)
    if item is None:
        return {"error": "approval_item_not_found", "approval_id": approval_id}
    return {"status": "ok", "item": item}


def read_manual_queue_item(item_id):
    if not item_id or not isinstance(item_id, str):
        return {"error": "item_id_required"}
    content = _safe_read(MANUAL_EXECUTION_QUEUE_FILE)
    if content is None:
        return {"error": "manual_queue_missing", "item_id": item_id}
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "manual_queue_invalid_json", "item_id": item_id}
    if not isinstance(payload, list):
        return {"error": "manual_queue_invalid_shape", "item_id": item_id}
    item = next((i for i in payload if isinstance(i, dict) and i.get("id") == item_id), None)
    if item is None:
        return {"error": "manual_queue_item_not_found", "item_id": item_id}
    return {"status": "ok", "item": item}


def read_next_actions():
    content = _safe_read(NEXT_ACTIONS_FILE)
    if content is None:
        return {"error": "next_actions.md not found", "expected_path": str(NEXT_ACTIONS_FILE)}
    return {"source": "14_context/next_actions.md", "content": content}


# ---------------------------------------------------------------------------
# MCP protocol layer
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "ghoti_status",
        "description": "Return a minimal Ghoti MCP health payload.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_repo_summary",
        "description": "Return a shallow repo summary from the repo root only.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_current_state",
        "description": "Return whether 14_context/current_state.md exists plus a short preview.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_latest_operator_state",
        "description": "Return the latest persisted supervised operator state snapshot.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_manual_execution_queue",
        "description": "Return all ready-for-manual-execution items. Read-only. Nothing executes.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_audit_trace",
        "description": "Return full supervised lifecycle trace for one approval id. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"approval_id": {"type": "string"}},
            "required": ["approval_id"],
        },
    },
    {
        "name": "read_control_center_state",
        "description": "Return unified supervised pipeline status: operator state, inbox counts, queue counts, health flags. Read-only.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_pipeline_items_overview",
        "description": "Return a compact per-item pipeline overview list across all approval/queue/review stages. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "enum": ["pending", "approved", "rejected", "ready", "reviewed"],
                    "description": "Optional filter by pipeline stage.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "read_approval_inbox",
        "description": "Return all items in the approval inbox with pending count. Read-only.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_approval_item",
        "description": "Return a single approval item by id. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"approval_id": {"type": "string"}},
            "required": ["approval_id"],
        },
    },
    {
        "name": "read_manual_queue_item",
        "description": "Return a single manual execution queue item by id. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"item_id": {"type": "string"}},
            "required": ["item_id"],
        },
    },
]


def _dispatch(name, arguments):
    if name == "ghoti_status":
        return ghoti_status()
    if name == "read_repo_summary":
        return read_repo_summary()
    if name == "read_current_state":
        return read_current_state()
    if name == "read_latest_operator_state":
        return read_latest_operator_state()
    if name == "read_manual_execution_queue":
        return read_manual_execution_queue()
    if name == "read_audit_trace":
        return read_audit_trace(arguments.get("approval_id", ""))
    if name == "read_control_center_state":
        return read_control_center_state()
    if name == "read_pipeline_items_overview":
        return read_pipeline_items_overview(arguments.get("status_filter") or None)
    if name == "read_approval_inbox":
        return read_approval_inbox()
    if name == "read_approval_item":
        return read_approval_item(arguments.get("approval_id", ""))
    if name == "read_manual_queue_item":
        return read_manual_queue_item(arguments.get("item_id", ""))
    return {"error": "unknown tool: " + name}


def _handle(req):
    method = req.get("method")
    req_id = req.get("id")  # None for notifications

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ghoti-mcp", "version": "0.1.0"},
            },
        }

    if method == "initialized":
        return None  # notification - no response

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = _dispatch(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": "error" in result,
            },
        }

    if method == "call_tool":
        params = req.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = _dispatch(name, arguments)
        if "error" in result:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(result["error"])}
            }
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": "method not found: " + method},
        }
    return None


def main():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as exc:
            sys.stdout.write(
                json.dumps({"jsonrpc": "2.0", "id": None,
                            "error": {"code": -32700, "message": "parse error: " + str(exc)}})
                + "\n"
            )
            sys.stdout.flush()
            continue

        response = _handle(req)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
