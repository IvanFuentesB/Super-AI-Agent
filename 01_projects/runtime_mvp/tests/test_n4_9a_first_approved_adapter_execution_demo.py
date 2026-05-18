#!/usr/bin/env python3
"""N+4.9A tests: First Approved Adapter Execution Demo.

Covers:
- runner --status/--json valid; --list-adapters includes agent_skills_eval
- unknown adapter rejected
- create-approval writes an approval record
- approval token required for non-dry-run; dry-run allowed without token
- dry-run demo creates all 6 required artifacts
- execution manifest: external_code_executed / installs_performed /
  desktop_control_enabled all false
- evaluation JSON has score and recommendations
- adapter exposes evaluate_skill_file / execute_demo / status / capabilities
- adapter imports no external repo packages
- dashboard labels + server endpoints exist; no shell:true
- live run-demo endpoint returns ok true
- no path escape; no secrets
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
RUNNER = REPO_ROOT / "03_scripts" / "approved_adapter_runner.py"
ADAPTER = REPO_ROOT / "02_automation" / "external_tool_adapters" / "agent_skills_eval_adapter.py"
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"
SERVER_JS = DASHBOARD_DIR / "server.js"
INDEX_HTML = DASHBOARD_DIR / "public" / "index.html"
PYTHON = sys.executable

REQUIRED_ARTIFACTS = [
    "00_demo_skill.md",
    "01_skill_evaluation.md",
    "02_skill_evaluation.json",
    "03_safety_review.md",
    "04_execution_manifest.json",
    "05_human_next_steps.md",
]
REQUIRED_DASHBOARD_LABELS = [
    "Approved Adapter Execution Truth",
    "Approved Adapter Execution",
    "agent-skills-eval Adapter",
    "Run Safe Adapter Demo",
    "Dry Run Available",
    "Approval Token Required",
    "Local Artifacts Only",
    "No External Repo Code Execution",
    "No Installs",
    "No Desktop Control",
    "No Live APIs",
    "Human Approval Required",
    "Latest Adapter Run",
]
SERVER_ENDPOINTS = [
    "/api/adapter-execution/status",
    "/api/adapter-execution/adapters",
    "/api/adapter-execution/create-approval",
    "/api/adapter-execution/run-demo",
    "/api/adapter-execution/latest",
]


def run_runner(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(RUNNER)] + list(args),
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180,
    )


def _load_adapter():
    spec = importlib.util.spec_from_file_location("n4_9a_agent_skills_eval_adapter", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# Runner status / catalog
# ===========================================================================

class TestRunnerStatus(unittest.TestCase):
    def test_status_json_valid(self):
        r = run_runner("--status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("runner"), "approved_adapter_runner")
        self.assertEqual(data.get("default_adapter"), "agent_skills_eval")

    def test_bare_json_valid(self):
        r = run_runner("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))

    def test_list_adapters_includes_agent_skills_eval(self):
        data = json.loads(run_runner("--list-adapters", "--json").stdout)
        keys = [a.get("key") for a in data.get("adapters", [])]
        self.assertIn("agent_skills_eval", keys)

    def test_unknown_adapter_rejected(self):
        r = run_runner("--execute-approved", "--adapter", "evil_tool", "--dry-run", "--json")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(json.loads(r.stdout).get("ok", True))

    def test_status_declares_safe_scope(self):
        data = json.loads(run_runner("--status", "--json").stdout)
        self.assertFalse(data.get("external_code_executed"))
        self.assertFalse(data.get("installs_performed"))
        self.assertFalse(data.get("desktop_control_enabled"))
        self.assertFalse(data.get("live_api_enabled"))
        self.assertTrue(data.get("human_approval_required"))


# ===========================================================================
# Approval flow
# ===========================================================================

class TestApprovalFlow(unittest.TestCase):
    def test_create_approval_writes_record(self):
        r = run_runner("--create-approval", "--adapter", "agent_skills_eval", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertIn("approval_id", data)
        record = data.get("approval_record", "")
        self.assertTrue(record.startswith("14_context/adapter_execution/approvals/"))
        self.assertTrue((REPO_ROOT / record).exists())

    def test_approval_token_required_for_non_dry_run(self):
        # No token, not dry-run -> refused.
        r = run_runner("--execute-approved", "--adapter", "agent_skills_eval", "--json")
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))
        self.assertIn("approval token required", (data.get("error") or "").lower())

    def test_dry_run_allowed_without_token(self):
        r = run_runner("--execute-approved", "--adapter", "agent_skills_eval", "--dry-run", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))

    def test_created_token_authorizes_non_dry_run(self):
        approval = json.loads(
            run_runner("--create-approval", "--adapter", "agent_skills_eval", "--json").stdout)
        token = approval.get("approval_token")
        self.assertTrue(token)
        r = run_runner("--execute-approved", "--adapter", "agent_skills_eval",
                        "--approval-token", token, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("mode"), "approved_execution")
        self.assertTrue(data.get("approval_verified"))


# ===========================================================================
# Dry-run demo artifacts
# ===========================================================================

class TestDryRunArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(
            run_runner("--execute-approved", "--adapter", "agent_skills_eval",
                       "--dry-run", "--json").stdout)
        cls.run_dir = REPO_ROOT / cls.result["run_dir"]

    def test_demo_run_ok(self):
        self.assertTrue(self.result.get("ok"))
        self.assertEqual(self.result.get("mode"), "dry_run")

    def test_all_six_artifacts_created(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertTrue((self.run_dir / name).exists(), "missing artifact: %s" % name)

    def test_execution_manifest_declares_safe_scope(self):
        manifest = json.loads((self.run_dir / "04_execution_manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest.get("external_code_executed"))
        self.assertFalse(manifest.get("installs_performed"))
        self.assertFalse(manifest.get("desktop_control_enabled"))
        self.assertFalse(manifest.get("live_api_used"))
        self.assertFalse(manifest.get("external_repo_packages_imported"))

    def test_evaluation_json_has_score_and_recommendations(self):
        ev = json.loads((self.run_dir / "02_skill_evaluation.json").read_text(encoding="utf-8"))
        self.assertIsInstance(ev.get("score"), int)
        self.assertGreaterEqual(ev.get("score"), 0)
        self.assertLessEqual(ev.get("score"), 100)
        self.assertIn("recommendations", ev)
        self.assertIsInstance(ev.get("recommendations"), list)
        self.assertIsInstance(ev.get("dimensions"), list)

    def test_run_dir_is_repo_local(self):
        rd = self.result["run_dir"]
        self.assertTrue(rd.startswith("14_context/adapter_execution/runs/"))
        self.assertNotIn("..", rd)


# ===========================================================================
# Adapter module
# ===========================================================================

class TestAdapterModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_adapter()
        cls.src = ADAPTER.read_text(encoding="utf-8")

    def test_adapter_is_promoted(self):
        self.assertTrue(getattr(self.mod, "ADAPTER_PROMOTED", False))
        self.assertIn("ADAPTER_PROMOTED = True", self.src)

    def test_adapter_exposes_evaluate_and_execute(self):
        self.assertTrue(callable(getattr(self.mod, "evaluate_skill_file", None)))
        self.assertTrue(callable(getattr(self.mod, "execute_demo", None)))
        self.assertTrue(callable(getattr(self.mod, "status", None)))
        self.assertTrue(callable(getattr(self.mod, "capabilities", None)))
        self.assertTrue(callable(getattr(self.mod, "safety_gates", None)))

    def test_adapter_status_safe(self):
        st = self.mod.status()
        self.assertFalse(st.get("wired"))
        self.assertFalse(st.get("external_code_executed"))
        self.assertFalse(st.get("desktop_control_enabled"))
        self.assertFalse(st.get("live_api_enabled"))
        self.assertTrue(st.get("requires_human_approval"))

    def test_adapter_imports_no_external_repo_packages(self):
        stdlib_allow = {"json", "os", "re", "sys", "datetime", "pathlib", "hashlib"}
        for line in self.src.splitlines():
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            module = stripped.split()[1].split(".")[0]
            with self.subTest(line=stripped):
                self.assertIn(module, stdlib_allow,
                              "adapter imports a non-stdlib module: %s" % stripped)

    def test_adapter_requires_approval_for_non_dry_run(self):
        self.assertTrue(getattr(self.mod, "REQUIRES_HUMAN_APPROVAL", False))
        gates = self.mod.safety_gates()
        self.assertIn("non_dry_run_requires_approval_token", gates)


# ===========================================================================
# Runner source safety
# ===========================================================================

class TestRunnerSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = RUNNER.read_text(encoding="utf-8")

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("shell = True", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system", self.src)

    def test_no_subprocess(self):
        # The runner itself launches no subprocess — it only imports Ghoti
        # adapter modules and reads/writes local files.
        self.assertNotIn("subprocess", self.src)

    def test_repo_local_containment(self):
        self.assertIn("def _is_repo_local(", self.src)

    def test_no_path_escape_patterns(self):
        self.assertNotIn("..\\", self.src)
        self.assertNotIn("../", self.src)

    def test_no_secrets(self):
        lowered = self.src.lower()
        for needle in ("api_key", "apikey", "password", "bearer "):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, lowered)

    def test_no_external_urls(self):
        self.assertNotIn("http://", self.src)
        self.assertNotIn("https://", self.src)


# ===========================================================================
# Dashboard + server
# ===========================================================================

class TestDashboardAndServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")
        cls.server = SERVER_JS.read_text(encoding="utf-8", errors="replace")

    def test_dashboard_card_present(self):
        self.assertIn('id="approved-adapter-execution-truth"', self.html)

    def test_all_required_labels_present(self):
        for label in REQUIRED_DASHBOARD_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_server_endpoints_present(self):
        for ep in SERVER_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, self.server)

    def test_server_section_no_shell_true(self):
        start = self.server.find("Approved Adapter Execution (N+4.9A)")
        if start == -1:
            start = self.server.find("/api/adapter-execution/status")
        self.assertGreater(start, 0)
        section = self.server[start:start + 6000]
        self.assertNotIn("shell: true", section)
        self.assertNotIn("shell:true", section)

    def test_server_endpoints_use_request_method(self):
        for ep in SERVER_ENDPOINTS:
            with self.subTest(endpoint=ep):
                idx = self.server.find('"%s"' % ep)
                self.assertGreater(idx, 0)
                line_start = self.server.rfind("\n", 0, idx) + 1
                guard = self.server[line_start:idx]
                self.assertIn("request.method", guard)
                self.assertIn("requestUrl.pathname", guard)

    def test_run_demo_endpoint_is_dry_run_only(self):
        idx = self.server.find("/api/adapter-execution/run-demo")
        self.assertGreater(idx, 0)
        block = self.server[idx:idx + 600]
        self.assertIn("--dry-run", block)


# ===========================================================================
# Live endpoints
# ===========================================================================

class TestLiveEndpoints(unittest.TestCase):
    PORT = 3267

    @classmethod
    def setUpClass(cls):
        cls.ready = False
        cls.proc = None
        env = dict(os.environ)
        env["PORT"] = str(cls.PORT)
        try:
            cls.proc = subprocess.Popen(
                ["node", "server.js"], cwd=str(DASHBOARD_DIR),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
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
                    "http://127.0.0.1:%d/api/health" % cls.PORT, timeout=2) as r:
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
            self.skipTest("dashboard Node server not ready")

    def _get(self, path):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d%s" % (self.PORT, path), timeout=20) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")

    def _post(self, path):
        req = urllib.request.Request(
            "http://127.0.0.1:%d%s" % (self.PORT, path),
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")

    def test_status_endpoint_live(self):
        status, body = self._get("/api/adapter-execution/status")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"))

    def test_adapters_endpoint_live(self):
        status, body = self._get("/api/adapter-execution/adapters")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"))

    def test_latest_endpoint_live(self):
        status, body = self._get("/api/adapter-execution/latest")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"))

    def test_run_demo_endpoint_live(self):
        status, body = self._post("/api/adapter-execution/run-demo")
        self.assertEqual(status, 200, body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertEqual(data.get("mode"), "dry_run")
        self.assertNotIn("method is not defined", body)

    def test_create_approval_endpoint_live(self):
        status, body = self._post("/api/adapter-execution/create-approval")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"), body)


if __name__ == "__main__":
    unittest.main()
