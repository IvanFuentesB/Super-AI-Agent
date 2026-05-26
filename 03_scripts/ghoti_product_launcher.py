#!/usr/bin/env python3
"""Ghoti Product Launcher (N+4.7A) — one-command local product launcher + smoke.

Makes Ghoti easy to open and test like a real local product:
  - start the dashboard (node server.js, fixed argv, no shell)
  - print the exact dashboard URL
  - optionally open the browser (localhost only, only when asked)
  - run a product smoke test against the 4 /api/product-control/* endpoints
  - generate a local demo prompt-pair smoke if requested
  - stop only the server process this launcher started (by recorded PID)

Local-only. stdlib only. No external API. No live account/posting/money actions.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"
SERVER_JS = DASHBOARD_DIR / "server.js"
STATE_FILE = DASHBOARD_DIR / "runtime_data" / "ghoti_product_launcher_state.json"
CONTEXT_PACK_SCRIPT = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"
LOCAL_WORKER_SCRIPT = REPO_ROOT / "03_scripts" / "local_model_worker_lane.py"
REPO_KNOWLEDGE_SCRIPT = REPO_ROOT / "03_scripts" / "ghoti_repo_knowledge_map.py"
HERMES_BRIDGE_SCRIPT = REPO_ROOT / "03_scripts" / "hermes_agent_workflow_bridge.py"
HERMES_MANUAL_BRIDGE_SCRIPT = REPO_ROOT / "03_scripts" / "hermes_manual_bridge_verifier.py"
GEMMA_READINESS_SCRIPT = REPO_ROOT / "03_scripts" / "gemma_model_readiness.py"

LAUNCHER_VERSION = "1.0.0"
MILESTONE = "N+4.7A"
DEFAULT_PORT = 3210
DEFAULT_TIMEOUT_SECONDS = 25

# The product smoke test exercises exactly these 4 product-control endpoints.
SMOKE_ENDPOINTS = [
    ("GET", "/api/product-control/status"),
    ("POST", "/api/product-control/create-relay-pair"),
    ("POST", "/api/product-control/run-content-studio-demo"),
    ("GET", "/api/product-control/latest"),
]

WHAT_GHOTI_CAN_DO = [
    "Local Content Studio — supervised dry-run content packets (no live posting)",
    "Desktop Operator Action Center — dry-run, approve, execute (approval-gated)",
    "Desktop Recipe Runner — allowlisted local recipes",
    "Parallel Agent Relay — copy-paste Claude + Codex prompt pairs (no auto-launch)",
    "Local Memory / Gemma fallback — local compression, no external API",
    "Local Memory / Context Pack — compact copy-paste handoff files for Codex/ChatGPT/Claude/Obsidian",
    "Local Model / Easy Worker Lane — Ollama/Gemma truth plus local_demo fallback tasks",
    "Local Model Routing / Guarded Worker — Gemma/local_demo safe task routing with repo-bundle hallucination guard",
    "Gemma / Local Model Quality — model availability, manual install decision, and quality plan",
    "Repo Knowledge / Graphify Lane — local file map and task bundles; Graphify runtime roadmap only",
    "Hermes Agent / Manual Bridge — safe WSL probes, skills index, and manual setup packet",
    "Hermes Manual Bridge / WSL Guide — Windows-to-WSL path mapping, safe/blocked commands, and manual bridge guide",
    "Hermes WSL truth — Ubuntu WSL safe probes, no setup/provider/token action",
    "Obsidian Compact Memory — repo-local vault and compressed memory plan",
    "Ruflo / Local Brain Bridge — status/readiness only, no runtime wiring",
    "Graphify / Token Plan — roadmap lane for knowledge graph compression",
    "UI-TARS Observation Only — dry-run observation packet, no desktop control",
    "Adapter Dry-Runs — approved local dry-runs with no live API",
    "Public Readiness and Model Council — local audits and provider-safe planning",
    "External Tool Intake — planning-only catalog review",
]

CONTROL_CENTER_LANES = [
    {
        "key": "hermes_wsl_truth",
        "label": "Hermes WSL Truth",
        "status": "verified_local_wsl",
        "truth": "Ubuntu WSL safe probes found /home/ai_sandbox/.local/bin/hermes, Hermes Agent v0.14.0.",
        "safe_next_step": "Run hermes_local_bootstrap.py --status --json; do not run setup/provider config or token flows.",
    },
    {
        "key": "hermes_agent_manual_bridge",
        "label": "Hermes Agent / Manual Bridge",
        "status": "manual_bridge_ready",
        "truth": "Safe WSL probes, skills index, manual checklist, and bridge packet are available; provider setup, Telegram, and browser/Playwright remain manual/not claimed.",
        "safe_next_step": "Run hermes_agent_workflow_bridge.py --status --json or --write-readiness --json; no live provider setup.",
    },
    {
        "key": "hermes_manual_bridge_wsl_guide",
        "label": "Hermes Manual Bridge / WSL Guide",
        "status": "manual_bridge_verified",
        "truth": "WSL usage, Windows-to-/mnt/c path mapping, safe commands, blocked commands, and future Apple comparison plan are generated locally.",
        "safe_next_step": "Run hermes_manual_bridge_verifier.py --write-guide --json; do not run provider setup, Telegram, browser automation, or computer-use control.",
    },
    {
        "key": "gemma_ollama_lane",
        "label": "Gemma / Ollama Lane",
        "status": "local_probe_or_demo_fallback",
        "truth": "Ollama/Gemma are optional local workers for summaries and diagnostics; unavailable models fall back truthfully.",
        "safe_next_step": "Use local_memory_compression_bridge.py --json for a local-only memory summary probe.",
    },
    {
        "key": "local_model_easy_worker_lane",
        "label": "Local Model / Easy Worker Lane",
        "status": "local_demo_or_ollama_gemma",
        "truth": "Ollama is checked locally; Gemma is used only if already installed, otherwise deterministic local_demo fallback stays active.",
        "safe_next_step": "Run local_model_worker_lane.py --status --json or --write-demo-output --json. Ghoti never runs ollama pull automatically.",
    },
    {
        "key": "local_model_guarded_worker",
        "label": "Local Model Routing / Guarded Worker",
        "status": "guarded_safe_tasks_only",
        "truth": "Gemma can be tried for allowlisted offline tasks only; repo-bundle hallucination guard rejects invented bundles/files and falls back to local_demo.",
        "safe_next_step": "Run local_model_worker_lane.py --routing-status --json or --route-task status-paragraph --json. Never execute model output.",
    },
    {
        "key": "gemma_local_model_quality",
        "label": "Gemma / Local Model Quality",
        "status": "manual_install_decision_ready",
        "truth": "Ollama/Gemma availability is checked locally; Gemma downloads require human approval, and production routing remains disabled.",
        "safe_next_step": "Run gemma_model_readiness.py --doctor --json or --quality-plan --json. Do not run ollama pull automatically.",
    },
    {
        "key": "obsidian_compact_memory",
        "label": "Obsidian Compact Memory",
        "status": "repo_local_plan",
        "truth": "Compact memory stays in repo-local files and Obsidian-compatible markdown.",
        "safe_next_step": "Follow docs/OBSIDIAN_COMPACT_MEMORY_PLAN.md before changing vault shape.",
    },
    {
        "key": "repo_knowledge_graphify_lane",
        "label": "Repo Knowledge / Graphify Lane",
        "status": "local_map_available",
        "truth": "Local repo knowledge map and task bundles are generated as JSON/Markdown; external Graphify runtime is roadmap only/not wired.",
        "safe_next_step": "Run ghoti_repo_knowledge_map.py --write --json or use --repo-bundle next-milestone for focused context.",
    },
    {
        "key": "ruflo_local_brain_bridge",
        "label": "Ruflo / Local Brain Bridge",
        "status": "status_only",
        "truth": "Ruflo/source bridge is a read-only/status lane unless a later audited milestone approves wiring.",
        "safe_next_step": "Use ruflo_install_gate.py --source-status for read-only source truth.",
    },
    {
        "key": "graphify_token_plan",
        "label": "Graphify / Token Plan",
        "status": "roadmap",
        "truth": "Graphify is a future knowledge graph/token-efficiency candidate; it is not installed or wired.",
        "safe_next_step": "Use TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md for planning only.",
    },
    {
        "key": "ui_tars_observation_only",
        "label": "UI-TARS Observation Only",
        "status": "dry_run_available",
        "truth": "Observation packets are local; UI-TARS runtime is not started and no desktop control is enabled.",
        "safe_next_step": "Run ui_tars_observation_adapter.py --observe --dry-run --json.",
    },
    {
        "key": "adapter_dry_runs",
        "label": "Adapter Dry-Runs",
        "status": "dry_run_available",
        "truth": "Approved adapter runner can create local demo artifacts without external code, installs, or live APIs.",
        "safe_next_step": "Run approved_adapter_runner.py --execute-approved --adapter agent_skills_eval --dry-run --json.",
    },
    {
        "key": "external_sandbox",
        "label": "External Sandbox",
        "status": "static_scan_only",
        "truth": "External tools remain static-scan/intake only unless separately approved.",
        "safe_next_step": "Run external_tool_sandbox_manager.py --status --json.",
    },
    {
        "key": "public_readiness",
        "label": "Public Readiness",
        "status": "audit_gate",
        "truth": "Public release remains human-reviewed after local security audit warnings are inspected.",
        "safe_next_step": "Run public_repo_security_audit.py --run --json.",
    },
    {
        "key": "model_council",
        "label": "Model Council",
        "status": "planning_only",
        "truth": "Provider/tool registry is local-only; runtime wiring and unsafe browser bypass are blocked.",
        "safe_next_step": "Run model_council_tool_intake.py --scan --json.",
    },
    {
        "key": "safety_gates",
        "label": "Safety Gates",
        "status": "enforced",
        "truth": "No live posting, money/trading/legal action, provider token setup, or hidden autonomy is enabled.",
        "safe_next_step": "Keep all real-world effects behind explicit human approval.",
    },
]

DAILY_OPERATOR_COMMANDS = [
    "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard",
    "python 03_scripts/ghoti_product_launcher.py --status --json",
    "python 03_scripts/ghoti_product_launcher.py --smoke --json",
    "python 03_scripts/ghoti_product_launcher.py --context-pack --json",
    "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json",
    "python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json",
    "python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json",
    "python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json",
    "python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json",
    "python 03_scripts/ghoti_product_launcher.py --gemma-status --json",
    "python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json",
    "python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json",
    "python 03_scripts/ghoti_product_launcher.py --local-model-eval --json",
    "python 03_scripts/ghoti_product_launcher.py --repo-map --json",
    "python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json",
    "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json",
    "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json",
    "python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json",
    "python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json",
    "python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json",
    "python 03_scripts/ghoti_product_launcher.py --stop-dashboard",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _is_repo_local(target) -> bool:
    """True only if the resolved path is the repo root or inside it."""
    try:
        resolved = Path(str(target)).resolve()
        repo = REPO_ROOT.resolve()
        return resolved == repo or repo in resolved.parents
    except Exception:
        return False


def _dashboard_url(port: int) -> str:
    return "http://127.0.0.1:%d" % int(port)


def _repo_rel(target) -> str:
    try:
        return str(Path(target).resolve().relative_to(REPO_ROOT.resolve())).replace(os.sep, "/")
    except Exception:
        return str(target)


def _port_responds(port: int) -> bool:
    """True if a TCP connection to 127.0.0.1:port succeeds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        return sock.connect_ex(("127.0.0.1", int(port))) == 0
    except Exception:
        return False
    finally:
        sock.close()


def _free_port() -> int:
    """Ask the OS for a free local port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def _read_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write_state(state: dict) -> None:
    if not _is_repo_local(STATE_FILE):
        raise ValueError("launcher state path is outside the repo root")
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _pid_alive(pid) -> bool:
    """Best-effort liveness check for a PID. Never terminates the process."""
    if not pid:
        return False
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    try:
        if os.name == "nt":
            # tasklist is read-only; os.kill(pid, 0) on Windows would TERMINATE.
            result = subprocess.run(
                ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
                capture_output=True, text=True, timeout=15, shell=False,
            )
            return ("%d" % pid) in (result.stdout or "")
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _kill_pid(pid) -> bool:
    """Terminate exactly the given PID (and its child tree). Returns True on
    a successful terminate call. Only ever called with the recorded PID."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["taskkill", "/PID", "%d" % pid, "/F", "/T"],
                capture_output=True, text=True, timeout=20, shell=False,
            )
            return result.returncode == 0
        import signal
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


def _http(method: str, url: str, timeout: int, body: dict = None):
    """Local HTTP request. Returns (status_code, body_text). Local only."""
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, (exc.read().decode("utf-8", "ignore") if exc.fp else "")
    except Exception as exc:  # connection refused, timeout, etc.
        return 0, "request failed: %s" % exc


def _wait_for_ready(port: int, timeout: int) -> bool:
    deadline = time.time() + max(1, int(timeout))
    url = _dashboard_url(port) + "/api/health"
    while time.time() < deadline:
        status, _ = _http("GET", url, timeout=3)
        if status == 200:
            return True
        time.sleep(0.5)
    return False


def _start_node_dashboard(port: int):
    """Start `node server.js` with fixed argv and no shell. Returns the Popen."""
    env = dict(os.environ)
    env["PORT"] = str(int(port))
    # Fixed argv. shell=False (explicit). cwd is the repo-local dashboard dir.
    return subprocess.Popen(
        ["node", "server.js"],
        cwd=str(DASHBOARD_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status() -> dict:
    state = _read_state()
    pid = state.get("pid")
    port = state.get("port") or DEFAULT_PORT
    running = bool(pid) and _pid_alive(pid) and _port_responds(port)
    return {
        "ok": True,
        "launcher": "ghoti_product_launcher",
        "launcher_version": LAUNCHER_VERSION,
        "milestone": MILESTONE,
        "dashboard_url": _dashboard_url(port),
        "default_port": DEFAULT_PORT,
        "state_file": _repo_rel(STATE_FILE),
        "state_file_repo_local": _is_repo_local(STATE_FILE),
        "recorded": {
            "pid": pid,
            "port": state.get("port"),
            "dashboard_url": state.get("dashboard_url"),
            "started_at": state.get("started_at"),
        },
        "dashboard_running": running,
        "localhost_only": True,
        "external_api": False,
        "live_account_actions": False,
        "live_posting": False,
        "opens_browser_by_default": False,
        "smoke_endpoints": ["%s %s" % (m, p) for m, p in SMOKE_ENDPOINTS],
        "daily_operator_commands": DAILY_OPERATOR_COMMANDS,
        "daily_operator_sequence": [
            "Launch dashboard",
            "Check status truth",
            "Run smoke/demo",
            "Review report",
            "Stop dashboard",
        ],
        "what_ghoti_can_do": WHAT_GHOTI_CAN_DO,
        "product_finish_milestone": "N+5.3A",
        "control_center_lanes": CONTROL_CENTER_LANES,
        "generated_at": _now(),
    }


def cmd_start_dashboard(port: int, open_browser: bool, timeout: int) -> dict:
    url = _dashboard_url(port)
    state = _read_state()
    recorded_pid = state.get("pid")

    # If our recorded dashboard is already up on this port, do not double-start.
    if (
        recorded_pid
        and _pid_alive(recorded_pid)
        and state.get("port") == port
        and _port_responds(port)
    ):
        return {
            "ok": True,
            "action": "start-dashboard",
            "already_running": True,
            "pid": recorded_pid,
            "port": port,
            "dashboard_url": url,
            "ready": True,
            "opened_browser": False,
            "note": "dashboard already running (recorded PID)",
            "state_file": _repo_rel(STATE_FILE),
            "generated_at": _now(),
        }

    # Truthfully detect a port already in use by something else.
    if _port_responds(port):
        return {
            "ok": False,
            "action": "start-dashboard",
            "already_running": False,
            "port": port,
            "dashboard_url": url,
            "port_in_use": True,
            "error": "port %d is already in use by another process" % port,
            "generated_at": _now(),
        }

    if not SERVER_JS.exists():
        return {
            "ok": False,
            "action": "start-dashboard",
            "error": "dashboard server.js not found",
            "generated_at": _now(),
        }

    proc = _start_node_dashboard(port)
    ready = _wait_for_ready(port, timeout)
    if not ready:
        # Failed to come up — terminate the process we just started.
        _kill_pid(proc.pid)
        return {
            "ok": False,
            "action": "start-dashboard",
            "pid": proc.pid,
            "port": port,
            "dashboard_url": url,
            "ready": False,
            "error": "dashboard did not become ready within %d seconds" % timeout,
            "generated_at": _now(),
        }

    _write_state({
        "pid": proc.pid,
        "port": port,
        "dashboard_url": url,
        "started_at": _now(),
        "launcher_version": LAUNCHER_VERSION,
    })

    opened = False
    if open_browser:
        # Localhost only, and only because --open-dashboard was passed.
        if url.startswith("http://127.0.0.1:"):
            try:
                webbrowser.open(url)
                opened = True
            except Exception:
                opened = False

    return {
        "ok": True,
        "action": "start-dashboard",
        "already_running": False,
        "pid": proc.pid,
        "port": port,
        "dashboard_url": url,
        "ready": True,
        "opened_browser": opened,
        "state_file": _repo_rel(STATE_FILE),
        "generated_at": _now(),
    }


def cmd_stop_dashboard() -> dict:
    state = _read_state()
    pid = state.get("pid")
    if not pid:
        return {
            "ok": True,
            "action": "stop-dashboard",
            "stopped": False,
            "pid": None,
            "note": "no launcher-recorded dashboard PID to stop",
            "generated_at": _now(),
        }
    if not _pid_alive(pid):
        # Stale record — clear it. Never touch any other process.
        _write_state({})
        return {
            "ok": True,
            "action": "stop-dashboard",
            "stopped": False,
            "pid": pid,
            "note": "recorded PID is not running; cleared stale launcher state",
            "generated_at": _now(),
        }
    killed = _kill_pid(pid)
    _write_state({})
    return {
        "ok": bool(killed),
        "action": "stop-dashboard",
        "stopped": bool(killed),
        "pid": pid,
        "note": "terminated recorded PID only" if killed else "failed to terminate recorded PID",
        "generated_at": _now(),
    }


def cmd_smoke(port: int, run_demo: bool, timeout: int) -> dict:
    """Run the product smoke test against the 4 product-control endpoints.

    If a launcher-recorded dashboard is already running, smoke that one and
    leave it running. Otherwise start a temporary dashboard on a free port,
    smoke it, and stop only that temporary process.
    """
    state = _read_state()
    recorded_pid = state.get("pid")
    recorded_port = state.get("port")
    used_existing = False
    started_temp = False
    temp_proc = None
    smoke_port = port

    if (
        recorded_pid
        and _pid_alive(recorded_pid)
        and recorded_port
        and _port_responds(recorded_port)
    ):
        used_existing = True
        smoke_port = recorded_port
    else:
        # Start a temporary dashboard on a guaranteed-free port.
        smoke_port = port if not _port_responds(port) else _free_port()
        if not SERVER_JS.exists():
            return {
                "ok": False,
                "action": "smoke",
                "error": "dashboard server.js not found",
                "generated_at": _now(),
            }
        temp_proc = _start_node_dashboard(smoke_port)
        started_temp = True
        if not _wait_for_ready(smoke_port, timeout):
            _kill_pid(temp_proc.pid)
            return {
                "ok": False,
                "action": "smoke",
                "started_temp_dashboard": True,
                "error": "temporary dashboard did not become ready",
                "generated_at": _now(),
            }

    base = _dashboard_url(smoke_port)
    endpoints = []
    demo = None
    try:
        for method, path in SMOKE_ENDPOINTS:
            body = {} if method == "POST" else None
            status, text = _http(method, base + path, timeout=timeout, body=body)
            ref_error = ("method is not defined" in text) or ("pathname is not defined" in text)
            parsed_ok = None
            try:
                parsed_ok = bool(json.loads(text).get("ok"))
            except Exception:
                parsed_ok = None
            passed = (status == 200) and (not ref_error)
            endpoints.append({
                "method": method,
                "path": path,
                "http_status": status,
                "ok": parsed_ok,
                "ref_error": ref_error,
                "passed": passed,
            })
            if run_demo and path == "/api/product-control/create-relay-pair":
                try:
                    payload = json.loads(text)
                    demo = demo or {}
                    demo["relay_pair_dir"] = payload.get("pair_dir")
                    demo["relay_pair_ok"] = bool(payload.get("ok"))
                except Exception:
                    pass
            if run_demo and path == "/api/product-control/run-content-studio-demo":
                try:
                    payload = json.loads(text)
                    demo = demo or {}
                    demo["content_studio_ok"] = bool(payload.get("ok"))
                    demo["content_studio_mode"] = payload.get("mode")
                except Exception:
                    pass
    finally:
        if started_temp and temp_proc is not None:
            _kill_pid(temp_proc.pid)

    all_passed = all(e["passed"] for e in endpoints) and len(endpoints) == len(SMOKE_ENDPOINTS)
    no_500 = all(e["http_status"] != 500 for e in endpoints)
    no_ref_error = all(not e["ref_error"] for e in endpoints)
    return {
        "ok": bool(all_passed),
        "action": "smoke",
        "dashboard_url": base,
        "used_existing_dashboard": used_existing,
        "started_temp_dashboard": started_temp,
        "smoke_endpoints": ["%s %s" % (m, p) for m, p in SMOKE_ENDPOINTS],
        "endpoints": endpoints,
        "all_passed": bool(all_passed),
        "no_500": bool(no_500),
        "no_ref_error": bool(no_ref_error),
        "demo_smoke_requested": bool(run_demo),
        "demo": demo,
        "external_api": False,
        "generated_at": _now(),
    }


def cmd_context_pack() -> dict:
    """Generate the local context pack through a fixed argv, never a shell."""
    if not CONTEXT_PACK_SCRIPT.exists():
        return {
            "ok": False,
            "action": "context-pack",
            "local_only": True,
            "external_api_used": False,
            "error": "ghoti_context_pack_builder.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(CONTEXT_PACK_SCRIPT), "--write", "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=30,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": "context-pack",
            "local_only": True,
            "external_api_used": False,
            "error": "context pack builder failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": "context-pack",
            "local_only": True,
            "external_api_used": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": "context-pack",
            "local_only": True,
            "external_api_used": False,
            "error": "context pack builder returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = "context-pack"
    return payload


def _run_local_worker(argv_tail, action: str, timeout: int = 30) -> dict:
    """Run the local worker script with fixed argv, never a shell."""
    if not LOCAL_WORKER_SCRIPT.exists():
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "error": "local_model_worker_lane.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(LOCAL_WORKER_SCRIPT), *argv_tail, "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "error": "local worker failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "error": "local worker returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = action
    return payload


def cmd_local_worker_status() -> dict:
    return _run_local_worker(["--status"], "local-worker-status", timeout=30)


def cmd_local_worker_demo() -> dict:
    return _run_local_worker(["--write-demo-output"], "local-worker-demo", timeout=45)


def cmd_local_worker_routing_status() -> dict:
    return _run_local_worker(["--routing-status"], "local-worker-routing-status", timeout=45)


def cmd_local_worker_route_task(task: str) -> dict:
    return _run_local_worker(["--route-task", task], "local-worker-route-task", timeout=90)


def cmd_local_worker_routing_demo() -> dict:
    return _run_local_worker(["--write-routing-demo"], "local-worker-routing-demo", timeout=180)


def _run_gemma_readiness(argv_tail, action: str, timeout: int = 45) -> dict:
    """Run the Gemma readiness script with fixed argv, never a shell."""
    if not GEMMA_READINESS_SCRIPT.exists():
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "auto_download_performed": False,
            "ollama_pull_performed": False,
            "error": "gemma_model_readiness.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(GEMMA_READINESS_SCRIPT), *argv_tail, "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "auto_download_performed": False,
            "ollama_pull_performed": False,
            "error": "Gemma readiness failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "auto_download_performed": False,
            "ollama_pull_performed": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "auto_download_performed": False,
            "ollama_pull_performed": False,
            "error": "Gemma readiness returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = action
    return payload


def cmd_gemma_status() -> dict:
    return _run_gemma_readiness(["--status"], "gemma-status", timeout=45)


def cmd_gemma_doctor() -> dict:
    return _run_gemma_readiness(["--doctor"], "gemma-doctor", timeout=45)


def cmd_gemma_recommend() -> dict:
    return _run_gemma_readiness(["--recommend"], "gemma-recommend", timeout=45)


def cmd_gemma_quality_plan() -> dict:
    return _run_gemma_readiness(["--quality-plan"], "gemma-quality-plan", timeout=45)


def cmd_local_model_eval() -> dict:
    return _run_gemma_readiness(["--local-model-eval"], "local-model-eval", timeout=150)


def cmd_gemma_write_readiness() -> dict:
    return _run_gemma_readiness(["--write-readiness"], "gemma-write-readiness", timeout=60)


def _run_repo_knowledge(argv_tail, action: str, timeout: int = 45) -> dict:
    """Run the repo knowledge map script with fixed argv, never a shell."""
    if not REPO_KNOWLEDGE_SCRIPT.exists():
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "network_used": False,
            "error": "ghoti_repo_knowledge_map.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(REPO_KNOWLEDGE_SCRIPT), *argv_tail, "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "network_used": False,
            "error": "repo knowledge map failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "network_used": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "external_api_used": False,
            "network_used": False,
            "error": "repo knowledge map returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = action
    return payload


def cmd_repo_map() -> dict:
    return _run_repo_knowledge(["--write"], "repo-map", timeout=60)


def cmd_repo_bundle(bundle: str) -> dict:
    return _run_repo_knowledge(["--bundle", bundle], "repo-bundle", timeout=45)


def _run_hermes_bridge(argv_tail, action: str, timeout: int = 60) -> dict:
    """Run the Hermes manual bridge script with fixed argv, never a shell."""
    if not HERMES_BRIDGE_SCRIPT.exists():
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "error": "hermes_agent_workflow_bridge.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(HERMES_BRIDGE_SCRIPT), *argv_tail, "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "error": "Hermes bridge failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "error": "Hermes bridge returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = action
    return payload


def cmd_hermes_bridge_status() -> dict:
    return _run_hermes_bridge(["--status"], "hermes-bridge-status", timeout=60)


def cmd_hermes_bridge_write() -> dict:
    return _run_hermes_bridge(["--write-readiness"], "hermes-bridge-write", timeout=90)


def _run_hermes_manual_bridge(argv_tail, action: str, timeout: int = 60) -> dict:
    """Run the N+6.2A Hermes manual bridge verifier with fixed argv."""
    if not HERMES_MANUAL_BRIDGE_SCRIPT.exists():
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "provider_setup_run": False,
            "telegram_setup_run": False,
            "tokens_read": False,
            "error": "hermes_manual_bridge_verifier.py not found",
            "generated_at": _now(),
        }
    argv = [sys.executable, str(HERMES_MANUAL_BRIDGE_SCRIPT), *argv_tail, "--json"]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "provider_setup_run": False,
            "telegram_setup_run": False,
            "tokens_read": False,
            "error": "Hermes manual bridge failed to start: %s" % exc,
            "generated_at": _now(),
        }
    if completed.returncode != 0:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "provider_setup_run": False,
            "telegram_setup_run": False,
            "tokens_read": False,
            "error": completed.stderr or completed.stdout or ("exit %s" % completed.returncode),
            "generated_at": _now(),
        }
    try:
        payload = json.loads(completed.stdout)
    except Exception:
        return {
            "ok": False,
            "action": action,
            "local_only": True,
            "live_api_used": False,
            "provider_setup_run": False,
            "telegram_setup_run": False,
            "tokens_read": False,
            "error": "Hermes manual bridge returned invalid JSON",
            "generated_at": _now(),
        }
    payload["action"] = action
    return payload


def cmd_hermes_manual_status() -> dict:
    return _run_hermes_manual_bridge(["--status"], "hermes-manual-status", timeout=60)


def cmd_hermes_wsl_guide() -> dict:
    return _run_hermes_manual_bridge(["--wsl-explain"], "hermes-wsl-guide", timeout=30)


def cmd_hermes_safe_commands() -> dict:
    return _run_hermes_manual_bridge(["--safe-commands"], "hermes-safe-commands", timeout=30)


def cmd_hermes_manual_write() -> dict:
    return _run_hermes_manual_bridge(["--write-guide"], "hermes-manual-write", timeout=90)


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------

def _print_human(result: dict) -> None:
    action = result.get("action", "status")
    if action == "status":
        print("Ghoti Product Launcher %s (%s)" % (result["launcher_version"], result["milestone"]))
        print("  dashboard_url: %s" % result["dashboard_url"])
        print("  dashboard_running: %s" % result["dashboard_running"])
        print("  localhost_only: %s | external_api: %s | live_account_actions: %s"
              % (result["localhost_only"], result["external_api"], result["live_account_actions"]))
        print("  smoke endpoints:")
        for ep in result["smoke_endpoints"]:
            print("    - %s" % ep)
        print("  daily operator commands:")
        for command in result["daily_operator_commands"]:
            print("    - %s" % command)
        print("  what Ghoti can do now:")
        for item in result["what_ghoti_can_do"]:
            print("    - %s" % item)
        print("  sequence: Launch dashboard -> Check status truth -> Run smoke/demo -> Review report -> Stop dashboard")
    elif action == "start-dashboard":
        if result.get("ok"):
            print("Dashboard URL: %s" % result["dashboard_url"])
            print("  pid: %s | port: %s | ready: %s | already_running: %s"
                  % (result.get("pid"), result.get("port"), result.get("ready"),
                     result.get("already_running")))
            print("  opened_browser: %s" % result.get("opened_browser"))
        else:
            print("Start failed: %s" % result.get("error"))
    elif action == "stop-dashboard":
        print("Stop dashboard: stopped=%s pid=%s — %s"
              % (result.get("stopped"), result.get("pid"), result.get("note")))
    elif action == "smoke":
        print("Product smoke test: %s" % ("PASS" if result.get("ok") else "FAIL"))
        for ep in result.get("endpoints", []):
            print("  %s %s -> HTTP %s passed=%s"
                  % (ep["method"], ep["path"], ep["http_status"], ep["passed"]))
        if result.get("demo"):
            print("  demo: %s" % json.dumps(result["demo"]))
    elif action == "context-pack":
        print("Context pack: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_short"):
            print("  %s" % result["status_short"])
        for filename, relpath in (result.get("paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))
    elif action in ("local-worker-status", "local-worker-demo", "local-worker-routing-status", "local-worker-route-task", "local-worker-routing-demo"):
        print("Local worker lane: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_line"):
            print("  %s" % result["status_line"])
        if result.get("readiness_percent") is not None:
            print("  readiness: %s%%" % result["readiness_percent"])
        if result.get("guard_result"):
            print("  guard: %s" % result["guard_result"].get("status"))
        if result.get("active_route"):
            print("  route: %s" % result["active_route"])
        for filename, relpath in (result.get("paths") or result.get("output_paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))
    elif action in ("gemma-status", "gemma-doctor", "gemma-recommend", "gemma-quality-plan", "gemma-write-readiness", "local-model-eval"):
        print("Gemma / Local Model Quality: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_line"):
            print("  %s" % result["status_line"])
        if result.get("gemma_readiness_percent") is not None:
            print("  readiness: %s%%" % result["gemma_readiness_percent"])
        if result.get("score_percent") is not None:
            print("  local eval score: %s%%" % result["score_percent"])
        if result.get("recommendation"):
            print("  recommendation: %s" % result["recommendation"])
        for filename, relpath in (result.get("paths") or result.get("output_paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))
    elif action in ("repo-map", "repo-bundle"):
        print("Repo Knowledge / Graphify Lane: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_line"):
            print("  %s" % result["status_line"])
        if result.get("readiness_percent") is not None:
            print("  readiness: %s%%" % result["readiness_percent"])
        if result.get("bundle"):
            print("  bundle: %s" % result["bundle"])
        for filename, relpath in (result.get("paths") or result.get("output_paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))
    elif action in ("hermes-bridge-status", "hermes-bridge-write"):
        print("Hermes Agent / Manual Bridge: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_line"):
            print("  %s" % result["status_line"])
        if result.get("readiness_percent") is not None:
            print("  readiness: %s%%" % result["readiness_percent"])
        for filename, relpath in (result.get("paths") or result.get("output_paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))
    elif action in ("hermes-manual-status", "hermes-wsl-guide", "hermes-safe-commands", "hermes-manual-write"):
        print("Hermes Manual Bridge / WSL Guide: %s" % ("PASS" if result.get("ok") else "FAIL"))
        if result.get("status_line"):
            print("  %s" % result["status_line"])
        if result.get("readiness_percent") is not None:
            print("  readiness: %s%%" % result["readiness_percent"])
        if result.get("wsl_repo_path"):
            print("  WSL path: %s" % result["wsl_repo_path"])
        for filename, relpath in (result.get("paths") or result.get("output_paths") or {}).items():
            print("  %s -> %s" % (filename, relpath))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Ghoti Product Launcher (N+4.7A) — one-command local launcher + smoke.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Daily operator sequence:\n"
            "  1. python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard\n"
            "  2. python 03_scripts/ghoti_product_launcher.py --status --json\n"
            "  3. python 03_scripts/ghoti_product_launcher.py --smoke --json\n"
            "  4. python 03_scripts/ghoti_product_launcher.py --context-pack --json\n"
            "  5. python 03_scripts/ghoti_product_launcher.py --local-worker-status --json\n"
            "  6. python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json\n"
            "  7. python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json\n"
            "  8. python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json\n"
            "  9. python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json\n"
            "  10. python 03_scripts/ghoti_product_launcher.py --gemma-status --json\n"
            "  11. python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json\n"
            "  12. python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json\n"
            "  13. python 03_scripts/ghoti_product_launcher.py --local-model-eval --json\n"
            "  14. python 03_scripts/ghoti_product_launcher.py --repo-map --json\n"
            "  15. python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json\n"
            "  16. python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json\n"
            "  17. python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json\n"
            "  18. python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json\n"
            "  19. python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json\n"
            "  20. python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json\n"
            "  21. review reports under 14_context/\n"
            "  22. python 03_scripts/ghoti_product_launcher.py --stop-dashboard\n"
        ),
    )
    parser.add_argument("--status", action="store_true", help="show launcher + dashboard status")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--start-dashboard", action="store_true", help="start the local dashboard")
    parser.add_argument("--stop-dashboard", action="store_true", help="stop the launcher-recorded dashboard")
    parser.add_argument("--smoke", action="store_true", help="run the product smoke test")
    parser.add_argument("--context-pack", action="store_true",
                        help="generate the Ghoti current context pack (repo-local, no external API)")
    parser.add_argument("--local-worker-status", action="store_true",
                        help="show Ollama/Gemma/local_demo worker readiness (local only)")
    parser.add_argument("--local-worker-demo", action="store_true",
                        help="write safe deterministic local worker demo outputs")
    parser.add_argument("--local-worker-routing-status", action="store_true",
                        help="show guarded local worker routing status")
    parser.add_argument("--local-worker-route-task",
                        choices=[
                            "summarize-latest-report",
                            "status-paragraph",
                            "codex-next-prompt",
                            "safety-classification",
                            "context-bundle-summary",
                            "next-milestone-outline",
                            "report-to-bullets",
                        ],
                        help="route one allowlisted offline local worker task through guard/fallback")
    parser.add_argument("--local-worker-routing-demo", action="store_true",
                        help="write a guarded local worker routing demo")
    parser.add_argument("--gemma-status", action="store_true",
                        help="show Gemma/Ollama model availability and active worker mode")
    parser.add_argument("--gemma-doctor", action="store_true",
                        help="run local Gemma/Ollama readiness checks without downloads")
    parser.add_argument("--gemma-recommend", action="store_true",
                        help="show manual Gemma install decision plan without pulling models")
    parser.add_argument("--gemma-quality-plan", action="store_true",
                        help="show local task quality evaluation plan and fallback result")
    parser.add_argument("--local-model-eval", action="store_true",
                        help="show the first local model evaluation summary or controlled fallback")
    parser.add_argument("--gemma-write-readiness", action="store_true",
                        help="write Gemma readiness and quality-plan files")
    parser.add_argument("--repo-map", action="store_true",
                        help="write the local repo knowledge map and task bundles")
    parser.add_argument("--repo-bundle",
                        choices=[
                            "audit-main",
                            "dashboard",
                            "local-memory",
                            "local-model-worker",
                            "local-model-routing",
                            "hermes",
                            "content-workflow",
                            "safety",
                            "next-milestone",
                        ],
                        help="emit a compact repo knowledge task bundle")
    parser.add_argument("--hermes-bridge-status", action="store_true",
                        help="show Hermes Agent manual bridge readiness (safe WSL probes only)")
    parser.add_argument("--hermes-bridge-write", action="store_true",
                        help="write Hermes manual bridge readiness files (local only)")
    parser.add_argument("--hermes-manual-status", action="store_true",
                        help="show Hermes manual bridge + WSL guide status (safe probes only)")
    parser.add_argument("--hermes-wsl-guide", action="store_true",
                        help="explain WSL path mapping for Ghoti and Hermes")
    parser.add_argument("--hermes-safe-commands", action="store_true",
                        help="list safe Hermes/WSL probe commands")
    parser.add_argument("--hermes-manual-write", action="store_true",
                        help="write Hermes manual bridge + WSL guide files")
    parser.add_argument("--open-dashboard", action="store_true",
                        help="open the localhost dashboard in a browser (only when explicitly passed)")
    parser.add_argument("--run-demo-smoke", action="store_true",
                        help="include a local demo prompt-pair smoke in the smoke result")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="dashboard port (default 3210)")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS,
                        help="readiness / request timeout in seconds")
    args = parser.parse_args(argv)

    port = int(args.port) if args.port else DEFAULT_PORT
    timeout = int(args.timeout_seconds) if args.timeout_seconds else DEFAULT_TIMEOUT_SECONDS

    try:
        if args.start_dashboard:
            result = cmd_start_dashboard(port, args.open_dashboard, timeout)
        elif args.stop_dashboard:
            result = cmd_stop_dashboard()
        elif args.smoke:
            result = cmd_smoke(port, args.run_demo_smoke, timeout)
        elif args.context_pack:
            result = cmd_context_pack()
        elif args.local_worker_status:
            result = cmd_local_worker_status()
        elif args.local_worker_demo:
            result = cmd_local_worker_demo()
        elif args.local_worker_routing_status:
            result = cmd_local_worker_routing_status()
        elif args.local_worker_route_task:
            result = cmd_local_worker_route_task(args.local_worker_route_task)
        elif args.local_worker_routing_demo:
            result = cmd_local_worker_routing_demo()
        elif args.gemma_status:
            result = cmd_gemma_status()
        elif args.gemma_doctor:
            result = cmd_gemma_doctor()
        elif args.gemma_recommend:
            result = cmd_gemma_recommend()
        elif args.gemma_quality_plan:
            result = cmd_gemma_quality_plan()
        elif args.local_model_eval:
            result = cmd_local_model_eval()
        elif args.gemma_write_readiness:
            result = cmd_gemma_write_readiness()
        elif args.repo_map:
            result = cmd_repo_map()
        elif args.repo_bundle:
            result = cmd_repo_bundle(args.repo_bundle)
        elif args.hermes_bridge_status:
            result = cmd_hermes_bridge_status()
        elif args.hermes_bridge_write:
            result = cmd_hermes_bridge_write()
        elif args.hermes_manual_status:
            result = cmd_hermes_manual_status()
        elif args.hermes_wsl_guide:
            result = cmd_hermes_wsl_guide()
        elif args.hermes_safe_commands:
            result = cmd_hermes_safe_commands()
        elif args.hermes_manual_write:
            result = cmd_hermes_manual_write()
        else:
            # --status, bare --json, or no mode -> status.
            result = cmd_status()
    except Exception as exc:  # never crash with a traceback in --json mode
        result = {"ok": False, "error": "launcher error: %s" % exc, "generated_at": _now()}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
