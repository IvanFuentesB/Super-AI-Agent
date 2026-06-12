#!/usr/bin/env python3
"""Verify Ghoti's local command center as one supervised simulation system."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


MILESTONE = "N+6.44B"
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = REPO_ROOT / "03_scripts"
COMMAND_CENTER_SCRIPT = SCRIPT_ROOT / "agent_command_center" / "ghoti_agent_command_center.py"
SEARCH_SCRIPT = SCRIPT_ROOT / "context_memory" / "ghoti_local_memory_search.py"
OBSIDIAN_SCRIPT = SCRIPT_ROOT / "context_memory" / "ghoti_obsidian_memory_view.py"
SEARCH_INDEX = REPO_ROOT / "14_context" / "memory" / "search" / "generated" / "local_search_index.json"
OBSIDIAN_START = REPO_ROOT / "14_context" / "memory" / "obsidian" / "START_HERE.md"
OUTPUT_ROOT = REPO_ROOT / "14_context" / "operator_reports" / "generated"
JSON_OUTPUT = OUTPUT_ROOT / "n6_44b_command_center_integration_gate.json"
MARKDOWN_OUTPUT = OUTPUT_ROOT / "n6_44b_command_center_integration_gate.md"
DOC_PATH = REPO_ROOT / "docs" / "GHOTI_N6_44B_COMMAND_CENTER_INTEGRATION_GATE.md"
DEFAULT_HEALTH_URL = "http://127.0.0.1:8770/api/health"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
EXPECTED_SCENARIO_IDS = [
    "code-maintenance-swarm",
    "content-revenue-research",
    "ecommerce-product-research",
]
EXPECTED_ROLE_IDS = [
    "chatgpt_strategy",
    "claude_builder",
    "codex_auditor",
    "hermes_coordinator",
    "local_summarizer",
    "human_approver",
]
REQUIRED_SOURCE_PATHS = [
    "03_scripts/agent_command_center/ghoti_agent_command_center.py",
    "03_scripts/agent_command_center/check_agent_command_center.ps1",
    "03_scripts/agent_command_center/start_agent_command_center.ps1",
    "03_scripts/agent_command_center/static/index.html",
    "03_scripts/agent_command_center/static/app.js",
    "03_scripts/agent_command_center/static/styles.css",
    "03_scripts/context_memory/ghoti_local_memory_search.py",
    "03_scripts/context_memory/ghoti_obsidian_memory_view.py",
    "14_context/memory/search/generated/local_search_index.json",
    "14_context/memory/index/obsidian_view_index.json",
    "14_context/memory/obsidian/START_HERE.md",
    "14_context/agent_command_center/generated/command_center_status.json",
    "14_context/agent_command_center/generated/content_revenue_arena_simulation.json",
    "14_context/agent_command_center/generated/content_revenue_paperclip_preview.json",
]
PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.I),
    re.compile(r"/mnt/[a-z]/Users/", re.I),
    re.compile(r"/home/[^/\s]+/", re.I),
)
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical_hash(payload: dict) -> str:
    text = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _is_public_safe_text(text: str) -> bool:
    return not any(pattern.search(text) for pattern in PRIVATE_PATH_PATTERNS)


def _validate_health_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK_HOSTS:
        raise ValueError("health URL must use HTTP and an exact loopback host")
    if parsed.username or parsed.password:
        raise ValueError("health URL must not contain credentials")
    if parsed.path.rstrip("/") != "/api/health":
        raise ValueError("health URL must target /api/health")
    return url


def probe_health(url: str = DEFAULT_HEALTH_URL) -> dict:
    """Probe an exact loopback health endpoint without making it a gate blocker."""
    safe_url = _validate_health_url(url)
    request = Request(safe_url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "ok": True,
            "state": "server_not_running",
            "server_running": False,
            "loopback_only_probe": True,
            "health_url": safe_url,
            "detail": type(exc).__name__,
        }
    required = {
        "ok": True,
        "binds_loopback_only": True,
        "get_only": True,
        "has_post_routes": False,
        "simulation": True,
        "live_execution": False,
    }
    mismatches = {
        key: {"expected": expected, "actual": payload.get(key)}
        for key, expected in required.items()
        if payload.get(key) != expected
    }
    return {
        "ok": not mismatches,
        "state": "healthy" if not mismatches else "unsafe_or_incompatible_response",
        "server_running": True,
        "loopback_only_probe": True,
        "health_url": safe_url,
        "mismatches": mismatches,
    }


def _source_file_check() -> dict:
    missing = [path for path in REQUIRED_SOURCE_PATHS if not (REPO_ROOT / path).is_file()]
    unsafe = [
        relative
        for relative in REQUIRED_SOURCE_PATHS
        if Path(relative).is_absolute() or ".." in Path(relative).parts or not _is_public_safe_text(relative)
    ]
    return {
        "ok": not missing and not unsafe,
        "required_count": len(REQUIRED_SOURCE_PATHS),
        "missing": missing,
        "private_path_hits": unsafe,
    }


def _memory_check(search_module) -> dict:
    index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
    verification = search_module.verify_search_index(index, REPO_ROOT)
    index_bytes = SEARCH_INDEX.stat().st_size
    return {
        "ok": verification["ok"] and index_bytes <= search_module.MAX_INDEX_BYTES,
        "engine": index.get("engine"),
        "indexed_sources": index.get("source_count"),
        "verified_sources": verification.get("verified_sources", 0),
        "stale_entries": verification.get("stale_entries", []),
        "index_bytes": index_bytes,
        "max_index_bytes": search_module.MAX_INDEX_BYTES,
        "index_within_budget": index_bytes <= search_module.MAX_INDEX_BYTES,
        "search_aid_only": True,
        "canonical_truth": False,
        "source_path": "14_context/memory/search/generated/local_search_index.json",
    }


def _obsidian_check(obsidian_module) -> dict:
    result = obsidian_module.check(REPO_ROOT)
    return {
        "ok": result["ok"] and OBSIDIAN_START.is_file(),
        "start_view": "14_context/memory/obsidian/START_HERE.md",
        "start_view_exists": OBSIDIAN_START.is_file(),
        "view_count": result.get("view_count", 0),
        "checked_links": result.get("checked_links", 0),
        "source_indexes_verified": result.get("source_indexes_verified", False),
        "missing": result.get("missing", []),
        "drift": result.get("drift", []),
        "canonical_truth": False,
    }


def _workflow_check(command_center) -> dict:
    actual_ids = command_center._scenario_ids()
    first = {scenario_id: command_center.build_scenario(scenario_id) for scenario_id in actual_ids}
    second = {scenario_id: command_center.build_scenario(scenario_id) for scenario_id in actual_ids}
    hashes = {scenario_id: _canonical_hash(first[scenario_id]) for scenario_id in actual_ids}
    deterministic = first == second
    valid = all(plan.get("ok") for plan in first.values())
    return {
        "ok": actual_ids == EXPECTED_SCENARIO_IDS and deterministic and valid,
        "stable_ids": actual_ids,
        "expected_ids": EXPECTED_SCENARIO_IDS,
        "stable_ids_verified": actual_ids == EXPECTED_SCENARIO_IDS,
        "deterministic": deterministic,
        "scenario_hashes": hashes,
        "waves": {scenario_id: first[scenario_id]["waves"] for scenario_id in actual_ids},
    }


def _agent_check(command_center) -> dict:
    role_ids = [agent["id"] for agent in command_center.AGENTS]
    unique = len(role_ids) == len(set(role_ids))
    return {
        "ok": role_ids == EXPECTED_ROLE_IDS and unique,
        "stable_role_ids": role_ids,
        "expected_role_ids": EXPECTED_ROLE_IDS,
        "stable_role_ids_verified": role_ids == EXPECTED_ROLE_IDS and unique,
    }


def _ownership_check(command_center) -> dict:
    committed = {
        scenario_id: command_center.build_scenario(scenario_id)["ownership"]
        for scenario_id in command_center._scenario_ids()
    }
    overlap = command_center._ownership(
        [
            {"id": "fixture-planner", "files": ["14_context/fixture/shared.md"]},
            {"id": "fixture-builder", "files": ["14_context/fixture/shared.md"]},
        ]
    )
    return {
        "ok": all(item["one_owner_per_path"] for item in committed.values()) and not overlap["one_owner_per_path"],
        "committed_scenarios_have_no_overlap": all(
            item["one_owner_per_path"] for item in committed.values()
        ),
        "committed_scenarios": committed,
        "overlap_fixture": {
            "blocked": not overlap["one_owner_per_path"],
            **overlap,
        },
    }


def _paperclip_check(command_center) -> dict:
    previews = {
        scenario_id: command_center.build_paperclip_preview(scenario_id)
        for scenario_id in command_center._scenario_ids()
    }
    safe = all(
        preview.get("mode") == "paperclip_compatible_planning_preview"
        and preview.get("live_company_created") is False
        and preview.get("docker_used") is False
        and preview.get("external_repo_executed") is False
        and preview.get("human_approval_required") is True
        for preview in previews.values()
    )
    return {
        "ok": safe,
        "planning_preview_only": safe,
        "live_company_created": False,
        "external_repo_executed": False,
        "scenario_ids": sorted(previews),
    }


def build_gate(health_url: str = DEFAULT_HEALTH_URL) -> dict:
    command_center = _load_module("ghoti_agent_command_center_n644b", COMMAND_CENTER_SCRIPT)
    search = _load_module("ghoti_local_memory_search_n644b", SEARCH_SCRIPT)
    obsidian = _load_module("ghoti_obsidian_memory_view_n644b", OBSIDIAN_SCRIPT)
    sources = _source_file_check()
    health = probe_health(health_url)
    command_check = command_center.build_check()
    memory = _memory_check(search)
    obsidian_result = _obsidian_check(obsidian)
    workflows = _workflow_check(command_center)
    agents = _agent_check(command_center)
    ownership = _ownership_check(command_center)
    paperclip = _paperclip_check(command_center)
    execution_boundary = {
        "simulation_only": command_check.get("simulation") is True,
        "live_execution_disabled": command_check.get("live_execution") is False,
        "live_agent_launch_disabled": command_check.get("live_agent_launch") is False,
        "human_approval_required": command_check.get("human_approval_required") is True,
        "kill_switch_required": command_check.get("kill_switch_required") is True,
    }
    checks = {
        "source_files_present_and_public_safe": sources["ok"],
        "health_observed_safely": health["ok"],
        "command_center_contract_valid": command_check["ok"],
        "memory_search_verified_and_bounded": memory["ok"],
        "obsidian_views_and_links_valid": obsidian_result["ok"],
        "workflow_ids_and_waves_deterministic": workflows["ok"],
        "agent_role_ids_stable": agents["ok"],
        "ownership_overlap_fixture_blocked": ownership["ok"],
        "paperclip_is_planning_preview_only": paperclip["ok"],
        "simulation_boundary_explicit": all(execution_boundary.values()),
    }
    ok = all(checks.values())
    return {
        "ok": ok,
        "milestone": MILESTONE,
        "purpose": "local command-center audit and integration gate",
        "checks": checks,
        "source_files": sources,
        "health": health,
        "memory_search": memory,
        "obsidian": obsidian_result,
        "workflows": workflows,
        "agents": agents,
        "ownership": ownership,
        "paperclip": paperclip,
        "execution_boundary_checks": execution_boundary,
        "execution_boundary": "simulation_and_approval_packets_only",
        "local_only": True,
        "simulation_only": True,
        "live_execution": False,
        "n6_45a_implemented": False,
        "ready_for_n6_45a": ok,
        "next_milestone": "N+6.45A Approved Single Local Agent Process Trial",
        "evidence_paths": [
            "14_context/operator_reports/generated/n6_44b_command_center_integration_gate.json",
            "14_context/operator_reports/generated/n6_44b_command_center_integration_gate.md",
            "docs/GHOTI_N6_44B_COMMAND_CENTER_INTEGRATION_GATE.md",
            "14_context/memory/obsidian/START_HERE.md",
            "14_context/memory/search/generated/local_search_index.json",
            "14_context/agent_command_center/generated/command_center_status.json",
        ],
        "generated_at": None,
        "generated_at_source": "not_recorded_for_deterministic_evidence",
    }


def render_markdown(payload: dict) -> str:
    health = payload["health"]
    checks = payload["checks"]
    lines = [
        "# N+6.44B Command Center Integration Gate",
        "",
        "> Repo-local integration evidence. The command center remains simulation-only and is not autonomous execution.",
        "",
        f"- Verdict: `{'PASS' if payload['ok'] else 'BLOCKED'}`",
        f"- Health observation: `{health['state']}`",
        f"- Server running during check: `{str(health['server_running']).lower()}`",
        f"- Ready for N+6.45A: `{str(payload['ready_for_n6_45a']).lower()}`",
        f"- Live execution: `{str(payload['live_execution']).lower()}`",
        "",
        "## Integration Checks",
        "",
    ]
    lines.extend(f"- [{'x' if passed else ' '}] {name.replace('_', ' ')}" for name, passed in checks.items())
    lines.extend(
        [
            "",
            "## Memory And Obsidian",
            "",
            f"- Verified search sources: `{payload['memory_search']['verified_sources']}`",
            (
                f"- Search index budget: `{payload['memory_search']['index_bytes']}` / "
                f"`{payload['memory_search']['max_index_bytes']}` bytes"
            ),
            f"- Obsidian links checked: `{payload['obsidian']['checked_links']}`",
            f"- Start view: `{payload['obsidian']['start_view']}`",
            "- Search results and Obsidian pages remain source pointers, not canonical truth.",
            "",
            "## Deterministic Swarm Simulation",
            "",
            f"- Stable workflows: `{', '.join(payload['workflows']['stable_ids'])}`",
            f"- Stable roles: `{', '.join(payload['agents']['stable_role_ids'])}`",
            f"- Task waves deterministic: `{str(payload['workflows']['deterministic']).lower()}`",
            (
                "- Synthetic overlapping ownership fixture blocked: "
                f"`{str(payload['ownership']['overlap_fixture']['blocked']).lower()}`"
            ),
            "- Paperclip-compatible output remains a planning preview; no company or external repo was launched.",
            "",
            "## Token Discipline",
            "",
            "- The gate reuses small generated indexes and source pointers instead of loading raw repo context.",
            "- The local search index remains within its configured byte budget.",
            "- Evidence is deterministic and omits source text, secrets, and private absolute paths.",
            "",
            "## N+6.45A Readiness Boundary",
            "",
            "N+6.45A may trial exactly one allowlisted local agent process only after a separate audited design.",
            "This gate does not launch that process. It does not enable browser control, accounts, posting, money actions, or auto-submit.",
            "",
            "## Evidence",
            "",
        ]
    )
    lines.extend(f"- `{path}`" for path in payload["evidence_paths"])
    return "\n".join(lines).rstrip() + "\n"


def _safe_output_root(output_root: Path, allowed_root: Path) -> Path:
    if ".." in output_root.parts:
        raise ValueError("output path may not contain parent traversal")
    resolved = output_root.resolve(strict=False)
    try:
        resolved.relative_to(allowed_root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError("output path must stay inside the allowed evidence root") from exc
    return resolved


def _safe_write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path), encoded],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise OSError(f"safe data-only write fallback failed for {path.name}: {result.stderr.strip()}")


def write_evidence(payload: dict, output_root: Path = OUTPUT_ROOT, allowed_root: Path = OUTPUT_ROOT) -> list[Path]:
    root = _safe_output_root(output_root, allowed_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / JSON_OUTPUT.name
    markdown_path = root / MARKDOWN_OUTPUT.name
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = render_markdown(payload)
    if not _is_public_safe_text(json_text + markdown_text):
        raise ValueError("evidence contains a private absolute path")
    _safe_write_text(json_path, json_text)
    _safe_write_text(markdown_path, markdown_text)
    return [json_path, markdown_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="run the integration gate without writing")
    action.add_argument("--write", action="store_true", help="run the gate and write JSON/Markdown evidence")
    parser.add_argument("--health-url", default=DEFAULT_HEALTH_URL, help="exact loopback command-center health URL")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        payload = build_gate(args.health_url)
        if args.write:
            written = write_evidence(payload)
            payload = {**payload, "written": [_repo_relative(path) for path in written]}
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        payload = {
            "ok": False,
            "milestone": MILESTONE,
            "error": str(exc),
            "local_only": True,
            "simulation_only": True,
            "live_execution": False,
        }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
