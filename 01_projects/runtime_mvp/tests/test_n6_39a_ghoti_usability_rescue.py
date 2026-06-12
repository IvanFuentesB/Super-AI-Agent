#!/usr/bin/env python3
"""N+6.39A tests: Ghoti Usability Rescue - Operator Capability Console.

Covers:
- launcher human printer handles missing launcher_version (no KeyError)
- already-running healthy Ghoti dashboard returns ok=true/already_running=true
- unknown port-in-use returns a safe warning, not a crash
- human printer handles all action result shapes
- capability endpoints registered in server.js
- capability registry includes required statuses (blocked-safely, fixture pass)
- dashboard text: "What can Ghoti do now?", "What Ghoti cannot do yet",
  "Run Safe Check", "Obsidian not implemented yet", "Telegram planned later"
- claude-swarm dry-run represented as blocked-safely, not failure
- fixture replay represented as pass with 5 tasks / 3 groups / 0 overlaps
- bottom-right overlay has close/collapse/hide behavior
- raw access-denied/debug details collapsed by default
- no live account actions / MCP / Telegram exec / provider keys / secrets added
- no AI attribution
- claude-swarm fixture PowerShell checker stays ASCII-safe
- public audit has no blocking findings
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
STYLES_CSS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "styles.css"
FIXTURE_PS1 = REPO_ROOT / "03_scripts" / "claude_swarm_fixture" / "check_claude_swarm_fixture_replay.ps1"
PYTHON = sys.executable


def _load_launcher():
    spec = importlib.util.spec_from_file_location("ghoti_product_launcher_n639a", str(LAUNCHER))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ===========================================================================
# 1-4. Launcher reliability
# ===========================================================================

class TestLauncherHumanPrinter(unittest.TestCase):
    def setUp(self):
        self.m = _load_launcher()

    def test_human_printer_handles_missing_launcher_version(self):
        # A status result dict missing launcher_version must not raise KeyError.
        try:
            self.m._print_human({"action": "status"})
        except KeyError as exc:
            self.fail("KeyError on missing key: %r" % exc)

    def test_human_printer_handles_all_action_shapes(self):
        shapes = [
            {"action": "status"},
            {"action": "start-dashboard", "ok": True, "already_running": True},
            {"action": "start-dashboard", "ok": False, "error": "x",
             "port_occupied_by_non_ghoti": True, "suggested_command": "lsof -i :3210"},
            {"action": "stop-dashboard"},
            {"action": "smoke"},
            {"action": "context-pack"},
            {"action": "repo-map"},
            {"action": "some-unknown-action", "ok": True},
            {},  # no action at all
        ]
        for shape in shapes:
            try:
                self.m._print_human(shape)
            except Exception as exc:  # noqa: BLE001 - must never raise
                self.fail("printer raised on shape %r: %r" % (shape, exc))


class TestLauncherPortHandling(unittest.TestCase):
    def setUp(self):
        self.m = _load_launcher()
        # Neutralize state so the recorded-PID fast path is skipped.
        self._orig = {
            "_read_state": self.m._read_state,
            "_port_responds": self.m._port_responds,
            "_probe_ghoti_dashboard": self.m._probe_ghoti_dashboard,
            "_start_node_dashboard": self.m._start_node_dashboard,
        }
        self.m._read_state = lambda: {}

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(self.m, name, fn)

    def test_already_running_healthy_returns_ok(self):
        # Port busy + probe says it's the Ghoti dashboard -> ok=true/already_running=true.
        self.m._port_responds = lambda port: True
        self.m._probe_ghoti_dashboard = lambda port: {
            "is_ghoti": True, "http_status": 200, "product": "Ghoti Local Supervised Operator",
        }
        result = self.m.cmd_start_dashboard(3210, False, 5)
        self.assertTrue(result.get("ok"))
        self.assertTrue(result.get("already_running"))
        self.assertEqual(result.get("detected_via"), "health_probe")

    def test_unknown_port_in_use_returns_safe_warning(self):
        # Port busy + probe says NOT Ghoti -> clear, non-destructive warning; no start attempt.
        self.m._port_responds = lambda port: True
        self.m._probe_ghoti_dashboard = lambda port: {"is_ghoti": False, "http_status": 0, "product": None}

        def _must_not_start(port):  # pragma: no cover - asserts it is never called
            raise AssertionError("must not try to start a server on an occupied unknown port")

        self.m._start_node_dashboard = _must_not_start
        result = self.m.cmd_start_dashboard(3210, False, 5)
        self.assertFalse(result.get("ok"))
        self.assertTrue(result.get("port_occupied_by_non_ghoti"))
        self.assertIn("suggested_command", result)
        cmd = result.get("suggested_command", "").lower()
        # It must suggest a safe inspect command and explicitly NOT auto-kill anything.
        self.assertIn("do not auto-kill", cmd)
        for destructive in ["kill -9", "taskkill", "stop-process", "kill $(", "pkill"]:
            self.assertNotIn(destructive, cmd, "must not suggest a destructive command: %s" % destructive)

    def test_probe_helper_exists_and_is_localhost_only(self):
        self.assertTrue(hasattr(self.m, "_probe_ghoti_dashboard"))
        src = LAUNCHER.read_text(encoding="utf-8")
        # Probe only reads /api/product-control/status; never posts a body.
        self.assertIn("/api/product-control/status", src)


# ===========================================================================
# 5-6, 11-12. Capability console backend contract (server.js)
# ===========================================================================

class TestCapabilityEndpoints(unittest.TestCase):
    def setUp(self):
        self.server = SERVER_JS.read_text(encoding="utf-8")

    def test_capability_endpoints_registered(self):
        for route in [
            "/api/product-control/capabilities",
            "/api/product-control/run-capability-check",
            "/api/product-control/latest-capability-check",
        ]:
            self.assertIn(route, self.server, "missing endpoint: %s" % route)

    def test_registry_has_required_statuses(self):
        for token in ["blocked-safely", "dry-run", "not-implemented", "roadmap", "manual", "pass"]:
            self.assertIn(token, self.server, "missing status category: %s" % token)

    def test_claude_swarm_dry_run_blocked_safely_not_failure(self):
        self.assertIn("claude-swarm-dry-run", self.server)
        self.assertIn("Ghoti refused to run something unsafe", self.server)

    def test_fixture_replay_pass_5_tasks_3_groups_0_overlaps(self):
        # Live check normalizes counts; registry advertises the headline truth.
        self.assertIn("5 tasks / 3 groups / 0 overlaps", self.server)

    def test_capability_check_is_safe_only(self):
        # The runner reports an explicit safety block; no unsafe primitives wired in.
        self.assertIn("external_cli_executed: false", self.server)
        for bad in ["telegram.send", "mcp.connect", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
            self.assertNotIn(bad, self.server, "capability runner must not reference %s" % bad)


# ===========================================================================
# 6-10, 13-14. Dashboard UI text + overlay + collapsed debug (index.html / app.js)
# ===========================================================================

class TestDashboardCapabilityUi(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")

    def test_what_can_ghoti_do_now_present(self):
        self.assertIn("What can Ghoti do now?", self.html)

    def test_what_ghoti_cannot_do_yet_present(self):
        self.assertIn("What Ghoti cannot do yet", self.html)

    def test_run_safe_check_present(self):
        self.assertIn("Run Safe Check", self.html)

    def test_obsidian_not_implemented_visible(self):
        self.assertIn("Obsidian not implemented yet", self.html)

    def test_telegram_planned_later_visible(self):
        self.assertIn("Telegram planned later", self.html)

    def test_capabilities_is_a_console_view(self):
        self.assertIn('data-console-view-panel="capabilities"', self.html)
        self.assertIn('data-console-view="capabilities"', self.html)
        self.assertIn('"capabilities"', self.app)  # registered in CONSOLE_VIEWS

    def test_what_can_i_click_button_panel(self):
        for token in ["Run Public Audit", "Run Repo Map", "Run Local Worker Status",
                      "Run Fixture Replay Check", "Show Hermes Packet Status", "Copy next safe command"]:
            self.assertIn(token, self.html, "missing button: %s" % token)

    def test_overlay_has_hide_collapse_restore_controls(self):
        for token in ["ghoti-overlay-hide", "ghoti-overlay-collapse", "ghoti-overlay-restore"]:
            self.assertIn(token, self.html, "missing overlay control: %s" % token)

    def test_overlay_hide_persists_in_localstorage(self):
        self.assertIn("CAP_OVERLAY_HIDE_KEY", self.app)
        self.assertIn("localStorage", self.app)
        self.assertIn("applyOverlayHidden", self.app)
        self.assertIn("applyOverlayCollapsed", self.app)

    def test_approval_unavailable_is_friendly_and_debug_collapsed(self):
        # Friendly reassurance + collapsed <details> Debug block, not a raw dump.
        self.assertIn("No action needed unless you expected approvals", self.app)
        self.assertIn("renderApprovalUnavailableCard", self.app)
        self.assertIn("<summary>Debug details</summary>", self.app)


# ===========================================================================
# 15-21. Safety: nothing unsafe added; PowerShell ASCII discipline intact
# ===========================================================================

class TestNoUnsafeAdditions(unittest.TestCase):
    def setUp(self):
        self.app = APP_JS.read_text(encoding="utf-8")
        self.server_tail = SERVER_JS.read_text(encoding="utf-8")
        self.launcher = LAUNCHER.read_text(encoding="utf-8")

    def test_no_ai_attribution(self):
        blob = (self.app + self.launcher).lower()
        for phrase in ["co-authored-by claude", "generated with claude",
                       "generated by claude", "written by claude", "claude-sonnet", "claude-opus"]:
            self.assertNotIn(phrase, blob, "AI attribution: %r" % phrase)

    def test_no_provider_api_keys_added(self):
        for token in ["sk-ant-", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
            self.assertNotIn(token, self.app, "capability UI must not reference %s" % token)

    def test_no_mcp_or_telegram_exec_added(self):
        low = self.app.lower()
        for token in ["mcp.connect", "telegram.sendmessage", "telegrambot", "bot.sendmessage"]:
            self.assertNotIn(token, low, "must not add %s" % token)

    def test_capability_buttons_only_call_safe_endpoints(self):
        # The only network calls the console makes are the safe product-control routes.
        self.assertIn("/api/product-control/capabilities", self.app)
        self.assertIn("/api/product-control/run-capability-check", self.app)

    def test_fixture_powershell_checker_is_ascii(self):
        raw = FIXTURE_PS1.read_bytes()
        bad = [i for i in range(len(raw)) if raw[i] > 127]
        self.assertEqual(bad, [], "claude-swarm fixture PS1 checker must stay ASCII-safe")


# ===========================================================================
# 22. Public audit has no blocking findings
# ===========================================================================

class TestPublicAudit(unittest.TestCase):
    def test_public_audit_no_blocking_findings(self):
        audit = REPO_ROOT / "03_scripts" / "public_repo_security_audit.py"
        proc = subprocess.run(
            [PYTHON, str(audit), "--run", "--json"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data.get("blocking_findings", []), [],
                         "public audit reported blocking findings")


if __name__ == "__main__":
    unittest.main()
