"""Tests for N+6.23A - Agent Arena real trace ingestion + memory vault status view.

These tests lock the safety and behavior of the read-only trace ingestion added to the
agent arena. They assert (1) every new file exists, (2) the trace loader is read-only
and file-only: no subprocess, no shell, no os.system, no file writes, and its --check
passes, (3) the loader's --trace-json is a local_trace with simulation/live_execution
false, four derived agents, a reports list, and a status block with the five required
cards, (4) the arena source still defines no POST handler and no subprocess/shell call,
exposes the new GET /api/trace and /api/trace-status routes, and its --check stays ok,
(5) the static page gained a buttons-only view toggle and a status-cards section with no
<form>, no external asset, and no dynamic code execution, (6) a live in-process server
answers GET /api/trace and /api/trace-status, still answers /api/simulation, returns 404
for an unknown path, and rejects POST, (7) the trace schema and sample trace are valid
and safe, and (8) no secret and no real local path / username is committed. Flagged
literals are assembled at runtime so this file never contains them.
"""

import importlib.util
import json
import re
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
LOADER = ARENA_DIR / "ghoti_agent_arena_trace_loader.py"
STATIC_DIR = ARENA_DIR / "static"
INDEX = STATIC_DIR / "index.html"
APP = STATIC_DIR / "app.js"
STYLES = STATIC_DIR / "styles.css"

CTX_DIR = REPO_ROOT / "14_context" / "agent_arena"
TRACE_SCHEMA = CTX_DIR / "trace_schema.json"
SAMPLE_TRACE = CTX_DIR / "sample_trace.json"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_23A_AGENT_ARENA_TRACE_INGESTION.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_23a_agent_arena_trace_ingestion.md"

NEW_FILES = [LOADER, TRACE_SCHEMA, SAMPLE_TRACE, DOC, REPORT]
TEXT_FILES = [LOADER, TRACE_SCHEMA, SAMPLE_TRACE, DOC, REPORT, ARENA, INDEX, APP, STYLES]

STATUS_CARDS = [
    "latest_main_commit_recorded", "latest_claude_branch", "latest_codex_audit",
    "memory_vault_present", "tool_intake_present",
]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
EXTERNAL_RE = re.compile(
    r"https?://|//cdn\.|fonts\.googleapis|fonts\.gstatic|unpkg|jsdelivr|cdnjs", re.IGNORECASE
)


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def run_py(script, *args, timeout=120):
    proc = subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def load_arena():
    spec = importlib.util.spec_from_file_location("ghoti_agent_arena_n6_23a", str(ARENA))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FilesExistTests(unittest.TestCase):
    def test_new_files_exist(self):
        for path in NEW_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class LoaderSourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(LOADER)

    def test_no_subprocess(self):
        self.assertNotIn("import subprocess", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system(", self.src)

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)

    def test_no_file_writes(self):
        self.assertNotIn(".write_text(", self.src)
        self.assertNotIn(".write_bytes(", self.src)
        self.assertNotIn(".mkdir(", self.src)

    def test_no_network(self):
        for token in ["import requests", "urllib.request", "http.client", "socket."]:
            self.assertNotIn(token, self.src, msg=f"loader must not use {token}")


class LoaderCliTests(unittest.TestCase):
    def test_check_ok(self):
        rc, out, err = run_py(LOADER, "--check")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"], msg=f"loader check not ok: {data}")
        for key in ["reads_files_only", "no_subprocess", "no_writes",
                    "trace_builds", "status_builds", "sample_trace_valid", "schema_present"]:
            self.assertTrue(data[key], msg=f"loader check.{key} must be true")

    def test_trace_json_is_safe_local_trace(self):
        rc, out, err = run_py(LOADER, "--trace-json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["mode"], "local_trace")
        self.assertFalse(data["simulation"])
        self.assertFalse(data["live_execution"])
        self.assertEqual(len(data["agents"]), 4)
        self.assertIsInstance(data["reports"], list)
        self.assertIsInstance(data["status"], dict)
        for card in STATUS_CARDS:
            self.assertIn(card, data["status"], msg=f"status missing {card}")

    def test_status_json_has_cards(self):
        rc, out, err = run_py(LOADER, "--status-json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertFalse(data["live_execution"])
        status = data["status"]
        for card in STATUS_CARDS:
            self.assertIn(card, status)
        self.assertIsInstance(status["memory_vault_present"], bool)
        self.assertIsInstance(status["tool_intake_present"], bool)


class ArenaSourceTests(unittest.TestCase):
    def setUp(self):
        self.src = read(ARENA)

    def test_no_post_handler(self):
        self.assertIsNone(re.search(r"def\s+do_POST", self.src))

    def test_no_subprocess_or_shell(self):
        self.assertNotIn("import subprocess", self.src)
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("os.system(", self.src)

    def test_trace_routes_present(self):
        self.assertIn("/api/trace", self.src)
        self.assertIn("/api/trace-status", self.src)

    def test_loopback_defaults_preserved(self):
        self.assertIn('DEFAULT_HOST = "127.0.0.1"', self.src)
        self.assertIn("DEFAULT_PORT = 8766", self.src)
        self.assertIn("ThreadingHTTPServer", self.src)

    def test_no_external_bind_capability(self):
        self.assertNotIn("allow_nonlocal", self.src)

    def test_check_ok_with_trace_keys(self):
        rc, out, err = run_py(ARENA, "--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"], msg=f"arena check not ok: {data}")
        for key in ["trace_loader_present", "trace_safe", "no_post_routes",
                    "no_external_bind_capability"]:
            self.assertTrue(data[key], msg=f"arena check.{key} must be true")
        self.assertFalse(data["trace_live_execution"])


class StaticUiTests(unittest.TestCase):
    def test_index_has_toggle_and_status_no_form(self):
        html = read(INDEX)
        self.assertIn("Ghoti Agent Arena", html)
        self.assertIn('id="view-sim"', html)
        self.assertIn('id="view-trace"', html)
        self.assertIn('id="status-cards"', html)
        self.assertNotIn("<form", html.lower())

    def test_app_uses_both_endpoints_no_dynamic_code(self):
        code = read(APP)
        self.assertIn("/api/simulation", code)
        self.assertIn("/api/trace", code)
        self.assertIsNone(re.search(r"\beval\s*\(", code))
        self.assertIsNone(re.search(r"\bnew\s+Function\s*\(", code))
        self.assertNotIn("WebSocket", code)

    def test_no_external_assets(self):
        for path in [INDEX, APP, STYLES]:
            self.assertIsNone(EXTERNAL_RE.search(read(path)), msg=f"external asset in {path.name}")


class TraceSchemaAndSampleTests(unittest.TestCase):
    def test_schema_safe_posture(self):
        schema = json.loads(read(TRACE_SCHEMA))
        self.assertFalse(schema["x_safety"]["live_execution"])
        self.assertFalse(schema["x_safety"]["simulation"])
        self.assertTrue(schema["x_safety"]["read_only"])

    def test_sample_trace_valid_and_safe(self):
        data = json.loads(read(SAMPLE_TRACE))
        self.assertEqual(data["mode"], "local_trace")
        self.assertFalse(data["simulation"])
        self.assertFalse(data["live_execution"])
        self.assertEqual(len(data["agents"]), 4)
        for card in STATUS_CARDS:
            self.assertIn(card, data["status"])


class DocsContentTests(unittest.TestCase):
    def test_doc_read_only_trace(self):
        doc = norm(read(DOC))
        self.assertIn("read-only", doc)
        self.assertIn("/api/trace", doc)

    def test_report_has_verdict(self):
        body = read(REPORT)
        self.assertIn("IMPLEMENTED_AND_PUSHED", body)


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


class NoLocalPathLeakTests(unittest.TestCase):
    """Committed N+6.23A files must carry no real local path / username. Forbidden
    tokens are assembled at runtime so this file never contains them literally."""

    def test_no_real_local_path_leak(self):
        bslash = chr(92)
        forbidden = [
            "ai" + "_sandbox",
            "Nav" + "if",
            "C:" + bslash + "Users" + bslash,
            "C:" + "/Users/",
            "/mnt/" + "c/Users/",
            "Documents" + bslash + "AI_Managed_Only",
        ]
        for path in TEXT_FILES:
            text = read(path)
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"local path/username leak in {path.name}")


class LiveServerSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_arena()
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

    def test_trace_endpoint(self):
        code, body = self._get("/api/trace")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data["mode"], "local_trace")
        self.assertFalse(data["simulation"])
        self.assertFalse(data["live_execution"])
        self.assertEqual(len(data["agents"]), 4)
        self.assertIsInstance(data["reports"], list)
        for card in STATUS_CARDS:
            self.assertIn(card, data["status"])

    def test_trace_status_endpoint(self):
        code, body = self._get("/api/trace-status")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertFalse(data["live_execution"])
        for card in STATUS_CARDS:
            self.assertIn(card, data["status"])

    def test_simulation_still_ok(self):
        code, body = self._get("/api/simulation")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertTrue(data["ok"])
        self.assertFalse(data["live_execution"])

    def test_unknown_path_404(self):
        code, _ = self._get("/api/does-not-exist")
        self.assertEqual(code, 404)

    def test_post_rejected(self):
        code, _ = self._post("/api/trace")
        self.assertGreaterEqual(code, 400)


if __name__ == "__main__":
    unittest.main()
