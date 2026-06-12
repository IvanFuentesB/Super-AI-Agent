"""N+6.44B command-center integration gate contract tests."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "agent_command_center" / "check_command_center_integration.py"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_44B_COMMAND_CENTER_INTEGRATION_GATE.md"
JSON_REPORT = (
    REPO_ROOT
    / "14_context"
    / "operator_reports"
    / "generated"
    / "n6_44b_command_center_integration_gate.json"
)
MARKDOWN_REPORT = JSON_REPORT.with_suffix(".md")

EXPECTED_SCENARIOS = [
    "code-maintenance-swarm",
    "content-revenue-research",
    "ecommerce-product-research",
]
EXPECTED_ROLES = [
    "chatgpt_strategy",
    "claude_builder",
    "codex_auditor",
    "hermes_coordinator",
    "local_summarizer",
    "human_approver",
]


def load_module():
    spec = importlib.util.spec_from_file_location("check_command_center_integration", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load command-center integration gate")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(*args: str) -> tuple[int, dict, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return result.returncode, payload, result.stderr


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = {
            "ok": True,
            "binds_loopback_only": True,
            "get_only": True,
            "has_post_routes": False,
            "simulation": True,
            "live_execution": False,
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


class CommandCenterIntegrationGateTests(unittest.TestCase):
    def test_expected_gate_files_exist(self):
        for path in (SCRIPT, DOC, JSON_REPORT, MARKDOWN_REPORT):
            self.assertTrue(path.is_file(), path)

    def test_cli_check_runs_and_returns_valid_json(self):
        rc, data, err = run_cli("--check", "--health-url", "http://127.0.0.1:65534/api/health")
        self.assertEqual(rc, 0, err or data)
        self.assertTrue(data["ok"], data)
        self.assertTrue(data["local_only"])
        self.assertTrue(data["simulation_only"])
        self.assertFalse(data["live_execution"])
        self.assertTrue(data["ready_for_n6_45a"])

    def test_health_probe_reports_server_not_running_cleanly(self):
        gate = load_module()
        health = gate.probe_health("http://127.0.0.1:65534/api/health")
        self.assertTrue(health["ok"])
        self.assertEqual(health["state"], "server_not_running")
        self.assertFalse(health["server_running"])
        self.assertTrue(health["loopback_only_probe"])

    def test_health_probe_accepts_safe_running_command_center(self):
        gate = load_module()
        server = ThreadingHTTPServer(("127.0.0.1", 0), _HealthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            health = gate.probe_health(f"http://127.0.0.1:{server.server_port}/api/health")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
        self.assertTrue(health["ok"], health)
        self.assertEqual(health["state"], "healthy")
        self.assertTrue(health["server_running"])

    def test_health_probe_rejects_non_loopback_urls(self):
        gate = load_module()
        with self.assertRaises(ValueError):
            gate.probe_health("https://example.com/api/health")

    def test_memory_search_and_obsidian_contracts_are_verified(self):
        gate = load_module()
        data = gate.build_gate("http://127.0.0.1:65534/api/health")
        self.assertTrue(data["memory_search"]["ok"], data["memory_search"])
        self.assertEqual(data["memory_search"]["verified_sources"], 12)
        self.assertTrue(data["memory_search"]["index_within_budget"])
        self.assertTrue(data["obsidian"]["ok"], data["obsidian"])
        self.assertGreater(data["obsidian"]["checked_links"], 10)
        self.assertEqual(data["obsidian"]["start_view"], "14_context/memory/obsidian/START_HERE.md")

    def test_workflow_and_role_ids_are_stable(self):
        gate = load_module()
        data = gate.build_gate("http://127.0.0.1:65534/api/health")
        self.assertEqual(data["workflows"]["stable_ids"], EXPECTED_SCENARIOS)
        self.assertEqual(data["agents"]["stable_role_ids"], EXPECTED_ROLES)
        self.assertTrue(data["workflows"]["stable_ids_verified"])
        self.assertTrue(data["agents"]["stable_role_ids_verified"])

    def test_task_waves_are_deterministic(self):
        gate = load_module()
        first = gate.build_gate("http://127.0.0.1:65534/api/health")
        second = gate.build_gate("http://127.0.0.1:65534/api/health")
        self.assertEqual(first["workflows"]["scenario_hashes"], second["workflows"]["scenario_hashes"])
        self.assertTrue(first["workflows"]["deterministic"])

    def test_file_ownership_overlap_fixture_is_blocked(self):
        gate = load_module()
        data = gate.build_gate("http://127.0.0.1:65534/api/health")
        fixture = data["ownership"]["overlap_fixture"]
        self.assertTrue(fixture["blocked"])
        self.assertFalse(fixture["one_owner_per_path"])
        self.assertTrue(fixture["conflicts"])
        self.assertTrue(data["ownership"]["committed_scenarios_have_no_overlap"])

    def test_paperclip_and_command_center_remain_simulation_only(self):
        gate = load_module()
        data = gate.build_gate("http://127.0.0.1:65534/api/health")
        self.assertTrue(data["paperclip"]["ok"])
        self.assertTrue(data["paperclip"]["planning_preview_only"])
        self.assertFalse(data["paperclip"]["live_company_created"])
        self.assertFalse(data["live_execution"])
        self.assertEqual(data["execution_boundary"], "simulation_and_approval_packets_only")

    def test_write_creates_small_public_safe_json_and_markdown(self):
        gate = load_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            written = gate.write_evidence(
                gate.build_gate("http://127.0.0.1:65534/api/health"),
                output_root=root,
                allowed_root=root,
            )
            self.assertEqual({path.suffix for path in written}, {".json", ".md"})
            for path in written:
                text = path.read_text(encoding="utf-8")
                self.assertLess(path.stat().st_size, 100_000)
                self.assertNotIn("C:" + chr(92) + "Users" + chr(92), text)
                self.assertNotIn("/" + "mnt/c/" + "Users/", text)
                self.assertNotIn("ai" + "_sandbox", text)
                self.assertIn("N+6.45A", text)

    def test_committed_reports_are_repo_relative_public_safe_and_simulation_visible(self):
        data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        markdown = MARKDOWN_REPORT.read_text(encoding="utf-8")
        self.assertTrue(data["simulation_only"])
        self.assertFalse(data["live_execution"])
        self.assertIn("simulation-only", markdown.lower())
        self.assertIn("N+6.45A", markdown)
        for path in data["evidence_paths"]:
            self.assertFalse(Path(path).is_absolute(), path)
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_gate_does_not_implement_or_launch_n6_45a(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            "os.system(",
            "shell=True",
            "Start-Process",
            "Invoke-Expression",
            "pyautogui",
            "SendKeys",
            "live_agent_launch = True",
        ):
            self.assertNotIn(forbidden, text)
        data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(data["next_milestone"], "N+6.45A Approved Single Local Agent Process Trial")
        self.assertFalse(data["n6_45a_implemented"])

    def test_data_only_write_fallback_has_no_command_surface(self):
        gate = load_module()
        helper = gate._NODE_WRITE_SCRIPT
        self.assertIn("writeFileSync", helper)
        self.assertIn("Buffer.from", helper)
        for forbidden in ("child_process", "exec", "spawn", "eval", "shell"):
            self.assertNotIn(forbidden, helper)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('["node", "-e", _NODE_WRITE_SCRIPT', text)
        self.assertNotIn("subprocess.Popen", text)
        self.assertNotIn("subprocess.call", text)
        self.assertNotIn("subprocess.check_", text)


if __name__ == "__main__":
    unittest.main()
