#!/usr/bin/env python3
"""N+4.6A tests: Productized Dashboard Control Center Usability Pass.

Covers:
- product dashboard labels exist in index.html
- product-control endpoints exist in server.js
- no shell:true / no arbitrary command execution in the product section
- product section reuses the N+4.4D isPathInsideRepo containment helper
- app.js product control handlers exist
- safety labels present; no live posting/account/API enabling
- N+4.5 relay route guards still intact (regression)
- N+4.4D path containment helper still intact (regression)
- live: status / create-relay-pair / run-content-studio-demo / latest endpoints
"""
import json
import os
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"
SERVER_JS = DASHBOARD_DIR / "server.js"
INDEX_HTML = DASHBOARD_DIR / "public" / "index.html"
APP_JS = DASHBOARD_DIR / "public" / "app.js"

PRODUCT_ENDPOINTS = [
    "/api/product-control/status",
    "/api/product-control/run-content-studio-demo",
    "/api/product-control/create-relay-pair",
    "/api/product-control/latest",
]

REQUIRED_DASHBOARD_LABELS = [
    "Ghoti Product Control Center",
    "What Ghoti Can Do Now",
    "Run Local Content Studio",
    "Open Latest Preview",
    "Generate Claude + Codex Prompt Pair",
    "Desktop Operator Safe Dry Run",
    "Recipe Runner",
    "Local Memory Compression",
    "Approval Gates Required",
    "Local Only",
    "No Live Posting",
    "No Live Account Actions",
    "External Tools Planning Only",
    "Latest Content Studio Run",
    "Latest Agent Relay Pair",
    "Latest Desktop Operator Run",
]


def _product_section(server_text: str) -> str:
    """Return the N+4.6A product-control endpoint block of server.js."""
    start = server_text.find("Ghoti Product Control Center (N+4.6A)")
    if start == -1:
        start = server_text.find("/api/product-control/status")
    if start == -1:
        return ""
    end = server_text.find("Route not found.", start)
    if end == -1:
        end = start + 9000
    return server_text[start:end]


# ===========================================================================
# Dashboard labels (index.html)
# ===========================================================================

class TestProductDashboardLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")

    def test_product_control_section_present(self):
        self.assertIn('id="section-product-control"', self.html)

    def test_all_required_labels_present(self):
        for label in REQUIRED_DASHBOARD_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html, "missing dashboard label: %s" % label)

    def test_product_control_in_sidebar_nav(self):
        self.assertIn('href="#section-product-control"', self.html)

    def test_action_buttons_have_ids(self):
        for btn_id in (
            "product-refresh-btn",
            "product-run-content-studio-btn",
            "product-create-relay-pair-btn",
            "product-open-preview-btn",
        ):
            with self.subTest(button=btn_id):
                self.assertIn('id="%s"' % btn_id, self.html)

    def test_latest_output_slots_present(self):
        for slot_id in (
            "product-latest-content-studio",
            "product-latest-relay-pair",
            "product-latest-desktop-operator",
            "product-latest-preview",
        ):
            with self.subTest(slot=slot_id):
                self.assertIn('id="%s"' % slot_id, self.html)


# ===========================================================================
# Server endpoints (server.js static checks)
# ===========================================================================

class TestProductServerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = SERVER_JS.read_text(encoding="utf-8", errors="replace")
        cls.section = _product_section(cls.server)

    def test_product_section_found(self):
        self.assertTrue(self.section, "N+4.6A product-control section not found in server.js")

    def test_all_four_endpoints_exist(self):
        for ep in PRODUCT_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn('"%s"' % ep, self.server)

    def test_product_endpoints_use_request_method_and_requesturl_pathname(self):
        # Guard against the N+4.5A bare method/pathname runtime route bug.
        for ep in PRODUCT_ENDPOINTS:
            with self.subTest(endpoint=ep):
                idx = self.section.find('"%s"' % ep)
                self.assertGreater(idx, 0, "endpoint %s not in product section" % ep)
                line_start = self.section.rfind("\n", 0, idx) + 1
                guard = self.section[line_start:idx]
                self.assertIn("request.method", guard,
                              "%s guard must use request.method" % ep)
                self.assertIn("requestUrl.pathname", guard,
                              "%s guard must use requestUrl.pathname" % ep)

    def test_no_shell_true_in_product_section(self):
        self.assertNotIn("shell: true", self.section)
        self.assertNotIn("shell:true", self.section)

    def test_no_arbitrary_command_execution(self):
        # Subprocess calls must go through runCommand(py.command, ...) with a
        # resolved python interpreter — never a string-literal command, never
        # a shell, never exec().
        self.assertIn("runCommand(py.command", self.section)
        self.assertNotIn('runCommand("', self.section)
        self.assertNotIn("runCommand('", self.section)
        self.assertNotIn("child_process", self.section)
        self.assertNotIn("execSync", self.section)

    def test_subprocess_endpoints_have_timeouts(self):
        # Both subprocess endpoints must pass a timeoutMs.
        self.assertIn("timeoutMs", self.section)

    def test_content_studio_demo_is_dry_run_only(self):
        # The content studio demo must run dry-run, never --apply.
        self.assertIn('"--dry-run"', self.section)
        self.assertNotIn('"--apply"', self.section)

    def test_latest_endpoint_uses_n44d_containment_helper(self):
        # The latest endpoint must reuse the N+4.4D isPathInsideRepo helper.
        idx = self.section.find("/api/product-control/latest")
        self.assertGreater(idx, 0)
        block = self.section[idx:]
        self.assertIn("isPathInsideRepo", block)

    def test_status_endpoint_declares_safe_scope(self):
        idx = self.section.find("/api/product-control/status")
        block = self.section[idx:idx + 1600]
        self.assertIn("local_only: true", block)
        self.assertIn("live_posting: false", block)
        self.assertIn("live_account_actions: false", block)
        self.assertIn("external_api: false", block)
        self.assertIn('external_tools: "planning_only"', block)

    def test_no_live_action_enabled_in_product_section(self):
        self.assertNotIn("live_posting: true", self.section)
        self.assertNotIn("live_account_actions: true", self.section)
        self.assertNotIn("external_api: true", self.section)


# ===========================================================================
# app.js client handlers
# ===========================================================================

class TestProductAppHandlers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_JS.read_text(encoding="utf-8", errors="replace")

    def test_product_control_iife_present(self):
        self.assertIn("attachProductControlCenter", self.app)

    def test_handlers_bound_for_each_button(self):
        for btn_id in (
            "product-refresh-btn",
            "product-run-content-studio-btn",
            "product-create-relay-pair-btn",
            "product-open-preview-btn",
        ):
            with self.subTest(button=btn_id):
                self.assertIn(btn_id, self.app)

    def test_app_calls_product_endpoints(self):
        for ep in PRODUCT_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, self.app)

    def test_open_preview_does_not_auto_open_browser(self):
        # Open Latest Preview must surface a path, not auto-launch a browser.
        self.assertNotIn("window.open", self.app[self.app.find("attachProductControlCenter"):])


# ===========================================================================
# Safety / scope labels
# ===========================================================================

class TestProductSafetyLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")

    def test_approval_gates_visible(self):
        self.assertIn("Approval Gates Required", self.html)

    def test_local_only_visible(self):
        self.assertIn("Local Only", self.html)

    def test_no_live_posting_label(self):
        self.assertIn("No Live Posting", self.html)

    def test_no_live_account_actions_label(self):
        self.assertIn("No Live Account Actions", self.html)

    def test_external_tools_planning_only_label(self):
        self.assertIn("External Tools Planning Only", self.html)

    def test_copy_paste_only_relay_noted(self):
        self.assertIn("copy-paste only", self.html.lower())


# ===========================================================================
# Regression guards — N+4.5 relay routes + N+4.4D containment still intact
# ===========================================================================

class TestProductRegressionGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = SERVER_JS.read_text(encoding="utf-8", errors="replace")

    def test_n45_relay_endpoints_still_use_request_method(self):
        # N+4.5C regression: relay route guards must still use request.method.
        for ep in (
            "/api/agent-relay/status",
            "/api/agent-relay/create-pair",
            "/api/agent-relay/latest",
            "/api/agent-relay/pair",
            "/api/agent-relay/prompt",
        ):
            with self.subTest(endpoint=ep):
                idx = self.server.find('"%s"' % ep)
                self.assertGreater(idx, 0, "relay endpoint %s missing" % ep)
                line_start = self.server.rfind("\n", 0, idx) + 1
                guard = self.server[line_start:idx]
                self.assertIn("request.method", guard)
                self.assertIn("requestUrl.pathname", guard)

    def test_n44d_containment_helper_still_present(self):
        # N+4.4D: real path.relative() containment must remain.
        self.assertIn("function isPathInsideRepo(", self.server)
        self.assertNotIn("startsWith(repoRoot)", self.server)


# ===========================================================================
# Live endpoint validation (spawns the real Node server)
# ===========================================================================

class TestProductLiveEndpoints(unittest.TestCase):
    """Spawns the real dashboard Node server and exercises every
    product-control endpoint. Confirms no 500s, no runtime ReferenceError,
    repo-local paths only."""

    PORT = 3266

    @classmethod
    def setUpClass(cls):
        cls.ready = False
        cls.proc = None
        env = dict(os.environ)
        env["PORT"] = str(cls.PORT)
        try:
            cls.proc = subprocess.Popen(
                ["node", "server.js"],
                cwd=str(DASHBOARD_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
        except (OSError, FileNotFoundError):
            cls.proc = None
            return
        deadline = time.time() + 20
        while time.time() < deadline:
            if cls.proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:%d/api/health" % cls.PORT, timeout=2
                ) as r:
                    if r.status == 200:
                        cls.ready = True
                        break
            except Exception:
                time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if cls.proc is not None:
            try:
                cls.proc.terminate()
                cls.proc.wait(timeout=5)
            except Exception:
                try:
                    cls.proc.kill()
                except Exception:
                    pass

    def setUp(self):
        if not self.ready:
            self.skipTest("dashboard Node server not ready (node missing or startup failed)")

    def _get(self, path_and_query: str):
        url = "http://127.0.0.1:%d%s" % (self.PORT, path_and_query)
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")

    def _post(self, path: str, payload: dict):
        url = "http://127.0.0.1:%d%s" % (self.PORT, path)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")

    def _assert_no_ref_error(self, body: str):
        self.assertNotIn("method is not defined", body)
        self.assertNotIn("pathname is not defined", body)

    def _assert_repo_local(self, value):
        if value is None:
            return
        text = str(value)
        self.assertFalse(text.startswith("/"), "path not repo-local: %s" % text)
        self.assertFalse(text.startswith("\\"), "path not repo-local: %s" % text)
        self.assertNotIn("..", text, "path escapes repo: %s" % text)
        self.assertNotIn(":", text, "path looks absolute: %s" % text)

    def test_status_endpoint_live(self):
        status, body = self._get("/api/product-control/status")
        self.assertEqual(status, 200, body)
        self._assert_no_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertTrue(data.get("local_only"))
        self.assertFalse(data.get("live_posting"))
        self.assertFalse(data.get("live_account_actions"))
        self.assertFalse(data.get("external_api"))
        self.assertEqual(data.get("external_tools"), "planning_only")
        self.assertIsInstance(data.get("capabilities"), list)

    def test_create_relay_pair_endpoint_live(self):
        status, body = self._post("/api/product-control/create-relay-pair", {})
        self.assertEqual(status, 200, body)
        self._assert_no_ref_error(body)
        data = json.loads(body)
        # Works: ok=true with a generated pair. The relay script is on main.
        self.assertTrue(data.get("ok"), body)
        self.assertIn("manifest", data)
        lanes = data["manifest"]["lanes"]
        self.assertIn("claude", lanes)
        self.assertIn("codex", lanes)

    def test_run_content_studio_demo_endpoint_live(self):
        # Must work OR truthfully report unavailable — never a 500.
        status, body = self._post("/api/product-control/run-content-studio-demo", {})
        self.assertEqual(status, 200, "content studio demo must not 500: %s" % body)
        self._assert_no_ref_error(body)
        data = json.loads(body)
        self.assertIn("ok", data)
        self.assertEqual(data.get("mode"), "dry_run")
        self.assertFalse(data.get("live_posting"))
        self.assertFalse(data.get("external_api"))

    def test_latest_endpoint_returns_repo_local_paths(self):
        status, body = self._get("/api/product-control/latest")
        self.assertEqual(status, 200, body)
        self._assert_no_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        latest = data.get("latest", {})
        for key in ("content_studio_run", "relay_pair", "desktop_operator_run"):
            entry = latest.get(key)
            if isinstance(entry, dict):
                for v in entry.values():
                    self._assert_repo_local(v)

    def test_latest_preview_path_contained(self):
        status, body = self._get("/api/product-control/latest")
        self.assertEqual(status, 200, body)
        data = json.loads(body)
        self._assert_repo_local(data.get("latest", {}).get("preview_path"))

    def test_no_endpoint_returns_500(self):
        for ep in ("/api/product-control/status", "/api/product-control/latest"):
            with self.subTest(endpoint=ep):
                status, body = self._get(ep)
                self.assertNotEqual(status, 500, body)
                self._assert_no_ref_error(body)


if __name__ == "__main__":
    unittest.main()
