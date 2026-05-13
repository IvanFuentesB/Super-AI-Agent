#!/usr/bin/env python3
"""Desktop Operator Control Plane MVP (N+4.4A).

Local-only safe control plane that converts a user goal into a validated
handoff payload, probes available model adapters (gemini_cli, local_demo,
ollama) and operator adapters (dry_run, local_preview_open, screenshot_probe),
and gates every action behind an explicit approval token.

Default mode is dry_run. No live Gemini prompts. No arbitrary click/type.
No shell execution from model output. No live accounts. No posting.

CLI:
  --status                                       text status
  --json                                         status JSON (also implied when bare)
  --create-handoff --goal "<goal>" --workflow <wf>
  --validate-handoff <handoff_path>
  --dry-run <handoff_path>
  --approve <handoff_path> --approval-token <tok>
  --execute-approved <handoff_path>
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import secrets
import shutil
import subprocess
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
RUNS_DIR = REPO_ROOT / "14_context" / "desktop_operator" / "runs"
MILESTONE = "N+4.4A"
PLANE_NAME = "desktop_operator_control_plane"

ALLOWED_MODEL_ADAPTERS = ["gemini_cli", "local_demo", "ollama", "manual"]
ALLOWED_OPERATOR_ADAPTERS = ["dry_run", "local_preview_open", "screenshot_probe"]
ALLOWED_WORKFLOWS = ["content_studio_demo", "memory_bridge", "dashboard_open"]
ALLOWED_RISK_LEVELS = ["low", "medium", "high"]

# Forbidden flags that must NEVER be True in any handoff
FORBIDDEN_TRUE_FLAGS = [
    "live_account_actions_enabled",
    "external_api_actions_enabled",
    "money_actions_enabled",
    "publish_actions_enabled",
]

# Forbidden action strings — any handoff with these in allowed_actions is rejected
FORBIDDEN_ACTIONS = frozenset([
    "arbitrary_click", "arbitrary_type", "arbitrary_keypress",
    "shell_exec", "run_shell", "sudo", "install_package",
    "live_browser_navigate", "live_browser_post", "live_account_login",
    "publish_to_social", "publish_to_youtube", "publish_to_tiktok",
    "send_email", "send_dm", "send_money", "place_trade",
    "clone_external_repo", "install_external_repo", "run_external_repo",
])

_SECRET_NAME_PATTERNS = frozenset([
    ".env", "secret", "credential", "token", "key", "password",
    "apikey", "api_key", "private", "passwd", "auth",
])


def _utc_timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slug(text: str, limit: int = 32) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return (s[:limit] or "goal").rstrip("_")


def _is_inside_repo(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _is_secret_path(p: pathlib.Path) -> bool:
    lowered = str(p).lower()
    return any(pat in lowered for pat in _SECRET_NAME_PATTERNS)

# ---------------------------------------------------------------------------
# Model adapter status probes (status-only; no live prompts)
# ---------------------------------------------------------------------------

def _probe_gemini_cli() -> Dict[str, Any]:
    """Status-only probe. NEVER pipes a user goal into Gemini."""
    gemini = shutil.which("gemini")
    if not gemini:
        return {
            "adapter": "gemini_cli",
            "available": False,
            "executable": None,
            "version": None,
            "quota": "unknown_free_tier_limited",
            "treated_as_unlimited": False,
            "live_prompt_executed": False,
            "probe_error": "gemini executable not found in PATH",
        }
    try:
        proc = subprocess.run(
            [gemini, "--version"],
            capture_output=True,
            timeout=10,
        )
        version_out = (proc.stdout or proc.stderr or b"").decode("utf-8", "ignore").strip().splitlines()
        version = version_out[0] if version_out else None
        return {
            "adapter": "gemini_cli",
            "available": True,
            "executable": gemini,
            "version": version,
            "quota": "unknown_free_tier_limited",
            "treated_as_unlimited": False,
            "live_prompt_executed": False,
            "probe_error": None,
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return {
            "adapter": "gemini_cli",
            "available": False,
            "executable": gemini,
            "version": None,
            "quota": "unknown_free_tier_limited",
            "treated_as_unlimited": False,
            "live_prompt_executed": False,
            "probe_error": f"probe failed: {exc}",
        }


def _probe_local_demo() -> Dict[str, Any]:
    return {
        "adapter": "local_demo",
        "available": True,
        "deterministic": True,
        "live_prompt_executed": False,
        "quota": "local_only_unlimited_local",
        "probe_error": None,
    }


def _probe_ollama_via_bridge() -> Dict[str, Any]:
    bridge = REPO_ROOT / "03_scripts" / "local_memory_compression_bridge.py"
    if not bridge.exists():
        return {
            "adapter": "ollama",
            "available": False,
            "via_bridge": False,
            "ollama_available": False,
            "gemma_model_found": False,
            "fallback_mode": "local_demo",
            "probe_error": "local_memory_compression_bridge.py not present",
        }
    py = sys.executable or "python"
    try:
        proc = subprocess.run(
            [py, str(bridge), "--status", "--json"],
            capture_output=True,
            timeout=15,
        )
        if proc.returncode != 0:
            return {
                "adapter": "ollama",
                "available": False,
                "via_bridge": True,
                "ollama_available": False,
                "gemma_model_found": False,
                "fallback_mode": "local_demo",
                "probe_error": f"bridge exit={proc.returncode}",
            }
        data = json.loads(proc.stdout.decode("utf-8", "ignore"))
        return {
            "adapter": "ollama",
            "available": bool(data.get("ollama_available")),
            "via_bridge": True,
            "ollama_available": bool(data.get("ollama_available")),
            "gemma_model_found": bool(data.get("gemma_model_found")),
            "fallback_mode": data.get("fallback_mode", "local_demo"),
            "probe_error": None,
        }
    except Exception as exc:
        return {
            "adapter": "ollama",
            "available": False,
            "via_bridge": True,
            "ollama_available": False,
            "gemma_model_found": False,
            "fallback_mode": "local_demo",
            "probe_error": f"probe exception: {exc}",
        }


def _probe_all_models() -> Dict[str, Any]:
    return {
        "gemini_cli": _probe_gemini_cli(),
        "local_demo": _probe_local_demo(),
        "ollama": _probe_ollama_via_bridge(),
    }


# ---------------------------------------------------------------------------
# Operator adapter status (safe only)
# ---------------------------------------------------------------------------

def _probe_operator_adapters() -> Dict[str, Any]:
    studio = REPO_ROOT / "03_scripts" / "supervised_content_studio_demo.py"
    return {
        "dry_run": {"available": True, "side_effects": "none"},
        "local_preview_open": {
            "available": True,
            "constraint": "repo_local_html_only",
            "actually_opens": False,
            "note": "Approved execution merely records the path; this milestone never spawns a browser process.",
        },
        "screenshot_probe": {
            "available": False,
            "reason": "Not enabled in N+4.4A. Status-only placeholder.",
        },
        "content_studio_demo_present": studio.exists(),
    }

# ---------------------------------------------------------------------------
# Handoff payload
# ---------------------------------------------------------------------------

def _build_handoff(
    goal: str,
    workflow: str,
    requested_model: str = "local_demo",
    requested_operator: str = "dry_run",
    risk_level: str = "low",
) -> Dict[str, Any]:
    task_id = f"task-{uuid.uuid4().hex[:12]}"
    payload = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "control_plane": PLANE_NAME,
        "task_id": task_id,
        "user_goal": goal,
        "created_at": _utc_timestamp(),
        "requested_model_adapter": requested_model,
        "requested_operator_adapter": requested_operator,
        "target_workflow": workflow,
        "risk_level": risk_level,
        "allowed_actions": _default_allowed_actions(workflow, requested_operator),
        "forbidden_actions": sorted(FORBIDDEN_ACTIONS),
        "requires_human_approval": True,
        "approval_token_required": True,
        "live_account_actions_enabled": False,
        "external_api_actions_enabled": False,
        "money_actions_enabled": False,
        "publish_actions_enabled": False,
        "external_repo_clone_install_run_enabled": False,
        "ui_tars_runtime_wired": False,
        "the_agency_runtime_wired": False,
        "weavy_runtime_wired": False,
        "manychat_runtime_wired": False,
        "vouch_runtime_wired": False,
        "aex_runtime_wired": False,
        "airllm_runtime_wired": False,
        "openfang_moneyprinter_runtime_wired": False,
    }
    return payload


def _default_allowed_actions(workflow: str, operator: str) -> List[str]:
    base = ["log_only", "produce_plan", "write_local_artifact_inside_repo"]
    if workflow == "content_studio_demo":
        base.append("run_supervised_content_studio_demo_local_only")
    if workflow == "memory_bridge":
        base.append("call_local_memory_bridge_status_only")
    if workflow == "dashboard_open":
        base.append("open_repo_local_dashboard_html_preview_only")
    if operator == "local_preview_open":
        base.append("record_repo_local_html_path_for_preview")
    return base


def validate_handoff(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return False, ["payload is not a dict"]

    required = [
        "task_id", "user_goal", "requested_model_adapter",
        "requested_operator_adapter", "target_workflow", "risk_level",
        "allowed_actions", "forbidden_actions",
        "requires_human_approval", "approval_token_required",
    ]
    for k in required:
        if k not in payload:
            errors.append(f"missing required field: {k}")

    # Forbidden flags must be False (and present)
    for flag in FORBIDDEN_TRUE_FLAGS:
        val = payload.get(flag, None)
        if val is True:
            errors.append(f"REJECTED: forbidden flag {flag} is True")
        if flag not in payload:
            errors.append(f"missing forbidden_true_flag declaration: {flag}")

    # Approval gates must be True
    if payload.get("requires_human_approval") is not True:
        errors.append("REJECTED: requires_human_approval must be True")
    if payload.get("approval_token_required") is not True:
        errors.append("REJECTED: approval_token_required must be True")

    # Model adapter
    if payload.get("requested_model_adapter") not in ALLOWED_MODEL_ADAPTERS:
        errors.append(f"REJECTED: requested_model_adapter not in allowed list {ALLOWED_MODEL_ADAPTERS}")

    # Operator adapter
    if payload.get("requested_operator_adapter") not in ALLOWED_OPERATOR_ADAPTERS:
        errors.append(f"REJECTED: requested_operator_adapter not in allowed list {ALLOWED_OPERATOR_ADAPTERS}")

    # Workflow
    if payload.get("target_workflow") not in ALLOWED_WORKFLOWS:
        errors.append(f"REJECTED: target_workflow not in allowed list {ALLOWED_WORKFLOWS}")

    # Risk level
    if payload.get("risk_level") not in ALLOWED_RISK_LEVELS:
        errors.append(f"REJECTED: risk_level not in allowed list {ALLOWED_RISK_LEVELS}")

    # Forbidden actions in allowed_actions
    allowed = payload.get("allowed_actions") or []
    if not isinstance(allowed, list):
        errors.append("allowed_actions must be a list")
    else:
        for a in allowed:
            if a in FORBIDDEN_ACTIONS:
                errors.append(f"REJECTED: forbidden action '{a}' in allowed_actions")

    # External tool runtime wiring must be False if declared
    external_flags = [
        "external_repo_clone_install_run_enabled",
        "ui_tars_runtime_wired", "the_agency_runtime_wired", "weavy_runtime_wired",
        "manychat_runtime_wired", "vouch_runtime_wired", "aex_runtime_wired",
        "airllm_runtime_wired", "openfang_moneyprinter_runtime_wired",
    ]
    for flag in external_flags:
        if payload.get(flag) is True:
            errors.append(f"REJECTED: external-tool flag {flag} must be False")

    return (len(errors) == 0), errors

# ---------------------------------------------------------------------------
# Safe write
# ---------------------------------------------------------------------------

def _safe_write(path: pathlib.Path, content: str) -> Tuple[bool, str]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True, "python"
    except (PermissionError, OSError) as e_py:
        try:
            import base64
            b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
            node = shutil.which("node")
            if not node:
                return False, f"python_failed: {e_py}; node not available"
            node_script = (
                "const fs=require('fs');"
                "const path=require('path');"
                f"const target={json.dumps(str(path))};"
                f"const data=Buffer.from({json.dumps(b64)},'base64');"
                "fs.mkdirSync(path.dirname(target),{recursive:true});"
                "fs.writeFileSync(target,data);"
            )
            proc = subprocess.run([node, "-e", node_script], capture_output=True, timeout=15)
            if proc.returncode == 0:
                return True, "node_fallback"
            return False, f"python_failed: {e_py}; node_failed"
        except Exception as e_node:
            return False, f"python_failed: {e_py}; node_exception: {e_node}"


# ---------------------------------------------------------------------------
# Run-folder logging
# ---------------------------------------------------------------------------

def _ensure_run_folder(payload: Dict[str, Any]) -> pathlib.Path:
    """Pick a run folder for a handoff. Use a stable slug from task_id."""
    slug = _slug(payload.get("user_goal", "goal"))
    ts = payload.get("created_at") or _utc_timestamp()
    run_dir = RUNS_DIR / f"{ts}_{slug}_{payload.get('task_id','')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_safety_review(run_dir: pathlib.Path, payload: Dict[str, Any]) -> pathlib.Path:
    lines = [
        "# Safety Review",
        "",
        "- live_account_actions_enabled: false",
        "- external_api_actions_enabled: false",
        "- money_actions_enabled: false",
        "- publish_actions_enabled: false",
        "- arbitrary_click_disabled: true",
        "- arbitrary_type_disabled: true",
        "- shell_exec_from_model_output_disabled: true",
        "- ui_tars_runtime_wired: false",
        "- the_agency_runtime_wired: false",
        "- weavy_runtime_wired: false",
        "- manychat_runtime_wired: false",
        "- vouch_runtime_wired: false",
        "- aex_runtime_wired: false",
        "- airllm_runtime_wired: false",
        "- openfang_moneyprinter_runtime_wired: false",
        "- external_repo_clone_install_run_enabled: false",
        "- approval_gate: required_with_token",
        "- default_mode: dry_run",
    ]
    safety_path = run_dir / "06_safety_review.md"
    _safe_write(safety_path, "\n".join(lines))
    return safety_path


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_status(json_out: bool) -> int:
    models = _probe_all_models()
    operator = _probe_operator_adapters()
    latest = _find_latest_run()
    data = {
        "control_plane": PLANE_NAME,
        "milestone": MILESTONE,
        "default_mode": "dry_run",
        "local_only": True,
        "live_account_actions_enabled": False,
        "external_api_actions_enabled": False,
        "money_actions_enabled": False,
        "publish_actions_enabled": False,
        "arbitrary_click_or_type_enabled": False,
        "shell_exec_from_model_output_enabled": False,
        "external_tools_status": "planning_only",
        "approval_gate": "required_with_token",
        "model_adapters": models,
        "operator_adapters": operator,
        "runs_dir": str(RUNS_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
        "latest_run_path": latest,
        "gemini_treated_as_unlimited": False,
        "gemini_live_prompt_executed": False,
    }
    if json_out:
        print(json.dumps(data, indent=2))
        return 0
    print(f"{PLANE_NAME} status")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    print(f"    {kk}: {{ available: {vv.get('available')} }}")
                else:
                    print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")
    return 0


def _find_latest_run() -> Optional[str]:
    if not RUNS_DIR.exists():
        return None
    children = [c for c in RUNS_DIR.iterdir() if c.is_dir()]
    if not children:
        return None
    latest = sorted(children)[-1]
    try:
        return str(latest.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return None

def cmd_create_handoff(goal: str, workflow: str, json_out: bool,
                       requested_model: str = "local_demo",
                       requested_operator: str = "dry_run") -> int:
    payload = _build_handoff(goal, workflow, requested_model, requested_operator)
    ok, errors = validate_handoff(payload)
    run_dir = _ensure_run_folder(payload)

    handoff_path = run_dir / "00_handoff_payload.json"
    _safe_write(handoff_path, json.dumps(payload, indent=2))

    validation_report = {
        "ok": ok,
        "errors": errors,
        "validated_at": _utc_timestamp(),
    }
    _safe_write(run_dir / "01_validation_report.json", json.dumps(validation_report, indent=2))

    model_status = _probe_all_models()
    _safe_write(run_dir / "02_model_adapter_status.json", json.dumps(model_status, indent=2))

    _write_safety_review(run_dir, payload)

    try:
        handoff_rel = str(handoff_path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
        run_rel = str(run_dir.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        handoff_rel = str(handoff_path)
        run_rel = str(run_dir)

    result = {
        "ok": ok,
        "task_id": payload["task_id"],
        "handoff_path": handoff_rel,
        "run_dir": run_rel,
        "validation_errors": errors,
        "default_mode": "dry_run",
        "approval_required": True,
    }
    if json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"Handoff created: {handoff_rel}")
        print(f"ok={ok}; approval_required=True; default_mode=dry_run")
    return 0 if ok else 1


def cmd_validate_handoff(path: str, json_out: bool) -> int:
    p = pathlib.Path(path).resolve()
    if not _is_inside_repo(p):
        msg = {"ok": False, "error": "REJECTED: handoff path outside repo root"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1
    if not p.exists():
        msg = {"ok": False, "error": "HANDOFF_NOT_FOUND", "path": str(p)}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        msg = {"ok": False, "error": f"INVALID_JSON: {e}"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1
    ok, errors = validate_handoff(payload)
    out = {"ok": ok, "errors": errors, "validated_at": _utc_timestamp()}
    if json_out:
        print(json.dumps(out, indent=2))
    else:
        print(f"validate: ok={ok}; errors={len(errors)}")
        for e in errors:
            print(f"  - {e}")
    return 0 if ok else 1


def _load_handoff(path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    p = pathlib.Path(path).resolve()
    if not _is_inside_repo(p):
        return None, "REJECTED: handoff path outside repo root"
    if not p.exists():
        return None, "HANDOFF_NOT_FOUND"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, f"INVALID_JSON: {e}"


def cmd_dry_run(handoff_path: str, json_out: bool) -> int:
    payload, err = _load_handoff(handoff_path)
    if payload is None:
        msg = {"ok": False, "error": err}
        print(json.dumps(msg, indent=2) if json_out else err)
        return 1
    ok, errors = validate_handoff(payload)
    if not ok:
        msg = {"ok": False, "errors": errors}
        print(json.dumps(msg, indent=2) if json_out else "VALIDATION_FAILED")
        return 1

    run_dir = pathlib.Path(handoff_path).resolve().parent
    plan_lines = [
        "# Operator plan (dry-run only -- no side effects executed)",
        f"- task_id: {payload['task_id']}",
        f"- user_goal: {payload['user_goal']}",
        f"- requested_model_adapter: {payload['requested_model_adapter']}",
        f"- requested_operator_adapter: {payload['requested_operator_adapter']}",
        f"- target_workflow: {payload['target_workflow']}",
        f"- risk_level: {payload['risk_level']}",
        "",
        "## Steps (planned, not executed)",
    ]
    workflow = payload["target_workflow"]
    if workflow == "content_studio_demo":
        plan_lines.append("1. Approval gate would be enforced.")
        plan_lines.append("2. After approval, the plane would invoke supervised_content_studio_demo.py --run-demo (local-only).")
        plan_lines.append("3. The plane would record the resulting run folder path; no live posting.")
    elif workflow == "memory_bridge":
        plan_lines.append("1. Approval gate would be enforced.")
        plan_lines.append("2. After approval, the plane would invoke local_memory_compression_bridge.py --status --json.")
        plan_lines.append("3. No external API call.")
    elif workflow == "dashboard_open":
        plan_lines.append("1. Approval gate would be enforced.")
        plan_lines.append("2. After approval, the plane would record a repo-local preview HTML path; no browser process is spawned.")
    plan_lines.append("")
    plan_lines.append("_No actions were executed in dry-run mode._")
    _safe_write(run_dir / "03_operator_plan.md", "\n".join(plan_lines))

    result = {
        "ok": True,
        "task_id": payload["task_id"],
        "actions_executed": 0,
        "default_mode": "dry_run",
        "plan_path": str((run_dir / "03_operator_plan.md").resolve().relative_to(REPO_ROOT)).replace("\\", "/"),
        "approval_required_next": True,
        "model_status_brief": {
            "gemini_treated_as_unlimited": False,
            "gemini_live_prompt_executed": False,
        },
    }
    if json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"DRY_RUN_OK plan={result['plan_path']}")
    return 0

def cmd_approve(handoff_path: str, approval_token: Optional[str], json_out: bool) -> int:
    payload, err = _load_handoff(handoff_path)
    if payload is None:
        msg = {"ok": False, "error": err}
        print(json.dumps(msg, indent=2) if json_out else err)
        return 1
    ok, errors = validate_handoff(payload)
    if not ok:
        msg = {"ok": False, "errors": errors}
        print(json.dumps(msg, indent=2) if json_out else "VALIDATION_FAILED")
        return 1

    if not approval_token or len(approval_token.strip()) < 4:
        msg = {"ok": False, "error": "REJECTED: approval_token required (min 4 chars)"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1

    # Store a token hash + timestamp; do not store the raw token directly.
    token_hash = hashlib.sha256(approval_token.encode("utf-8")).hexdigest()
    run_dir = pathlib.Path(handoff_path).resolve().parent
    record = {
        "task_id": payload["task_id"],
        "approved_at": _utc_timestamp(),
        "approval_token_hash": token_hash,
        "approver": "human_local",
        "approval_grants": ["execute_approved_local_safe_action"],
        "live_account_actions_enabled": False,
        "external_api_actions_enabled": False,
        "money_actions_enabled": False,
        "publish_actions_enabled": False,
    }
    _safe_write(run_dir / "04_approval_record.json", json.dumps(record, indent=2))

    result = {
        "ok": True,
        "task_id": payload["task_id"],
        "approval_record_path": str((run_dir / "04_approval_record.json").resolve().relative_to(REPO_ROOT)).replace("\\", "/"),
        "approved": True,
    }
    if json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"APPROVED record={result['approval_record_path']}")
    return 0


def cmd_execute_approved(handoff_path: str, json_out: bool) -> int:
    payload, err = _load_handoff(handoff_path)
    if payload is None:
        msg = {"ok": False, "error": err}
        print(json.dumps(msg, indent=2) if json_out else err)
        return 1
    ok, errors = validate_handoff(payload)
    if not ok:
        msg = {"ok": False, "errors": errors}
        print(json.dumps(msg, indent=2) if json_out else "VALIDATION_FAILED")
        return 1

    run_dir = pathlib.Path(handoff_path).resolve().parent
    approval_file = run_dir / "04_approval_record.json"
    if not approval_file.exists():
        msg = {"ok": False, "error": "APPROVAL_RECORD_MISSING; run --approve first"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1

    # Re-check the approval record looks well-formed
    try:
        approval = json.loads(approval_file.read_text(encoding="utf-8"))
    except Exception as e:
        msg = {"ok": False, "error": f"APPROVAL_RECORD_INVALID: {e}"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1
    if not approval.get("approval_token_hash"):
        msg = {"ok": False, "error": "APPROVAL_RECORD_MISSING_TOKEN_HASH"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1

    operator = payload.get("requested_operator_adapter")
    workflow = payload.get("target_workflow")

    # Only safe adapters/workflows are executed.
    if operator not in {"dry_run", "local_preview_open"}:
        msg = {"ok": False, "error": f"REJECTED: operator adapter '{operator}' not allowed for execute"}
        print(json.dumps(msg, indent=2) if json_out else msg["error"])
        return 1

    actions_executed: List[str] = []
    exec_summary: Dict[str, Any] = {"ok": True, "task_id": payload["task_id"]}

    if workflow == "content_studio_demo":
        studio = REPO_ROOT / "03_scripts" / "supervised_content_studio_demo.py"
        if not studio.exists():
            exec_summary["content_studio_link"] = "unavailable"
            exec_summary["ok"] = False
            exec_summary["error"] = "content_studio_demo script not present in this worktree"
        else:
            try:
                proc = subprocess.run(
                    [sys.executable, str(studio), "--status", "--json"],
                    capture_output=True,
                    timeout=30,
                )
                ok_status = proc.returncode == 0
                exec_summary["content_studio_link"] = "available" if ok_status else "probe_failed"
                exec_summary["content_studio_status_exit"] = proc.returncode
                actions_executed.append("content_studio_status_probe_only")
            except Exception as e:
                exec_summary["content_studio_link"] = "probe_exception"
                exec_summary["content_studio_probe_error"] = str(e)

    elif workflow == "memory_bridge":
        bridge = REPO_ROOT / "03_scripts" / "local_memory_compression_bridge.py"
        if bridge.exists():
            try:
                proc = subprocess.run(
                    [sys.executable, str(bridge), "--status", "--json"],
                    capture_output=True,
                    timeout=15,
                )
                exec_summary["memory_bridge_status_exit"] = proc.returncode
                actions_executed.append("memory_bridge_status_only")
            except Exception as e:
                exec_summary["memory_bridge_probe_error"] = str(e)
        else:
            exec_summary["memory_bridge_link"] = "unavailable"

    elif workflow == "dashboard_open":
        # Record-only. We never spawn a browser.
        actions_executed.append("recorded_repo_local_preview_path_no_spawn")

    exec_summary["actions_executed"] = actions_executed
    exec_summary["arbitrary_click_or_type_executed"] = False
    exec_summary["shell_exec_from_model_output_executed"] = False
    exec_summary["live_account_actions_executed"] = False
    exec_summary["posting_executed"] = False
    exec_summary["external_repo_clone_install_run_executed"] = False

    _safe_write(run_dir / "05_execution_result.json", json.dumps(exec_summary, indent=2))

    if json_out:
        print(json.dumps(exec_summary, indent=2))
    else:
        print(f"EXECUTED safely. actions_executed={actions_executed}")
    return 0 if exec_summary["ok"] else 1

def main() -> int:
    parser = argparse.ArgumentParser(description="Desktop Operator Control Plane MVP (N+4.4A) -- local-only, dry-run by default.")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--json", dest="json_out", action="store_true")
    parser.add_argument("--create-handoff", action="store_true")
    parser.add_argument("--goal", default=None)
    parser.add_argument("--workflow", default="content_studio_demo", choices=ALLOWED_WORKFLOWS)
    parser.add_argument("--model-adapter", default="local_demo", choices=ALLOWED_MODEL_ADAPTERS)
    parser.add_argument("--operator-adapter", default="dry_run", choices=ALLOWED_OPERATOR_ADAPTERS)
    parser.add_argument("--validate-handoff", metavar="PATH", default=None)
    parser.add_argument("--dry-run", metavar="PATH", default=None)
    parser.add_argument("--approve", metavar="PATH", default=None)
    parser.add_argument("--approval-token", default=None)
    parser.add_argument("--execute-approved", metavar="PATH", default=None)
    args = parser.parse_args()

    if args.create_handoff:
        if not args.goal:
            msg = {"ok": False, "error": "REJECTED: --goal required for --create-handoff"}
            print(json.dumps(msg, indent=2) if args.json_out else msg["error"])
            return 1
        return cmd_create_handoff(args.goal, args.workflow, args.json_out,
                                  args.model_adapter, args.operator_adapter)
    if args.validate_handoff:
        return cmd_validate_handoff(args.validate_handoff, args.json_out)
    if args.dry_run:
        return cmd_dry_run(args.dry_run, args.json_out)
    if args.approve:
        return cmd_approve(args.approve, args.approval_token, args.json_out)
    if args.execute_approved:
        return cmd_execute_approved(args.execute_approved, args.json_out)
    if args.status:
        return cmd_status(args.json_out)
    if args.json_out:
        return cmd_status(json_out=True)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())