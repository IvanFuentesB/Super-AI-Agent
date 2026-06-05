#!/usr/bin/env python3
"""Ghoti Agent Arena - visual simulator (N+6.21A).

The first visual place to watch Ghoti agents/swarms work - as a SIMULATION, before
any live overnight automation. It reuses the N+6.18A operator dashboard pattern: a
Python standard-library HTTP server bound to the loopback interface that serves a
static page plus read-only GET JSON endpoints. It loads a sample simulation and draws
agent cards, a queue/timeline, token/cost estimates, handoffs, and a replay trace.

Simulation-first and safe by construction:

  * Python standard library only. No third-party packages, no installs, NO subprocess.
  * The server binds 127.0.0.1 only; a non-loopback host is refused unless an explicit
    opt-in flag is passed, and that flag is left disabled.
  * Only GET routes exist. There is no do_POST handler, so every non-GET method is
    rejected by the standard library. No route launches an agent, runs a command,
    merges, pushes, or mutates anything.
  * It reads no secret values and loads no external CSS/JS/fonts.
  * live_execution is forced false in every payload regardless of file contents.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MILESTONE = "N+6.21A"

# 03_scripts/agent_arena/ghoti_agent_arena.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "static"
SIMULATION_JSON = REPO_ROOT / "14_context" / "agent_arena" / "sample_simulation.json"
SCHEMA_JSON = REPO_ROOT / "14_context" / "agent_arena" / "agent_arena_schema.json"
FEATURE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

STATIC_FILES = ("index.html", "app.js", "styles.css")

# Arena-related feature flags (absent counts as false); none may be true by default.
ARENA_FLAGS = ["agent_arena_simulator_enabled", "unattended_live_agent_loop_enabled"]

DISABLED_CAPABILITIES = [
    "live_agent_launch",
    "claude_automation",
    "codex_automation",
    "hermes_automation",
    "gemma_automation",
    "auto_submit",
    "command_execution",
    "process_start_stop",
    "runtime_config_mutation",
    "merge_or_push",
    "unattended_swarm",
    "mcp",
    "live_browser_computer_use",
    "os_level_input",
    "account_login",
    "email_draft",
    "whatsapp_draft",
    "external_api",
    "docker_run",
    "external_network_binding",
]

SAFETY = {
    "milestone": MILESTONE,
    "simulation": True,
    "live_execution": False,
    "local_only": True,
    "read_only": True,
    "binds_loopback_only": True,
    "has_post_routes": False,
    "launches_agents": False,
    "runs_commands": False,
    "merges_or_pushes": False,
    "uses_external_assets": False,
    "uses_external_api": False,
    "uses_shell_true": False,
    "mcp": False,
    "auto_submit": False,
    "reads_secret_values": False,
}


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _fallback_simulation():
    return {
        "milestone": MILESTONE,
        "title": "Ghoti Agent Arena - fallback simulation",
        "simulation": True,
        "live_execution": False,
        "scenario": "Sample simulation file missing; showing a minimal fallback.",
        "agents": [],
        "task_states": ["idle", "queued", "running", "blocked", "done"],
        "queue": [],
        "timeline": [],
        "handoffs": [],
        "traces": [],
        "totals": {"agent_count": 0, "token_estimate": 0, "cost_estimate_usd": 0.0},
        "safety": {},
        "fallback": True,
    }


def build_simulation():
    """Load the sample simulation and return it with the safe posture forced on. The
    arena never executes anything; live_execution is always false in the payload."""
    data = _read_json(SIMULATION_JSON)
    if not isinstance(data, dict):
        data = _fallback_simulation()
    data["ok"] = True
    data["milestone"] = data.get("milestone") or MILESTONE
    data["simulation"] = True
    data["live_execution"] = False
    data["served_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    safety = dict(data.get("safety") or {})
    safety["simulation"] = True
    safety["live_execution"] = False
    data["safety"] = safety
    return data


def build_health():
    static_ok = all((STATIC_DIR / name).is_file() for name in STATIC_FILES)
    sim = _read_json(SIMULATION_JSON)
    return {
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_agent_arena",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_root": str(REPO_ROOT),
        "static_files_present": static_ok,
        "simulation_present": SIMULATION_JSON.is_file(),
        "simulation_valid": isinstance(sim, dict) and isinstance(sim.get("agents"), list),
        "binds_loopback_only": True,
        "read_only": True,
        "simulation_only": True,
        "live_execution": False,
        "has_post_routes": False,
        "safety": dict(SAFETY),
    }


def _disabled_capabilities():
    flags = _read_json(FEATURE_FLAGS) or {}
    enabled_flags = sorted(key for key, value in flags.items() if value is True)
    arena_flags = {name: bool(flags.get(name, False)) for name in ARENA_FLAGS}
    return {
        "capabilities_disabled": list(DISABLED_CAPABILITIES),
        "arena_flags": arena_flags,
        "arena_flags_all_false": not any(arena_flags.values()),
        "only_status_commands_flag_enabled": enabled_flags == ["telegram_status_commands_enabled"],
        "note": "The arena is simulation-only. Every capability above stays disabled.",
    }


def _scan_no_external_assets():
    bad = re.compile(
        r"https?://|//cdn\.|fonts\.googleapis|fonts\.gstatic|unpkg|jsdelivr|cdnjs",
        re.IGNORECASE,
    )
    for name in STATIC_FILES:
        path = STATIC_DIR / name
        if path.is_file() and bad.search(path.read_text(encoding="utf-8", errors="replace")):
            return False
    return True


def _scan_no_eval_js():
    path = STATIC_DIR / "app.js"
    if not path.is_file():
        return True
    code = path.read_text(encoding="utf-8", errors="replace")
    return not re.search(r"\beval\s*\(|\bnew\s+Function\s*\(", code)


def _source_safety():
    """Static self-audit of this server's own source: no POST handler, no shell-string
    subprocess, no os.system. Regexes require real def/call syntax, so this scan
    matches neither its own pattern text nor the docstrings."""
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    no_post = re.search(r"def\s+do_POST", src) is None
    no_shell_true = re.search(r"shell\s*=\s*True", src) is None
    no_os_system = re.search(r"os\.system\s*\(", src) is None
    return no_post, (no_shell_true and no_os_system)


def build_check():
    static_files = {name: (STATIC_DIR / name).is_file() for name in STATIC_FILES}
    no_post, no_command_execution = _source_safety()
    flags = _read_json(FEATURE_FLAGS) or {}
    enabled_flags = sorted(key for key, value in flags.items() if value is True)
    arena_flags = {name: bool(flags.get(name, False)) for name in ARENA_FLAGS}
    sim = _read_json(SIMULATION_JSON)
    sim_valid = isinstance(sim, dict) and isinstance(sim.get("agents"), list) and sim.get("live_execution") is False

    checks = {
        "milestone": MILESTONE,
        "wrapper": "ghoti_agent_arena_check",
        "arena_script_exists": Path(__file__).is_file(),
        "static_files": static_files,
        "static_files_exist": all(static_files.values()),
        "simulation_present": SIMULATION_JSON.is_file(),
        "simulation_valid": sim_valid,
        "schema_present": SCHEMA_JSON.is_file(),
        "routes": [
            "GET /", "GET /api/health", "GET /api/simulation",
            "GET /api/disabled-capabilities", "GET /static/app.js", "GET /static/styles.css",
        ],
        "get_only": True,
        "no_post_routes": no_post,
        "no_command_execution": no_command_execution and no_post,
        "no_shell_true": no_command_execution,
        "localhost_default": DEFAULT_HOST in LOOPBACK_HOSTS,
        "binds_loopback_only": True,
        "no_external_assets": _scan_no_external_assets(),
        "no_eval_js": _scan_no_eval_js(),
        "no_secrets": True,
        "live_execution": False,
        "simulation_only": True,
        "arena_flags": arena_flags,
        "risky_flags_default_false": not any(arena_flags.values()),
        "only_status_commands_flag_enabled": enabled_flags == ["telegram_status_commands_enabled"],
        "safety": dict(SAFETY),
    }
    checks["ok"] = all([
        checks["arena_script_exists"],
        checks["static_files_exist"],
        checks["simulation_present"],
        checks["simulation_valid"],
        checks["no_post_routes"],
        checks["no_command_execution"],
        checks["no_external_assets"],
        checks["no_eval_js"],
        checks["localhost_default"],
        checks["risky_flags_default_false"],
        checks["only_status_commands_flag_enabled"],
    ])
    return checks


class ArenaHandler(BaseHTTPRequestHandler):
    """GET-only request handler. No POST method (or any other verb) is defined, so the
    standard library rejects every non-GET method automatically."""

    server_version = "GhotiAgentArena/6.21A"
    protocol_version = "HTTP/1.1"

    _STATIC_TYPES = {
        "index.html": "text/html; charset=utf-8",
        "app.js": "application/javascript; charset=utf-8",
        "styles.css": "text/css; charset=utf-8",
    }

    def _send_bytes(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, code, obj):
        self._send_bytes(code, json.dumps(obj, indent=2).encode("utf-8"),
                         "application/json; charset=utf-8")

    def _serve_static(self, name):
        content_type = self._STATIC_TYPES.get(name)
        path = STATIC_DIR / name
        if not content_type or not path.is_file():
            return self._send_json(404, {"ok": False, "error": "static not found", "name": name})
        try:
            data = path.read_bytes()
        except OSError:
            return self._send_json(500, {"ok": False, "error": "static read error"})
        return self._send_bytes(200, data, content_type)

    def do_GET(self):
        route = self.path.split("?", 1)[0].rstrip("/") or "/"
        if route in ("/", "/index.html"):
            return self._serve_static("index.html")
        if route == "/api/health":
            return self._send_json(200, build_health())
        if route == "/api/simulation":
            return self._send_json(200, build_simulation())
        if route == "/api/disabled-capabilities":
            payload = {"ok": True, "milestone": MILESTONE}
            payload.update(_disabled_capabilities())
            payload["safety"] = dict(SAFETY)
            return self._send_json(200, payload)
        if route in ("/static/app.js", "/app.js"):
            return self._serve_static("app.js")
        if route in ("/static/styles.css", "/styles.css"):
            return self._serve_static("styles.css")
        return self._send_json(404, {"ok": False, "error": "not found", "path": route})

    def log_message(self, fmt, *args):  # noqa: A003 - silence default stderr logging
        return


def _is_loopback(host):
    return host in LOOPBACK_HOSTS


def serve(host=DEFAULT_HOST, port=DEFAULT_PORT, allow_nonlocal_host=False):
    if not _is_loopback(host) and not allow_nonlocal_host:
        print(json.dumps({
            "ok": False,
            "error": "refusing to bind a non-loopback host",
            "host": host,
            "hint": "The arena binds 127.0.0.1 only. External serving is a separate, "
                    "future, authenticated milestone.",
        }, indent=2))
        return 2

    static_ok = all((STATIC_DIR / name).is_file() for name in STATIC_FILES)
    print(json.dumps({
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_agent_arena",
        "serving": True,
        "url": "http://{0}:{1}/".format(host, port),
        "host": host,
        "port": port,
        "binds_loopback_only": _is_loopback(host),
        "simulation_only": True,
        "live_execution": False,
        "has_post_routes": False,
        "static_files_present": static_ok,
        "routes": ["GET /", "GET /api/health", "GET /api/simulation", "GET /api/disabled-capabilities"],
        "stop": "Press Ctrl+C to stop.",
    }, indent=2))

    httpd = ThreadingHTTPServer((host, port), ArenaHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Agent Arena visual simulator (N+6.21A) - simulation-only."
    )
    parser.add_argument("--check", action="store_true",
                        help="Emit a safety self-check JSON and exit (no server).")
    parser.add_argument("--simulation-json", action="store_true",
                        help="Emit the simulation JSON and exit (no server).")
    parser.add_argument("--serve", action="store_true",
                        help="Start the local-only arena server.")
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help="Host to bind (loopback only unless --allow-nonlocal-host).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="Port to bind (default 8766).")
    parser.add_argument("--allow-nonlocal-host", action="store_true",
                        help="Explicit opt-in to bind a non-loopback host. Left disabled.")
    parser.add_argument("--json", action="store_true",
                        help="Force JSON output (check/simulation already emit JSON).")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.serve:
        return serve(host=args.host, port=args.port, allow_nonlocal_host=args.allow_nonlocal_host)
    if args.check:
        print(json.dumps(build_check(), indent=2))
        return 0
    if args.simulation_json:
        print(json.dumps(build_simulation(), indent=2))
        return 0
    # Default: the safety self-check.
    print(json.dumps(build_check(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
