#!/usr/bin/env python3
"""Guard local model output against invented repo sources and unsafe claims.

N+6.1A keeps Gemma useful for small offline tasks without trusting free-form
model text. The guard accepts only known repo knowledge bundle IDs and source
files from the generated repo map, requires explicit source metadata, and
rejects live/API/action claims. It never executes model output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
REPO_MAP_PATH = REPO_ROOT / "14_context" / "repo_knowledge" / "generated" / "repo_knowledge_map.json"

FALLBACK_BUNDLE_IDS = [
    "audit-main",
    "dashboard",
    "local-memory",
    "local-model-worker",
    "local-model-routing",
    "hermes",
    "content-workflow",
    "safety",
    "next-milestone",
]

FALLBACK_FILE_PATHS = [
    "README.md",
    "03_scripts/local_model_worker_lane.py",
    "03_scripts/gemma_model_readiness.py",
    "03_scripts/ghoti_repo_knowledge_map.py",
    "03_scripts/ghoti_context_pack_builder.py",
    "14_context/compact_memory/generated/ghoti_codex_next_prompt.md",
    "14_context/compact_memory/generated/ghoti_current_context_pack.md",
    "14_context/repo_knowledge/generated/task_bundle_next_milestone.md",
    "14_context/repo_knowledge/generated/task_bundle_local_model_worker.md",
    "14_context/repo_knowledge/generated/task_bundle_local_model_routing.md",
    "14_context/repo_knowledge/generated/repo_knowledge_map.json",
]

SAFE_ROUTED_TASKS = [
    "summarize-latest-report",
    "status-paragraph",
    "codex-next-prompt",
    "safety-classification",
    "context-bundle-summary",
    "next-milestone-outline",
    "report-to-bullets",
]

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"https?://", re.IGNORECASE),
    re.compile(r"\bgit(?:hub)?\.com\b", re.IGNORECASE),
    re.compile(r"\btelegram\s+(?:is\s+)?(?:configured|working|enabled)\b", re.IGNORECASE),
    re.compile(r"\bbrowser(?:/playwright)?\s+(?:is\s+)?(?:working|enabled|fixed)\b", re.IGNORECASE),
    re.compile(r"\bproduction routing\s+(?:is\s+)?enabled\b", re.IGNORECASE),
    re.compile(r"\blive api(?:s)?\s+(?:used|enabled)\b", re.IGNORECASE),
    re.compile(r"\bprovider\s+setup\s+(?:done|configured|enabled)\b", re.IGNORECASE),
]


def _repo_rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _load_json(path: pathlib.Path) -> Dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _normalize_path(value: object) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    return raw


def load_repo_catalog(map_path: pathlib.Path | None = None) -> Dict[str, object]:
    """Load known bundle IDs and source files from the generated repo map."""
    path = map_path or REPO_MAP_PATH
    data = _load_json(path)
    bundle_ids = set(str(item) for item in data.get("task_bundles", []) if item)
    file_paths = set()

    for item in data.get("important_files", []) or []:
        if isinstance(item, dict) and item.get("path"):
            file_paths.add(_normalize_path(item["path"]))
    for item in data.get("latest_reports", []) or []:
        if isinstance(item, dict) and item.get("path"):
            file_paths.add(_normalize_path(item["path"]))
    for mapping_name in ("output_paths", "task_bundle_paths"):
        mapping = data.get(mapping_name) or {}
        if isinstance(mapping, dict):
            for value in mapping.values():
                file_paths.add(_normalize_path(value))

    bundle_ids.update(FALLBACK_BUNDLE_IDS)
    file_paths.update(FALLBACK_FILE_PATHS)
    file_paths = {path for path in file_paths if path and not path.startswith("http")}

    return {
        "ok": True,
        "map_path": _repo_rel(path),
        "bundle_ids": sorted(bundle_ids),
        "file_paths": sorted(file_paths),
        "bundle_count": len(bundle_ids),
        "file_count": len(file_paths),
    }


def _json_candidate(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    if "{" in stripped and "}" in stripped:
        return stripped[stripped.find("{"):stripped.rfind("}") + 1]
    return stripped


def _parse_output(output: object) -> Tuple[Dict[str, object] | None, str]:
    if isinstance(output, dict):
        return output, json.dumps(output, sort_keys=True)
    text = str(output or "")
    try:
        parsed = json.loads(_json_candidate(text))
    except Exception:
        return None, text
    return parsed if isinstance(parsed, dict) else None, text


def _as_list(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def validate_model_output(
    output: object,
    task: str,
    catalog: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Validate one routed model response against repo-source and safety rules."""
    normalized_task = str(task or "").strip().lower()
    catalog_payload = catalog or load_repo_catalog()
    known_bundles = set(catalog_payload.get("bundle_ids") or [])
    known_files = set(catalog_payload.get("file_paths") or [])
    parsed, raw_text = _parse_output(output)
    reasons: List[str] = []
    warnings: List[str] = []

    if normalized_task not in SAFE_ROUTED_TASKS:
        reasons.append("unsupported routed task")

    if parsed is None:
        reasons.append("model output is not valid JSON with source_metadata")
        metadata = {}
    else:
        metadata = parsed.get("source_metadata")
        if not isinstance(metadata, dict):
            reasons.append("missing required source_metadata block")
            metadata = {}

    bundle_ids = _as_list(metadata.get("bundle_ids"))
    file_paths = [_normalize_path(path) for path in _as_list(metadata.get("file_paths"))]

    if not bundle_ids:
        reasons.append("source_metadata.bundle_ids is required")
    if not file_paths:
        reasons.append("source_metadata.file_paths is required")

    for bundle in bundle_ids:
        if bundle not in known_bundles:
            reasons.append(f"invented or unsupported bundle: {bundle}")
    for source_path in file_paths:
        if source_path not in known_files:
            reasons.append(f"unknown source file: {source_path}")

    local_only = metadata.get("local_only")
    live_api_used = metadata.get("live_api_used")
    if local_only is not True:
        reasons.append("source_metadata.local_only must be true")
    if live_api_used is not False:
        reasons.append("source_metadata.live_api_used must be false")

    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(raw_text):
            reasons.append(f"forbidden or unsupported claim matched: {pattern.pattern}")

    answer = ""
    if isinstance(parsed, dict):
        answer = str(parsed.get("answer") or parsed.get("summary") or parsed.get("text") or "")
    if parsed is not None and not answer.strip():
        warnings.append("model output has source metadata but no answer text")

    status = "reject" if reasons else ("warn" if warnings else "pass")
    return {
        "ok": status in ("pass", "warn"),
        "status": status,
        "task": normalized_task,
        "local_only": local_only is True,
        "live_api_used": live_api_used is True,
        "bundle_ids": bundle_ids,
        "file_paths": file_paths,
        "known_bundle_count": len(known_bundles),
        "known_file_count": len(known_files),
        "reasons": reasons,
        "warnings": warnings,
        "requires_fallback": status == "reject",
    }


def fallback_guard_result(original_result: Dict[str, object], fallback_reason: str) -> Dict[str, object]:
    return {
        "ok": True,
        "status": "fallback_used",
        "task": original_result.get("task"),
        "local_only": True,
        "live_api_used": False,
        "bundle_ids": original_result.get("bundle_ids") or [],
        "file_paths": original_result.get("file_paths") or [],
        "known_bundle_count": original_result.get("known_bundle_count", 0),
        "known_file_count": original_result.get("known_file_count", 0),
        "reasons": list(original_result.get("reasons") or []) + [fallback_reason],
        "warnings": original_result.get("warnings") or [],
        "requires_fallback": False,
    }


def self_test() -> Dict[str, object]:
    catalog = load_repo_catalog()
    valid = validate_model_output({
        "answer": "Use the next milestone bundle.",
        "source_metadata": {
            "bundle_ids": ["next-milestone"],
            "file_paths": ["14_context/repo_knowledge/generated/task_bundle_next_milestone.md"],
            "local_only": True,
            "live_api_used": False,
        },
    }, task="context-bundle-summary", catalog=catalog)
    invented_bundle = validate_model_output({
        "answer": "Use StableLM-DanceDiffusion.",
        "source_metadata": {
            "bundle_ids": ["StableLM-DanceDiffusion"],
            "file_paths": ["14_context/repo_knowledge/generated/task_bundle_next_milestone.md"],
            "local_only": True,
            "live_api_used": False,
        },
    }, task="context-bundle-summary", catalog=catalog)
    unknown_file = validate_model_output({
        "answer": "Use an unknown file.",
        "source_metadata": {
            "bundle_ids": ["next-milestone"],
            "file_paths": ["docs/DOES_NOT_EXIST.md"],
            "local_only": True,
            "live_api_used": False,
        },
    }, task="status-paragraph", catalog=catalog)
    checks = {
        "valid_metadata_passed": valid["status"] == "pass",
        "invented_bundle_rejected": invented_bundle["status"] == "reject",
        "unknown_file_rejected": unknown_file["status"] == "reject",
    }
    return {
        "ok": all(checks.values()),
        "action": "self-test",
        "local_only": True,
        "live_api_used": False,
        "guard_enabled": True,
        "checks": checks,
        "catalog": {
            "bundle_count": catalog["bundle_count"],
            "file_count": catalog["file_count"],
            "bundle_ids": catalog["bundle_ids"],
        },
        "results": {
            "valid": valid,
            "invented_bundle": invented_bundle,
            "unknown_file": unknown_file,
        },
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local model output against Ghoti repo source guards.")
    parser.add_argument("--self-test", action="store_true", help="run built-in guard self-test")
    parser.add_argument("--task", default="status-paragraph", help="routed task name for --output validation")
    parser.add_argument("--output", help="model output JSON/text to validate")
    parser.add_argument("--status", action="store_true", help="show guard catalog/status")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if args.self_test:
        payload = self_test()
    elif args.output is not None:
        payload = validate_model_output(args.output, task=args.task)
    else:
        catalog = load_repo_catalog()
        payload = {
            "ok": True,
            "action": "status",
            "local_only": True,
            "live_api_used": False,
            "guard_enabled": True,
            "safe_routed_tasks": SAFE_ROUTED_TASKS,
            "catalog": catalog,
        }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
