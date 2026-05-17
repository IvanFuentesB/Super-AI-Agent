#!/usr/bin/env python3
"""N+4.8A tests: External Tool Sandbox + Adapter Discovery MVP.

Covers:
- approved catalog has exactly the approved repos; unknown repo rejected
- status --json / bare --json valid; sandbox-static-inspection-only mode
- sync-approved degrades truthfully (per-repo clone_status, degraded flag)
- clone target is repo-local (21_repos/third_party/sandboxed/)
- no install commands executed; no external code executed
- adapter stubs generated; do not import external repo packages;
  expose status/capabilities/safety_gates; require human approval
- approval packet generated
- dashboard labels + server endpoints exist
- no shell:true; no live API/account; no desktop control; no secrets
- external tools remain approval-gated
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SCRIPT = REPO_ROOT / "03_scripts" / "external_tool_sandbox_manager.py"
ADAPTERS_DIR = REPO_ROOT / "02_automation" / "external_tool_adapters"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
PYTHON = sys.executable

APPROVED_SLUGS = [
    "bytedance/UI-TARS-desktop",
    "bytedance/UI-TARS",
    "the-agency-ai/the-agency",
    "darkrishabh/agent-skills-eval",
    "vouch-protocol/vouch",
]
ADAPTER_FILES = [
    "ui_tars_desktop_adapter.py",
    "ui_tars_model_adapter.py",
    "the_agency_adapter.py",
    "agent_skills_eval_adapter.py",
    "vouch_adapter.py",
]
REQUIRED_DASHBOARD_LABELS = [
    "External Tool Sandbox",
    "External Tool Sandbox Truth",
    "UI-TARS Desktop",
    "UI-TARS Model",
    "TheAgency",
    "agent-skills-eval",
    "Vouch Protocol",
    "Clone Status",
    "Static Scan Only",
    "No Install Yet",
    "No Runtime Wiring",
    "No Desktop Control Yet",
    "No Live APIs",
    "Human Approval Required",
    "Adapter Stubs Generated",
    "Approval Packet Required",
]
SERVER_ENDPOINTS = [
    "/api/external-tool-sandbox/status",
    "/api/external-tool-sandbox/sync-approved",
    "/api/external-tool-sandbox/scan",
    "/api/external-tool-sandbox/latest",
]


def run_manager(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT)] + list(args),
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=600,
    )


def _load_adapter(filename):
    path = ADAPTERS_DIR / filename
    spec = importlib.util.spec_from_file_location("n4_8a_" + filename[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# Approved catalog
# ===========================================================================

class TestApprovedCatalog(unittest.TestCase):
    def test_catalog_has_exactly_the_approved_repos(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        slugs = sorted(e["slug"] for e in data.get("approved_catalog", []))
        self.assertEqual(slugs, sorted(APPROVED_SLUGS))
        self.assertEqual(data.get("approved_catalog_count"), 5)

    def test_unknown_repo_rejected(self):
        r = run_manager("--status", "--repo", "evil/not-approved", "--json")
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertFalse(data.get("ok", True))

    def test_known_repo_accepted(self):
        r = run_manager("--status", "--repo", "vouch-protocol/vouch", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))


# ===========================================================================
# Manager status
# ===========================================================================

class TestManagerStatus(unittest.TestCase):
    def test_status_json_valid(self):
        r = run_manager("--status", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("manager"), "external_tool_sandbox_manager")

    def test_bare_json_valid(self):
        r = run_manager("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout).get("ok"))

    def test_mode_is_static_inspection_only(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertEqual(data.get("mode"), "sandbox_static_inspection_only")

    def test_status_declares_safe_scope(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertFalse(data.get("installs_performed"))
        self.assertFalse(data.get("external_code_executed"))
        self.assertFalse(data.get("desktop_control_enabled"))
        self.assertFalse(data.get("live_api_enabled"))
        self.assertFalse(data.get("live_account_actions"))
        self.assertEqual(data.get("runtime_wiring"), "none")
        self.assertTrue(data.get("human_approval_required"))

    def test_sandbox_dir_repo_local(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertTrue(data.get("sandbox_dir_repo_local"))
        self.assertEqual(data.get("sandbox_dir"), "21_repos/third_party/sandboxed")


# ===========================================================================
# Sync + scan (truthful degradation, repo-local, no installs)
# ===========================================================================

class TestSyncAndScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sync = json.loads(run_manager("--sync-approved", "--json").stdout)
        cls.scan = json.loads(run_manager("--scan", "--json").stdout)

    def test_sync_ok_and_lists_all_five(self):
        self.assertTrue(self.sync.get("ok"))
        self.assertEqual(len(self.sync.get("repos", [])), 5)

    def test_sync_degrades_truthfully(self):
        # Every repo has an explicit clone_status; degraded is a bool that is
        # True iff at least one repo failed.
        statuses = [r.get("clone_status") for r in self.sync.get("repos", [])]
        for st in statuses:
            self.assertIn(st, ("cloned", "failed", "not_attempted"))
        failed = sum(1 for s in statuses if s == "failed")
        self.assertEqual(self.sync.get("degraded"), failed > 0)

    def test_sync_performs_no_install_and_no_external_code(self):
        self.assertFalse(self.sync.get("installs_performed"))
        self.assertFalse(self.sync.get("external_code_executed"))

    def test_clone_targets_are_repo_local(self):
        for repo in self.sync.get("repos", []):
            cp = repo.get("clone_path")
            if cp:
                with self.subTest(repo=repo.get("slug")):
                    self.assertTrue(cp.startswith("21_repos/third_party/sandboxed/"))
                    self.assertNotIn("..", cp)

    def test_scan_performs_no_install(self):
        self.assertTrue(self.scan.get("ok"))
        self.assertFalse(self.scan.get("installs_performed"))
        self.assertFalse(self.scan.get("external_code_executed"))


# ===========================================================================
# Adapter stubs
# ===========================================================================

class TestAdapterStubs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = json.loads(run_manager("--generate-adapters", "--json").stdout)

    def test_generate_adapters_ok(self):
        self.assertTrue(self.gen.get("ok"))
        self.assertEqual(self.gen.get("count"), 5)

    def test_all_five_adapter_stubs_exist(self):
        for fname in ADAPTER_FILES:
            with self.subTest(adapter=fname):
                self.assertTrue((ADAPTERS_DIR / fname).exists(), "missing adapter: %s" % fname)

    def test_adapters_do_not_import_external_repo_packages(self):
        forbidden = ("ui_tars", "uitars", "the_agency", "theagency",
                     "agent_skills_eval", "vouch_protocol", "import bytedance")
        for fname in ADAPTER_FILES:
            src = (ADAPTERS_DIR / fname).read_text(encoding="utf-8")
            for line in src.splitlines():
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    with self.subTest(adapter=fname, line=stripped):
                        # Only the stdlib `json` import is allowed.
                        self.assertTrue(
                            stripped in ("import json",),
                            "adapter %s has a non-stdlib import: %s" % (fname, stripped),
                        )
                low = stripped.lower()
                for needle in forbidden:
                    if low.startswith("import " + needle) or low.startswith("from " + needle):
                        self.fail("adapter %s imports external repo package: %s" % (fname, stripped))

    def test_adapters_expose_status_capabilities_safety_gates(self):
        for fname in ADAPTER_FILES:
            with self.subTest(adapter=fname):
                mod = _load_adapter(fname)
                self.assertTrue(callable(getattr(mod, "status", None)))
                self.assertTrue(callable(getattr(mod, "capabilities", None)))
                self.assertTrue(callable(getattr(mod, "safety_gates", None)))
                st = mod.status()
                self.assertFalse(st.get("wired"))
                self.assertFalse(st.get("external_code_executed"))
                self.assertFalse(st.get("desktop_control_enabled"))
                self.assertFalse(st.get("live_api_enabled"))
                self.assertTrue(st.get("requires_human_approval"))
                self.assertIsInstance(mod.capabilities(), list)
                gates = mod.safety_gates()
                self.assertIn("human_approval_required", gates)
                self.assertIn("no_external_code_execution", gates)
                self.assertIn("no_desktop_control_without_approval", gates)

    def test_adapters_require_human_approval(self):
        for fname in ADAPTER_FILES:
            with self.subTest(adapter=fname):
                mod = _load_adapter(fname)
                self.assertTrue(getattr(mod, "REQUIRES_HUMAN_APPROVAL", False))


# ===========================================================================
# Approval packet
# ===========================================================================

class TestApprovalPacket(unittest.TestCase):
    def test_approval_packet_generated(self):
        r = run_manager("--write-approval-packet", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data.get("ok"))
        packet = data.get("approval_packet", "")
        self.assertTrue(packet.startswith("14_context/external_tools/approval_packets/"))
        self.assertTrue((REPO_ROOT / packet).exists())


# ===========================================================================
# Manager source safety
# ===========================================================================

class TestManagerSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SCRIPT.read_text(encoding="utf-8")

    def test_no_shell_true(self):
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("shell = True", self.src)

    def test_uses_explicit_shell_false(self):
        self.assertIn("shell=False", self.src)

    def test_clone_is_fixed_shallow_argv(self):
        self.assertIn('"clone", "--depth", "1"', self.src)

    def test_no_install_subprocess(self):
        # No subprocess ever runs an installer.
        for token in ("npm install", "pnpm install", "pip install", "yarn install"):
            self.assertNotIn(token, self.src)

    def test_allow_install_never_installs(self):
        # The --allow-install flag exists but installs are never performed.
        self.assertIn("--allow-install", self.src)
        self.assertIn("install_still_performed", self.src)

    def test_no_os_system(self):
        self.assertNotIn("os.system", self.src)

    def test_no_secrets(self):
        lowered = self.src.lower()
        for needle in ("api_key =", "apikey =", "password", "secret_key =", "bearer "):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, lowered)


# ===========================================================================
# Dashboard + server
# ===========================================================================

class TestDashboardAndServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")
        cls.server = SERVER_JS.read_text(encoding="utf-8", errors="replace")

    def test_dashboard_card_present(self):
        self.assertIn('id="external-tool-sandbox-truth"', self.html)

    def test_all_required_labels_present(self):
        for label in REQUIRED_DASHBOARD_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_server_endpoints_present(self):
        for ep in SERVER_ENDPOINTS:
            with self.subTest(endpoint=ep):
                self.assertIn(ep, self.server)

    def test_server_sandbox_section_no_shell_true(self):
        start = self.server.find("External Tool Sandbox (N+4.8A)")
        if start == -1:
            start = self.server.find("/api/external-tool-sandbox/status")
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


# ===========================================================================
# Safety / approval-gated
# ===========================================================================

class TestSafety(unittest.TestCase):
    def test_external_tools_remain_approval_gated(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertTrue(data.get("human_approval_required"))
        self.assertEqual(data.get("runtime_wiring"), "none")
        for adapter in data.get("adapters", []):
            self.assertTrue(adapter.get("adapter"))

    def test_no_desktop_control_enabled(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertFalse(data.get("desktop_control_enabled"))

    def test_no_live_api_or_account(self):
        data = json.loads(run_manager("--status", "--json").stdout)
        self.assertFalse(data.get("live_api_enabled"))
        self.assertFalse(data.get("live_account_actions"))

    def test_adapter_safety_gates_block_unapproved_wiring(self):
        for fname in ADAPTER_FILES:
            with self.subTest(adapter=fname):
                mod = _load_adapter(fname)
                gates = mod.safety_gates()
                self.assertIn("no_live_api_calls_without_approval", gates)
                self.assertIn("no_live_account_actions", gates)


if __name__ == "__main__":
    unittest.main()
