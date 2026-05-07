"""Approval-bound JSONL audit trail for Ghoti ActionIntents.

Appends audit events to 05_logs/action_audit.jsonl.
Uses PowerShell for all file writes to handle the restricted ai_sandbox path.
Logs payload hashes only; never raw payloads, secrets, or credentials.
Status label: contract_created / local_demo_only / not_external_adapter_wired
"""

from __future__ import annotations

import base64
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[4]
AUDIT_LOG_PATH = REPO_ROOT / "05_logs" / "action_audit.jsonl"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_write_bytes(path: Path, data: bytes) -> None:
    encoded = base64.b64encode(data).decode("ascii")
    ps_path = str(path).replace("'", "''")
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command",
         f"[System.IO.File]::WriteAllBytes('{ps_path}', [Convert]::FromBase64String('{encoded}'))"],
        check=True, capture_output=True, text=True,
    )


def _append_event_line(line: str) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = b""
    try:
        if AUDIT_LOG_PATH.exists():
            existing = AUDIT_LOG_PATH.read_bytes()
    except OSError:
        existing = b""
    new_content = existing + (line + "\n").encode("utf-8")
    try:
        AUDIT_LOG_PATH.write_bytes(new_content)
    except OSError:
        _ps_write_bytes(AUDIT_LOG_PATH, new_content)


def log_event(
    event_type: str,
    intent: dict,
    summary: str,
    adapter_id: Optional[str] = None,
) -> None:
    event = {
        "timestamp": _utc_now(),
        "event_type": event_type,
        "intent_id": intent.get("intent_id", ""),
        "requested_by_agent": intent.get("requested_by_agent", ""),
        "adapter_id_ref": intent.get("adapter_id", adapter_id),
        "action_type": intent.get("action_type", ""),
        "risk_level": intent.get("risk_level", ""),
        "status": intent.get("status", ""),
        "approval_required": intent.get("requires_approval", True),
        "consuming_adapter": adapter_id,
        "summary": summary,
        "payload_hash": (intent.get("payload_hash") or "")[:16],
    }
    _append_event_line(json.dumps(event))


def log_demo_completed(run_summary_path: str, stats: dict[str, int]) -> None:
    event = {
        "timestamp": _utc_now(),
        "event_type": "demo_completed",
        "intent_id": "demo",
        "requested_by_agent": "action_demo",
        "adapter_id_ref": "native-demo-adapter",
        "action_type": "demo_completed",
        "risk_level": "low",
        "status": "consumed",
        "approval_required": False,
        "consuming_adapter": "native-demo-adapter",
        "summary": f"Demo completed — stats: {stats}. Run summary: {run_summary_path}",
        "payload_hash": "demo",
    }
    _append_event_line(json.dumps(event))


def count_audit_events() -> int:
    if not AUDIT_LOG_PATH.exists():
        return 0
    count = 0
    try:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    count += 1
    except OSError:
        pass
    return count


def latest_audit_event() -> Optional[dict[str, Any]]:
    if not AUDIT_LOG_PATH.exists():
        return None
    last: Optional[dict[str, Any]] = None
    try:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped:
                    try:
                        last = json.loads(stripped)
                    except json.JSONDecodeError:
                        pass
    except OSError:
        pass
    return last
