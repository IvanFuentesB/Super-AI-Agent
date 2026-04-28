"""Local brain router — preview only.

Loads policy from 23_configs/local_brain_router_policy.example.json.
Runs one safe local task via ollama. Writes artifacts to
05_logs/local_brain_runs/<run_id>/. Does not call any external API.
Does not execute model output. Does not edit the repo from model output.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_POLICY_PATH = _REPO_ROOT / "23_configs" / "local_brain_router_policy.example.json"
_LOG_ROOT = _REPO_ROOT / "05_logs" / "local_brain_runs"

_PREVIEW_TASK_TYPE = "draft_checklist"
_PREVIEW_PROMPT = (
    "Create a 5 item checklist for validating a local-only AI agent task before execution."
)
_TIMEOUT_SECONDS = 90


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_write(path: Path, text: str) -> None:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    ps_path = str(path).replace("'", "''")
    ps_dir = str(path.parent).replace("'", "''")
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            (
                f"New-Item -ItemType Directory -Force -Path '{ps_dir}' | Out-Null; "
                f"[System.IO.File]::WriteAllBytes('{ps_path}', "
                f"[Convert]::FromBase64String('{encoded}'))"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _write_artifact(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError:
        _ps_write(path, content)


def _load_policy() -> dict:
    if not _POLICY_PATH.exists():
        return {}
    try:
        return json.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[local_brain_router] WARNING: could not load policy: {exc}", file=sys.stderr)
        return {}


def _ensure_run_dir(run_dir: Path) -> None:
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        ps_dir = str(run_dir).replace("'", "''")
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                f"New-Item -ItemType Directory -Force -Path '{ps_dir}' | Out-Null",
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def run_preview(policy: dict) -> int:
    model = policy.get("default_local_model", "gemma3:4b")
    provider = policy.get("local_provider", "ollama")
    run_id = f"preview_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = _LOG_ROOT / run_id
    _ensure_run_dir(run_dir)

    print(f"[local_brain_router] PREVIEW MODE — enabled=false, routing_mode=preview_only")
    print(f"[local_brain_router] provider={provider} model={model}")
    print(f"[local_brain_router] task_type={_PREVIEW_TASK_TYPE}")
    print(f"[local_brain_router] run_dir={run_dir.relative_to(_REPO_ROOT)}")
    print()

    request_data = {
        "run_id": run_id,
        "mode": "preview_only",
        "enabled": False,
        "provider": provider,
        "model": model,
        "task_type": _PREVIEW_TASK_TYPE,
        "prompt": _PREVIEW_PROMPT,
        "api_usage": "none",
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "request.json", json.dumps(request_data, indent=2) + "\n")

    cmd = [provider, "run", model, _PREVIEW_PROMPT]
    print(f"[local_brain_router] running: {' '.join(cmd[:3])} <prompt>")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=_TIMEOUT_SECONDS,
        )
        exit_code = result.returncode
        raw_out = result.stdout or b""
        raw_err = result.stderr or b""
        # Strip ANSI/VT escape sequences before decoding
        import re as _re
        ansi_escape = _re.compile(rb'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        raw_out = ansi_escape.sub(b"", raw_out)
        raw_err = ansi_escape.sub(b"", raw_err)
        stdout = raw_out.decode("utf-8", errors="replace").strip()
        stderr = raw_err.decode("utf-8", errors="replace").strip()
    except FileNotFoundError:
        print(f"[local_brain_router] ERROR: '{provider}' not found on PATH.", file=sys.stderr)
        _write_artifact(run_dir / "response.txt", "ERROR: provider not found on PATH\n")
        _write_artifact(
            run_dir / "summary.md",
            f"# Local Brain Router Preview — {run_id}\n\n"
            f"Status: FAIL\nReason: {provider} not found on PATH\n"
            f"API usage: none\nModel: {model}\n",
        )
        return 1
    except subprocess.TimeoutExpired:
        print(
            f"[local_brain_router] ERROR: inference timed out after {_TIMEOUT_SECONDS}s.",
            file=sys.stderr,
        )
        _write_artifact(run_dir / "response.txt", f"ERROR: timed out after {_TIMEOUT_SECONDS}s\n")
        _write_artifact(
            run_dir / "summary.md",
            f"# Local Brain Router Preview — {run_id}\n\n"
            f"Status: FAIL\nReason: timeout after {_TIMEOUT_SECONDS}s\n"
            f"API usage: none\nModel: {model}\n",
        )
        return 1

    response_text = stdout if stdout else f"(no stdout)\nstderr: {stderr}"
    _write_artifact(run_dir / "response.txt", response_text + "\n")

    status = "PASS" if exit_code == 0 else "FAIL"
    summary = (
        f"# Local Brain Router Preview — {run_id}\n\n"
        f"Date: {_utc_now()}\n"
        f"Status: {status}\n"
        f"Mode: preview_only (enabled=false)\n"
        f"Provider: {provider}\n"
        f"Model: {model}\n"
        f"Task type: {_PREVIEW_TASK_TYPE}\n"
        f"Exit code: {exit_code}\n"
        f"API usage: none\n"
        f"External calls: none\n"
        f"Model output executed: NO\n"
        f"Repo edits from model output: NO\n\n"
        f"## Prompt\n\n{_PREVIEW_PROMPT}\n\n"
        f"## Response\n\n{response_text}\n"
    )
    _write_artifact(run_dir / "summary.md", summary)

    print(f"[local_brain_router] exit_code={exit_code} status={status}")
    print()
    print("--- response ---")
    safe_display = response_text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
        sys.stdout.encoding or "utf-8", errors="replace"
    )
    print(safe_display)
    print("--- end ---")
    print()
    print(f"[local_brain_router] artifacts written to: {run_dir.relative_to(_REPO_ROOT)}")
    return exit_code


def main() -> int:
    preview = "--preview" in sys.argv
    policy = _load_policy()

    if not preview:
        print("[local_brain_router] No --preview flag. Pass --preview to run the preview task.")
        print(f"  Policy: enabled={policy.get('enabled', False)}")
        print(f"  Routing mode: {policy.get('routing_mode', 'unknown')}")
        return 0

    return run_preview(policy)


if __name__ == "__main__":
    sys.exit(main())
