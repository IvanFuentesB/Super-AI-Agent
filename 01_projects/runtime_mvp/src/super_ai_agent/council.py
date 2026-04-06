from __future__ import annotations

import json
from dataclasses import dataclass

from .providers import get_provider_profile
from .storage import get_project_root

COUNCIL_POLICY_PATH = get_project_root().parents[1] / "23_configs" / "council_policy.example.json"


@dataclass
class CouncilPlan:
    goal_type: str
    lead_provider: str
    reviewer_provider: str | None
    local_fallback_provider: str
    reasoning_summary: str
    notes: list[str]


def _load_policy() -> dict:
    with COUNCIL_POLICY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_goal(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def build_council_plan(
    goal_type: str,
    privacy_preference: str,
    speed_preference: str,
    require_reviewer: bool,
) -> CouncilPlan:
    policy = _load_policy()
    goal_key = _normalize_goal(goal_type)
    route = policy.get("routing_examples", {}).get(goal_key, {})
    local_fallback_provider = policy.get("local_fallback_provider", "gemma_local")

    notes: list[str] = []
    privacy_key = privacy_preference.strip().lower()
    speed_key = speed_preference.strip().lower()

    if privacy_key in {"local", "strict", "sensitive"}:
        lead_provider = local_fallback_provider
        notes.append("Privacy preference pushes the plan toward the local fallback profile.")
    else:
        lead_provider = route.get("lead_provider", "chatgpt")

    if speed_key in {"fast", "quick"} and privacy_key in {"local", "strict", "sensitive", "local_preferred"}:
        lead_provider = local_fallback_provider
        notes.append("Fast local preference keeps the lead provider local.")
    elif speed_key in {"fast", "quick"} and lead_provider == "claude":
        lead_provider = "chatgpt"
        notes.append("Fast preference nudged the lead provider toward a quicker general profile.")

    reviewer_provider: str | None = None
    if require_reviewer:
        if privacy_key in {"local", "strict", "sensitive"}:
            notes.append("Reviewer omitted because the current example policy has no separate strict-local reviewer.")
        else:
            reviewer_provider = route.get("reviewer_provider", "claude")

    lead_profile = get_provider_profile(lead_provider)
    fallback_profile = get_provider_profile(local_fallback_provider)
    reasoning_parts = [
        f"Lead provider: {lead_profile.display_name} for goal type '{goal_key}'.",
        f"Local fallback: {fallback_profile.display_name}.",
    ]

    if reviewer_provider:
        reviewer_profile = get_provider_profile(reviewer_provider)
        reasoning_parts.append(f"Reviewer provider: {reviewer_profile.display_name}.")
    else:
        reasoning_parts.append("No reviewer provider selected.")

    policy_notes = policy.get("notes")
    if isinstance(policy_notes, str) and policy_notes:
        notes.append(policy_notes)

    return CouncilPlan(
        goal_type=goal_key,
        lead_provider=lead_provider,
        reviewer_provider=reviewer_provider,
        local_fallback_provider=local_fallback_provider,
        reasoning_summary=" ".join(reasoning_parts),
        notes=notes,
    )
