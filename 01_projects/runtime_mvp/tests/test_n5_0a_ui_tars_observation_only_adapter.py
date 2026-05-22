#!/usr/bin/env python3
"""N+5.0A tests: UI-TARS Observation-Only Adapter.

Covers:
- CLI --status/--json/--latest valid
- create-approval writes a hash-only approval record
- dry-run observation creates all required artifacts
- observation manifest unsafe flags all false
- capture-screen without token rejected; non-dry-run without token rejected
- optional capture degrades truthfully (or succeeds) with a valid token
- adapter module exists, stdlib-only, no UI-TARS imports, no click/type enabled
- dashboard labels + server endpoints exist; no shell:true
- live dry-run endpoint returns ok; capture-approved without token rejected
- GET endpoints do not leak a raw token; path containment; no secrets
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
CLI = REPO_ROOT / "03_scripts" / "ui_tars_observation_adapter.py"
ADAPTER = REPO_ROOT / "02_automation" / "external_tool_adapters" / "ui_tars_observation_adapter.py"
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"
SERVER_JS = DASHBOARD_DIR / "server.js"
INDEX_HTML = DASHBOARD_DIR / "public" / "index.html"
PYTHON = sys.executable

REQUIRED_ARTIFACTS = [
    "00_observation_manifest.json",
    "01_ui_tars_static_context.md",
    "02_observation_report.md",
    "03_observation.json",
    "04_safety_review.md",
    "05_human_next_steps.md",
    "10_preview.html",
]
REQUIRED_DASHBOARD_LABELS = [
    "UI-TARS Observation Truth",
    "UI-TARS Observation Only",
    "Observation Packet",
    "Dry Run Observation",
    "Screenshot Capture Requires Approval",
    "No Click",
    "No Type",
    "No Hotkeys",
    "No Desktop Control Yet",
    "No UI-TARS Runtime Yet",
    "No External Repo Code Execution",
    "No Installs",
    "Local Artifacts Only",
    "Human Approval Required",
    "Latest Observation Run",
]
SERVER_ENDPOINTS = [
    "/api/ui-tars-observation/status",
    "/api/ui-tars-observation/create-approval",
    "/api/ui-tars-observation/dry-run",
    "/api/ui-tars-observation/capture-approved",
    "/api/ui-tars-observation/latest",
]


def run_cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(CLI)] + list(args),
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180,
    )


def _load_adapter():
    spec = importlib.util.spec_from_file_location("n5_0a_ui_tars_observation_adapter", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# CLI status
# ===========================================================================

class TestObservationCli(unittest.TestCase):
    def test_status_json_valid(self):
        r = run_cli("--status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("mode"), "observation_only")
        self.assertEqual(data.get("default_run_mode"), "dry_run")

    def test_bare_json_valid(self):
        r = run_cli("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))

    def test_latest_json_valid(self):
        r = run_cli("--latest", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))

    def test_status_unsafe_flags_false(self):
        data = json.loads(run_cli("--status", "--json").stdout)
        for flag in ("ui_tars_runtime_started", "external_code_executed",
                     "installs_performed", "desktop_control_enabled",
                     "click_enabled", "type_enabled", "hotkeys_enabled",
                     "live_api_enabled"):
            self.assertFalse(data.get(flag), "%s must be false" % flag)


# ===========================================================================
# Approval + gating
# ===========================================================================

class TestApprovalAndGating(unittest.TestCase):
    def test_create_approval_writes_hash_only_record(self):
        r = run_cli("--create-approval", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        record_rel = data.get("approval_record", "")
        self.assertTrue(record_rel.startswith("14_context/ui_tars_observation/approvals/"))
        record = json.loads((REPO_ROOT / record_rel).read_text(encoding="utf-8"))
        self.assertIn("token_hash", record)
        # The stored record must NOT contain the raw token.
        self.assertNotIn("token", record)
        self.assertNotIn("approval_token", record)

    def test_capture_screen_without_token_rejected(self):
        r = run_cli("--observe", "--capture-screen", "--json")
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))
        self.assertIn("token", (data.get("error") or "").lower())

    def test_non_dry_run_without_token_rejected(self):
        # A non-dry-run is intended via --capture-screen; without a token it fails.
        r = run_cli("--observe", "--capture-screen", "--json")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(json.loads(r.stdout).get("ok", True))

    def test_invalid_token_rejected(self):
        r = run_cli("--observe", "--capture-screen", "--approval-token", "deadbeef", "--json")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(json.loads(r.stdout).get("ok", True))


# ===========================================================================
# Dry-run observation artifacts
# ===========================================================================

class TestDryRunArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(run_cli("--observe", "--dry-run", "--json").stdout)
        cls.run_dir = REPO_ROOT / cls.result["run_dir"]

    def test_dry_run_ok(self):
        self.assertTrue(self.result.get("ok"))
        self.assertEqual(self.result.get("mode"), "dry_run")

    def test_all_required_artifacts_created(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertTrue((self.run_dir / name).exists(), "missing artifact: %s" % name)

    def test_dry_run_did_not_capture(self):
        self.assertFalse(self.result.get("screenshot_captured"))

    def test_manifest_unsafe_flags_false(self):
        manifest = json.loads((self.run_dir / "00_observation_manifest.json").read_text(encoding="utf-8"))
        for flag in ("external_repo_code_executed", "installs_performed",
                     "ui_tars_runtime_started", "desktop_control_enabled", "live_api_used"):
            self.assertFalse(manifest.get(flag), "%s must be false" % flag)

    def test_manifest_includes_contract_fields(self):
        # N+5.0B manifest contract: local_only / click_enabled / type_enabled
        # must be present in 00_observation_manifest.json (not just in
        # 03_observation.json).
        manifest = json.loads((self.run_dir / "00_observation_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("local_only", manifest)
        self.assertIn("click_enabled", manifest)
        self.assertIn("type_enabled", manifest)
        self.assertTrue(manifest.get("local_only") is True, "manifest local_only must be true")
        self.assertTrue(manifest.get("click_enabled") is False, "manifest click_enabled must be false")
        self.assertTrue(manifest.get("type_enabled") is False, "manifest type_enabled must be false")

    def test_observation_json_unsafe_flags_false(self):
        obs = json.loads((self.run_dir / "03_observation.json").read_text(encoding="utf-8"))
        self.assertEqual(obs.get("adapter_name"), "ui_tars_observation_only")
        for flag in ("external_repo_code_executed", "installs_performed",
                     "ui_tars_runtime_started", "desktop_control_enabled",
                     "click_enabled", "type_enabled", "hotkeys_enabled", "live_api_used"):
            self.assertFalse(obs.get(flag), "%s must be false" % flag)
        self.assertTrue(obs.get("approval_required_for_capture"))
        self.assertIsInstance(obs.get("next_safe_step_recommendations"), list)

    def test_run_dir_repo_local(self):
        rd = self.result["run_dir"]
        self.assertTrue(rd.startswith("14_context/ui_tars_observation/runs/"))
        self.assertNotIn("..", rd)


# ===========================================================================
# Optional capture degrades truthfully
# ===========================================================================

class TestCaptureDegrade(unittest.TestCase):
    def test_capture_with_token_is_truthful(self):
        approval = json.loads(run_cli("--create-approval", "--json").stdout)
        token = approval.get("approval_token")
        self.assertTrue(token)
        r = run_cli("--observe", "--capture-screen", "--approval-token", token, "--json")
        # The observation packet is always produced; capture either succeeds
        # (local PNG) or degrades truthfully with a reason.
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"), r.stdout)
        captured = data.get("screenshot_captured")
        self.assertIn(captured, (True, False))
        if captured:
            self.assertTrue(data.get("screenshot_path"))
        else:
            self.assertTrue(data.get("screenshot_skipped_reason"))
        # Never UI-TARS, never desktop control regardless of capture outcome.
        self.assertFalse(data.get("ui_tars_runtime_started"))
        self.assertFalse(data.get("desktop_control_enabled"))


# ===========================================================================
# Adapter module
# ===========================================================================

class TestAdapterModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_adapter()
        cls.src = ADAPTER.read_text(encoding="utf-8")

    def test_adapter_exists_and_exposes_functions(self):
        self.assertTrue(callable(getattr(self.mod, "status", None)))
        self.assertTrue(callable(getattr(self.mod, "capabilities", None)))
        self.assertTrue(callable(getattr(self.mod, "safety_gates", None)))
        self.assertTrue(callable(getattr(self.mod, "create_observation_packet", None)))

    def test_adapter_status_observation_only(self):
        st = self.mod.status()
        self.assertEqual(st.get("adapter_kind"), "observation_only")
        self.assertFalse(st.get("ui_tars_runtime_started"))
        self.assertFalse(st.get("desktop_control_enabled"))
        self.assertFalse(st.get("click_enabled"))
        self.assertFalse(st.get("type_enabled"))
        self.assertFalse(st.get("hotkeys_enabled"))
        self.assertTrue(st.get("requires_human_approval"))

    def test_adapter_stdlib_only_no_ui_tars_imports(self):
        stdlib_allow = {"json", "os", "re", "sys", "subprocess", "tempfile",
                        "datetime", "pathlib", "hashlib"}
        for line in self.src.splitlines():
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            module = stripped.split()[1].split(".")[0]
            with self.subTest(line=stripped):
                self.assertIn(module, stdlib_allow,
                              "adapter imports a non-stdlib module: %s" % stripped)
            low = stripped.lower()
            for needle in ("ui_tars", "uitars"):
                self.assertNotIn(needle, low, "adapter imports UI-TARS: %s" % stripped)

    def test_adapter_no_desktop_control_libraries(self):
        low = self.src.lower()
        for needle in ("pyautogui", "sendkeys", "mouse_event", "keybd_event",
                       ".click(", "pynput"):
            self.assertNotIn(needle, low, "adapter must not use desktop-control: %s" % needle)

    def test_safety_gates_block_unapproved(self):
        gates = self.mod.safety_gates()
        self.assertIn("observation_only_no_desktop_control", gates)
        self.assertIn("no_click_no_type_no_hotkeys", gates)
        self.assertIn("no_ui_tars_runtime", gates)
        self.assertIn("screenshot_capture_requires_approval_token", gates)


# ===========================================================================
# CLI source safety
# ===========================================================================

class TestCliSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = CLI.read_text(encoding="utf-8")

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("shell = True", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system", self.src)

    def test_path_containment(self):
        self.assertIn("def _is_repo_local(", self.src)

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
        self.assertIn('id="ui-tars-observation-truth"', self.html)

    def test_all_required_labels_present(self):
        for label in REQUIRED_DASHBOARD_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_server_endpoints_present(self):
        for ep in SERVER_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, self.server)

    def test_server_section_no_shell_true(self):
        start = self.server.find("UI-TARS Observation Only (N+5.0A)")
        if start == -1:
            start = self.server.find("/api/ui-tars-observation/status")
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

    def test_dry_run_endpoint_is_dry_run_only(self):
        idx = self.server.find("/api/ui-tars-observation/dry-run")
        self.assertGreater(idx, 0)
        block = self.server[idx:idx + 500]
        self.assertIn("--dry-run", block)


# ===========================================================================
# Live endpoints
# ===========================================================================

class TestLiveEndpoints(unittest.TestCase):
    PORT = 3268

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

    def _post(self, path, payload=None):
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:%d%s" % (self.PORT, path),
            data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")

    def test_status_endpoint_live(self):
        status, body = self._get("/api/ui-tars-observation/status")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"))

    def test_dry_run_endpoint_live(self):
        status, body = self._post("/api/ui-tars-observation/dry-run")
        self.assertEqual(status, 200, body)
        data = json.loads(body)
        self.assertTrue(data.get("ok"), body)
        self.assertEqual(data.get("mode"), "dry_run")
        self.assertFalse(data.get("screenshot_captured"))

    def test_dry_run_endpoint_manifest_has_contract_fields(self):
        # The endpoint-generated observation manifest must satisfy the N+5.0B
        # contract: local_only / click_enabled / type_enabled present.
        status, body = self._post("/api/ui-tars-observation/dry-run")
        self.assertEqual(status, 200, body)
        data = json.loads(body)
        run_dir = data.get("run_dir")
        self.assertTrue(run_dir)
        manifest_path = REPO_ROOT / run_dir / "00_observation_manifest.json"
        self.assertTrue(manifest_path.exists(), "endpoint did not write a manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIs(manifest.get("local_only"), True)
        self.assertIs(manifest.get("click_enabled"), False)
        self.assertIs(manifest.get("type_enabled"), False)

    def test_create_approval_endpoint_live(self):
        status, body = self._post("/api/ui-tars-observation/create-approval")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"), body)

    def test_capture_approved_without_token_rejected(self):
        status, body = self._post("/api/ui-tars-observation/capture-approved", {})
        self.assertEqual(status, 200, body)
        self.assertFalse(json.loads(body).get("ok", True))

    def test_latest_endpoint_does_not_leak_token(self):
        status, body = self._get("/api/ui-tars-observation/latest")
        self.assertEqual(status, 200, body)
        self.assertTrue(json.loads(body).get("ok"))
        self.assertNotIn("approval_token", body)

    def test_status_endpoint_does_not_leak_token(self):
        status, body = self._get("/api/ui-tars-observation/status")
        self.assertEqual(status, 200, body)
        self.assertNotIn("approval_token", body)


# ===========================================================================
# N+5.0B manifest contract — every observation run manifest must be complete
# ===========================================================================

class TestAllRunManifestsContract(unittest.TestCase):
    """Every observation run manifest on disk must satisfy the full N+5.0B
    manifest contract. Guards against the N+5.0A blocker recurring."""

    CONTRACT_TRUE = ["local_only"]
    CONTRACT_FALSE = [
        "click_enabled", "type_enabled", "external_repo_code_executed",
        "installs_performed", "ui_tars_runtime_started", "desktop_control_enabled",
        "live_api_used",
    ]

    @classmethod
    def setUpClass(cls):
        # Ensure at least one fresh run exists.
        run_cli("--observe", "--dry-run", "--json")
        runs_dir = REPO_ROOT / "14_context" / "ui_tars_observation" / "runs"
        cls.manifests = sorted(runs_dir.glob("*/00_observation_manifest.json"))

    def test_at_least_one_manifest_present(self):
        self.assertTrue(self.manifests, "no observation run manifests found")

    def test_every_manifest_satisfies_contract(self):
        for mpath in self.manifests:
            with self.subTest(manifest=mpath.parent.name):
                manifest = json.loads(mpath.read_text(encoding="utf-8"))
                for field in self.CONTRACT_TRUE:
                    self.assertIs(manifest.get(field), True,
                                  "%s: %s must be true" % (mpath.parent.name, field))
                for field in self.CONTRACT_FALSE:
                    self.assertIn(field, manifest,
                                  "%s: missing contract field %s" % (mpath.parent.name, field))
                    self.assertIs(manifest.get(field), False,
                                  "%s: %s must be false" % (mpath.parent.name, field))


if __name__ == "__main__":
    unittest.main()
