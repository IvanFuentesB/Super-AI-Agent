#!/usr/bin/env python3
"""Ghoti local agent command-center simulation.

Combines reviewed repo-local memory, deterministic scenario planning, swarm
ownership/wave checks, Agent Arena-shaped previews, and a Paperclip-compatible
company-plan preview. It launches nothing and performs no live business or
computer-use action.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


MILESTONE = "N+6.44A"
REPO_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_ROOT = REPO_ROOT / "14_context" / "agent_command_center"
SCENARIO_ROOT = CONTEXT_ROOT / "scenarios"
STATIC_ROOT = Path(__file__).resolve().parent / "static"
SEARCH_SCRIPT = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_local_memory_search.py"
SEARCH_INDEX = REPO_ROOT / "14_context" / "memory" / "search" / "generated" / "local_search_index.json"
SYSTEMS_INVENTORY = REPO_ROOT / "14_context" / "agent_systems_trial" / "agent_systems_inventory_n6_35a.json"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8770
LOOPBACK_HOSTS = {"127.0.0.1": "127.0.0.1", "localhost": "127.0.0.1", "::1": "::1"}
STATIC_FILES = ("index.html", "app.js", "styles.css")

REQUIRED_BLOCKS = {
    "live agent launch",
    "mouse click",
    "keyboard input",
    "account login",
    "purchase",
    "payment",
    "auto-submit",
    "live posting",
}

AGENTS = [
    {"id": "chatgpt_strategy", "name": "ChatGPT strategy", "role": "planner"},
    {"id": "claude_builder", "name": "Claude builder", "role": "builder"},
    {"id": "codex_auditor", "name": "Codex auditor", "role": "auditor"},
    {"id": "hermes_coordinator", "name": "Hermes coordinator", "role": "coordinator"},
    {"id": "local_summarizer", "name": "local model summarizer", "role": "summarizer"},
    {"id": "human_approver", "name": "Human approver", "role": "human_approver"},
]
ROLE_TO_AGENT = {agent["role"]: agent["id"] for agent in AGENTS}


def safety_flags() -> dict:
    return {
        "local_only": True,
        "simulation": True,
        "live_execution": False,
        "live_agent_launch": False,
        "mouse_click_enabled": False,
        "keyboard_input_enabled": False,
        "account_actions_enabled": False,
        "money_actions_enabled": False,
        "posting_enabled": False,
        "auto_submit_enabled": False,
        "browser_computer_use_enabled": False,
        "mcp_enabled": False,
        "external_repo_executed": False,
        "provider_calls_used": False,
        "secrets_read": False,
        "human_approval_required": True,
        "kill_switch_required": True,
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_path(scenario_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9-]+", scenario_id):
        raise ValueError("scenario id must use lowercase letters, digits, and hyphens")
    for path in sorted(SCENARIO_ROOT.glob("*.json")):
        try:
            if _read_json(path).get("scenario_id") == scenario_id:
                return path
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    raise ValueError(f"unknown scenario: {scenario_id}")


def _load_scenario(scenario_id: str) -> dict:
    return _read_json(_scenario_path(scenario_id))


def _ownership(tasks: list[dict]) -> dict:
    owners: dict[str, list[str]] = {}
    for task in tasks:
        for path in task.get("files", []):
            if Path(path).is_absolute() or ".." in Path(path).parts:
                owners.setdefault(f"INVALID:{path}", []).append(task["id"])
            else:
                owners.setdefault(path, []).append(task["id"])
    conflicts = [
        {"path": path, "task_ids": sorted(task_ids)}
        for path, task_ids in sorted(owners.items())
        if len(task_ids) > 1 or path.startswith("INVALID:")
    ]
    return {"one_owner_per_path": not conflicts, "conflicts": conflicts}


def _waves(tasks: list[dict]) -> list[list[str]]:
    by_id = {task["id"]: task for task in tasks}
    done: set[str] = set()
    remaining = set(by_id)
    waves: list[list[str]] = []
    while remaining:
        ready = sorted(
            task_id
            for task_id in remaining
            if all(dependency in done for dependency in by_id[task_id].get("depends_on", []))
        )
        if not ready:
            return []
        waves.append(ready)
        done.update(ready)
        remaining.difference_update(ready)
    return waves


def _validate_scenario(scenario: dict) -> list[str]:
    errors = []
    blocked = {item.lower() for item in scenario.get("blocked_actions", [])}
    missing_blocks = sorted(REQUIRED_BLOCKS - blocked)
    if missing_blocks:
        errors.append("missing blocked actions: " + ", ".join(missing_blocks))
    if scenario.get("simulation") is not True or scenario.get("live_execution") is not False:
        errors.append("scenario must be simulation=true and live_execution=false")
    tasks = scenario.get("tasks", [])
    if not tasks:
        errors.append("scenario has no tasks")
    task_ids = [task.get("id") for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        errors.append("scenario contains duplicate task ids")
    if not _ownership(tasks)["one_owner_per_path"]:
        errors.append("scenario contains overlapping or invalid file ownership")
    if not _waves(tasks):
        errors.append("scenario dependencies are cyclic or invalid")
    return errors


def _scenario_ids() -> list[str]:
    return sorted(_read_json(path)["scenario_id"] for path in SCENARIO_ROOT.glob("*.json"))


def build_scenario(scenario_id: str) -> dict:
    scenario = _load_scenario(scenario_id)
    errors = _validate_scenario(scenario)
    tasks = scenario["tasks"]
    roles = sorted({task["role"] for task in tasks})
    return {
        "ok": not errors,
        "milestone": MILESTONE,
        "mode": "command_center_scenario_simulation",
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "business_lane": scenario["business_lane"],
        "objective": scenario["objective"],
        "revenue_hypothesis": scenario["revenue_hypothesis"],
        "evidence_required": scenario["evidence_required"],
        "roles": roles,
        "tasks": tasks,
        "waves": _waves(tasks),
        "ownership": _ownership(tasks),
        "approval_gates": scenario["approval_gates"],
        "blocked_actions": scenario["blocked_actions"],
        "errors": errors,
        "repo_pattern_sources": scenario["repo_pattern_sources"],
        "safety": safety_flags(),
    }


def build_arena_preview(scenario_id: str) -> dict:
    plan = build_scenario(scenario_id)
    task_agent = {
        task["id"]: ROLE_TO_AGENT.get(task["role"], "hermes_coordinator")
        for task in plan["tasks"]
    }
    used_agents = set(task_agent.values()) | {"hermes_coordinator", "human_approver"}
    agents = []
    for agent in AGENTS:
        state = "queued" if agent["id"] in used_agents else "idle"
        if agent["id"] == "hermes_coordinator":
            state = "coordinating"
        if agent["id"] == "human_approver":
            state = "approval_pending"
        agents.append({**agent, "state": state, "current_task": None, "live": False})
    queue = [
        {
            "task_id": task["id"],
            "assigned_agent": task_agent[task["id"]],
            "state": "queued",
            "depends_on": task.get("depends_on", []),
            "executed": False,
        }
        for task in plan["tasks"]
    ]
    timeline = [
        {"step": index + 1, "wave": wave, "event": "would_queue_after_approval", "executed": False}
        for index, wave in enumerate(plan["waves"])
    ]
    return {
        "ok": plan["ok"],
        "milestone": MILESTONE,
        "title": plan["title"],
        "scenario": plan["scenario_id"],
        "simulation": True,
        "live_execution": False,
        "agents": agents,
        "task_states": ["idle", "queued", "coordinating", "approval_pending", "blocked", "done"],
        "queue": queue,
        "timeline": timeline,
        "handoffs": [],
        "traces": [],
        "totals": {"agent_count": len(agents), "task_count": len(queue), "estimated_paid_cost_usd": 0.0},
        "safety": safety_flags(),
    }


def build_paperclip_preview(scenario_id: str) -> dict:
    plan = build_scenario(scenario_id)
    departments: dict[str, list[str]] = {}
    for task in plan["tasks"]:
        departments.setdefault(task["role"], []).append(task["id"])
    return {
        "ok": plan["ok"],
        "milestone": MILESTONE,
        "mode": "paperclip_compatible_planning_preview",
        "source_pattern": "paperclipai/paperclip",
        "source_license": "MIT",
        "company_name": f"Ghoti simulated {plan['business_lane'].replace('_', ' ')} team",
        "company_objective": plan["objective"],
        "departments": [
            {"role": role, "work_item_ids": task_ids}
            for role, task_ids in sorted(departments.items())
        ],
        "work_items": plan["tasks"],
        "approval_gates": plan["approval_gates"],
        "blocked_actions": plan["blocked_actions"],
        "live_company_created": False,
        "docker_used": False,
        "external_repo_executed": False,
        "human_approval_required": True,
        "note": "Planning-shape adaptation only; Paperclip is not installed, run, or connected.",
        "safety": safety_flags(),
    }


_SEARCH_MODULE = None


def _search_module():
    global _SEARCH_MODULE
    if _SEARCH_MODULE is None:
        spec = importlib.util.spec_from_file_location("ghoti_local_memory_search", SEARCH_SCRIPT)
        if spec is None or spec.loader is None:
            raise ValueError("memory search module unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _SEARCH_MODULE = module
    return _SEARCH_MODULE


def build_memory_query(query: str) -> dict:
    module = _search_module()
    index = _read_json(SEARCH_INDEX)
    result = module.search(query, index, REPO_ROOT, 3)
    result["milestone"] = MILESTONE
    result["command_center_mode"] = "read_only_memory_discovery"
    return result


def build_status() -> dict:
    module = _search_module()
    index = _read_json(SEARCH_INDEX)
    verification = module.verify_search_index(index, REPO_ROOT)
    inventory = _read_json(SYSTEMS_INVENTORY)
    repos = {repo["id"]: repo for repo in inventory["repos"]}
    return {
        "ok": verification["ok"],
        "milestone": MILESTONE,
        "service": "ghoti_local_agent_command_center",
        "mode": "local_simulation_and_planning",
        "memory": {
            "engine": index["engine"],
            "indexed_sources": index["source_count"],
            "verified_sources": verification["verified_sources"],
            "search_aid_only": True,
            "canonical_truth": False,
            "obsidian_shared_memory": "14_context/memory/obsidian/START_HERE.md",
        },
        "available_scenarios": _scenario_ids(),
        "agents": AGENTS,
        "agent_systems": {
            "repo_patterns": sorted(repos),
            "paperclip": {
                "source_url": repos["paperclip"]["source_url"],
                "license": repos["paperclip"]["license"],
                "mode": "planning_preview_only",
                "live_company_launch": False,
                "docker_used": False,
            },
            "hermes_paperclip_adapter": {
                "mode": "future_adapter_only",
                "live_connection": False,
            },
        },
        "launch_policy": {
            "current": "simulate_and_prepare_approval_packets_only",
            "future": "audited human-approved launch adapters",
            "live_launch_available": False,
        },
        "safety": safety_flags(),
    }


def build_check() -> dict:
    scenario_results = {scenario_id: build_scenario(scenario_id) for scenario_id in _scenario_ids()}
    status = build_status()
    checks = {
        "status_ok": status["ok"],
        "scenario_count": len(scenario_results),
        "scenarios_valid": all(result["ok"] for result in scenario_results.values()),
        "memory_verified": status["memory"]["verified_sources"] == status["memory"]["indexed_sources"],
        "paperclip_preview_only": status["agent_systems"]["paperclip"]["mode"] == "planning_preview_only",
    }
    return {
        "ok": all(checks.values()),
        "milestone": MILESTONE,
        "checks": checks,
        **safety_flags(),
    }


def build_health() -> dict:
    return {
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_local_agent_command_center",
        "binds_loopback_only": True,
        "get_only": True,
        "has_post_routes": False,
        "static_files_present": all((STATIC_ROOT / name).is_file() for name in STATIC_FILES),
        "routes": [
            "GET /",
            "GET /api/health",
            "GET /api/status",
            "GET /api/scenario/<id>",
            "GET /api/arena/<id>",
            "GET /api/paperclip/<id>",
        ],
        **safety_flags(),
    }


class CommandCenterHandler(BaseHTTPRequestHandler):
    server_version = "GhotiAgentCommandCenter/6.44A"
    protocol_version = "HTTP/1.1"
    _STATIC_TYPES = {
        "index.html": "text/html; charset=utf-8",
        "app.js": "application/javascript; charset=utf-8",
        "styles.css": "text/css; charset=utf-8",
    }

    def _send_bytes(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        self._send_bytes(code, json.dumps(payload, indent=2).encode("utf-8"), "application/json; charset=utf-8")

    def _serve_static(self, name: str) -> None:
        content_type = self._STATIC_TYPES.get(name)
        path = STATIC_ROOT / name
        if not content_type or not path.is_file():
            self._send_json(404, {"ok": False, "error": "static file not found"})
            return
        self._send_bytes(200, path.read_bytes(), content_type)

    def do_GET(self) -> None:
        route = unquote(self.path.split("?", 1)[0]).rstrip("/") or "/"
        try:
            if route in ("/", "/index.html"):
                self._serve_static("index.html")
                return
            if route in ("/app.js", "/static/app.js"):
                self._serve_static("app.js")
                return
            if route in ("/styles.css", "/static/styles.css"):
                self._serve_static("styles.css")
                return
            if route == "/api/health":
                self._send_json(200, build_health())
                return
            if route == "/api/status":
                self._send_json(200, build_status())
                return
            for prefix, builder in (
                ("/api/scenario/", build_scenario),
                ("/api/arena/", build_arena_preview),
                ("/api/paperclip/", build_paperclip_preview),
            ):
                if route.startswith(prefix):
                    self._send_json(200, builder(route[len(prefix):]))
                    return
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            self._send_json(400, {"ok": False, "error": str(exc), "safety": safety_flags()})
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        return


def _normalize_loopback(host: str) -> str | None:
    return LOOPBACK_HOSTS.get(str(host).strip().lower())


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> int:
    bind_host = _normalize_loopback(host)
    if bind_host is None:
        print(json.dumps({
            "ok": False,
            "error": "refusing non-loopback host",
            "host": host,
            "binds_loopback_only": True,
            "live_execution": False,
        }, indent=2))
        return 2
    print(json.dumps({
        "ok": True,
        "serving": True,
        "url": f"http://{bind_host}:{port}/",
        "binds_loopback_only": True,
        "get_only": True,
        "has_post_routes": False,
        "live_execution": False,
    }, indent=2))
    server = ThreadingHTTPServer((bind_host, port), CommandCenterHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--status", action="store_true")
    action.add_argument("--health", action="store_true")
    action.add_argument("--serve", action="store_true")
    action.add_argument("--scenario")
    action.add_argument("--arena-preview")
    action.add_argument("--paperclip-preview")
    action.add_argument("--memory-query")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.serve:
        return serve(args.host, args.port)
    try:
        if args.check:
            payload = build_check()
        elif args.status:
            payload = build_status()
        elif args.health:
            payload = build_health()
        elif args.scenario:
            payload = build_scenario(args.scenario)
        elif args.arena_preview:
            payload = build_arena_preview(args.arena_preview)
        elif args.paperclip_preview:
            payload = build_paperclip_preview(args.paperclip_preview)
        else:
            payload = build_memory_query(args.memory_query)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "milestone": MILESTONE, "error": str(exc), "safety": safety_flags()}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
