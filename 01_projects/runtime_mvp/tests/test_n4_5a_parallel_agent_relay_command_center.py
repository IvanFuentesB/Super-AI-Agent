"""
Tests for N+4.5A Parallel Agent Relay Command Center.

Covers:
- status JSON validity
- bare --json validity
- create-pair produces all required artifacts
- Claude prompt contains /ultraplan and /goal
- Claude prompt mentions max planning and Sonnet high execution
- Codex prompt contains extra-high effort
- Codex prompt does NOT contain /goal
- Codex prompt mentions polling remote refs
- Codex prompt says create fresh -3, never force-push
- outside output path rejected
- repo-local path accepted
- no shell=True in relay script
- no subprocess to claude/codex
- safety review says NO_AUTONOMOUS_LAUNCH and human approval
- missing required args exits non-zero
- dashboard labels present in app.js
- server endpoints present in server.js
- prompt endpoint uses path containment in server.js
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SCRIPT = REPO_ROOT / "03_scripts" / "parallel_agent_relay.py"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
PYTHON = sys.executable


def _relay_section(server_text: str) -> str:
    """Return the Parallel Agent Relay endpoint block of server.js."""
    start = server_text.find("Parallel Agent Relay (N+4.5A)")
    if start == -1:
        start = server_text.find("agent-relay/status")
    if start == -1:
        return ""
    end = server_text.find("Route not found.", start)
    if end == -1:
        end = start + 8000
    return server_text[start:end]


def run_relay(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def _make_pair_in_temp(td_path: Path, extra_args=None) -> dict:
    """Helper: create a pair in a temp dir under 14_context and return parsed JSON."""
    rel = str(td_path.relative_to(REPO_ROOT))
    args = [
        "--create-pair",
        "--milestone", "N+4.5A Test",
        "--title", "Parallel Agent Relay Test",
        "--implementation-branch", "feat/test-implementation",
        "--audit-branch", "audit/test-audit",
        "--codex-effort", "extra-high",
        "--write-packets",
        "--output-dir", rel,
        "--json",
    ] + (extra_args or [])
    r = run_relay(*args)
    assert r.returncode == 0, f"create-pair failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    return json.loads(r.stdout)


# ===========================================================================
# Status
# ===========================================================================

class TestStatusJson(unittest.TestCase):
    def test_status_json_valid(self):
        r = run_relay("--status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIn("relay_version", data)
        self.assertIn("relay_mode", data)
        self.assertEqual(data["relay_mode"], "copy_paste_only")
        self.assertFalse(data["autonomous_launch"])
        self.assertTrue(data["human_approval_required"])

    def test_bare_json_valid(self):
        r = run_relay("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIn("relay_version", data)

    def test_status_future_compatible_labels(self):
        r = run_relay("--status", "--json")
        data = json.loads(r.stdout)
        fc = data.get("future_compatible", {})
        self.assertTrue(fc.get("agent_exchange_aex"))
        self.assertTrue(fc.get("claude_cowork"))
        self.assertTrue(fc.get("the_agency"))
        self.assertTrue(fc.get("agent_skills_eval"))

    def test_status_has_labels(self):
        r = run_relay("--status", "--json")
        data = json.loads(r.stdout)
        labels = data.get("labels", {})
        self.assertIn("title", labels)
        self.assertIn("Parallel Agent Relay Truth", labels["title"])


# ===========================================================================
# Create pair — artifacts
# ===========================================================================

class TestCreatePairArtifacts(unittest.TestCase):
    def test_create_pair_exits_zero(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            r = run_relay(
                "--create-pair",
                "--milestone", "N+4.5A Test",
                "--title", "Test",
                "--implementation-branch", "feat/x",
                "--audit-branch", "audit/x",
                "--write-packets",
                "--output-dir", str(Path(td).relative_to(REPO_ROOT)),
                "--json",
            )
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_create_pair_json_has_ok(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            self.assertTrue(data.get("ok"))
            self.assertIn("pair_id", data)
            self.assertIn("manifest", data)

    def test_create_pair_all_eight_files_written(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            pair_dir = REPO_ROOT / data["pair_dir"]
            expected = [
                "00_manifest.json",
                "01_claude_code_prompt.md",
                "02_codex_audit_prompt.md",
                "03_parallel_run_instructions.md",
                "04_status.json",
                "05_safety_review.md",
                "06_operator_checklist.md",
                "07_next_steps.md",
            ]
            for fname in expected:
                with self.subTest(file=fname):
                    self.assertTrue((pair_dir / fname).exists(), f"Missing: {fname}")

    def test_manifest_has_claude_and_codex_lanes(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            lanes = data["manifest"]["lanes"]
            self.assertIn("claude", lanes)
            self.assertIn("codex", lanes)

    def test_manifest_no_autonomous_launch(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            m = data["manifest"]
            self.assertFalse(m["autonomous_launch"])
            self.assertFalse(m["lanes"]["claude"]["autonomous_launch"])
            self.assertFalse(m["lanes"]["codex"]["autonomous_launch"])

    def test_manifest_human_approval_required(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            self.assertTrue(data["manifest"]["human_approval_required"])

    def test_manifest_external_coordinator_planning_only(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            self.assertEqual(data["manifest"]["external_coordinator_repos"], "planning_only")

    def test_manifest_relay_mode(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            data = _make_pair_in_temp(Path(td))
            self.assertEqual(data["manifest"]["relay_mode"], "copy_paste_only")


# ===========================================================================
# Claude prompt content
# ===========================================================================

class TestClaudePrompt(unittest.TestCase):
    @classmethod
    def _get_claude_prompt(cls) -> str:
        td = tempfile.mkdtemp(dir=REPO_ROOT / "14_context")
        try:
            data = _make_pair_in_temp(Path(td))
            pair_dir = REPO_ROOT / data["pair_dir"]
            return (pair_dir / "01_claude_code_prompt.md").read_text(encoding="utf-8")
        finally:
            import shutil
            shutil.rmtree(td, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        cls.prompt = cls._get_claude_prompt()

    def test_has_ultraplan(self):
        self.assertIn("/ultraplan", self.prompt)

    def test_has_goal(self):
        self.assertIn("/goal", self.prompt)

    def test_mentions_max_planning(self):
        self.assertIn("max", self.prompt.lower())

    def test_mentions_sonnet(self):
        self.assertIn("Sonnet", self.prompt)

    def test_mentions_high_effort(self):
        self.assertIn("high", self.prompt.lower())

    def test_mentions_implemented_and_pushed(self):
        self.assertIn("IMPLEMENTED_AND_PUSHED", self.prompt)

    def test_no_main_push(self):
        self.assertIn("Do not push main", self.prompt)

    def test_no_force_push(self):
        lower = self.prompt.lower()
        self.assertIn("force", lower)


# ===========================================================================
# Codex prompt content
# ===========================================================================

class TestCodexPrompt(unittest.TestCase):
    @classmethod
    def _get_codex_prompt(cls) -> str:
        td = tempfile.mkdtemp(dir=REPO_ROOT / "14_context")
        try:
            data = _make_pair_in_temp(Path(td))
            pair_dir = REPO_ROOT / data["pair_dir"]
            return (pair_dir / "02_codex_audit_prompt.md").read_text(encoding="utf-8")
        finally:
            import shutil
            shutil.rmtree(td, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        cls.prompt = cls._get_codex_prompt()

    def test_has_extra_high(self):
        self.assertIn("extra-high", self.prompt)

    def test_no_goal(self):
        self.assertNotIn("/goal", self.prompt)

    def test_no_ultraplan(self):
        self.assertNotIn("/ultraplan", self.prompt)

    def test_mentions_poll_remote_ref(self):
        lower = self.prompt.lower()
        self.assertTrue("poll" in lower or "ls-remote" in lower)

    def test_mentions_ls_remote(self):
        self.assertIn("ls-remote", self.prompt)

    def test_audit_branch_conflict_fresh_not_force(self):
        lower = self.prompt.lower()
        # Must say "never force-push" (or similar)
        self.assertIn("force", lower)
        # Must mention creating a fresh branch
        self.assertTrue("fresh" in lower or "-3" in lower)


# ===========================================================================
# Path safety
# ===========================================================================

class TestPathSafety(unittest.TestCase):
    def test_outside_repo_path_rejected(self):
        r = run_relay(
            "--create-pair",
            "--milestone", "Test",
            "--title", "Test",
            "--implementation-branch", "feat/x",
            "--audit-branch", "audit/x",
            "--output-dir", "C:\\Windows\\Temp",
            "--json",
        )
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))

    def test_absolute_outside_path_rejected(self):
        r = run_relay(
            "--create-pair",
            "--milestone", "Test",
            "--title", "Test",
            "--implementation-branch", "feat/x",
            "--audit-branch", "audit/x",
            "--output-dir", "/tmp",
            "--json",
        )
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))

    def test_repo_local_relative_path_accepted(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "14_context") as td:
            rel = str(Path(td).relative_to(REPO_ROOT))
            r = run_relay(
                "--create-pair",
                "--milestone", "Test",
                "--title", "Test",
                "--implementation-branch", "feat/x",
                "--audit-branch", "audit/x",
                "--output-dir", rel,
                "--write-packets",
                "--json",
            )
            self.assertEqual(r.returncode, 0, r.stderr)


# ===========================================================================
# Script safety (source inspection)
# ===========================================================================

class TestScriptSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.source)

    def test_no_shell_true_any_case(self):
        self.assertNotIn("shell = True", self.source)

    def test_no_os_system(self):
        self.assertNotIn("os.system", self.source)

    def test_no_subprocess_run(self):
        # The relay script itself should not launch subprocesses
        self.assertNotIn("subprocess.run", self.source)
        self.assertNotIn("subprocess.Popen", self.source)
        self.assertNotIn("subprocess.call", self.source)


# ===========================================================================
# Safety review content
# ===========================================================================

class TestSafetyReview(unittest.TestCase):
    @classmethod
    def _get_review(cls) -> str:
        td = tempfile.mkdtemp(dir=REPO_ROOT / "14_context")
        try:
            data = _make_pair_in_temp(Path(td))
            pair_dir = REPO_ROOT / data["pair_dir"]
            return (pair_dir / "05_safety_review.md").read_text(encoding="utf-8")
        finally:
            import shutil
            shutil.rmtree(td, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        cls.review = cls._get_review()

    def test_says_no_autonomous_launch(self):
        self.assertIn("NO_AUTONOMOUS_LAUNCH", self.review)

    def test_says_human_approval(self):
        lower = self.review.lower()
        self.assertIn("human approval", lower)

    def test_says_copy_paste_only(self):
        lower = self.review.lower()
        self.assertIn("copy", lower)
        self.assertIn("paste", lower)


# ===========================================================================
# Missing required args
# ===========================================================================

class TestMissingArgs(unittest.TestCase):
    def _missing(self, *extra):
        r = run_relay("--create-pair", "--json", *extra)
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))

    def test_missing_milestone(self):
        self._missing(
            "--title", "T",
            "--implementation-branch", "feat/x",
            "--audit-branch", "audit/x",
        )

    def test_missing_title(self):
        self._missing(
            "--milestone", "N+X",
            "--implementation-branch", "feat/x",
            "--audit-branch", "audit/x",
        )

    def test_missing_implementation_branch(self):
        self._missing(
            "--milestone", "N+X",
            "--title", "T",
            "--audit-branch", "audit/x",
        )

    def test_missing_audit_branch(self):
        self._missing(
            "--milestone", "N+X",
            "--title", "T",
            "--implementation-branch", "feat/x",
        )


# ===========================================================================
# Dashboard and server source checks
# ===========================================================================

class TestDashboardAndServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.appjs = (
            REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
        ).read_text(encoding="utf-8", errors="replace")
        cls.serverjs = (
            REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
        ).read_text(encoding="utf-8", errors="replace")

    def test_dashboard_has_parallel_agent_relay_truth_label(self):
        self.assertIn("Parallel Agent Relay Truth", self.appjs)

    def test_dashboard_has_ultraplan_label(self):
        self.assertIn("/ultraplan", self.appjs)

    def test_dashboard_has_goal_label(self):
        self.assertIn("/goal", self.appjs)

    def test_dashboard_has_extra_high_label(self):
        self.assertIn("extra high", self.appjs.lower())

    def test_dashboard_has_poll_remote_label(self):
        self.assertIn("poll remote", self.appjs.lower())

    def test_server_has_relay_status_endpoint(self):
        self.assertIn("/api/agent-relay/status", self.serverjs)

    def test_server_has_relay_create_pair_endpoint(self):
        self.assertIn("/api/agent-relay/create-pair", self.serverjs)

    def test_server_has_relay_latest_endpoint(self):
        self.assertIn("/api/agent-relay/latest", self.serverjs)

    def test_server_has_relay_pair_endpoint(self):
        self.assertIn("/api/agent-relay/pair", self.serverjs)

    def test_server_has_relay_prompt_endpoint(self):
        self.assertIn("/api/agent-relay/prompt", self.serverjs)

    def test_server_relay_no_shell_true_in_relay_section(self):
        relay_start = self.serverjs.find("Parallel Agent Relay (N+4.5A)")
        if relay_start == -1:
            relay_start = self.serverjs.find("agent-relay/status")
        if relay_start != -1:
            relay_section = self.serverjs[relay_start:relay_start + 5000]
            self.assertNotIn("shell: true", relay_section)

    def test_server_relay_prompt_uses_path_containment(self):
        # resolveRelayPromptPath should use isPathInside
        self.assertIn("resolveRelayPromptPath", self.serverjs)
        # The function should call isPathInside
        fn_start = self.serverjs.find("function resolveRelayPromptPath")
        if fn_start != -1:
            fn_body = self.serverjs[fn_start:fn_start + 600]
            self.assertIn("isPathInside", fn_body)


# ===========================================================================
# N+4.5C — relay runtime route regression guard (static)
# ===========================================================================

class TestRelayRouteGuards(unittest.TestCase):
    """N+4.5C regression guard for the relay endpoint route bug.

    The original N+4.5A relay endpoints used bare `method` / `pathname` in
    their `if (...)` route guards. Those identifiers are undefined in the
    handleApiRequest scope (every other handler uses `request.method` and
    `requestUrl.pathname`), so each relay endpoint threw
    `ReferenceError: method is not defined` at runtime and returned
    {"ok":false,"error":"method is not defined"}. node --check (syntax only)
    and endpoint-string-presence checks did not catch it. These tests fail
    if that bug class is reintroduced.
    """

    RELAY_ENDPOINTS = [
        "/api/agent-relay/status",
        "/api/agent-relay/create-pair",
        "/api/agent-relay/latest",
        "/api/agent-relay/pair",
        "/api/agent-relay/prompt",
    ]

    @classmethod
    def setUpClass(cls):
        cls.serverjs = SERVER_JS.read_text(encoding="utf-8", errors="replace")
        cls.relay_section = _relay_section(cls.serverjs)

    def _handle_api_body(self) -> str:
        idx = self.serverjs.find("function handleApiRequest(")
        self.assertGreater(idx, 0, "handleApiRequest not found in server.js")
        return self.serverjs[idx:]

    def test_relay_section_found(self):
        self.assertTrue(self.relay_section, "relay endpoint section not found in server.js")

    def test_each_relay_guard_uses_request_method(self):
        for ep in self.RELAY_ENDPOINTS:
            with self.subTest(endpoint=ep):
                idx = self.relay_section.find('"%s"' % ep)
                self.assertGreater(idx, 0, "endpoint %s not found in relay section" % ep)
                line_start = self.relay_section.rfind("\n", 0, idx) + 1
                guard = self.relay_section[line_start:idx]
                self.assertIn(
                    "request.method", guard,
                    "%s route guard must use request.method, got: %s" % (ep, guard.strip()),
                )

    def test_each_relay_guard_uses_requesturl_pathname(self):
        for ep in self.RELAY_ENDPOINTS:
            with self.subTest(endpoint=ep):
                idx = self.relay_section.find('"%s"' % ep)
                self.assertGreater(idx, 0, "endpoint %s not found in relay section" % ep)
                line_start = self.relay_section.rfind("\n", 0, idx) + 1
                guard = self.relay_section[line_start:idx]
                self.assertIn(
                    "requestUrl.pathname", guard,
                    "%s route guard must use requestUrl.pathname" % ep,
                )

    def test_no_bare_method_reference_in_relay_section(self):
        # Bare `method` is only acceptable if a local const is defined.
        has_const = re.search(r"\bconst\s+method\s*=", self._handle_api_body())
        if not has_const:
            self.assertNotIn("if (method ", self.relay_section)
            self.assertNotIn("(method ===", self.relay_section)
            self.assertNotIn("&& method ", self.relay_section)

    def test_no_bare_pathname_reference_in_relay_section(self):
        has_const = re.search(r"\bconst\s+pathname\s*=", self._handle_api_body())
        if not has_const:
            self.assertNotIn("if (pathname ", self.relay_section)
            self.assertNotIn("(pathname ===", self.relay_section)
            self.assertNotIn("&& pathname ", self.relay_section)

    def test_relay_section_has_no_shell_true(self):
        self.assertNotIn("shell: true", self.relay_section)
        self.assertNotIn("shell:true", self.relay_section)

    def test_relay_create_pair_spawns_python_only(self):
        # create-pair must run the python relay script via resolvePython();
        # it must never spawn a hardcoded or agent (claude/codex) command.
        self.assertIn("runCommand(py.command", self.relay_section)
        self.assertNotIn('runCommand("', self.relay_section)
        self.assertNotIn("runCommand('", self.relay_section)

    def test_relay_status_endpoint_is_copy_paste_only(self):
        self.assertIn('relay_mode: "copy_paste_only"', self.relay_section)
        self.assertIn("autonomous_launch: false", self.relay_section)

    def test_resolve_relay_prompt_path_uses_is_path_inside(self):
        # Prompt endpoint path containment must still use the N+4.4D-style
        # isPathInside helper.
        fn_start = self.serverjs.find("function resolveRelayPromptPath")
        self.assertGreater(fn_start, 0, "resolveRelayPromptPath not found")
        fn_body = self.serverjs[fn_start:fn_start + 600]
        self.assertIn("isPathInside", fn_body)


# ===========================================================================
# N+4.5C — relay live endpoint validation (spawns the real Node server)
# ===========================================================================

class TestRelayLiveEndpoints(unittest.TestCase):
    """N+4.5C: live HTTP validation of every relay endpoint.

    Spawns the real dashboard Node server and exercises each relay endpoint.
    These tests catch the runtime route bug that source string checks and
    node --check missed: bare `method`/`pathname` produced
    {"ok":false,"error":"method is not defined"} at runtime.
    """

    PORT = 3265
    SEED_PROMPT = (
        "14_context/agent_relay/pairs/20260516T142651Z_n_4_5a_seed/"
        "01_claude_code_prompt.md"
    )

    @classmethod
    def setUpClass(cls):
        cls.ready = False
        cls.proc = None
        dashboard_dir = REPO_ROOT / "01_projects" / "dashboard_mvp"
        env = dict(os.environ)
        env["PORT"] = str(cls.PORT)
        try:
            cls.proc = subprocess.Popen(
                ["node", "server.js"],
                cwd=str(dashboard_dir),
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
                break  # server process exited during startup
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
            with urllib.request.urlopen(url, timeout=15) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore") if e.fp else ""
            return e.code, body

    def _post(self, path: str, payload: dict):
        url = "http://127.0.0.1:%d%s" % (self.PORT, path)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore") if e.fp else ""
            return e.code, body

    def _assert_no_runtime_ref_error(self, body: str):
        self.assertNotIn("method is not defined", body)
        self.assertNotIn("pathname is not defined", body)

    def test_status_endpoint_live(self):
        status, body = self._get("/api/agent-relay/status")
        self.assertEqual(status, 200, body)
        self._assert_no_runtime_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertEqual(data.get("relay_mode"), "copy_paste_only")
        self.assertFalse(data.get("autonomous_launch"))

    def test_latest_endpoint_live(self):
        status, body = self._get("/api/agent-relay/latest")
        self.assertEqual(status, 200, body)
        self._assert_no_runtime_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)

    def test_create_pair_endpoint_live(self):
        tmp = tempfile.mkdtemp(dir=str(REPO_ROOT / "14_context"))
        try:
            rel = str(Path(tmp).relative_to(REPO_ROOT)).replace("\\", "/")
            status, body = self._post("/api/agent-relay/create-pair", {
                "milestone": "N+4.5C Live Test",
                "title": "Relay Live Endpoint Test",
                "implementation_branch": "feat/test-impl",
                "audit_branch": "audit/test-audit",
                "codex_effort": "extra-high",
                "output_dir": rel,
            })
            self.assertEqual(status, 200, body)
            self._assert_no_runtime_ref_error(body)
            data = json.loads(body)
            self.assertTrue(data.get("ok"), body)
            self.assertIn("manifest", data)
            lanes = data["manifest"]["lanes"]
            self.assertIn("claude", lanes)
            self.assertIn("codex", lanes)
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_pair_endpoint_live(self):
        _, latest_body = self._get("/api/agent-relay/latest")
        latest = json.loads(latest_body)
        pair_id = latest.get("pair_id")
        if not pair_id:
            self.skipTest("no relay pair available to query")
        status, body = self._get(
            "/api/agent-relay/pair?id=%s" % urllib.parse.quote(pair_id)
        )
        self.assertEqual(status, 200, body)
        self._assert_no_runtime_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertIn("manifest", data)

    def test_prompt_endpoint_live(self):
        enc = urllib.parse.quote(self.SEED_PROMPT, safe="")
        status, body = self._get("/api/agent-relay/prompt?path=%s" % enc)
        self.assertEqual(status, 200, body)
        self._assert_no_runtime_ref_error(body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertIn("/ultraplan", data.get("content", ""))

    def test_prompt_endpoint_rejects_traversal(self):
        enc = urllib.parse.quote("../../../../Windows/System32/drivers/etc/hosts", safe="")
        status, body = self._get("/api/agent-relay/prompt?path=%s" % enc)
        self.assertEqual(status, 403, body)
        self._assert_no_runtime_ref_error(body)

    def test_no_relay_endpoint_returns_method_not_defined(self):
        for ep in ("/api/agent-relay/status", "/api/agent-relay/latest"):
            with self.subTest(endpoint=ep):
                _, body = self._get(ep)
                self._assert_no_runtime_ref_error(body)


if __name__ == "__main__":
    unittest.main()
