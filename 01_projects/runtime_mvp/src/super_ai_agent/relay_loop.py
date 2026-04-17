from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .storage import (
    get_allowed_workspace_root,
    get_project_root,
    read_relay_loop_state_object,
    runtime_data_lock,
    write_relay_loop_state_object,
)

RELAY_STATES = {
    "idle",
    "copying_from_chatgpt",
    "switching_to_codex",
    "setting_codex_preset",
    "pasting_into_codex",
    "submitting_to_codex",
    "waiting_for_codex",
    "copying_from_codex",
    "switching_to_chatgpt",
    "pasting_into_chatgpt",
    "blocked",
    "waiting_for_usage_reset",
    "completed",
}
RELAY_TARGET_ALIASES = {"chatgpt", "codex"}
RELAY_CODEX_EXECUTION_STATUSES = {
    "unknown",
    "running",
    "finished",
    "blocked",
    "usage_exhausted",
}
PRESET_APPLICATION_STATUSES = {
    "stored_only",
    "pending_manual_application",
    "applied",
    "blocked",
}
KNOWN_DIALOG_STATUSES = {
    "none",
    "blocked_unrecognized",
    "allowlisted_dialog_ready",
    "allowlisted_dialog_handled",
}


@dataclass
class RelayTargetBinding:
    alias: str
    candidate_id: str
    title: str
    binding_status: str
    last_checked_at: str
    last_error: str


@dataclass
class RelayLoopStatus:
    relay_state: str
    current_step: str
    source_target_alias: str
    source_target_candidate_id: str
    source_target_title: str
    source_target_status: str
    destination_target_alias: str
    destination_target_candidate_id: str
    destination_target_title: str
    destination_target_status: str
    codex_mode_preset: str
    codex_reasoning_preset: str
    preset_application_status: str
    codex_execution_status: str
    next_usage_reset_at: str
    resume_after_usage_reset: bool
    waiting_reason: str
    blocked_reason: str
    last_payload_preview: str
    last_result_preview: str
    last_completion_status: str
    last_transition_at: str
    last_updated_at: str
    last_used_task_id: str
    last_known_dialog_status: str
    last_known_dialog_note: str
    source_binding: RelayTargetBinding
    destination_binding: RelayTargetBinding
    notes: list[str]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _preview(text: str, limit: int = 160) -> str:
    normalized = " ".join((text or "").split())
    if not normalized:
        return ""
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


def _normalize_alias(value: str, *, label: str = "target") -> str:
    alias = (value or "").strip().lower()
    if alias not in RELAY_TARGET_ALIASES:
        raise ValueError(f"{label} alias must be one of: chatgpt, codex")
    return alias


def _normalize_state(value: str) -> str:
    state = (value or "").strip().lower()
    if state not in RELAY_STATES:
        raise ValueError("relay state must be one of: " + ", ".join(sorted(RELAY_STATES)))
    return state


def _normalize_codex_execution_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in RELAY_CODEX_EXECUTION_STATUSES:
        raise ValueError(
            "codex execution status must be one of: "
            + ", ".join(sorted(RELAY_CODEX_EXECUTION_STATUSES))
        )
    return normalized


def _normalize_preset_application_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in PRESET_APPLICATION_STATUSES:
        raise ValueError(
            "preset application status must be one of: "
            + ", ".join(sorted(PRESET_APPLICATION_STATUSES))
        )
    return normalized


def _normalize_dialog_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in KNOWN_DIALOG_STATUSES:
        raise ValueError(
            "dialog status must be one of: "
            + ", ".join(sorted(KNOWN_DIALOG_STATUSES))
        )
    return normalized


def _desktop_bridge_script_path() -> Path:
    return (
        get_project_root().parents[1]
        / "01_projects"
        / "desktop_playground"
        / "desktop_bridge_actions.ps1"
    ).resolve(strict=False)


def _parse_key_value_output(output: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    values: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    current_section = ""
    for raw_line in (output or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and " " not in line[:-1]:
            current_section = line[:-1]
            sections.setdefault(current_section, [])
            continue
        if line.startswith("- "):
            if current_section:
                sections.setdefault(current_section, []).append(line[2:].strip())
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            values[key.strip()] = value.strip()
            current_section = ""
    return values, sections


def _list_visible_handoff_targets() -> list[dict]:
    script_path = _desktop_bridge_script_path()
    if not script_path.is_file():
        return []
    command = [
        "powershell.exe",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-Action",
        "list_windows",
        "-AllowedRoot",
        str(get_allowed_workspace_root()),
    ]
    result = subprocess.run(
        command,
        cwd=get_allowed_workspace_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(
        part.strip()
        for part in ((result.stdout or "").strip(), (result.stderr or "").strip())
        if part.strip()
    ).strip()
    values, sections = _parse_key_value_output(output)
    if result.returncode != 0 or values.get("status") == "blocked":
        return []
    targets: list[dict] = []
    for entry in sections.get("windows", []):
        parts = [segment.strip() for segment in entry.split(" | ") if segment.strip()]
        if len(parts) < 3:
            continue
        alias = (parts[0] or "").strip().lower()
        if alias not in RELAY_TARGET_ALIASES:
            continue
        targets.append(
            {
                "alias": alias,
                "title": parts[1] or "",
                "candidate_id": (parts[2] or "").strip().lower(),
            }
        )
    return targets


def _default_binding(alias: str) -> dict:
    return {
        "alias": alias,
        "candidate_id": "",
        "title": "",
        "binding_status": "not_bound",
        "last_checked_at": "",
        "last_error": "",
    }


def _default_state() -> dict:
    now = _now()
    return {
        "relay_state": "idle",
        "current_step": "idle",
        "source_target_alias": "chatgpt",
        "source_target_candidate_id": "",
        "source_target_title": "",
        "destination_target_alias": "codex",
        "destination_target_candidate_id": "",
        "destination_target_title": "",
        "codex_mode_preset": "Implementing new feature",
        "codex_reasoning_preset": "Medium",
        "preset_application_status": "stored_only",
        "codex_execution_status": "unknown",
        "next_usage_reset_at": "",
        "resume_after_usage_reset": False,
        "waiting_reason": "",
        "blocked_reason": "",
        "last_payload_preview": "",
        "last_result_preview": "",
        "last_completion_status": "not_started",
        "last_transition_at": now,
        "last_updated_at": now,
        "last_used_task_id": "",
        "last_known_dialog_status": "none",
        "last_known_dialog_note": "",
        "saved_targets": {
            "chatgpt": _default_binding("chatgpt"),
            "codex": _default_binding("codex"),
        },
    }


def _merge_with_defaults(payload: dict | None) -> dict:
    state = _default_state()
    if isinstance(payload, dict):
        state.update({key: value for key, value in payload.items() if key != "saved_targets"})
        saved_targets = payload.get("saved_targets", {})
        if isinstance(saved_targets, dict):
            merged_targets = {}
            for alias in RELAY_TARGET_ALIASES:
                merged = _default_binding(alias)
                candidate = saved_targets.get(alias, {})
                if isinstance(candidate, dict):
                    merged.update(candidate)
                merged["alias"] = alias
                merged_targets[alias] = merged
            state["saved_targets"] = merged_targets
    return state


def _validated_binding(binding: dict, visible_targets: list[dict]) -> RelayTargetBinding:
    alias = (binding.get("alias") or "").strip().lower()
    candidate_id = (binding.get("candidate_id") or "").strip().lower()
    title = str(binding.get("title") or "")
    checked_at = _now()
    if alias not in RELAY_TARGET_ALIASES or not candidate_id:
        return RelayTargetBinding(alias or "unknown", candidate_id, title, "not_bound", checked_at, "No saved candidate is stored yet.")
    matches = [
        item
        for item in visible_targets
        if item.get("alias") == alias and item.get("candidate_id") == candidate_id
    ]
    if len(matches) == 1:
        return RelayTargetBinding(alias, candidate_id, str(matches[0].get("title") or title), "ready", checked_at, "")
    same_alias_matches = [item for item in visible_targets if item.get("alias") == alias]
    if same_alias_matches:
        return RelayTargetBinding(alias, candidate_id, title, "stale", checked_at, f"Saved candidate {candidate_id} is no longer visible for {alias}.")
    return RelayTargetBinding(alias, candidate_id, title, "missing", checked_at, f"No visible allowlisted {alias} target is available right now.")


def _write_memory_files(state: dict) -> None:
    compact_root = get_project_root().parents[1] / "14_context" / "compact_memory"
    compact_root.mkdir(parents=True, exist_ok=True)
    relay_state = str(state.get("relay_state", "idle"))
    current_step = str(state.get("current_step", "idle"))
    source = str(state.get("source_target_alias", "chatgpt"))
    destination = str(state.get("destination_target_alias", "codex"))
    mode = str(state.get("codex_mode_preset", "Implementing new feature"))
    reasoning = str(state.get("codex_reasoning_preset", "Medium"))
    reset_at = str(state.get("next_usage_reset_at") or "unknown")
    waiting_reason = str(state.get("waiting_reason") or "none")
    blocked_reason = str(state.get("blocked_reason") or "none")
    payload_preview = str(state.get("last_payload_preview") or "none")
    result_preview = str(state.get("last_result_preview") or "none")
    files = {
        "current_working_summary.md": "\n".join([
            "# Current Working Summary",
            "",
            f"- Relay state: `{relay_state}`",
            f"- Current step: `{current_step}`",
            f"- Source target: `{source}`",
            f"- Destination target: `{destination}`",
            f"- Codex preset: `{mode}` / `{reasoning}`",
            f"- Last payload preview: {payload_preview}",
            f"- Last result preview: {result_preview}",
        ]) + "\n",
        "current_loop_state.md": "\n".join([
            "# Current Loop State",
            "",
            f"- relay_state: `{relay_state}`",
            f"- current_step: `{current_step}`",
            f"- codex_execution_status: `{state.get('codex_execution_status', 'unknown')}`",
            f"- preset_application_status: `{state.get('preset_application_status', 'stored_only')}`",
            f"- waiting_reason: {waiting_reason}",
            f"- blocked_reason: {blocked_reason}",
            f"- next_usage_reset_at: {reset_at}",
        ]) + "\n",
        "compact_build_context.md": "\n".join([
            "# Compact Build Context",
            "",
            "- Goal: supervised ChatGPT ↔ Codex relay foundation with smaller context carry-over.",
            "- Keep safe blocks on stale or ambiguous targets.",
            "- Store preset truth even when UI preset application is not automated yet.",
            "- Prefer compact reusable summaries over large pass-by-pass narratives.",
        ]) + "\n",
        "last_successful_step.md": "\n".join([
            "# Last Successful Step",
            "",
            f"- status: `{state.get('last_completion_status', 'not_started')}`",
            f"- last_transition_at: `{state.get('last_transition_at') or 'unknown'}`",
            f"- payload_preview: {payload_preview}",
            f"- result_preview: {result_preview}",
        ]) + "\n",
        "next_exact_step.md": "\n".join([
            "# Next Exact Step",
            "",
            f"- Current relay state says the next operator-visible move is: `{current_step}`",
            "- If target bindings are not `ready`, rebind ChatGPT and Codex before any paste or send action.",
            f"- If usage reset time is known, wait until `{reset_at}` before resuming Codex work.",
        ]) + "\n",
        "blocker_state.md": "\n".join([
            "# Blocker State",
            "",
            f"- blocked_reason: {blocked_reason}",
            f"- waiting_reason: {waiting_reason}",
            f"- dialog_status: `{state.get('last_known_dialog_status', 'none')}`",
            f"- dialog_note: {state.get('last_known_dialog_note') or 'none'}",
        ]) + "\n",
        "operator_handoff_summary.md": "\n".join([
            "# Operator Handoff Summary",
            "",
            f"- Relay step: `{current_step}`",
            f"- Source -> destination: `{source}` -> `{destination}`",
            f"- Stored Codex preset: `{mode}` / `{reasoning}`",
            f"- Safe block reason: {blocked_reason}",
            f"- Resume time if known: {reset_at}",
        ]) + "\n",
    }
    for name, content in files.items():
        (compact_root / name).write_text(content, encoding='utf-8')


def get_relay_loop_status() -> RelayLoopStatus:
    state = _merge_with_defaults(read_relay_loop_state_object())
    visible_targets = _list_visible_handoff_targets()
    source_binding = _validated_binding(
        state['saved_targets'].get(state.get('source_target_alias', 'chatgpt'), {}),
        visible_targets,
    )
    destination_binding = _validated_binding(
        state['saved_targets'].get(state.get('destination_target_alias', 'codex'), {}),
        visible_targets,
    )
    notes = [
        'Relay-loop state is a supervised local runtime scaffold, not a full autonomous loop.',
        'Saved targets must stay exact-candidate matches or the relay should block before any paste or send step.',
        'Codex preset values are stored truthfully even when UI preset application still needs manual confirmation.',
    ]
    if source_binding.binding_status != 'ready' or destination_binding.binding_status != 'ready':
        notes.append('One or more saved relay targets are not ready; rebind before trusting a relay paste or send path.')
    if (state.get('next_usage_reset_at') or '').strip():
        notes.append('A next usage reset time is stored for future resume reminders.')
    return RelayLoopStatus(
        relay_state=str(state.get('relay_state', 'idle')),
        current_step=str(state.get('current_step', 'idle')),
        source_target_alias=str(state.get('source_target_alias', 'chatgpt')),
        source_target_candidate_id=str(state.get('source_target_candidate_id', '')),
        source_target_title=str(state.get('source_target_title', '')),
        source_target_status=source_binding.binding_status,
        destination_target_alias=str(state.get('destination_target_alias', 'codex')),
        destination_target_candidate_id=str(state.get('destination_target_candidate_id', '')),
        destination_target_title=str(state.get('destination_target_title', '')),
        destination_target_status=destination_binding.binding_status,
        codex_mode_preset=str(state.get('codex_mode_preset', 'Implementing new feature')),
        codex_reasoning_preset=str(state.get('codex_reasoning_preset', 'Medium')),
        preset_application_status=str(state.get('preset_application_status', 'stored_only')),
        codex_execution_status=str(state.get('codex_execution_status', 'unknown')),
        next_usage_reset_at=str(state.get('next_usage_reset_at', '')),
        resume_after_usage_reset=bool(state.get('resume_after_usage_reset', False)),
        waiting_reason=str(state.get('waiting_reason', '')),
        blocked_reason=str(state.get('blocked_reason', '')),
        last_payload_preview=str(state.get('last_payload_preview', '')),
        last_result_preview=str(state.get('last_result_preview', '')),
        last_completion_status=str(state.get('last_completion_status', 'not_started')),
        last_transition_at=str(state.get('last_transition_at', '')),
        last_updated_at=str(state.get('last_updated_at', '')),
        last_used_task_id=str(state.get('last_used_task_id', '')),
        last_known_dialog_status=str(state.get('last_known_dialog_status', 'none')),
        last_known_dialog_note=str(state.get('last_known_dialog_note', '')),
        source_binding=source_binding,
        destination_binding=destination_binding,
        notes=notes,
    )


def update_relay_loop_state(*, relay_state: str | None = None, current_step: str | None = None, source_alias: str | None = None, destination_alias: str | None = None, waiting_reason: str | None = None, blocked_reason: str | None = None, last_payload_preview: str | None = None, last_result_preview: str | None = None, codex_execution_status: str | None = None, next_usage_reset_at: str | None = None, resume_after_usage_reset: bool | None = None, last_completion_status: str | None = None, task_id: str | None = None, preset_application_status: str | None = None, dialog_status: str | None = None, dialog_note: str | None = None) -> RelayLoopStatus:
    with runtime_data_lock():
        state = _merge_with_defaults(read_relay_loop_state_object())
        if relay_state is not None:
            state['relay_state'] = _normalize_state(relay_state)
            state['last_transition_at'] = _now()
        if current_step is not None:
            state['current_step'] = current_step.strip() or state['current_step']
        if source_alias is not None:
            normalized = _normalize_alias(source_alias, label='source')
            state['source_target_alias'] = normalized
            binding = state['saved_targets'].get(normalized, _default_binding(normalized))
            state['source_target_candidate_id'] = binding.get('candidate_id', '')
            state['source_target_title'] = binding.get('title', '')
        if destination_alias is not None:
            normalized = _normalize_alias(destination_alias, label='destination')
            state['destination_target_alias'] = normalized
            binding = state['saved_targets'].get(normalized, _default_binding(normalized))
            state['destination_target_candidate_id'] = binding.get('candidate_id', '')
            state['destination_target_title'] = binding.get('title', '')
        if waiting_reason is not None:
            state['waiting_reason'] = waiting_reason.strip()
        if blocked_reason is not None:
            state['blocked_reason'] = blocked_reason.strip()
        if last_payload_preview is not None:
            state['last_payload_preview'] = _preview(last_payload_preview)
        if last_result_preview is not None:
            state['last_result_preview'] = _preview(last_result_preview)
        if codex_execution_status is not None:
            state['codex_execution_status'] = _normalize_codex_execution_status(codex_execution_status)
        if next_usage_reset_at is not None:
            state['next_usage_reset_at'] = next_usage_reset_at.strip()
        if resume_after_usage_reset is not None:
            state['resume_after_usage_reset'] = bool(resume_after_usage_reset)
        if last_completion_status is not None:
            state['last_completion_status'] = last_completion_status.strip() or state['last_completion_status']
        if task_id is not None:
            state['last_used_task_id'] = task_id.strip()
        if preset_application_status is not None:
            state['preset_application_status'] = _normalize_preset_application_status(preset_application_status)
        if dialog_status is not None:
            state['last_known_dialog_status'] = _normalize_dialog_status(dialog_status)
        if dialog_note is not None:
            state['last_known_dialog_note'] = _preview(dialog_note)
        state['last_updated_at'] = _now()
        write_relay_loop_state_object(state)
        _write_memory_files(state)
    return get_relay_loop_status()


def save_relay_target_binding(*, alias: str, candidate_id: str) -> RelayLoopStatus:
    normalized_alias = _normalize_alias(alias)
    normalized_candidate_id = (candidate_id or '').strip().lower()
    if not normalized_candidate_id:
        raise ValueError('candidate id is required for a relay target binding')
    visible_targets = _list_visible_handoff_targets()
    matches = [item for item in visible_targets if item.get('alias') == normalized_alias and item.get('candidate_id') == normalized_candidate_id]
    if len(matches) != 1:
        raise ValueError(f'Could not bind {normalized_alias}: candidate {normalized_candidate_id} is not a unique visible allowlisted target.')
    match = matches[0]
    with runtime_data_lock():
        state = _merge_with_defaults(read_relay_loop_state_object())
        binding = state['saved_targets'].get(normalized_alias, _default_binding(normalized_alias))
        binding.update({'alias': normalized_alias, 'candidate_id': normalized_candidate_id, 'title': str(match.get('title') or ''), 'binding_status': 'ready', 'last_checked_at': _now(), 'last_error': ''})
        state['saved_targets'][normalized_alias] = binding
        if state.get('source_target_alias') == normalized_alias:
            state['source_target_candidate_id'] = normalized_candidate_id
            state['source_target_title'] = binding['title']
        if state.get('destination_target_alias') == normalized_alias:
            state['destination_target_candidate_id'] = normalized_candidate_id
            state['destination_target_title'] = binding['title']
        state['last_updated_at'] = _now()
        write_relay_loop_state_object(state)
        _write_memory_files(state)
    return get_relay_loop_status()


def save_codex_preset(*, mode: str, reasoning: str, application_status: str = 'stored_only') -> RelayLoopStatus:
    clean_mode = (mode or '').strip() or 'Implementing new feature'
    clean_reasoning = (reasoning or '').strip() or 'Medium'
    with runtime_data_lock():
        state = _merge_with_defaults(read_relay_loop_state_object())
        state['codex_mode_preset'] = clean_mode
        state['codex_reasoning_preset'] = clean_reasoning
        state['preset_application_status'] = _normalize_preset_application_status(application_status)
        state['last_updated_at'] = _now()
        write_relay_loop_state_object(state)
        _write_memory_files(state)
    return get_relay_loop_status()
