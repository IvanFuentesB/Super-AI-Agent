"""Fixed, process-isolated repo summary worker for Ghoti Agent OS.

The worker reads one JSON invocation from stdin and writes one JSON result to
stdout. It has no process, network, command, or file-write surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path, PurePosixPath


WORKER_ID = "repo-summary-worker"
ALLOWED_TASKS = {"repo_status_summary", "bounded_wait_probe"}
INPUT_ROOTS = ("14_context/", "docs/")
MAX_INPUT_BYTES = 64 * 1024
MAX_INPUT_FILES = 8


def _normalize_repo_path(raw: object) -> str:
    text = str(raw or "").strip().replace("\\", "/")
    path = PurePosixPath(text)
    if (
        not text
        or path.is_absolute()
        or ":" in text
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError("input path must be normalized and repo-relative")
    normalized = path.as_posix()
    if not any(normalized.startswith(root) for root in INPUT_ROOTS):
        raise ValueError("input path is outside worker read roots")
    return normalized


def _first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if clean:
            return clean[:200]
    return "(empty file)"


def _read_inputs(repo_root: Path, raw_paths: list[object]) -> list[dict]:
    if len(raw_paths) > MAX_INPUT_FILES:
        raise ValueError("too many input paths")
    evidence = []
    for raw_path in raw_paths:
        relative = _normalize_repo_path(raw_path)
        source = (repo_root / relative).resolve()
        source.relative_to(repo_root)
        if not source.is_file():
            raise ValueError(f"input file is missing: {relative}")
        data = source.read_bytes()
        if len(data) > MAX_INPUT_BYTES:
            raise ValueError(f"input file is too large: {relative}")
        text = data.decode("utf-8", errors="replace")
        evidence.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "first_nonempty_line": _first_nonempty_line(text),
            }
        )
    return evidence


def run(invocation: dict) -> dict:
    if invocation.get("schema") != "ghoti_local_worker_invocation/1":
        raise ValueError("unsupported worker invocation schema")
    if invocation.get("worker_id") != WORKER_ID:
        raise ValueError("worker id is not allowlisted")
    task = str(invocation.get("task") or "")
    if task not in ALLOWED_TASKS:
        raise ValueError("worker task is not allowlisted")

    repo_root = Path(str(invocation.get("repo_root") or "")).resolve()
    if not repo_root.is_dir():
        raise ValueError("repo root is unavailable")
    input_evidence = _read_inputs(repo_root, list(invocation.get("input_paths") or []))

    if task == "bounded_wait_probe":
        wait_seconds = float(invocation.get("wait_seconds") or 0)
        if not 0 <= wait_seconds <= 5:
            raise ValueError("wait probe must be between 0 and 5 seconds")
        time.sleep(wait_seconds)

    lines = [
        "# Sandboxed Local Agent Result",
        "",
        f"- Worker: `{WORKER_ID}`",
        f"- Task: `{task}`",
        f"- Request: `{invocation.get('request_id', 'unknown')}`",
        "- Process isolation: fixed stdin/stdout JSON protocol",
        "- Network used: false",
        "- Commands executed from model output: false",
        "",
        "## Repo-local source evidence",
        "",
    ]
    for item in input_evidence:
        lines.append(
            f"- `{item['path']}` sha256 `{item['sha256']}`: "
            f"{item['first_nonempty_line']}"
        )
    lines.append("")
    return {
        "schema": "ghoti_local_worker_result/1",
        "ok": True,
        "worker_id": WORKER_ID,
        "task": task,
        "request_id": invocation.get("request_id"),
        "summary_markdown": "\n".join(lines),
        "input_evidence": input_evidence,
        "network_used": False,
        "writes_files": False,
        "model_output_as_command": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ghoti fixed repo summary worker")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.json:
        parser.error("--json is required")
    try:
        invocation = json.loads(sys.stdin.read())
        payload = run(invocation)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        payload = {
            "schema": "ghoti_local_worker_result/1",
            "ok": False,
            "worker_id": WORKER_ID,
            "reason": "worker_input_refused",
            "error": str(error),
            "network_used": False,
            "writes_files": False,
            "model_output_as_command": False,
        }
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
