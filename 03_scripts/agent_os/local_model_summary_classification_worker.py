"""Deterministic local summary and classification worker."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


WORKER_ID = "local-model-summary-classification-worker"
INPUT_ROOTS = ("14_context/", "docs/")
MAX_INPUT_BYTES = 64 * 1024
MAX_INPUT_FILES = 8


def _normalize(raw: object) -> str:
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


def _read_sources(repo_root: Path, raw_paths: list[object]) -> tuple[list[dict], str]:
    if len(raw_paths) > MAX_INPUT_FILES:
        raise ValueError("too many input paths")
    pointers = []
    excerpts = []
    for raw in raw_paths:
        relative = _normalize(raw)
        source = (repo_root / relative).resolve()
        source.relative_to(repo_root)
        data = source.read_bytes()
        if len(data) > MAX_INPUT_BYTES:
            raise ValueError(f"input file is too large: {relative}")
        text = data.decode("utf-8", errors="replace")
        excerpts.append(text)
        pointers.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        )
    return pointers, "\n".join(excerpts)


def _classify(text: str) -> tuple[list[str], str]:
    lowered = text.lower()
    tags = ["local-first", "supervised"]
    if "rust" in lowered or "guard" in lowered:
        tags.append("safety-guard")
    if "approval" in lowered:
        tags.append("approval-gated")
    if "browser" in lowered or "account" in lowered:
        tags.append("blocked-live-actions")
    target = "Codex" if "test" in lowered or "guard" in lowered else "Hermes"
    return sorted(set(tags)), target


def run(invocation: dict) -> dict:
    if invocation.get("schema") != "ghoti_local_worker_invocation/1":
        raise ValueError("unsupported worker invocation schema")
    if invocation.get("worker_id") != WORKER_ID:
        raise ValueError("worker id is not allowlisted")
    if invocation.get("task") != "summary_classification":
        raise ValueError("worker task is not allowlisted")
    repo_root = Path(str(invocation.get("repo_root") or "")).resolve()
    if not repo_root.is_dir():
        raise ValueError("repo root is unavailable")
    pointers, source_text = _read_sources(
        repo_root, list(invocation.get("input_paths") or [])
    )
    tags, target = _classify(source_text)
    summary = (
        "The reviewed repo-local context describes a supervised, local-first "
        "Agent OS path with explicit approval and safety boundaries."
    )
    lines = [
        "# Local Model Summary and Classification",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## Classification tags",
        "",
        *[f"- `{tag}`" for tag in tags],
        "",
        "## Source pointers",
        "",
        *[f"- `{item['path']}` sha256 `{item['sha256']}`" for item in pointers],
        "",
        "## Confidence and uncertainty",
        "",
        "- Confidence: medium",
        "- Uncertainty: deterministic fallback summarizes only declared local inputs.",
        "",
        "## Next suggested handoff target",
        "",
        f"- {target}",
        "",
    ]
    return {
        "schema": "ghoti_local_worker_result/1",
        "ok": True,
        "worker_id": WORKER_ID,
        "task": "summary_classification",
        "request_id": invocation.get("request_id"),
        "summary_markdown": "\n".join(lines),
        "input_evidence": pointers,
        "source_pointers": pointers,
        "classification_tags": tags,
        "confidence": "medium",
        "uncertainty_note": "Deterministic fallback summarizes only declared local inputs.",
        "next_handoff_target": target,
        "model_mode": "deterministic_local_fallback",
        "provider_api_used": False,
        "network_used": False,
        "writes_files": False,
        "model_output_as_command": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ghoti local summary classifier")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.json:
        parser.error("--json is required")
    try:
        payload = run(json.loads(sys.stdin.read()))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        payload = {
            "schema": "ghoti_local_worker_result/1",
            "ok": False,
            "worker_id": WORKER_ID,
            "reason": "worker_input_refused",
            "error": str(error),
            "provider_api_used": False,
            "network_used": False,
            "writes_files": False,
            "model_output_as_command": False,
        }
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
