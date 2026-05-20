#!/usr/bin/env python3
"""UI-TARS Observation-Only Adapter CLI (N+5.0A).

Drives the UI-TARS observation-only adapter to produce a local observation
packet. Observation-only: it never runs UI-TARS, never executes external repo
code, never clicks/types/uses hotkeys, never controls the desktop, never calls
a live API.

Approval model:
  - dry-run observation needs no token and never captures the screen
  - a screen capture or any non-dry-run observation requires a valid approval
    token (--create-approval issues one; only its SHA-256 hash is stored)
"""
import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
ADAPTER_FILE = (REPO_ROOT / "02_automation" / "external_tool_adapters"
                / "ui_tars_observation_adapter.py")
OBS_DIR = REPO_ROOT / "14_context" / "ui_tars_observation"
APPROVALS_DIR = OBS_DIR / "approvals"
RUNS_DIR = OBS_DIR / "runs"
LATEST_FILE = OBS_DIR / "latest.json"

CLI_VERSION = "1.0.0"
MILESTONE = "N+5.0A"
ADAPTER_KEY = "ui_tars_observation_only"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _is_repo_local(target) -> bool:
    try:
        resolved = Path(str(target)).resolve()
        repo = REPO_ROOT.resolve()
        return resolved == repo or repo in resolved.parents
    except Exception:
        return False


def _repo_rel(target) -> str:
    try:
        return str(Path(target).resolve().relative_to(REPO_ROOT.resolve())).replace(os.sep, "/")
    except Exception:
        return str(target)


def _load_adapter():
    spec = importlib.util.spec_from_file_location(
        "ghoti_ui_tars_observation_adapter", ADAPTER_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _verify_token(token: str) -> bool:
    if not token:
        return False
    wanted = _token_hash(token)
    try:
        for rec_path in APPROVALS_DIR.glob("*.json"):
            rec = _read_json(rec_path)
            if rec.get("status") == "approved" and rec.get("token_hash") == wanted:
                return True
    except Exception:
        return False
    return False


def cmd_status() -> dict:
    return {
        "ok": True,
        "adapter": "ui_tars_observation_adapter_cli",
        "cli_version": CLI_VERSION,
        "milestone": MILESTONE,
        "adapter_key": ADAPTER_KEY,
        "mode": "observation_only",
        "default_run_mode": "dry_run",
        "ui_tars_runtime_started": False,
        "external_code_executed": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "click_enabled": False,
        "type_enabled": False,
        "hotkeys_enabled": False,
        "live_api_enabled": False,
        "approval_required_for_capture": True,
        "human_approval_required": True,
        "approvals_dir": _repo_rel(APPROVALS_DIR),
        "runs_dir": _repo_rel(RUNS_DIR),
        "latest_run": _read_json(LATEST_FILE) or None,
        "generated_at": _now(),
    }


def cmd_create_approval() -> dict:
    if not _is_repo_local(APPROVALS_DIR):
        return {"ok": False, "error": "approvals dir is outside the repo root"}
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    token = secrets.token_hex(16)
    ts = _now()
    approval_id = "approval-" + secrets.token_hex(6)
    record = {
        "approval_id": approval_id,
        "adapter": ADAPTER_KEY,
        "status": "approved",
        "token_hash": _token_hash(token),
        "token_algo": "sha256",
        "scope": "ui_tars_observation: screen capture and non-dry-run observation",
        "created_at": ts,
        "note": "Single-use local approval. Only the SHA-256 token hash is stored.",
    }
    record_path = APPROVALS_DIR / ("%s_approval.json" % ts)
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "action": "create-approval",
        "approval_id": approval_id,
        "approval_record": _repo_rel(record_path),
        # Raw token shown ONCE; only the hash is persisted.
        "approval_token": token,
        "token_note": "Store this token now — required for screen capture / non-dry-run.",
        "generated_at": ts,
    }


def cmd_latest() -> dict:
    latest = _read_json(LATEST_FILE)
    return {"ok": True, "action": "latest", "latest": latest or None, "generated_at": _now()}


def cmd_observe(dry_run_flag, capture_screen, approval_token, output_dir) -> dict:
    non_dry_run_intended = bool(capture_screen) or bool(approval_token)
    approval_verified = False

    if dry_run_flag:
        dry_run = True
    elif non_dry_run_intended:
        if not approval_token:
            return {
                "ok": False, "action": "observe",
                "error": "screen capture / non-dry-run observation requires --approval-token",
                "generated_at": _now(),
            }
        if not _verify_token(approval_token):
            return {
                "ok": False, "action": "observe",
                "error": "invalid or unknown approval token",
                "generated_at": _now(),
            }
        approval_verified = True
        dry_run = False
    else:
        dry_run = True

    adapter = _load_adapter()
    if adapter is None or not hasattr(adapter, "create_observation_packet"):
        return {"ok": False, "error": "ui_tars_observation adapter not available"}

    base_runs = RUNS_DIR
    if output_dir:
        cand = Path(str(output_dir).replace("/", os.sep))
        if not cand.is_absolute():
            cand = REPO_ROOT / cand
        if _is_repo_local(cand):
            base_runs = cand
    ts = _now()
    run_id = "%s_ui_tars_observation" % ts
    run_dir = base_runs / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = adapter.create_observation_packet(
            str(run_dir), dry_run=dry_run, capture_screen=bool(capture_screen),
            approval_token=approval_token,
        )
    except Exception as exc:
        return {"ok": False, "error": "observation error: %s" % exc, "run_id": run_id}

    artifacts = [_repo_rel(a) for a in (result.get("artifacts") or [])]
    mode = "dry_run" if dry_run else "approved_observation"

    latest = {
        "adapter": ADAPTER_KEY,
        "run_id": run_id,
        "run_dir": _repo_rel(run_dir),
        "mode": mode,
        "dry_run": bool(dry_run),
        "screenshot_captured": bool(result.get("screenshot_captured")),
        "artifacts": artifacts,
        "generated_at": ts,
    }
    try:
        OBS_DIR.mkdir(parents=True, exist_ok=True)
        LATEST_FILE.write_text(json.dumps(latest, indent=2), encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": bool(result.get("ok")),
        "action": "observe",
        "adapter": ADAPTER_KEY,
        "run_id": run_id,
        "run_dir": _repo_rel(run_dir),
        "mode": mode,
        "dry_run": bool(dry_run),
        "approval_verified": approval_verified,
        "capture_requested": bool(capture_screen),
        "screenshot_captured": bool(result.get("screenshot_captured")),
        "screenshot_path": result.get("screenshot_path"),
        "screenshot_skipped_reason": result.get("screenshot_skipped_reason"),
        "ui_tars_runtime_started": False,
        "external_repo_code_executed": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "live_api_used": False,
        "artifacts": artifacts,
        "generated_at": ts,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="UI-TARS Observation-Only Adapter CLI (N+5.0A).",
    )
    parser.add_argument("--status", action="store_true", help="show observation adapter status")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--create-approval", action="store_true", help="issue a one-time approval token")
    parser.add_argument("--observe", action="store_true", help="run an observation")
    parser.add_argument("--dry-run", action="store_true", help="force dry-run observation (no capture)")
    parser.add_argument("--capture-screen", action="store_true",
                        help="request a read-only screen capture (requires approval token)")
    parser.add_argument("--approval-token", default=None, help="approval token for capture / non-dry-run")
    parser.add_argument("--output-dir", default=None, help="optional repo-local run output dir")
    parser.add_argument("--latest", action="store_true", help="show the latest observation run")
    args = parser.parse_args(argv)

    try:
        if args.create_approval:
            result = cmd_create_approval()
        elif args.observe:
            result = cmd_observe(args.dry_run, args.capture_screen,
                                 args.approval_token, args.output_dir)
        elif args.latest:
            result = cmd_latest()
        else:
            result = cmd_status()
    except Exception as exc:
        result = {"ok": False, "error": "cli error: %s" % exc, "generated_at": _now()}

    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
