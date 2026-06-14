"""Run exactly one fixed local worker after a positive Rust guard decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import data_only_writer


SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_REGISTRY = {
    "repo-summary-worker": {
        "entrypoint": Path(__file__).resolve().parent / "repo_summary_worker.py",
        "fixed_args": ("--json",),
        "tasks": frozenset(
            {"repo_status_summary", "bounded_wait_probe", "bounded_log_probe"}
        ),
    },
    "local-model-summary-classification-worker": {
        "entrypoint": (
            Path(__file__).resolve().parent
            / "local_model_summary_classification_worker.py"
        ),
        "fixed_args": ("--json",),
        "tasks": frozenset({"summary_classification"}),
    },
}
WORKER_REGISTRY_FINGERPRINT = (
    "13e24b9f2aa491b79517f612ae92f35766d548a2e3881685beeccbe245c09f3a"
)
MAX_CAPTURE_BYTES = 64 * 1024
ALLOWED_OUTPUT_ROOTS = (
    "14_context/agent_os/",
    "14_context/memory/agent_handoffs/",
    "14_context/operator_reports/generated/",
)
ALLOWED_INPUT_ROOTS = ("14_context/", "docs/")
DYNAMIC_PROCESS_FIELDS = {
    "args",
    "code",
    "command",
    "env",
    "environment",
    "executable",
    "script",
    "shell",
}
SECRET_MARKERS = (
    "api_key=",
    "apikey=",
    "authorization: bearer",
    "password=",
    "private_key",
    "secret=",
    "sk-ant-",
    "ghp_",
)
REQUEST_ID_RE = re.compile(r"^req-[a-z0-9][a-z0-9-]{7,63}$")
POLL_SECONDS = 0.05
TERMINATE_GRACE_SECONDS = 2


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize(raw: object, roots: tuple[str, ...]) -> str:
    text = str(raw or "").strip().replace("\\", "/")
    path = PurePosixPath(text)
    if (
        not text
        or path.is_absolute()
        or ":" in text
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError("path must be normalized and repo-relative")
    normalized = path.as_posix()
    if not any(normalized.startswith(root) for root in roots):
        raise ValueError("path is outside approved roots")
    return normalized


def _destination(repo_root: Path, raw: object, roots: tuple[str, ...]) -> tuple[Path, str]:
    relative = _normalize(raw, roots)
    destination = (repo_root / relative).resolve()
    destination.relative_to(repo_root)
    return destination, relative


def _write(repo_root: Path, raw: object, content: str) -> str:
    destination, relative = _destination(repo_root, raw, ALLOWED_OUTPUT_ROOTS)
    data_only_writer.write_text(destination, content)
    return relative


def _public_safe(text: str) -> bool:
    lowered = text.lower()
    return not any(marker in lowered for marker in SECRET_MARKERS) and all(
        marker not in lowered
        for marker in ("c:\\users\\", "c:/users/", "/mnt/c/users/")
    )


def _fixed_control_paths(request_id: str) -> dict[str, str]:
    return {
        "runner_state_path": f"14_context/agent_os/runner_control/state_{request_id}.json",
        "cancel_path": f"14_context/agent_os/runner_control/cancel_{request_id}.json",
        "active_lock_path": "14_context/agent_os/runner_control/active_worker.json",
    }


def _validate_request(request: dict, guard_decision: dict) -> tuple[dict, dict[str, str]]:
    if request.get("schema") != "ghoti_action_request/1":
        raise ValueError("unsupported request schema")
    request_id = str(request.get("request_id") or "")
    if not REQUEST_ID_RE.match(request_id):
        raise ValueError("invalid request id")
    if request.get("action_id") != "run_local_worker":
        raise ValueError("request is not a local worker action")
    if request.get("mode") != "approved_local" or request.get("approval_state") != "approved":
        raise ValueError("request is not explicitly approved")
    if not request.get("approval_token_hash"):
        raise ValueError("approval hash is missing")
    if not guard_decision.get("allow") or guard_decision.get("request_id") != request_id:
        raise ValueError("positive Rust guard decision is required")
    if not (guard_decision.get("safety") or {}).get("allowlisted_local_process"):
        raise ValueError("Rust guard did not approve the allowlisted worker process")

    payload = request.get("payload") or {}
    if payload.get("kind") != "run_allowlisted_worker":
        raise ValueError("unsupported worker payload")
    worker_id = str(payload.get("worker_id") or "")
    if worker_id not in WORKER_REGISTRY:
        raise ValueError("worker is not allowlisted")
    if payload.get("worker_registry_fingerprint") != WORKER_REGISTRY_FINGERPRINT:
        raise ValueError("worker registry fingerprint is invalid")
    if payload.get("task") not in WORKER_REGISTRY[worker_id]["tasks"]:
        raise ValueError("worker task is not allowlisted")
    if any(field in payload for field in DYNAMIC_PROCESS_FIELDS):
        raise ValueError("dynamic process surface is forbidden")
    runtime = int(request.get("max_runtime_seconds") or 0)
    if not 1 <= runtime <= 30:
        raise ValueError("worker runtime must be between 1 and 30 seconds")

    controls = _fixed_control_paths(request_id)
    for key, expected in controls.items():
        if payload.get(key) != expected:
            raise ValueError(f"{key} must use its fixed repo-local path")
    required = {
        payload.get("artifact_path"),
        payload.get("run_record_path"),
        payload.get("evidence_path"),
        payload.get("handoff_path"),
        *controls.values(),
    }
    declared = set(request.get("output_paths") or [])
    owned = set(request.get("owned_files") or [])
    if None in required or not required.issubset(declared) or not required.issubset(owned):
        raise ValueError("runner paths must be declared and owned")
    for output in declared:
        _normalize(output, ALLOWED_OUTPUT_ROOTS)
    for input_path in request.get("input_paths") or []:
        _normalize(input_path, ALLOWED_INPUT_ROOTS)
    return payload, controls


def _minimal_environment() -> dict[str, str]:
    allowed = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
    environment = {key: os.environ[key] for key in allowed if key in os.environ}
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    return environment


def _terminate(process: subprocess.Popen) -> bool:
    if process.poll() is not None:
        return False
    process.terminate()
    try:
        process.wait(timeout=TERMINATE_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=TERMINATE_GRACE_SECONDS)
    return True


def _write_active_lock(path: Path, request_id: str) -> bool:
    content = json.dumps(
        {"request_id": request_id, "started_at": _now()}, sort_keys=True
    ) + "\n"
    return data_only_writer.write_text_exclusive(path, content)


def _safe_unlink(path: Path) -> None:
    try:
        data_only_writer.remove_file(path)
    except OSError:
        pass


def _read_capped_log(handle) -> tuple[str, dict]:
    handle.flush()
    handle.seek(0)
    raw = handle.read(MAX_CAPTURE_BYTES + 1)
    captured = raw[:MAX_CAPTURE_BYTES]
    return captured.decode("utf-8", errors="replace"), {
        "captured_bytes": len(captured),
        "truncated": len(raw) > MAX_CAPTURE_BYTES,
        "sha256": hashlib.sha256(captured).hexdigest(),
    }


def _write_outcome(
    request: dict,
    repo_root: Path,
    payload: dict,
    *,
    guard_decision: dict,
    worker_result: dict | None,
    exit_reason: str,
    process_terminated: bool,
    duration_ms: int,
    return_code: int | None,
    stdout_log: dict,
    stderr_log: dict,
) -> dict:
    request_id = request["request_id"]
    completed = exit_reason == "completed" and bool(worker_result and worker_result.get("ok"))
    artifact_path = None
    if completed:
        content = str(worker_result.get("summary_markdown") or "")
        if not content or not _public_safe(content):
            completed = False
            exit_reason = "worker_output_refused"
        else:
            artifact_path = _write(repo_root, payload["artifact_path"], content)

    lifecycle_state = {
        "worker_timeout": "timed_out",
        "worker_cancelled": "cancelled",
    }.get(exit_reason, exit_reason)
    run_record = {
        "schema": "ghoti_local_agent_run/1",
        "request_id": request_id,
        "request_fingerprint": guard_decision.get("request_fingerprint"),
        "guard_version": guard_decision.get("guard_version"),
        "worker_id": payload["worker_id"],
        "task": payload["task"],
        "workflow_id": request.get("workflow_id"),
        "approval_state": "executed" if completed else "failed",
        "exit_reason": lifecycle_state,
        "return_code": return_code,
        "duration_ms": duration_ms,
        "processes_launched": 1,
        "process_terminated": process_terminated,
        "artifact_path": artifact_path,
        "input_evidence": (worker_result or {}).get("input_evidence", []),
        "worker_result_metadata": {
            "classification_tags": (worker_result or {}).get("classification_tags", []),
            "source_pointers": (worker_result or {}).get("source_pointers", []),
            "confidence": (worker_result or {}).get("confidence"),
            "uncertainty_note": (worker_result or {}).get("uncertainty_note"),
            "next_handoff_target": (worker_result or {}).get("next_handoff_target"),
            "model_mode": (worker_result or {}).get("model_mode", "not_applicable"),
            "provider_api_used": bool((worker_result or {}).get("provider_api_used")),
        },
        "stdout_log": stdout_log,
        "stderr_log": stderr_log,
        "network_used": False,
        "provider_api_used": bool((worker_result or {}).get("provider_api_used")),
        "model_mode": (worker_result or {}).get("model_mode", "not_applicable"),
        "external_write": False,
        "browser_used": False,
        "account_action": False,
        "mouse_keyboard_used": False,
        "model_output_as_command": False,
        "completed_at": _now(),
    }
    run_record_path = _write(
        repo_root,
        payload["run_record_path"],
        json.dumps(run_record, indent=2, sort_keys=True) + "\n",
    )
    evidence_lines = [
        "# Sandboxed Local Agent Process Evidence",
        "",
        f"- Request: `{request_id}`",
        f"- Rust fingerprint: `{guard_decision.get('request_fingerprint', 'missing')}`",
        f"- Worker: `{payload['worker_id']}`",
        f"- Task: `{payload['task']}`",
        f"- Exit reason: `{exit_reason}`",
        f"- Run record: `{run_record_path}`",
        f"- Artifact: `{artifact_path or 'not written'}`",
        "- Explicit approval and positive Rust guard decision: yes",
        "- Local agent processes launched: 1",
        "- Browser, accounts, posting, purchases, payments, mouse/keyboard: none",
        "- External writes and model-output-to-command: none",
        "",
    ]
    evidence_path = _write(repo_root, payload["evidence_path"], "\n".join(evidence_lines))
    handoff_lines = [
        "# Sandboxed Local Agent Run Handoff",
        "",
        f"- Request: `{request_id}`",
        f"- Result: `{exit_reason}`",
        f"- Artifact: `{artifact_path or 'not written'}`",
        f"- Evidence: `{evidence_path}`",
        "- Next action: review the evidence before proposing another worker run.",
        "",
    ]
    handoff_path = _write(repo_root, payload["handoff_path"], "\n".join(handoff_lines))
    return {
        "ok": completed,
        "reason": exit_reason,
        "request_id": request_id,
        "worker_id": payload["worker_id"],
        "task": payload["task"],
        "processes_launched": 1,
        "process_terminated": process_terminated,
        "local_agent_process_executed": True,
        "artifact_path": artifact_path,
        "run_record_path": run_record_path,
        "evidence_path": evidence_path,
        "handoff_path": handoff_path,
        "network_used": False,
        "provider_api_used": bool((worker_result or {}).get("provider_api_used")),
        "model_mode": (worker_result or {}).get("model_mode", "not_applicable"),
        "external_write": False,
        "model_output_as_command": False,
        "live_execution": False,
    }


def execute_allowlisted_worker_request(
    request: dict,
    repo_root: Path,
    *,
    guard_decision: dict,
) -> dict:
    """Launch one fixed worker and supervise timeout/cancel/final evidence."""
    repo_root = repo_root.resolve()
    try:
        payload, controls = _validate_request(request, guard_decision)
        worker_spec = WORKER_REGISTRY[payload["worker_id"]]
        worker_path = worker_spec["entrypoint"].resolve()
        if not worker_path.is_file():
            raise ValueError("allowlisted worker entrypoint is missing")
        state_path, _ = _destination(
            repo_root, controls["runner_state_path"], ALLOWED_OUTPUT_ROOTS
        )
        cancel_path, _ = _destination(repo_root, controls["cancel_path"], ALLOWED_OUTPUT_ROOTS)
        active_path, _ = _destination(
            repo_root, controls["active_lock_path"], ALLOWED_OUTPUT_ROOTS
        )
    except (OSError, ValueError, KeyError) as error:
        return {"ok": False, "reason": "runner_request_refused", "error": str(error)}

    if not _write_active_lock(active_path, request["request_id"]):
        return {"ok": False, "reason": "another_worker_is_active"}
    _safe_unlink(cancel_path)
    _write(
        repo_root,
        controls["runner_state_path"],
        json.dumps(
            {
                "schema": "ghoti_runner_state/1",
                "request_id": request["request_id"],
                "worker_id": payload["worker_id"],
                "status": "running",
                "started_at": _now(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    invocation = {
        "schema": "ghoti_local_worker_invocation/1",
        "request_id": request["request_id"],
        "worker_id": payload["worker_id"],
        "task": payload["task"],
        "workflow_id": request.get("workflow_id"),
        "repo_root": str(repo_root),
        "input_paths": request.get("input_paths") or [],
        "wait_seconds": payload.get("wait_seconds", 0),
    }
    started = time.monotonic()
    process_terminated = False
    exit_reason = "worker_failed"
    worker_result = None
    return_code = None
    process = None
    stdout_text = ""
    stdout_log = {"captured_bytes": 0, "truncated": False, "sha256": hashlib.sha256(b"").hexdigest()}
    stderr_log = dict(stdout_log)
    stdout_file = tempfile.TemporaryFile(mode="w+b")
    stderr_file = tempfile.TemporaryFile(mode="w+b")
    try:
        process = subprocess.Popen(
            [sys.executable, str(worker_path), *worker_spec["fixed_args"]],
            cwd=str(worker_path.parent),
            env=_minimal_environment(),
            stdin=subprocess.PIPE,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
            shell=False,
        )
        assert process.stdin is not None
        process.stdin.write(json.dumps(invocation))
        process.stdin.close()
        process.stdin = None
        while process.poll() is None:
            if cancel_path.is_file():
                process_terminated = _terminate(process)
                exit_reason = "worker_cancelled"
                break
            if time.monotonic() - started >= int(request["max_runtime_seconds"]):
                process_terminated = _terminate(process)
                exit_reason = "worker_timeout"
                break
            time.sleep(POLL_SECONDS)
        process.wait(timeout=TERMINATE_GRACE_SECONDS)
        return_code = process.returncode
        stdout_text, stdout_log = _read_capped_log(stdout_file)
        _stderr_text, stderr_log = _read_capped_log(stderr_file)
        if exit_reason not in {"worker_cancelled", "worker_timeout"}:
            if stdout_log["truncated"]:
                exit_reason = "worker_output_too_large"
            elif process.returncode == 0:
                try:
                    worker_result = json.loads(stdout_text)
                except json.JSONDecodeError:
                    exit_reason = "worker_output_invalid"
                else:
                    exit_reason = "completed" if worker_result.get("ok") else "worker_failed"
            else:
                exit_reason = "worker_failed"
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        exit_reason = "worker_launch_failed"
        worker_result = {"error": str(error)}
    finally:
        if process is not None and process.poll() is None:
            process_terminated = _terminate(process) or process_terminated
            return_code = process.returncode
        duration_ms = int((time.monotonic() - started) * 1000)
        _safe_unlink(active_path)
        stdout_file.close()
        stderr_file.close()

    outcome = _write_outcome(
        request,
        repo_root,
        payload,
        guard_decision=guard_decision,
        worker_result=worker_result,
        exit_reason=exit_reason,
        process_terminated=process_terminated,
        duration_ms=duration_ms,
        return_code=return_code,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
    )
    _write(
        repo_root,
        controls["runner_state_path"],
        json.dumps(
            {
                "schema": "ghoti_runner_state/1",
                "request_id": request["request_id"],
                "worker_id": payload["worker_id"],
                "status": outcome["reason"],
                "run_record_path": outcome["run_record_path"],
                "artifact_path": outcome["artifact_path"],
                "completed_at": _now(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    return outcome


def cancel_worker(request_id: str, repo_root: Path = SOURCE_REPO_ROOT) -> dict:
    if not REQUEST_ID_RE.match(request_id):
        return {"ok": False, "action": "cancel-worker", "reason": "invalid_request_id"}
    repo_root = repo_root.resolve()
    active_path = repo_root / _fixed_control_paths(request_id)["active_lock_path"]
    try:
        active = json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "action": "cancel-worker", "reason": "worker_not_active"}
    if active.get("request_id") != request_id:
        return {"ok": False, "action": "cancel-worker", "reason": "different_worker_active"}
    cancel_path = _fixed_control_paths(request_id)["cancel_path"]
    try:
        written = _write(
            repo_root,
            cancel_path,
            json.dumps(
                {
                    "schema": "ghoti_worker_cancel/1",
                    "request_id": request_id,
                    "requested_at": _now(),
                    "requested_by": "human-cli",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
    except (OSError, ValueError) as error:
        return {"ok": False, "action": "cancel-worker", "reason": str(error)}
    return {
        "ok": True,
        "action": "cancel-worker",
        "request_id": request_id,
        "cancel_path": written,
        "human_approval_required": True,
    }


def runner_status(repo_root: Path = SOURCE_REPO_ROOT) -> dict:
    repo_root = repo_root.resolve()
    control = repo_root / "14_context" / "agent_os" / "runner_control"
    active = None
    active_path = control / "active_worker.json"
    if active_path.is_file():
        try:
            active = json.loads(active_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            active = {"status": "unreadable"}
    states = []
    if control.is_dir():
        for path in sorted(control.glob("state_req-*.json")):
            try:
                states.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    return {
        "ok": True,
        "action": "runner-status",
        "worker_allowlist": sorted(WORKER_REGISTRY),
        "worker_registry_fingerprint": WORKER_REGISTRY_FINGERPRINT,
        "active_worker": active,
        "active_count": 1 if active else 0,
        "latest_state": states[-1] if states else None,
        "latest_local_model_state": next(
            (
                state
                for state in reversed(states)
                if state.get("worker_id")
                == "local-model-summary-classification-worker"
            ),
            None,
        ),
        "local_process_execution_enabled": True,
        "external_live_execution_enabled": False,
        "human_approval_required": True,
        "model_output_as_command": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ghoti sandboxed local agent runner")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--cancel", metavar="REQUEST_ID")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if args.status:
        payload = runner_status()
    elif args.cancel:
        payload = cancel_worker(args.cancel)
    else:
        parser.print_help()
        return 2
    print(json.dumps(payload, indent=2) if args.as_json else payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
