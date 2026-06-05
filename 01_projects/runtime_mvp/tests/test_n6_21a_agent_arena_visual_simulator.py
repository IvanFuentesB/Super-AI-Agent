"""Tests for N+6.21A - Agent Arena Visual Simulator.

These tests lock the safety and behavior of the simulation-only agent arena in
03_scripts/agent_arena/. They assert (1) every file exists, (2) the arena --check and
--simulation-json work and the simulation is live-execution-free with six agents
covering all five states, (3) the server source defines no POST handler, makes no
subprocess/shell call, and binds the loopback interface by default, (4) the static
page loads no external assets and uses no dynamic code execution, (5) no secret is
committed, (6) a live in-process server answers GET health/simulation, returns 404 for
an unknown path, and rejects POST, and (7) the docs are simulation-first and point to
real trace ingestion as a later milestone.
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

ARENA_DIR = REPO_ROOT / "03_scripts" / "agent_arena"
ARENA = ARENA_DIR / "ghoti_agent_arena.py"
CHECK_PS = ARENA_DIR / "check_agent_arena.ps1"
START_PS = ARENA_DIR / "start_agent_arena.ps1"
STATIC_DIR = ARENA_DIR / "static"
INDEX = STATIC_DIR / "index.html"
APP = STATIC_DIR / "app.js"
STYLES = STATIC_DIR / "styles.css"

CTX_DIR = REPO_ROOT / "14_context" / "agent_arena"
SIM = CTX_DIR / "sample_simulation.json"
SCHEMA = CTX_DIR / "agent_arena_schema.json"
CTX_README = CTX_DIR / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_21A_AGENT_ARENA_VISUAL_SIMULATOR.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_21a_agent_arena_visual_simulator.md"

STATIC_PAGE_FILES = [INDEX, APP, STYLES]
ALL_FILES = [DOC, CTX_README, SIM, SCHEMA, ARENA, CHECK_PS, START_PS, INDEX, APP, STYLES, REPORT]
TEXT_FILES = [DOC, CTX_README, SIM, SCHEMA, ARENA, CHECK_PS, START_PS, INDEX, APP, STYLES, REPORT]

EXPECTED_STATES = {"idle", "queued", "running", "blocked", "done"}

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
EXTERNAL_RE = re.compile(
    r"https?://|//cdn\.|fonts\.googleapis|fonts\.gstatic|unpkg|jsdelivr|cdnjs", re.IGNORECASE
)

PS = shutil.which("pwsh") or shutil.which("powershell")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def run_py(*args, timeout=120):
    proc = subprocess.run([sys.executable, str(ARENA), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, json.loads(proc.stdout), proc.stderr


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=300)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    return proc.returncode, json.loads(out), proc.stderr.decode("utf-8", errors="replace")


def load_module():
    spec = importlib.util.spec_from_file_location("ghoti_agent_arena_under_test", str(ARENA))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class ArenaCliTests(unittest.TestCase):
    def test_check_json(self):
        rc, data, err = run_py("--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"], msg=f"check not ok: {data}")
        for key in ["no_post_routes", "no_command_execution", "no_external_assets",
                    "no_eval_js", "simulation_valid", "static_files_exist",
                    "risky_flags_default_false", "only_status_commands_flag_enabled"]:
            self.assertTrue(data[key], msg=f"check.{key} must be true")
        self.assertFalse(data["live_execution"])

    def test_simulation_json(self):
        rc, data, err = run_py("--simulation-json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertFalse(data["live_execution"])
        self.assertIsInstance(data["agents"], list)
        self.assertEqual(len(data["agents"]), 6)
        states = {a["state"] for a in data["agents"]}
        self.assertEqual(states, EXPECTED_STATES)


class SourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(ARENA)

    def test_no_post_handler(self):
        self.assertIsNone(re.search(r"def\s+do_POST", self.src))

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system(", self.src)

    def test_no_subprocess_command_execution(self):
        self.assertNotIn("import subprocess", self.src)

    def test_binds_loopback_by_default(self):
        self.assertIn('DEFAULT_HOST = "127.0.0.1"', self.src)
        self.assertIn("DEFAULT_PORT = 8766", self.src)
        self.assertIn("ThreadingHTTPServer", self.src)


class ExternalBindTests(unittest.TestCase):
    """Prove the arena cannot bind a non-loopback address (Codex N+6.21A blocker fix)."""

    def test_no_external_bind_capability_in_source(self):
        src = read(ARENA)
        self.assertNotIn("allow_nonlocal", src)
        self.assertNotIn("--allow-nonlocal-host", src)

    def test_normalize_loopback_rejects_external(self):
        mod = load_module()
        for bad in ["0.0.0.0", "::", "192.168.1.50", "10.0.0.1", "example.com", "8.8.8.8"]:
            self.assertIsNone(mod._normalize_loopback(bad), msg=f"{bad} must be refused")
        self.assertEqual(mod._normalize_loopback("127.0.0.1"), "127.0.0.1")
        self.assertEqual(mod._normalize_loopback("localhost"), "127.0.0.1")
        self.assertEqual(mod._normalize_loopback("LOCALHOST"), "127.0.0.1")
        self.assertEqual(mod._normalize_loopback("::1"), "::1")

    def test_serve_has_no_allow_nonlocal_param(self):
        import inspect
        mod = load_module()
        self.assertNotIn("allow_nonlocal_host", inspect.signature(mod.serve).parameters)

    def test_serve_cli_refuses_external_host(self):
        proc = subprocess.run(
            [sys.executable, str(ARENA), "--serve", "--host", "0.0.0.0", "--port", "8791"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 2)
        data = json.loads(proc.stdout)
        self.assertFalse(data["ok"])
        self.assertFalse(data["external_bind_possible"])

    def test_check_reports_loopback_only(self):
        rc, data, err = run_py("--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["no_external_bind_capability"])
        self.assertTrue(data["loopback_only_enforced"])


class StaticAssetTests(unittest.TestCase):
    def test_no_external_assets(self):
        for path in STATIC_PAGE_FILES:
            self.assertIsNone(EXTERNAL_RE.search(read(path)), msg=f"external asset in {path.name}")

    def test_app_js_no_dynamic_code(self):
        code = read(APP)
        self.assertIsNone(re.search(r"\beval\s*\(", code))
        self.assertIsNone(re.search(r"\bnew\s+Function\s*\(", code))
        self.assertNotIn("WebSocket", code)

    def test_index_local_assets_and_no_forms(self):
        html = read(INDEX)
        self.assertIn("Ghoti Agent Arena", html)
        self.assertIn("/static/app.js", html)
        self.assertIn("/static/styles.css", html)
        self.assertNotIn("<form", html.lower())

    def test_app_calls_simulation(self):
        self.assertIn("/api/simulation", read(APP))


class SecretScanTests(unittest.TestCase):
    def test_no_token_or_chat_id(self):
        for path in TEXT_FILES:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9]{20,}")
        self.assertNotRegex(combined, r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")


class SimulationDataTests(unittest.TestCase):
    def test_sample_simulation_is_safe(self):
        data = json.loads(read(SIM))
        self.assertFalse(data["live_execution"])
        self.assertTrue(data["simulation"])
        self.assertEqual(len(data["agents"]), 6)
        self.assertEqual({a["state"] for a in data["agents"]}, EXPECTED_STATES)

    def test_schema_safe_posture(self):
        schema = json.loads(read(SCHEMA))
        self.assertFalse(schema["x_safety"]["live_execution"])
        self.assertTrue(schema["x_safety"]["simulation"])
        self.assertFalse(schema["x_safety"]["has_post_routes"])


class DocsContentTests(unittest.TestCase):
    def test_simulation_first(self):
        self.assertIn("simulation-first", norm(read(DOC)))

    def test_real_trace_ingestion_later(self):
        doc = norm(read(DOC))
        self.assertIn("real trace ingestion", doc)
        self.assertTrue("next milestone" in doc or "later milestone" in doc or "later" in doc)


class LiveServerSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), cls.mod.ArenaHandler)
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
        req = urllib.request.Request("http://127.0.0.1:{0}{1}".format(self.port, path),
                                     data=b"{}", method="POST")
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

    def test_simulation_ok(self):
        code, body = self._get("/api/simulation")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertTrue(data["ok"])
        self.assertFalse(data["live_execution"])
        self.assertEqual(len(data["agents"]), 6)

    def test_unknown_path_404(self):
        code, _ = self._get("/api/does-not-exist")
        self.assertEqual(code, 404)

    def test_post_rejected(self):
        code, _ = self._post("/api/simulation")
        self.assertGreaterEqual(code, 400)


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class PowerShellWrapperTests(unittest.TestCase):
    def test_check_emits_safe_json(self):
        rc, data, err = run_ps_json(CHECK_PS)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["check_json_works"])
        self.assertTrue(data["simulation_json_works"])
        self.assertTrue(data["no_post_routes"])
        self.assertTrue(data["no_external_assets"])
        self.assertTrue(data["only_status_commands_flag_enabled"])
        self.assertTrue(data["ok"])

    def test_start_dry_run(self):
        rc, data, err = run_ps_json(START_PS, "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["simulation_only"])
        self.assertFalse(data["open_browser"])
        self.assertFalse(data["live_execution"])
        self.assertIn("--serve", data["would_run_command"])
        self.assertIn("127.0.0.1", data["would_run_command"])
        self.assertIn("--port", data["would_run_command"])


if __name__ == "__main__":
    unittest.main()
