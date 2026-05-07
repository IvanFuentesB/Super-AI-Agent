from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

from .storage import ensure_runtime_files, get_project_root, get_runtime_data_dir

REPO_ROOT = get_project_root().parents[1]
CONFIG_PATH = REPO_ROOT / "23_configs" / "brain_provider.example.json"
RUNTIME_CONFIG_PATH = get_runtime_data_dir() / "brain_config.json"
RUNTIME_STATE_PATH = get_runtime_data_dir() / "brain_state.json"

DEFAULT_BRAIN_CONFIG = {
    "active_provider": "gemma_local",
    "active_model": "gemma3:4b",
    "ollama_base_url": "http://127.0.0.1:11434",
    "request_timeout_seconds": 60,
    "notes": "Gemma local is the default local-first brain target, but a pulled Ollama model is still required before live inference works.",
}


@dataclass
class BrainConfig:
    active_provider: str
    active_model: str
    ollama_base_url: str
    request_timeout_seconds: int
    notes: str = ""
    config_source: str = "default"


@dataclass
class BrainRuntimeState:
    last_call_status: str = "never_called"
    last_called_at: str = ""
    last_provider: str = ""
    last_model: str = ""
    last_source: str = ""
    last_task_id: str = ""
    last_error: str = ""
    last_response_preview: str = ""
    last_inference_used: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BrainRuntimeState":
        return cls(
            last_call_status=data.get("last_call_status", "never_called"),
            last_called_at=data.get("last_called_at", ""),
            last_provider=data.get("last_provider", ""),
            last_model=data.get("last_model", ""),
            last_source=data.get("last_source", ""),
            last_task_id=data.get("last_task_id", ""),
            last_error=data.get("last_error", ""),
            last_response_preview=data.get("last_response_preview", ""),
            last_inference_used=bool(data.get("last_inference_used", False)),
        )


@dataclass
class BrainStatus:
    active_provider: str
    active_model: str
    config_source: str
    ollama_base_url: str
    provider_ready: bool
    ollama_available: bool
    ollama_version: str
    installed_models: list[str]
    model_installed: bool
    inference_ready: bool
    live_call_path: str
    notes: list[str]
    last_call_status: str
    last_called_at: str
    last_call_source: str
    last_task_id: str
    last_error: str
    last_response_preview: str


class BrainInferenceError(RuntimeError):
    pass


def _read_json_object(path: Path, default: dict) -> dict:
    ensure_runtime_files()
    if not path.exists():
        return dict(default)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return dict(default)
    merged = dict(default)
    merged.update(payload)
    return merged


def _write_json_object(path: Path, payload: dict) -> None:
    ensure_runtime_files()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_ollama_list(stdout: str) -> list[str]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return []
    models: list[str] = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0].strip())
    return models


def load_brain_config() -> BrainConfig:
    payload = dict(DEFAULT_BRAIN_CONFIG)
    config_source = "default"

    if CONFIG_PATH.exists():
        payload.update(_read_json_object(CONFIG_PATH, DEFAULT_BRAIN_CONFIG))
        config_source = "example_config"

    if RUNTIME_CONFIG_PATH.exists():
        runtime_override = _read_json_object(RUNTIME_CONFIG_PATH, {})
        runtime_override = {
            key: value
            for key, value in runtime_override.items()
            if value not in ("", None, {})
        }
        if runtime_override:
            payload.update(runtime_override)
            config_source = "runtime_override"

    env_provider = os.environ.get("SUPER_AGENT_BRAIN_PROVIDER", "").strip()
    env_model = os.environ.get("SUPER_AGENT_BRAIN_MODEL", "").strip()
    env_url = os.environ.get("SUPER_AGENT_OLLAMA_BASE_URL", "").strip()
    if env_provider:
        payload["active_provider"] = env_provider
        config_source = "environment_override"
    if env_model:
        payload["active_model"] = env_model
        config_source = "environment_override"
    if env_url:
        payload["ollama_base_url"] = env_url
        config_source = "environment_override"

    return BrainConfig(
        active_provider=str(payload.get("active_provider", DEFAULT_BRAIN_CONFIG["active_provider"])).strip(),
        active_model=str(payload.get("active_model", DEFAULT_BRAIN_CONFIG["active_model"])).strip(),
        ollama_base_url=str(payload.get("ollama_base_url", DEFAULT_BRAIN_CONFIG["ollama_base_url"])).strip(),
        request_timeout_seconds=max(int(payload.get("request_timeout_seconds", 60) or 60), 5),
        notes=str(payload.get("notes", "") or ""),
        config_source=config_source,
    )


def save_brain_config_override(
    *,
    provider: str,
    model: str,
    ollama_base_url: str | None = None,
) -> BrainConfig:
    config = load_brain_config()
    payload = {
        "active_provider": provider.strip(),
        "active_model": model.strip(),
        "ollama_base_url": (ollama_base_url or config.ollama_base_url).strip(),
        "request_timeout_seconds": config.request_timeout_seconds,
        "notes": config.notes,
    }
    _write_json_object(RUNTIME_CONFIG_PATH, payload)
    return load_brain_config()


def get_brain_runtime_state() -> BrainRuntimeState:
    default = BrainRuntimeState().to_dict()
    return BrainRuntimeState.from_dict(_read_json_object(RUNTIME_STATE_PATH, default))


def record_brain_runtime_state(state: BrainRuntimeState) -> None:
    _write_json_object(RUNTIME_STATE_PATH, state.to_dict())


def _detect_ollama() -> tuple[bool, str, list[str]]:
    try:
        version_result = subprocess.run(
            ["ollama", "--version"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False, "", []

    version_text = (version_result.stdout or version_result.stderr or "").strip()
    if version_result.returncode != 0:
        return False, version_text, []

    list_result = subprocess.run(
        ["ollama", "list"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    installed_models = _parse_ollama_list(list_result.stdout or "")
    return True, version_text, installed_models


def get_brain_status() -> BrainStatus:
    config = load_brain_config()
    runtime_state = get_brain_runtime_state()
    ollama_available, ollama_version, installed_models = _detect_ollama()
    provider_ready = config.active_provider == "gemma_local"
    model_installed = config.active_model in installed_models
    inference_ready = provider_ready and ollama_available and model_installed
    notes: list[str] = []

    if config.notes:
        notes.append(config.notes)
    if config.active_provider != "gemma_local":
        notes.append(
            "Only gemma_local is wired for live inference right now. Other providers are still profile/planning entries."
        )
    if not ollama_available:
        notes.append("Ollama is not available on PATH, so the local Gemma provider cannot run yet.")
    elif not installed_models:
        notes.append("Ollama is installed, but no local models are currently pulled.")
    elif not model_installed:
        notes.append(
            f"Configured model {config.active_model} is not in the local Ollama list yet."
        )

    return BrainStatus(
        active_provider=config.active_provider,
        active_model=config.active_model,
        config_source=config.config_source,
        ollama_base_url=config.ollama_base_url,
        provider_ready=provider_ready,
        ollama_available=ollama_available,
        ollama_version=ollama_version,
        installed_models=installed_models,
        model_installed=model_installed,
        inference_ready=inference_ready,
        live_call_path="cli -> super_ai_agent.brain -> Ollama /api/generate",
        notes=notes,
        last_call_status=runtime_state.last_call_status,
        last_called_at=runtime_state.last_called_at,
        last_call_source=runtime_state.last_source,
        last_task_id=runtime_state.last_task_id,
        last_error=runtime_state.last_error,
        last_response_preview=runtime_state.last_response_preview,
    )


def run_brain_inference(prompt: str, *, source: str = "cli", task_id: str = "") -> str:
    config = load_brain_config()
    status = get_brain_status()
    runtime_state = get_brain_runtime_state()
    runtime_state.last_called_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    runtime_state.last_provider = config.active_provider
    runtime_state.last_model = config.active_model
    runtime_state.last_source = source
    runtime_state.last_task_id = task_id
    runtime_state.last_inference_used = False
    runtime_state.last_error = ""
    runtime_state.last_response_preview = ""

    if config.active_provider != "gemma_local":
        runtime_state.last_call_status = "provider_not_implemented"
        runtime_state.last_error = (
            f"Provider {config.active_provider} is configured, but only gemma_local is wired for live inference."
        )
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error)

    if not status.ollama_available:
        runtime_state.last_call_status = "ollama_unavailable"
        runtime_state.last_error = "Ollama is not available on PATH for the local Gemma provider."
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error)

    if not status.model_installed:
        runtime_state.last_call_status = "model_missing"
        runtime_state.last_error = (
            f"Configured Ollama model {config.active_model} is not installed locally yet."
        )
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error)

    payload = json.dumps(
        {
            "model": config.active_model,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")
    request_url = config.ollama_base_url.rstrip("/") + "/api/generate"
    http_request = request.Request(
        request_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=config.request_timeout_seconds) as response:
            raw_payload = response.read().decode("utf-8")
        response_payload = json.loads(raw_payload)
        result_text = str(response_payload.get("response", "") or "").strip()
        if not result_text:
            raise BrainInferenceError("Ollama returned no response text.")
    except error.HTTPError as exc:
        runtime_state.last_call_status = "failed"
        runtime_state.last_error = f"Ollama HTTP {exc.code}: {exc.reason}"
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error) from exc
    except error.URLError as exc:
        runtime_state.last_call_status = "failed"
        runtime_state.last_error = f"Ollama connection failed: {exc.reason}"
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error) from exc
    except json.JSONDecodeError as exc:
        runtime_state.last_call_status = "failed"
        runtime_state.last_error = "Ollama returned invalid JSON."
        record_brain_runtime_state(runtime_state)
        raise BrainInferenceError(runtime_state.last_error) from exc

    runtime_state.last_call_status = "succeeded"
    runtime_state.last_inference_used = True
    runtime_state.last_response_preview = result_text[:240]
    record_brain_runtime_state(runtime_state)
    return result_text
