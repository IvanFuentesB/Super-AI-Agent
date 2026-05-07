"""Native Ghoti ActionIntent + CapabilityAdapter contracts.

This module creates approval-bound proposed actions and a read-only adapter
status model. It never executes adapters, clicks, types, posts, purchases,
trades, files legal/tax items, or bypasses usage limits.

Status label: contract_created / approval_gated / not_external_adapter_wired
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .operator_loop import APPROVAL_INBOX_PATH
from .storage import RUNTIME_DATA_DIR, _write_text, get_allowed_workspace_root, runtime_data_lock

ACTION_INTENTS_PATH = RUNTIME_DATA_DIR / "action_intents.json"
ACTION_INTENT_AUDIT_PATH = RUNTIME_DATA_DIR / "action_intent_audit.json"
ACTION_AUDIT_LIMIT = 500

FORBIDDEN_ACTION_TYPES: frozenset[str] = frozenset(
    {
        "external_posting",
        "external_outreach",
        "autonomous_outreach",
        "purchase",
        "payment",
        "trade",
        "investment_execution",
        "legal_filing",
        "tax_filing",
        "credential_use_without_approval",
        "cap_bypass",
        "quota_evasion",
        "usage_limit_bypass",
        "fake_engagement",
        "fake_account_creation",
        "stealth_scraping",
        "unrestricted_filesystem_access",
        "install_third_party_tool",
        "clone_external_repo",
        "external_adapter_execution_without_approval",
    }
)

FORBIDDEN_TEXT_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bcap\s*bypass\b",
        r"\bquota\s*evasion\b",
        r"\busage\s*limit\s*bypass\b",
        r"\bfake\s+engagement\b",
        r"\bfake\s+account",
        r"\bphone\s*farm\b",
        r"\bautonomous\s+(outreach|posting|purchase|payment|trade|filing)\b",
        r"\bcredential\s+(theft|abuse)\b",
        r"\bstealth\s+scrap",
        r"\bweapon\b",
        r"\bguided\s+rocket\b",
    )
)

LOW_RISK_ACTION_TYPES: frozenset[str] = frozenset(
    {
        "summarize_local_file",
        "write_local_artifact",
        "update_compact_memory",
        "propose_next_step",
        "read_dashboard_state",
        "read_local_status",
    }
)


@dataclass
class ActionIntent:
    intent_id: str
    created_at_utc: str
    requested_by_agent: str
    adapter_id: str
    action_type: str
    target: str
    payload: dict
    payload_hash: str
    risk_level: str
    status: str
    requires_approval: bool
    approval_id: str | None = None
    approval_status: str = "not_created"
    consumed_at_utc: str | None = None
    consumed_by_adapter_id: str | None = None
    result_status: str = "not_executed"
    reason: str = ""
    errors: list[str] = field(default_factory=list)
    audit_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CapabilityAdapterDescriptor:
    adapter_id: str
    display_name: str
    status: str
    can_execute: bool
    supported_capabilities: list[str]
    allowed_actions: list[str]
    forbidden_actions: list[str]
    requires_human_approval: bool
    external_service_required: bool
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"{path.name}_invalid_shape")
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"{path.name}_invalid_item")
    return payload


def _write_json_list(path: Path, items: list[dict]) -> None:
    _write_text(path, json.dumps(items, indent=2, sort_keys=True) + "\n")


def payload_hash(payload: dict) -> str:
    encoded = json.dumps(payload or {}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _compact_payload_preview(payload: dict) -> dict:
    encoded = json.dumps(payload or {}, sort_keys=True)
    if len(encoded) <= 600:
        return payload or {}
    return {
        "preview": encoded[:600],
        "truncated": True,
        "original_bytes": len(encoded.encode("utf-8")),
    }


def _payload_text(action_type: str, target: str, payload: dict) -> str:
    return json.dumps(
        {"action_type": action_type, "target": target, "payload": payload or {}},
        sort_keys=True,
        default=str,
    )


def _is_path_outside_workspace(value: str) -> bool:
    candidate = value.strip()
    if not candidate:
        return False
    if not re.match(r"^[A-Za-z]:[\\/]", candidate) and not candidate.startswith("\\\\"):
        return False
    try:
        resolved = Path(candidate).resolve(strict=False)
        allowed_root = get_allowed_workspace_root().resolve(strict=False)
        return allowed_root not in [resolved, *resolved.parents]
    except OSError:
        return True


def classify_action(action_type: str, target: str, payload: dict) -> tuple[str, bool, str, list[str]]:
    normalized_type = action_type.strip().lower()
    text = _payload_text(normalized_type, target, payload)
    errors: list[str] = []

    if normalized_type in FORBIDDEN_ACTION_TYPES:
        errors.append("forbidden_action_type")
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(f"forbidden_text_pattern:{pattern.pattern}")
            break

    path_values = [target]
    if isinstance(payload, dict):
        for key in ("path", "file", "target_path", "source_path", "destination_path"):
            value = payload.get(key)
            if isinstance(value, str):
                path_values.append(value)
    if any(_is_path_outside_workspace(value) for value in path_values):
        errors.append("path_outside_allowed_workspace")

    if errors:
        return ("blocked", True, "blocked", errors)
    if normalized_type in LOW_RISK_ACTION_TYPES:
        return ("low", True, "approval_required", [])
    return ("medium", True, "approval_required", [])


def list_capability_adapters() -> list[dict]:
    adapters = [
        CapabilityAdapterDescriptor(
            adapter_id="native-demo-adapter",
            display_name="Native Demo Adapter (contracts only)",
            status="contract_ready_disabled",
            can_execute=False,
            supported_capabilities=["local_status", "local_artifact_planning"],
            allowed_actions=sorted(LOW_RISK_ACTION_TYPES),
            forbidden_actions=sorted(FORBIDDEN_ACTION_TYPES),
            requires_human_approval=True,
            external_service_required=False,
            notes="Repo-local descriptor for ActionIntent validation. It consumes approvals but does not execute actions.",
        ),
        CapabilityAdapterDescriptor(
            adapter_id="autobrowser-reference",
            display_name="AutoBrowser Reference Adapter",
            status="research_only",
            can_execute=False,
            supported_capabilities=["browser_control_candidate"],
            allowed_actions=[],
            forbidden_actions=sorted(FORBIDDEN_ACTION_TYPES),
            requires_human_approval=True,
            external_service_required=True,
            notes="External candidate only. Not cloned, installed, imported, called, or runtime-wired by this contract.",
        ),
        CapabilityAdapterDescriptor(
            adapter_id="ruflo-reference",
            display_name="RUFLO Reference Adapter",
            status="research_only_security_blocked",
            can_execute=False,
            supported_capabilities=["multi_agent_orchestration_candidate"],
            allowed_actions=[],
            forbidden_actions=sorted(FORBIDDEN_ACTION_TYPES),
            requires_human_approval=True,
            external_service_required=True,
            notes="Top-priority concept, but not trusted or wired. Requires isolated review before any runtime use.",
        ),
        CapabilityAdapterDescriptor(
            adapter_id="obscura-reference",
            display_name="Obscura Reference Adapter",
            status="research_only_tos_risk",
            can_execute=False,
            supported_capabilities=["headless_browser_candidate"],
            allowed_actions=[],
            forbidden_actions=sorted(FORBIDDEN_ACTION_TYPES),
            requires_human_approval=True,
            external_service_required=True,
            notes="Research only. Stealth/scraping capabilities carry TOS/legal risk and are not wired.",
        ),
        CapabilityAdapterDescriptor(
            adapter_id="cua-driver-reference",
            display_name="CUA Driver / TryCUA Reference Adapter",
            status="descriptor_only",
            can_execute=False,
            supported_capabilities=["observe_screen", "propose_click", "propose_type"],
            allowed_actions=[],
            forbidden_actions=sorted(FORBIDDEN_ACTION_TYPES),
            requires_human_approval=True,
            external_service_required=True,
            notes=(
                "Sandbox-only descriptor. risk_level=high. No live accounts, no runtime wiring, no execution. "
                "Canonical source: github.com/trycua/cua (MIT license; macOS/Apple Silicon only — "
                "incompatible with current Windows host). "
                "Supported action types: observe_screen, propose_click, propose_type — all disabled until sandbox approval. "
                "Sandbox profile: 23_configs/cua_sandbox_profile.example.json. "
                "Evaluation: 14_context/cua_trycua_exact_source_evaluation.md."
            ),
        ),
    ]
    return [adapter.to_dict() for adapter in adapters]


def _adapter_exists(adapter_id: str) -> bool:
    return any(adapter["adapter_id"] == adapter_id for adapter in list_capability_adapters())


def _append_audit_event_unlocked(event: dict) -> None:
    events = _read_json_list(ACTION_INTENT_AUDIT_PATH)
    events.insert(
        0,
        {
            "event_id": f"audit-{uuid4().hex}",
            "timestamp_utc": _utc_now(),
            **event,
        },
    )
    _write_json_list(ACTION_INTENT_AUDIT_PATH, events[:ACTION_AUDIT_LIMIT])


def _create_approval_item(intent: ActionIntent) -> dict:
    return {
        "id": f"approval-{uuid4().hex}",
        "timestamp_utc": _utc_now(),
        "source": "action_intent",
        "decision": "operator_approval_required",
        "proposed_action": (
            f"ActionIntent {intent.intent_id}: {intent.action_type} via "
            f"{intent.adapter_id}; target={intent.target or 'none'}; "
            f"payload_hash={intent.payload_hash[:16]}"
        ),
        "status": "pending",
        "reason": "",
        "operator_snapshot": {
            "action_intent_id": intent.intent_id,
            "adapter_id": intent.adapter_id,
            "action_type": intent.action_type,
            "target": intent.target,
            "payload_hash": intent.payload_hash,
            "payload_preview": _compact_payload_preview(intent.payload),
            "risk_level": intent.risk_level,
            "approval_bound": True,
            "payload_bound": True,
            "execution_mode": "manual_approval_required_no_execution",
            "autonomous_execution": False,
        },
        "action_intent_id": intent.intent_id,
        "adapter_id": intent.adapter_id,
        "action_type": intent.action_type,
        "payload_hash": intent.payload_hash,
    }


def create_action_intent(
    *,
    requested_by_agent: str,
    adapter_id: str,
    action_type: str,
    target: str = "",
    payload: dict | None = None,
    reason: str = "",
    audit_tags: list[str] | None = None,
) -> dict:
    payload = payload or {}
    action_type = action_type.strip().lower()
    adapter_id = adapter_id.strip()
    if not adapter_id:
        adapter_id = "native-demo-adapter"
    if not _adapter_exists(adapter_id):
        return {
            "status": "error",
            "reason": "unknown_adapter_id",
            "adapter_id": adapter_id,
            "known_adapters": [adapter["adapter_id"] for adapter in list_capability_adapters()],
        }

    risk_level, requires_approval, status, errors = classify_action(action_type, target, payload)
    intent = ActionIntent(
        intent_id=f"intent-{uuid4().hex}",
        created_at_utc=_utc_now(),
        requested_by_agent=requested_by_agent.strip() or "operator",
        adapter_id=adapter_id,
        action_type=action_type,
        target=target,
        payload=payload,
        payload_hash=payload_hash(payload),
        risk_level=risk_level,
        status=status,
        requires_approval=requires_approval,
        approval_status="not_created" if status == "blocked" else "pending",
        result_status="blocked" if status == "blocked" else "not_executed",
        reason=reason,
        errors=errors,
        audit_tags=list(audit_tags or []),
    )

    approval_item: dict | None = None
    try:
        with runtime_data_lock():
            intents = _read_json_list(ACTION_INTENTS_PATH)
            if intent.status != "blocked":
                approval_items = _read_json_list(APPROVAL_INBOX_PATH)
                approval_item = _create_approval_item(intent)
                approval_items.append(approval_item)
                intent.approval_id = approval_item["id"]
                _write_json_list(APPROVAL_INBOX_PATH, approval_items)
            intents.insert(0, intent.to_dict())
            _write_json_list(ACTION_INTENTS_PATH, intents[:ACTION_AUDIT_LIMIT])
            _append_audit_event_unlocked(
                {
                    "event": "action_intent_created",
                    "intent_id": intent.intent_id,
                    "approval_id": intent.approval_id,
                    "status": intent.status,
                    "risk_level": intent.risk_level,
                    "payload_hash": intent.payload_hash,
                    "execution_performed": False,
                }
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "status": "error",
            "reason": f"action_intent_create_failed: {exc}",
            "intent": intent.to_dict(),
        }

    return {
        "status": "ok" if intent.status != "blocked" else "blocked",
        "intent": intent.to_dict(),
        "approval_item": approval_item,
        "approval_bound": intent.approval_id is not None,
        "payload_bound": True,
        "execution_performed": False,
    }


def _find_intent_unlocked(intent_id: str) -> tuple[list[dict], dict | None]:
    intents = _read_json_list(ACTION_INTENTS_PATH)
    for intent in intents:
        if intent.get("intent_id") == intent_id:
            return intents, intent
    return intents, None


def _find_approval_item_unlocked(approval_id: str) -> dict | None:
    if not approval_id:
        return None
    for item in _read_json_list(APPROVAL_INBOX_PATH):
        if item.get("id") == approval_id:
            return item
    return None


def consume_action_intent(
    *,
    intent_id: str,
    adapter_id: str,
    action_type: str,
    payload: dict | None = None,
) -> dict:
    payload = payload or {}
    attempted_hash = payload_hash(payload)
    event_base = {
        "event": "action_intent_consume_attempted",
        "intent_id": intent_id,
        "adapter_id": adapter_id,
        "action_type": action_type,
        "attempted_payload_hash": attempted_hash,
        "execution_performed": False,
    }
    try:
        with runtime_data_lock():
            intents, intent = _find_intent_unlocked(intent_id)
            if intent is None:
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "intent_not_found"})
                return {"status": "error", "reason": "intent_not_found", "execution_performed": False}
            if intent.get("consumed_at_utc"):
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "intent_already_consumed"})
                return {
                    "status": "error",
                    "reason": "intent_already_consumed",
                    "intent": intent,
                    "execution_performed": False,
                }
            if intent.get("status") == "blocked":
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "intent_blocked"})
                return {"status": "error", "reason": "intent_blocked", "intent": intent, "execution_performed": False}
            if adapter_id != intent.get("adapter_id"):
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "adapter_id_mismatch"})
                return {"status": "error", "reason": "adapter_id_mismatch", "intent": intent, "execution_performed": False}
            if action_type.strip().lower() != intent.get("action_type"):
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "action_type_mismatch"})
                return {"status": "error", "reason": "action_type_mismatch", "intent": intent, "execution_performed": False}
            if attempted_hash != intent.get("payload_hash"):
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": "payload_hash_mismatch"})
                return {"status": "error", "reason": "payload_hash_mismatch", "intent": intent, "execution_performed": False}

            approval_id = str(intent.get("approval_id") or "")
            approval_item = _find_approval_item_unlocked(approval_id)
            if not approval_item or approval_item.get("status") != "approved":
                reason = "approval_not_approved"
                intent["approval_status"] = str(approval_item.get("status", "missing") if approval_item else "missing")
                _write_json_list(ACTION_INTENTS_PATH, intents)
                _append_audit_event_unlocked({**event_base, "status": "rejected", "reason": reason})
                return {"status": "error", "reason": reason, "intent": intent, "execution_performed": False}

            intent["status"] = "approval_consumed"
            intent["approval_status"] = "approved"
            intent["consumed_at_utc"] = _utc_now()
            intent["consumed_by_adapter_id"] = adapter_id
            intent["result_status"] = "manual_adapter_not_wired"
            _write_json_list(ACTION_INTENTS_PATH, intents)
            _append_audit_event_unlocked(
                {
                    **event_base,
                    "status": "accepted",
                    "reason": "approval_and_payload_matched",
                    "approval_id": approval_id,
                }
            )
            return {
                "status": "ok",
                "reason": "approval_and_payload_matched_no_execution_performed",
                "intent": intent,
                "approval_item": approval_item,
                "approval_bound": True,
                "payload_bound": True,
                "execution_performed": False,
                "next_required_step": "manual adapter implementation remains disabled",
            }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "error", "reason": f"action_intent_consume_failed: {exc}", "execution_performed": False}


def get_action_intent_read_model(limit: int = 20) -> dict:
    limit = max(1, min(int(limit or 20), 100))
    try:
        with runtime_data_lock():
            intents = _read_json_list(ACTION_INTENTS_PATH)
            audit = _read_json_list(ACTION_INTENT_AUDIT_PATH)
    except FileNotFoundError:
        intents = []
        audit = []
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "error", "reason": f"action_intent_read_failed: {exc}"}

    status_counts: dict[str, int] = {}
    for intent in intents:
        status = str(intent.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1

    adapters = list_capability_adapters()
    return {
        "status": "ok",
        "generated_at_utc": _utc_now(),
        "summary": {
            "intent_count": len(intents),
            "status_counts": status_counts,
            "audit_event_count": len(audit),
            "adapter_count": len(adapters),
            "runtime_wired_adapters": 0,
            "execution_performed": False,
            "approval_bound": True,
            "payload_bound": True,
            "state_paths": {
                "action_intents_path": str(ACTION_INTENTS_PATH),
                "action_intent_audit_path": str(ACTION_INTENT_AUDIT_PATH),
                "approval_inbox_path": str(APPROVAL_INBOX_PATH),
            },
        },
        "intents": intents[:limit],
        "adapters": adapters,
        "audit": audit[:limit],
        "honest_status": {
            "runtime_wired": False,
            "external_adapters_wired": False,
            "autonomous_execution": False,
            "approval_required_before_consumption": True,
            "payload_hash_must_match": True,
        },
    }
