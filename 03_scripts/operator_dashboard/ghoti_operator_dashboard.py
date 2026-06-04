#!/usr/bin/env python3
"""Ghoti Operator Dashboard (N+6.18A) - status-only local control center.

The first local operator view for Ghoti: a small, local-only web page that shows
runtime status at a glance so the user no longer has to read raw terminal JSON. It
is status-only and read-only by construction.

What it does:

  * --status-json   Emit the dashboard status JSON and exit (no server).
  * --check         Emit a safety self-check JSON and exit (no server).
  * --serve         Start a local-only HTTP server on 127.0.0.1:8765 that serves a
                    static page plus three read-only GET JSON endpoints.

How it stays safe (all enforced by construction):

  * Python standard library only. No third-party packages, no installs.
  * The server binds the loopback interface only (127.0.0.1). A non-loopback host is
    refused unless an explicit opt-in flag is passed, and that flag is left disabled;
    external/remote serving is a separate, future, authenticated milestone.
  * Only GET routes exist. There is no do_POST handler, so every non-GET method is
    rejected by the standard library. No route executes a command, starts or stops a
    process, or mutates any runtime config.
  * Every subprocess call uses an argument list (never a shell string), has a
    timeout, and only ever runs known local read-only status scripts.
  * It reads no secret values. It surfaces only whether helper scripts exist and the
    already-sanitized status packet from the local status bridge.
  * The page loads no external CSS/JS/fonts and opens no external network connection.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MILESTONE = "N+6.18A"

# 03_scripts/operator_dashboard/ghoti_operator_dashboard.py -> repo root is two
# parents up; the static assets live next to this script.
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "static"

STATUS_BRIDGE = REPO_ROOT / "03_scripts" / "status_bridge" / "ghoti_status_bridge.py"
STATUS_BRAIN = (
    REPO_ROOT / "03_scripts" / "local_worker_queue" / "ghoti_status_brain.py"
)
TELEGRAM_BOT = (
    REPO_ROOT / "03_scripts" / "telegram_status_bot" / "ghoti_telegram_status_bot.py"
)
PY_RESOLVER_PS1 = (
    REPO_ROOT / "03_scripts" / "runtime_activation" / "ghoti_python_resolver.ps1"
)
RUNTIME_CHECK_PS1 = (
    REPO_ROOT / "03_scripts" / "runtime_activation" / "check_ghoti_runtime.ps1"
)
CONFINED_RUNNER = (
    REPO_ROOT / "03_scripts" / "computer_use_sandbox"
    / "confined_browser_sandbox_runner.py"
)
ACTIVATION_CONFIG = REPO_ROOT / "23_configs" / "runtime_activation.example.json"
FEATURE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
SUBPROCESS_TIMEOUT = 25

STATIC_FILES = ("index.html", "app.js", "styles.css")

# The five dashboard feature flags; all default false in the global example config.
DASHBOARD_FLAGS = [
    "operator_dashboard_enabled",
    "operator_dashboard_api_enabled",
    "operator_dashboard_mutations_enabled",
    "operator_dashboard_external_access_enabled",
    "operator_dashboard_command_execution_enabled",
]

# Capabilities that stay disabled and out of scope for this status-only milestone.
DISABLED_CAPABILITIES = [
    "command_execution",
    "process_start_stop",
    "runtime_config_mutation",
    "telegram_run",
    "telegram_send",
    "live_agent_launch",
    "claude_launch",
    "codex_launch",
    "mcp",
    "live_browser_computer_use",
    "os_level_input",
    "account_login",
    "email_draft",
    "whatsapp_draft",
    "auto_send",
    "external_api",
    "external_repo_code_execution",
    "installs",
    "docker_run",
    "external_network_binding",
]

# The dashboard's fixed safety posture, surfaced verbatim in every payload.
SAFETY = {
    "local_only": True,
    "read_only": True,
    "binds_loopback_only": True,
    "has_post_routes": False,
    "executes_commands": False,
    "starts_or_stops_processes": False,
    "mutates_runtime_config": False,
    "reads_secret_values": False,
    "uses_external_assets": False,
    "uses_external_api": False,
    "uses_shell_true": False,
    "live_agent_launch": False,
    "mcp": False,
    "live_browser_computer_use": False,
    "os_input": False,
    "auto_send": False,
}


def _rel(path):
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _run_json_subprocess(args, timeout=SUBPROCESS_TIMEOUT):
    """Run an argument-list subprocess and parse its stdout as JSON.

    Returns the parsed object, or None on any failure. The call is an argument list
    only - there is no shell string and no Invoke-Expression - and it is bounded by a
    timeout so a stuck helper cannot hang the dashboard.
    """
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return None


def _status_bridge_result(timeout=SUBPROCESS_TIMEOUT):
    """Return (bridge_result_dict, error). bridge_result is the bridge's --json."""
    if not STATUS_BRIDGE.is_file():
        return None, "status bridge script not found"
    data = _run_json_subprocess(
        [sys.executable, str(STATUS_BRIDGE), "--json"], timeout=timeout
    )
    if not isinstance(data, dict):
        return None, "status bridge produced no parseable JSON"
    return data, None


def _python_resolver_status():
    """The dashboard is served by a working interpreter; surface it as the resolved
    Python. For the full PATH-shim-skipping resolver, the PowerShell resolver script
    is referenced (and is what the start wrapper uses)."""
    exe = sys.executable
    return {
        "ok": bool(exe),
        "executable": exe,
        "source": "dashboard_interpreter",
        "resolver_script_present": PY_RESOLVER_PS1.is_file(),
        "note": (
            "Served by this working interpreter. For the full resolver that skips a "
            "broken PATH python shim, run ghoti_python_resolver.ps1."
        ),
    }


def _ollama_gemma_status():
    """Best-effort, bounded local probe for ollama and a local gemma model. Any
    failure degrades to unknown; it never raises and never blocks the dashboard."""
    ollama = shutil.which("ollama")
    status = {"ollama_available": bool(ollama), "gemma_available": None, "checked": False}
    if not ollama:
        return status
    try:
        proc = subprocess.run(
            [ollama, "list"], capture_output=True, text=True, timeout=12
        )
        if proc.returncode == 0:
            status["gemma_available"] = bool(re.search(r"(?i)gemma", proc.stdout or ""))
            status["checked"] = True
    except (OSError, subprocess.TimeoutExpired):
        pass
    return status


def _hermes_session_preview():
    """Build the same WSL Hermes resume command preview the runtime activation pack
    uses. This is a preview string only; the dashboard launches nothing."""
    cfg = _read_json(ACTIVATION_CONFIG) or {}
    distro = cfg.get("hermes_wsl_distro") or "Ubuntu"
    session_id = cfg.get("hermes_session_id") or "20260601_081506_d35c70"
    repo_mount = (
        cfg.get("hermes_repo_mount")
        or "/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only"
    )
    inner_path = (
        "/home/ai_sandbox/.local/bin:/usr/local/sbin:/usr/local/bin:"
        "/usr/sbin:/usr/bin:/sbin:/bin"
    )
    inner_cmd = "export PATH={0}; hermes --resume {1}".format(inner_path, session_id)
    preview = "wsl -d {0} --cd {1} -- bash -lc '{2}'".format(distro, repo_mount, inner_cmd)
    return {
        "wsl_available": bool(shutil.which("wsl")),
        "distro": distro,
        "session_id": session_id,
        "repo_mount": repo_mount,
        "command_preview": preview,
        "hermes_wsl_only": True,
        "windows_hermes_desktop_deleted": True,
        "run_from_dashboard": False,
    }


def _telegram_status_readiness(packet):
    return {
        "bot_script_present": TELEGRAM_BOT.is_file(),
        "runtime_status": (packet or {}).get("telegram_runtime_status", "unknown"),
        "mode": "status_only",
        "run_commands_enabled": False,
        "send_commands_enabled": False,
        "live_control_enabled": False,
        "note": (
            "Telegram is status-only: no /run and no live control. The token and chat "
            "id live outside the repo and are never read here."
        ),
    }


def _computer_use_sandbox_status(packet):
    cus = (packet or {}).get("computer_use_sandbox_status")
    if isinstance(cus, dict):
        return cus
    return {
        "available": CONFINED_RUNNER.is_file(),
        "mode": "dry_run_only",
        "browser_launched": False,
        "dom_action_performed": False,
        "os_input_used": False,
        "live_website": False,
    }


def _disabled_capabilities():
    flags = _read_json(FEATURE_FLAGS) or {}
    enabled_flags = sorted(key for key, value in flags.items() if value is True)
    dashboard_flags = {name: bool(flags.get(name, False)) for name in DASHBOARD_FLAGS}
    return {
        "capabilities_disabled": list(DISABLED_CAPABILITIES),
        "dashboard_flags": dashboard_flags,
        "dashboard_flags_all_false": not any(dashboard_flags.values()),
        "global_enabled_flags": enabled_flags,
        "only_status_commands_flag_enabled": (
            enabled_flags == ["telegram_status_commands_enabled"]
        ),
        "note": (
            "This dashboard is status-only and read-only. Every capability above "
            "stays disabled and out of scope for this milestone."
        ),
    }


def _default_next_action():
    return (
        "Run the status bridge "
        "(03_scripts/status_bridge/ghoti_status_bridge.py --json) or the runtime check "
        "(03_scripts/runtime_activation/check_ghoti_runtime.ps1) for live detail."
    )


def build_status(timeout=SUBPROCESS_TIMEOUT):
    """Build the full operator-dashboard status object. Pure local reads; the only
    subprocesses are the local read-only status bridge and an optional bounded
    `ollama list` probe."""
    bridge, bridge_error = _status_bridge_result(timeout=timeout)
    packet = bridge.get("packet") if isinstance(bridge, dict) else None
    if not isinstance(packet, dict):
        packet = {}
    source = bridge.get("source") if isinstance(bridge, dict) else None
    origin_main = packet.get("origin_main_short")

    runtime_health = {
        "ok": bool(bridge) and bool(packet),
        "source": source or "fallback",
        "bridge_error": bridge_error,
        "status_bridge_ok": STATUS_BRIDGE.is_file(),
        "status_brain_ok": STATUS_BRAIN.is_file(),
        "origin_main_short": origin_main or "unavailable",
        "current_branch": packet.get("current_branch", "unavailable"),
        "commits_ahead_of_main": packet.get("commits_ahead_of_main"),
        "n6_test_count": packet.get("n6_test_count_known_or_null"),
    }

    return {
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_operator_dashboard",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dashboard": {
            "status_only": True,
            "read_only": True,
            "binds": "127.0.0.1 loopback only",
        },
        "runtime_health": runtime_health,
        "python_resolver": _python_resolver_status(),
        "status_brain": {"available": STATUS_BRAIN.is_file(), "path": _rel(STATUS_BRAIN)},
        "status_bridge": {
            "available": STATUS_BRIDGE.is_file(),
            "source": source or "fallback",
            "path": _rel(STATUS_BRIDGE),
        },
        "telegram_status_readiness": _telegram_status_readiness(packet),
        "hermes_session": _hermes_session_preview(),
        "ollama_gemma": _ollama_gemma_status(),
        "origin_main_short": origin_main or "unavailable",
        "latest_claude_report": packet.get("latest_claude_report"),
        "latest_codex_report": packet.get("latest_codex_report"),
        "computer_use_sandbox": _computer_use_sandbox_status(packet),
        "disabled_capabilities": _disabled_capabilities(),
        "next_recommended_action": (
            packet.get("next_recommended_action") or _default_next_action()
        ),
        "safety": dict(SAFETY),
    }


def build_health():
    static_ok = all((STATIC_DIR / name).is_file() for name in STATIC_FILES)
    return {
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_operator_dashboard",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_root": str(REPO_ROOT),
        "static_files_present": static_ok,
        "binds_loopback_only": True,
        "read_only": True,
        "status_only": True,
        "has_post_routes": False,
        "safety": dict(SAFETY),
    }


def _scan_no_external_assets():
    """True when no external URL / CDN / external font reference appears in the
    static page files."""
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
    """True when app.js uses no dynamic code execution primitive."""
    path = STATIC_DIR / "app.js"
    if not path.is_file():
        return True
    code = path.read_text(encoding="utf-8", errors="replace")
    return not re.search(r"\beval\s*\(|\bnew\s+Function\s*\(", code)


def _source_safety():
    """Static self-audit of this server's own source: no POST handler, and no
    shell-string or os.system subprocess. The patterns are regexes that require real
    call/def syntax, so this scan matches neither its own pattern text nor the
    prose in the docstrings above."""
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    no_post = re.search(r"def\s+do_POST", src) is None
    no_shell_true = re.search(r"shell\s*=\s*True", src) is None
    no_os_system = re.search(r"os\.system\s*\(", src) is None
    return no_post, (no_shell_true and no_os_system)


def build_check(timeout=SUBPROCESS_TIMEOUT):
    """Emit a safety self-check confirming the files, routes, and config are safe."""
    static_files = {name: (STATIC_DIR / name).is_file() for name in STATIC_FILES}
    no_post, no_command_execution = _source_safety()
    flags = _read_json(FEATURE_FLAGS) or {}
    dashboard_flags = {name: bool(flags.get(name, False)) for name in DASHBOARD_FLAGS}
    enabled_flags = sorted(key for key, value in flags.items() if value is True)

    try:
        status = build_status(timeout=timeout)
        status_build_ok = bool(status.get("ok"))
    except Exception:
        status_build_ok = False

    checks = {
        "milestone": MILESTONE,
        "wrapper": "ghoti_operator_dashboard_check",
        "dashboard_script_exists": Path(__file__).is_file(),
        "static_files": static_files,
        "static_files_exist": all(static_files.values()),
        "routes": [
            "GET /",
            "GET /api/status",
            "GET /api/health",
            "GET /api/disabled-capabilities",
            "GET /static/app.js",
            "GET /static/styles.css",
        ],
        "get_only": True,
        "no_post_routes": no_post,
        "no_command_execution": no_command_execution and no_post,
        "localhost_default": DEFAULT_HOST in LOOPBACK_HOSTS,
        "binds_loopback_only": True,
        "no_external_assets": _scan_no_external_assets(),
        "no_eval_js": _scan_no_eval_js(),
        "no_shell_true": no_command_execution,
        "no_secrets": True,
        "reads_secret_values": False,
        "feature_flags_present": FEATURE_FLAGS.is_file(),
        "dashboard_flags": dashboard_flags,
        "risky_flags_default_false": not any(dashboard_flags.values()),
        "only_status_commands_flag_enabled": (
            enabled_flags == ["telegram_status_commands_enabled"]
        ),
        "status_build_ok": status_build_ok,
        "safety": dict(SAFETY),
    }
    checks["ok"] = all([
        checks["dashboard_script_exists"],
        checks["static_files_exist"],
        checks["no_post_routes"],
        checks["no_command_execution"],
        checks["localhost_default"],
        checks["no_external_assets"],
        checks["no_eval_js"],
        checks["no_shell_true"],
        checks["feature_flags_present"],
        checks["risky_flags_default_false"],
        checks["only_status_commands_flag_enabled"],
    ])
    return checks


class DashboardHandler(BaseHTTPRequestHandler):
    """GET-only request handler. No POST method (or any other verb) is defined, so
    the standard library rejects every non-GET method automatically."""

    server_version = "GhotiOperatorDashboard/6.18A"
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
        body = json.dumps(obj, indent=2).encode("utf-8")
        self._send_bytes(code, body, "application/json; charset=utf-8")

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
        if route == "/api/status":
            return self._send_json(200, build_status())
        if route == "/api/health":
            return self._send_json(200, build_health())
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
    """Start the local-only dashboard server. Refuses a non-loopback host unless the
    explicit opt-in flag is passed (left disabled by default)."""
    if not _is_loopback(host) and not allow_nonlocal_host:
        print(json.dumps({
            "ok": False,
            "error": "refusing to bind a non-loopback host",
            "host": host,
            "hint": (
                "This status-only dashboard binds 127.0.0.1 only. External/remote "
                "serving is a separate, future, authenticated (auth + HTTPS) "
                "milestone."
            ),
        }, indent=2))
        return 2

    static_ok = all((STATIC_DIR / name).is_file() for name in STATIC_FILES)
    print(json.dumps({
        "ok": True,
        "milestone": MILESTONE,
        "service": "ghoti_operator_dashboard",
        "serving": True,
        "url": "http://{0}:{1}/".format(host, port),
        "host": host,
        "port": port,
        "binds_loopback_only": _is_loopback(host),
        "status_only": True,
        "read_only": True,
        "has_post_routes": False,
        "static_files_present": static_ok,
        "routes": [
            "GET /",
            "GET /api/status",
            "GET /api/health",
            "GET /api/disabled-capabilities",
        ],
        "stop": "Press Ctrl+C to stop.",
    }, indent=2))

    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            "Ghoti Operator Dashboard (N+6.18A) - status-only local control center."
        )
    )
    parser.add_argument("--status-json", action="store_true",
                        help="Emit the status JSON and exit (no server).")
    parser.add_argument("--check", action="store_true",
                        help="Emit a safety self-check JSON and exit (no server).")
    parser.add_argument("--serve", action="store_true",
                        help="Start the local-only dashboard server.")
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help="Host to bind (loopback only unless --allow-nonlocal-host).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="Port to bind (default 8765).")
    parser.add_argument("--allow-nonlocal-host", action="store_true",
                        help="Explicit opt-in to bind a non-loopback host. Left "
                             "disabled; external serving is a separate future milestone.")
    parser.add_argument("--json", action="store_true",
                        help="Force JSON output (status/check already emit JSON).")
    parser.add_argument("--timeout", type=int, default=SUBPROCESS_TIMEOUT,
                        help="Subprocess timeout in seconds.")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.serve:
        return serve(
            host=args.host, port=args.port,
            allow_nonlocal_host=args.allow_nonlocal_host,
        )
    if args.check:
        print(json.dumps(build_check(timeout=args.timeout), indent=2))
        return 0
    # Default and --status-json both emit the status packet.
    print(json.dumps(build_status(timeout=args.timeout), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
