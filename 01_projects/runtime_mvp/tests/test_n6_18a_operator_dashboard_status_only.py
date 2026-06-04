"""Tests for N+6.18A - Ghoti Operator Dashboard (status-only MVP).

These tests lock the safety and behavior of the first local operator view in
03_scripts/operator_dashboard/. They assert (1) every dashboard file exists, (2) the
Python CLI emits a valid status JSON and a passing safety self-check without starting
a server, (3) the server source binds the loopback interface by default, defines no
POST handler, and uses no shell-string subprocess, (4) the static page loads no
external assets and uses no dynamic code execution, (5) the five operator_dashboard_*
feature flags default false and the global example config keeps only
telegram_status_commands_enabled true, (6) the status schema declares a safe posture,
(7) no token / chat id / secret blob is committed, (8) the docs say status-only, no
live automation, no external access, and that a future public dashboard is a separate
milestone needing authentication and HTTPS, (9) the PowerShell check emits JSON and
the start wrapper supports -DryRun, and (10) a live in-process server answers GET
health/disabled-capabilities, returns 404 for an unknown path, and rejects a POST.
The server is only ever exercised on an ephemeral loopback port here; nothing live is
started on the default port.
"""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

DASH_DIR = REPO_ROOT / "03_scripts" / "operator_dashboard"
DASHBOARD = DASH_DIR / "ghoti_operator_dashboard.py"
CHECK_PS = DASH_DIR / "check_operator_dashboard.ps1"
START_PS = DASH_DIR / "start_operator_dashboard.ps1"
DASH_README = DASH_DIR / "README.md"
STATIC_DIR = DASH_DIR / "static"
INDEX_HTML = STATIC_DIR / "index.html"
APP_JS = STATIC_DIR / "app.js"
STYLES_CSS = STATIC_DIR / "styles.css"

CTX_DIR = REPO_ROOT / "14_context" / "operator_dashboard"
CTX_README = CTX_DIR / "README.md"
STATUS_SCHEMA = CTX_DIR / "operator_dashboard_status_schema.json"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_18A_OPERATOR_DASHBOARD_STATUS_ONLY.md"
HANDOFF = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
    / "NEXT_OPERATOR_DASHBOARD_TASK.md"
)
FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"
REPORT = REPO_ROOT / "14_context" / "claude_n6_18a_operator_dashboard_status_only.md"

# Existing scripts the dashboard reads (must remain present for it to aggregate).
STATUS_BRIDGE = REPO_ROOT / "03_scripts" / "status_bridge" / "ghoti_status_bridge.py"

PS_SCRIPTS = [CHECK_PS, START_PS]
STATIC_PAGE_FILES = [INDEX_HTML, APP_JS, STYLES_CSS]

ALL_FILES = [
    DASHBOARD, CHECK_PS, START_PS, DASH_README,
    INDEX_HTML, APP_JS, STYLES_CSS,
    CTX_README, STATUS_SCHEMA, DOC, HANDOFF, FLAGS, REPORT,
]

# Committed text scanned for secrets (this test file is excluded on purpose: it
# carries the regexes and forbidden-token literals it searches for).
TEXT_FILES = [
    DASHBOARD, CHECK_PS, START_PS, DASH_README,
    INDEX_HTML, APP_JS, STYLES_CSS,
    CTX_README, STATUS_SCHEMA, DOC, HANDOFF, REPORT,
]

DASHBOARD_FLAGS = [
    "operator_dashboard_enabled",
    "operator_dashboard_api_enabled",
    "operator_dashboard_mutations_enabled",
    "operator_dashboard_external_access_enabled",
    "operator_dashboard_command_execution_enabled",
]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")

PS = shutil.which("pwsh") or shutil.which("powershell")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase and collapse whitespace so a phrase matches across wrapped lines."""
    return " ".join(text.lower().split())


def run_dashboard(*args, timeout=150):
    cmd = [sys.executable, str(DASHBOARD), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, json.loads(proc.stdout), proc.stderr


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=300)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


def load_dashboard_module():
    spec = importlib.util.spec_from_file_location(
        "ghoti_operator_dashboard_under_test", str(DASHBOARD)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing dashboard file: {path}")

    def test_data_source_present(self):
        self.assertTrue(STATUS_BRIDGE.is_file(), msg="status bridge must remain present")


class PythonCliTests(unittest.TestCase):
    REQUIRED_KEYS = [
        "ok", "milestone", "runtime_health", "python_resolver", "status_brain",
        "status_bridge", "telegram_status_readiness", "hermes_session",
        "ollama_gemma", "computer_use_sandbox", "disabled_capabilities",
        "next_recommended_action", "safety",
    ]

    def test_status_json_shape_and_safety(self):
        rc, data, err = run_dashboard("--status-json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, data, msg=f"status JSON missing {key}")
        self.assertTrue(data["dashboard"]["status_only"])
        self.assertTrue(data["dashboard"]["read_only"])
        safety = data["safety"]
        self.assertTrue(safety["local_only"])
        self.assertTrue(safety["read_only"])
        self.assertTrue(safety["binds_loopback_only"])
        for flag in [
            "has_post_routes", "executes_commands", "starts_or_stops_processes",
            "mutates_runtime_config", "reads_secret_values", "uses_external_assets",
            "uses_external_api", "uses_shell_true", "live_agent_launch", "mcp",
            "live_browser_computer_use", "os_input", "auto_send",
        ]:
            self.assertFalse(safety[flag], msg=f"{flag} must be false")

    def test_status_hermes_preview_is_preview_only(self):
        rc, data, err = run_dashboard("--status-json")
        self.assertEqual(rc, 0, msg=err)
        hermes = data["hermes_session"]
        self.assertIn("hermes --resume", hermes["command_preview"])
        self.assertIn("wsl -d", hermes["command_preview"])
        self.assertFalse(hermes["run_from_dashboard"])

    def test_status_telegram_is_status_only(self):
        rc, data, err = run_dashboard("--status-json")
        self.assertEqual(rc, 0, msg=err)
        tg = data["telegram_status_readiness"]
        self.assertEqual(tg["mode"], "status_only")
        self.assertFalse(tg["run_commands_enabled"])
        self.assertFalse(tg["send_commands_enabled"])
        self.assertFalse(tg["live_control_enabled"])

    def test_status_disabled_capabilities(self):
        rc, data, err = run_dashboard("--status-json")
        self.assertEqual(rc, 0, msg=err)
        dc = data["disabled_capabilities"]
        self.assertTrue(dc["dashboard_flags_all_false"])
        self.assertTrue(dc["only_status_commands_flag_enabled"])

    def test_check_json_is_all_safe(self):
        rc, data, err = run_dashboard("--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"], msg=f"check not ok: {data}")
        for key in [
            "no_post_routes", "no_command_execution", "localhost_default",
            "binds_loopback_only", "no_external_assets", "no_eval_js",
            "no_shell_true", "static_files_exist", "dashboard_script_exists",
            "feature_flags_present", "risky_flags_default_false",
            "only_status_commands_flag_enabled",
        ]:
            self.assertTrue(data[key], msg=f"check.{key} must be true")


class SourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(DASHBOARD)

    def test_no_post_handler(self):
        self.assertIsNone(
            re.search(r"def\s+do_POST", self.src),
            msg="dashboard must define no POST handler",
        )

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system(", self.src)

    def test_binds_loopback_by_default(self):
        self.assertIn("127.0.0.1", self.src)
        self.assertIn('DEFAULT_HOST = "127.0.0.1"', self.src)
        self.assertIn("ThreadingHTTPServer", self.src)

    def test_default_port_8765(self):
        self.assertIn("DEFAULT_PORT = 8765", self.src)


class StaticAssetTests(unittest.TestCase):
    EXTERNAL_RE = re.compile(
        r"https?://|//cdn\.|fonts\.googleapis|fonts\.gstatic|unpkg|jsdelivr|cdnjs",
        re.IGNORECASE,
    )

    def test_no_external_assets(self):
        for path in STATIC_PAGE_FILES:
            self.assertIsNone(
                self.EXTERNAL_RE.search(read(path)),
                msg=f"external asset/URL in {path.name}",
            )

    def test_app_js_no_dynamic_code_or_socket(self):
        code = read(APP_JS)
        self.assertIsNone(re.search(r"\beval\s*\(", code), msg="app.js must not use eval")
        self.assertIsNone(re.search(r"\bnew\s+Function\s*\(", code))
        self.assertNotIn("WebSocket", code)

    def test_index_references_local_assets_and_controls(self):
        html = read(INDEX_HTML)
        self.assertIn("Ghoti Operator Dashboard", html)
        self.assertIn("/static/app.js", html)
        self.assertIn("/static/styles.css", html)
        self.assertIn('id="refresh"', html)

    def test_index_has_no_action_forms(self):
        self.assertNotIn("<form", read(INDEX_HTML).lower())

    def test_app_js_calls_status_endpoint(self):
        self.assertIn("/api/status", read(APP_JS))


class FeatureFlagTests(unittest.TestCase):
    def setUp(self):
        self.flags = json.loads(read(FLAGS))

    def test_dashboard_flags_present_and_false(self):
        for name in DASHBOARD_FLAGS:
            self.assertIn(name, self.flags, msg=f"missing flag {name}")
            self.assertFalse(self.flags[name], msg=f"{name} must default false")

    def test_only_status_commands_flag_is_true(self):
        enabled = sorted(k for k, v in self.flags.items() if v is True)
        self.assertEqual(enabled, ["telegram_status_commands_enabled"])


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(read(STATUS_SCHEMA))

    def test_safe_posture(self):
        safety = self.schema["x_safety"]
        self.assertTrue(safety["local_only"])
        self.assertTrue(safety["read_only"])
        self.assertTrue(safety["binds_loopback_only"])
        for flag in [
            "has_post_routes", "executes_commands", "starts_or_stops_processes",
            "mutates_runtime_config", "reads_secret_values", "uses_external_assets",
            "uses_external_api", "uses_shell_true", "live_agent_launch", "mcp",
            "live_browser_computer_use", "os_input", "auto_send",
        ]:
            self.assertFalse(safety[flag], msg=f"schema {flag} must be false")

    def test_routes_are_get_only(self):
        for route in self.schema["x_routes"]:
            self.assertTrue(route.startswith("GET "), msg=f"non-GET route {route}")


class SecretScanTests(unittest.TestCase):
    def test_no_token_or_chat_id_committed(self):
        for path in TEXT_FILES:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_no_shell_true_in_dashboard(self):
        self.assertNotIn("shell=True", read(DASHBOARD))


class PowerShellSafetyScanTests(unittest.TestCase):
    @staticmethod
    def _strip_ps_comments(text):
        text = re.sub(r"<#.*?#>", "", text, flags=re.DOTALL)
        return re.sub(r"#.*", "", text)

    def test_ps_scripts_have_no_invoke_expression(self):
        for path in PS_SCRIPTS:
            code = self._strip_ps_comments(read(path))
            self.assertNotIn("invoke-expression", code.lower(),
                             msg=f"{path.name} uses Invoke-Expression")
            self.assertIsNone(re.search(r"(?i)(?:^|[\s|;(])iex(?:[\s|;)]|$)", code),
                              msg=f"{path.name} uses the iex alias")

    def test_ps_scripts_emit_json(self):
        for path in PS_SCRIPTS:
            self.assertIn("ConvertTo-Json", read(path), msg=f"{path.name} should emit JSON")


class DocsContentTests(unittest.TestCase):
    def test_status_only_and_no_live_automation(self):
        doc = norm(read(DOC))
        self.assertIn("status-only", doc)
        self.assertIn("no live automation", doc)
        self.assertIn("no external access", doc)

    def test_future_public_dashboard_requires_auth_https_and_separate_milestone(self):
        doc = norm(read(DOC))
        self.assertIn("separate milestone", doc)
        self.assertIn("authentication", doc)
        self.assertIn("https", doc)

    def test_report_has_skills_section(self):
        report = read(REPORT).lower()
        self.assertIn("skills", report)
        self.assertTrue(
            "## skills" in report or "skills detected" in report,
            msg="final report must include a skills section",
        )


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class PowerShellWrapperTests(unittest.TestCase):
    def test_check_emits_safe_json(self):
        rc, data, err = run_ps_json(CHECK_PS)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["localhost_only"])
        self.assertTrue(data["no_post_routes"])
        self.assertTrue(data["no_command_execution"])
        self.assertTrue(data["no_external_assets"])
        self.assertTrue(data["no_secrets"])
        self.assertTrue(data["risky_flags_default_false"])
        self.assertTrue(data["dashboard_script_exists"])
        self.assertTrue(data["static_files_exist"])
        self.assertTrue(data["status_json_works"])
        self.assertTrue(data["check_json_works"])
        self.assertTrue(data["ok"])

    def test_start_dry_run_is_status_only(self):
        rc, data, err = run_ps_json(START_PS, "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["status_only"])
        self.assertTrue(data["read_only"])
        self.assertTrue(data["localhost_only"])
        self.assertFalse(data["open_browser"])
        self.assertFalse(data["external_access_enabled"])
        self.assertFalse(data["command_execution_enabled"])
        self.assertIn("--serve", data["would_run_command"])
        self.assertIn("127.0.0.1", data["would_run_command"])
        self.assertIn("--port", data["would_run_command"])


class LiveServerSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_dashboard_module()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), cls.mod.DashboardHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _get(self, path):
        url = "http://127.0.0.1:{0}{1}".format(self.port, path)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()

    def _post(self, path):
        url = "http://127.0.0.1:{0}{1}".format(self.port, path)
        req = urllib.request.Request(url, data=b"{}", method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except urllib.error.URLError:
            return 0, b""

    def test_health_ok(self):
        code, body = self._get("/api/health")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertTrue(data["ok"])
        self.assertFalse(data["has_post_routes"])
        self.assertTrue(data["binds_loopback_only"])

    def test_disabled_capabilities_ok(self):
        code, body = self._get("/api/disabled-capabilities")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertTrue(data["ok"])
        self.assertTrue(data["only_status_commands_flag_enabled"])

    def test_unknown_path_is_404(self):
        code, _ = self._get("/api/does-not-exist")
        self.assertEqual(code, 404)

    def test_post_is_rejected(self):
        code, _ = self._post("/api/status")
        self.assertGreaterEqual(code, 400)


if __name__ == "__main__":
    unittest.main()
