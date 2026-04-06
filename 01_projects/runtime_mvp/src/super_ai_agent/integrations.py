from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrationStatus:
    integration_id: str
    mode: str
    summary: str


def list_supported_integrations() -> list[IntegrationStatus]:
    return [
        IntegrationStatus(
            integration_id="github",
            mode="live_read",
            summary="Read-only local repo and optional GitHub CLI-backed project checks.",
        ),
        IntegrationStatus(
            integration_id="mail",
            mode="planning_only",
            summary="Inbox triage and reply planning only.",
        ),
        IntegrationStatus(
            integration_id="notion",
            mode="planning_only",
            summary="Workspace and page update planning only.",
        ),
        IntegrationStatus(
            integration_id="linkedin",
            mode="planned_only",
            summary="Future owned-account planning path only.",
        ),
    ]


def get_integration_status(integration_id: str) -> IntegrationStatus:
    for item in list_supported_integrations():
        if item.integration_id == integration_id:
            return item
    raise ValueError(f"Integration not found: {integration_id}")
