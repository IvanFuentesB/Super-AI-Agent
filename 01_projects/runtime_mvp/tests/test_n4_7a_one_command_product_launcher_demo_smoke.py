#!/usr/bin/env python3
"""N+4.7A tests: One-Command Ghoti Product Launcher + Local Demo Smoke.

Covers:
- --status --json valid; bare --json valid
- launcher state path is repo-local
- fixed argv / no shell:true in the launcher
- smoke endpoint list has the 4 product-control endpoints
- --open-dashboard is off by default
- no external API / live account labels
- stop-dashboard targets only the recorded PID
- dashboard HTML has the Ghoti Local Launcher Truth labels
- no path escape (repo-local containment)
- no secrets in the launcher
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SCRIPT = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
PYTHON = sys.executable

PRODUCT_ENDPOINTS = [
    "/api/product-control/status",
    "/api/product-control/create-relay-pair",
    "/api/product-control/run-content-studio-demo",
    "/api/product-control/latest",
]

REQUIRED_LAUNCHER_LABELS = [
    "Ghoti Local Launcher Truth",
    "One-Command Launcher",
    "Dashboard URL",
    "Start Dashboard",
    "Stop Dashboard",
    "Product Smoke Test",
    "Open Dashboard Optional",
    "Localhost Only",
    "No External API",
    "No Live Account Actions",
    "Safe PID Tracking",
    "Run Demo Smoke",
]


def run_launcher(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


# ===========================================================================
# CLI: --status --json and bare --json
# ===========================================================================

class TestLauncherStatusJson(unittest.TestCase):
    def test_status_json_valid(self):
        r = run_launcher("--status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("launcher"), "ghoti_product_launcher")
        self.assertIn("dashboard_url", data)
        self.assertEqual(data.get("milestone"), "N+4.7A")

    def test_bare_json_valid(self):
        r = run_launcher("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertIn("launcher_version", data)

    def test_status_dashboard_url_is_localhost(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertTrue(data["dashboard_url"].startswith("http://127.0.0.1:"))

    def test_status_default_port_3210(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertEqual(data.get("default_port"), 3210)

    def test_smoke_endpoint_list_has_four_product_endpoints(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        smoke = data.get("smoke_endpoints", [])
        self.assertEqual(len(smoke), 4)
        joined = " ".join(smoke)
        for ep in PRODUCT_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, joined)

    def test_open_dashboard_off_by_default(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertFalse(data.get("opens_browser_by_default"))

    def test_no_external_api_or_live_account(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertFalse(data.get("external_api"))
        self.assertFalse(data.get("live_account_actions"))
        self.assertFalse(data.get("live_posting"))
        self.assertTrue(data.get("localhost_only"))

    def test_state_file_repo_local(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertTrue(data.get("state_file_repo_local"))
        state_file = data.get("state_file", "")
        self.assertFalse(state_file.startswith("/"))
        self.assertFalse(state_file.startswith("\\"))
        self.assertNotIn("..", state_file)
        self.assertTrue(state_file.startswith("01_projects/dashboard_mvp/runtime_data/"))

    def test_status_explains_what_ghoti_can_do(self):
        data = json.loads(run_launcher("--status", "--json").stdout)
        self.assertIsInstance(data.get("what_ghoti_can_do"), list)
        self.assertGreaterEqual(len(data["what_ghoti_can_do"]), 4)


# ===========================================================================
# Launcher source safety
# ===========================================================================

class TestLauncherSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SCRIPT.read_text(encoding="utf-8")

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("shell = True", self.src)

    def test_uses_explicit_shell_false(self):
        # Subprocess calls explicitly pass shell=False.
        self.assertIn("shell=False", self.src)

    def test_fixed_argv_for_node(self):
        # Dashboard is started with a fixed argv list, not a shell string.
        self.assertIn('["node", "server.js"]', self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system", self.src)

    def test_smoke_endpoints_are_the_four_product_endpoints(self):
        for ep in PRODUCT_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, self.src)

    def test_open_browser_is_gated(self):
        # webbrowser.open must only run when --open-dashboard was passed.
        self.assertIn("webbrowser.open", self.src)
        self.assertIn("if open_browser:", self.src)

    def test_stop_dashboard_targets_only_recorded_pid(self):
        start = self.src.find("def cmd_stop_dashboard(")
        self.assertGreater(start, 0)
        end = self.src.find("\ndef ", start + 1)
        body = self.src[start:end if end > 0 else len(self.src)]
        self.assertIn("_read_state()", body)
        self.assertIn('state.get("pid")', body)
        self.assertIn("_kill_pid(pid)", body)
        # The stop command must not run a broad kill of all node processes.
        self.assertNotIn("/IM", body)
        self.assertNotIn("node.exe", body)

    def test_repo_local_containment_used(self):
        self.assertIn("def _is_repo_local(", self.src)
        # The state writer enforces repo-local containment.
        start = self.src.find("def _write_state(")
        end = self.src.find("\ndef ", start + 1)
        body = self.src[start:end if end > 0 else len(self.src)]
        self.assertIn("_is_repo_local(", body)

    def test_state_file_is_in_runtime_data(self):
        self.assertIn('"runtime_data"', self.src)
        self.assertIn("ghoti_product_launcher_state.json", self.src)

    def test_no_external_urls(self):
        # Local-only: no external http(s) endpoints.
        self.assertNotIn("https://", self.src)
        for line in self.src.splitlines():
            if "http://" in line and "127.0.0.1" not in line:
                self.fail("non-localhost http URL in launcher: %s" % line.strip())

    def test_no_secrets(self):
        lowered = self.src.lower()
        for needle in ("api_key", "apikey", "password", "secret", "bearer "):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, lowered)

    def test_no_path_escape_patterns(self):
        self.assertNotIn("..\\", self.src)
        self.assertNotIn("../", self.src)


# ===========================================================================
# Dashboard launcher card labels
# ===========================================================================

class TestLauncherDashboardLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")

    def test_launcher_card_present(self):
        self.assertIn('id="ghoti-local-launcher-truth"', self.html)

    def test_all_required_launcher_labels_present(self):
        for label in REQUIRED_LAUNCHER_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_launcher_card_shows_one_command(self):
        self.assertIn("ghoti_product_launcher.py --start-dashboard", self.html)

    def test_launcher_card_shows_dashboard_url(self):
        self.assertIn("http://127.0.0.1:3210", self.html)


if __name__ == "__main__":
    unittest.main()
