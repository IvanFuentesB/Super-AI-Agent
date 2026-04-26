"""N+3.1 ActionIntent approval-bound demo.

Demonstrates the full gated path: propose -> classify -> approve/block -> consume.
Creates 5 ActionIntents from N+3.0 multi-agent roles, runs them through the
policy gate (classify_action), writes a JSONL audit trail, and saves a run
summary artifact.

Uses PowerShell for file writes to handle the restricted ai_sandbox path.
Runnable directly: python action_demo.py
Status label: contract_created / local_demo_only / not_external_adapter_wired
"""

from __future__ import annotations

# Allow direct invocation in addition to package-level import.
import sys as _sys
from pathlib import Path as _Path
_SRC = _Path(__file__).resolve().parents[1]
if str(_SRC) not in _sys.path:
    _sys.path.insert(0, str(_SRC))

import base64
import hashlib
import json
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from super_ai_agent.action_intent import (
    FORBIDDEN_ACTION_TYPES,
    LOW_RISK_ACTION_TYPES,
    classify_action,
    list_capability_adapters,
)
from super_ai_agent.action_audit import log_event, log_demo_completed, AUDIT_LOG_PATH

REPO_ROOT = _Path(__file__).resolve().parents[4]
RUNS_ROOT = REPO_ROOT / "05_logs" / "action_intent_runs"
SHARED_MEMORY_PATH = REPO_ROOT / "14_context" / "multi_agent_shared_memory.json"

DEMO_ADAPTER_ID = "native-demo-adapter"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def _payload_hash(payload: dict) -> str:
    encoded = json.dumps(payload or {}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _ps_write(path: Path, text: str) -> None:
    data = text.encode("utf-8")
    try:
        path.write_bytes(data)
    except OSError:
        encoded = base64.b64encode(data).decode("ascii")
        ps_path = str(path).replace("'", "''")
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             f"[System.IO.File]::WriteAllBytes('{ps_path}', [Convert]::FromBase64String('{encoded}'))"],
            check=True, capture_output=True, text=True,
        )


def _ensure_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        escaped = str(path).replace("'", "''")
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             f"[System.IO.Directory]::CreateDirectory('{escaped}') | Out-Null"],
            check=True, capture_output=True, text=True,
        )


def _load_shared_memory() -> dict[str, Any]:
    if not SHARED_MEMORY_PATH.exists():
        return {}
    try:
        return json.loads(SHARED_MEMORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _make_intent(
    requested_by_agent: str,
    adapter_id: str,
    action_type: str,
    target: str,
    payload: dict,
    reason: str,
    audit_tags: list[str],
) -> dict:
    risk_level, requires_approval, status, errors = classify_action(action_type, target, payload)
    return {
        "intent_id": f"intent-{uuid.uuid4().hex[:12]}",
        "created_at_utc": _utc_now(),
        "requested_by_agent": requested_by_agent,
        "adapter_id": adapter_id,
        "action_type": action_type,
        "target": target,
        "payload": payload,
        "payload_hash": _payload_hash(payload),
        "risk_level": risk_level,
        "status": status,
        "requires_approval": requires_approval,
        "approval_id": None,
        "approval_status": "not_created" if status == "blocked" else "pending",
        "result_status": "blocked" if status == "blocked" else "not_executed",
        "reason": reason,
        "errors": errors,
        "audit_tags": audit_tags,
        "execution_performed": False,
    }


def _approve_intent(intent: dict) -> dict:
    intent = dict(intent)
    intent["approval_id"] = f"approval-{uuid.uuid4().hex[:12]}"
    intent["approval_status"] = "approved"
    intent["approved_by"] = "local-demo-auto-approver"
    intent["approved_at_utc"] = _utc_now()
    intent["status"] = "approved"
    intent["audit_tags"] = list(intent.get("audit_tags", [])) + ["approved_by:local-demo-auto-approver"]
    return intent


def _consume_intent(intent: dict) -> dict:
    intent = dict(intent)
    intent["status"] = "consumed"
    intent["consumed_at_utc"] = _utc_now()
    intent["consumed_by_adapter_id"] = DEMO_ADAPTER_ID
    intent["result_status"] = "local_demo_no_execution"
    intent["audit_tags"] = list(intent.get("audit_tags", [])) + [f"consumed_by:{DEMO_ADAPTER_ID}"]
    return intent


def _sample_specs() -> list[dict]:
    return [
        {
            "requested_by_agent": "memory-agent",
            "adapter_id": DEMO_ADAPTER_ID,
            "action_type": "update_compact_memory",
            "target": "14_context/multi_agent_shared_memory.json",
            "payload": {"update_scope": "current_priorities"},
            "reason": "Refresh compact memory after N+3.1 ActionIntent milestone.",
            "audit_tags": ["milestone:N+3.1", "role:memory-agent"],
        },
        {
            "requested_by_agent": "token-saver-agent",
            "adapter_id": DEMO_ADAPTER_ID,
            "action_type": "write_local_artifact",
            "target": "05_logs/token_saver_checkpoint.md",
            "payload": {"content_type": "checkpoint_summary"},
            "reason": "Write a token-saving checkpoint artifact for this milestone.",
            "audit_tags": ["milestone:N+3.1", "role:token-saver-agent"],
        },
        {
            "requested_by_agent": "browser-candidate-agent",
            "adapter_id": DEMO_ADAPTER_ID,
            "action_type": "external_adapter_execution_without_approval",
            "target": "autobrowser://start",
            "payload": {"adapter": "autobrowser"},
            "reason": "Attempting AutoBrowser — must be blocked by policy gate.",
            "audit_tags": ["milestone:N+3.1", "role:browser-candidate-agent", "should_block"],
        },
        {
            "requested_by_agent": "ruflo-review-agent",
            "adapter_id": DEMO_ADAPTER_ID,
            "action_type": "propose_next_step",
            "target": "14_context/next_actions.md",
            "payload": {"proposal": "Evaluate AutoBrowser after ActionIntent gate is validated."},
            "reason": "Propose safe next architecture step based on RUFLO audit.",
            "audit_tags": ["milestone:N+3.1", "role:ruflo-review-agent"],
        },
        {
            "requested_by_agent": "implementation-planner-agent",
            "adapter_id": DEMO_ADAPTER_ID,
            "action_type": "summarize_local_file",
            "target": "14_context/ghoti_external_repo_tool_intake.md",
            "payload": {"max_chars": 2000},
            "reason": "Summarize external repo tool intake for planning context.",
            "audit_tags": ["milestone:N+3.1", "role:implementation-planner-agent"],
        },
    ]


def run_demo() -> dict[str, Any]:
    run_id = _run_id()
    run_dir = RUNS_ROOT / run_id
    _ensure_dir(run_dir)

    shared_memory = _load_shared_memory()
    current_priorities = shared_memory.get("current_priorities", [])

    specs = _sample_specs()
    stats = {"proposed": 0, "approved": 0, "blocked": 0, "consumed": 0}
    processed: list[dict] = []
    final_intents: list[dict] = []

    for spec in specs:
        intent = _make_intent(**spec)
        stats["proposed"] += 1

        if intent["status"] == "blocked":
            stats["blocked"] += 1
            final_intents.append(intent)
            log_event(
                "intent_blocked",
                intent,
                f"BLOCKED: {spec['action_type']} by {spec['requested_by_agent']} — forbidden action type",
            )
            processed.append({
                "intent_id": intent["intent_id"],
                "agent": spec["requested_by_agent"],
                "action_type": spec["action_type"],
                "outcome": "blocked",
                "risk_level": intent["risk_level"],
            })
        else:
            log_event(
                "intent_proposed",
                intent,
                f"Intent proposed by {spec['requested_by_agent']}: {spec['action_type']} -> {spec['target'] or '(no target)'}",
            )
            intent = _approve_intent(intent)
            stats["approved"] += 1
            log_event(
                "intent_approved",
                intent,
                f"Auto-approved low-risk local demo action: {spec['action_type']}",
                adapter_id="local-demo-auto-approver",
            )
            intent = _consume_intent(intent)
            stats["consumed"] += 1
            log_event(
                "intent_consumed",
                intent,
                f"Consumed by {DEMO_ADAPTER_ID}: {spec['action_type']}",
                adapter_id=DEMO_ADAPTER_ID,
            )
            final_intents.append(intent)
            processed.append({
                "intent_id": intent["intent_id"],
                "agent": spec["requested_by_agent"],
                "action_type": spec["action_type"],
                "outcome": "consumed",
                "risk_level": intent["risk_level"],
            })

    intents_path = run_dir / "action_intents.json"
    _ps_write(intents_path, json.dumps(final_intents, indent=2) + "\n")

    adapters = list_capability_adapters()

    summary_lines = [
        "# ActionIntent Demo Run Summary",
        "",
        f"Run id: `{run_id}`",
        "Status label: `contract_created / local_demo_only / not_external_adapter_wired`",
        f"Timestamp: `{_utc_now()}`",
        "",
        "## Stats",
        "",
        f"- Proposed: {stats['proposed']}",
        f"- Approved: {stats['approved']}",
        f"- Blocked: {stats['blocked']}",
        f"- Consumed: {stats['consumed']}",
        "",
        "## Intent Outcomes",
        "",
    ]
    for p in processed:
        outcome_label = p["outcome"].upper()
        summary_lines.append(
            f"- `{p['agent']}` -> `{p['action_type']}` -> **{outcome_label}** (risk: {p['risk_level']})"
        )

    summary_lines += [
        "",
        "## Approval Gate Truth",
        "",
        "- Low-risk local actions auto-approved by `local-demo-auto-approver`.",
        "- Forbidden action `external_adapter_execution_without_approval` blocked by policy gate.",
        "- Blocked intents are never consumed or executed.",
        "- Execution performed: NO (all consumed intents get result_status=local_demo_no_execution).",
        "- External adapters: NOT wired. `browser-candidate-agent` action blocked by classify_action.",
        "",
        "## Adapter Descriptors",
        "",
    ]
    for adapter in adapters:
        summary_lines.append(
            f"- `{adapter['adapter_id']}` — status: `{adapter['status']}` — external: {adapter['external_service_required']}"
        )

    summary_lines += [
        "",
        "## Shared Memory Current Priorities",
        "",
    ]
    if current_priorities:
        for item in current_priorities:
            summary_lines.append(f"- {item}")
    else:
        summary_lines.append("- (shared memory not found or empty)")

    try:
        audit_rel = str(AUDIT_LOG_PATH.relative_to(REPO_ROOT))
    except ValueError:
        audit_rel = str(AUDIT_LOG_PATH)

    summary_lines += [
        "",
        "## Audit Log",
        "",
        f"- Path: `{audit_rel}`",
        "",
        "## Run Artifacts",
        "",
        f"- Intents JSON: `{intents_path.relative_to(REPO_ROOT)}`",
        f"- Run dir: `{run_dir.relative_to(REPO_ROOT)}`",
    ]

    summary_md = "\n".join(summary_lines) + "\n"
    summary_path = run_dir / "action_intent_demo_summary.md"
    _ps_write(summary_path, summary_md)

    try:
        summary_rel = str(summary_path.relative_to(REPO_ROOT))
    except ValueError:
        summary_rel = str(summary_path)

    log_demo_completed(run_summary_path=summary_rel, stats=stats)

    return {
        "run_id": run_id,
        "stats": stats,
        "audit_path": audit_rel,
        "run_summary_path": summary_rel,
        "intents_path": str(intents_path.relative_to(REPO_ROOT)),
        "processed": processed,
    }


def main() -> int:
    result = run_demo()
    print(f"run_id:       {result['run_id']}")
    print(f"proposed:     {result['stats']['proposed']}")
    print(f"approved:     {result['stats']['approved']}")
    print(f"blocked:      {result['stats']['blocked']}")
    print(f"consumed:     {result['stats']['consumed']}")
    print(f"audit_path:   {result['audit_path']}")
    print(f"run_summary:  {result['run_summary_path']}")
    print("intent_outcomes:")
    for p in result["processed"]:
        print(f"  {p['agent']} -> {p['action_type']} -> {p['outcome']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
