from __future__ import annotations

import json
from dataclasses import dataclass

from .storage import get_project_root

CONFIG_PATH = get_project_root().parents[1] / "23_configs" / "provider_profiles.example.json"


@dataclass
class ProviderProfile:
    provider_id: str
    display_name: str
    role_strengths: list[str]
    good_for: list[str]
    weak_for: list[str]
    privacy_mode: str
    speed_bias: str
    cost_bias: str
    notes: str

    @classmethod
    def from_dict(cls, data: dict) -> "ProviderProfile":
        return cls(**data)


def _load_provider_payload() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_provider_profiles() -> list[ProviderProfile]:
    payload = _load_provider_payload()
    providers = payload.get("providers", [])
    return [ProviderProfile.from_dict(item) for item in providers]


def get_provider_profile(provider_id: str) -> ProviderProfile:
    for profile in list_provider_profiles():
        if profile.provider_id == provider_id:
            return profile
    raise ValueError(f"Provider profile not found: {provider_id}")
