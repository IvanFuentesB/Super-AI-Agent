"""
test_n6_34a_cua_real_repo_trial.py

N+6.34A — CUA Isolated Dry-Run / Observation Adapter.

Proves:
  1. CUA sandbox is gitignored (no CUA code can be committed).
  2. No CUA third-party code is tracked in git.
  3. Adapter refuses live OS actions (plan validation).
  4. Rust policy gate denies unsafe capabilities.
  5. External URLs / account / logins blocked.
  6. Dry-run observation plan is produced correctly.
  7. Safe observation plan passes the dual gate (adapter + Rust policy).
  8. Docker/VM/MCP capabilities denied at both gates.
  9. Metadata smoke works when sandbox is present.
 10. check mode works without CUA.
 11. No CUA code is imported by the adapter.

Pure stdlib; no real OS actions; no CUA code executed.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_ROOT = REPO_ROOT / "03_scripts"

sys.path.insert(0, str(_SCRIPTS_ROOT / "cua_trial"))
sys.path.insert(0, str(_SCRIPTS_ROOT / "computer_use_adapter"))

import ghoti_cua_trial_adapter as cua_adapter  # noqa: E402


CUA_SANDBOX = REPO_ROOT / "21_repos" / "third_party_runtime_sandbox" / "cua"


# ------------------------------------------------------------------
# 1 & 2: Gitignore and no committed code
# ------------------------------------------------------------------

class TestSandboxIsolation(unittest.TestCase):
    def test_sandbox_path_is_gitignored(self):
        """CUA sandbox path must match a .gitignore rule."""
        gitignore = REPO_ROOT / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore must exist")
        content = gitignore.read_text(encoding="utf-8")
        # The rule should cover the entire runtime sandbox
        self.assertIn("21_repos/third_party_runtime_sandbox/*", content)

    def test_no_cua_code_tracked_in_git(self):
        """git ls-files must return nothing for the runtime sandbox."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "--", "21_repos/third_party_runtime_sandbox/"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        # Only .gitkeep is allowed (the sentinel file keeping the dir in git)
        tracked = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and not line.strip().endswith(".gitkeep")
        ]
        self.assertEqual(
            tracked, [],
            msg=f"CUA code appears committed: {tracked}",
        )

    def test_adapter_source_does_not_import_cua(self):
        """The adapter source must not import any CUA package."""
        src = (_SCRIPTS_ROOT / "cua_trial" / "ghoti_cua_trial_adapter.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "import cua", "from cua", "import lume", "import computer_server",
            "import cua_core", "from cua_core",
            "pyautogui", "selenium", "playwright", "pynput",
        ):
            self.assertNotIn(
                forbidden, src,
                msg=f"adapter imports/uses forbidden token: {forbidden}",
            )

    def test_adapter_flags_cua_code_not_imported(self):
        result = cua_adapter._run_check()
        self.assertFalse(result["cua_code_imported"])
        self.assertFalse(result["cua_code_executed"])


# ------------------------------------------------------------------
# 3: Adapter refuses live OS actions
# ------------------------------------------------------------------

class TestLiveActionRefusal(unittest.TestCase):
    def _validate(self, plan: dict) -> dict:
        return cua_adapter._validate_trial_plan(plan)

    def _base_plan(self) -> dict:
        return {
            "plan_id": "test_plan",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": [],
            "actions": [],
        }

    def test_docker_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["docker"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])
        self.assertFalse(result["adapter_allowed"])

    def test_computer_use_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["computer_use"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_mcp_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["mcp"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_vm_launch_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["vm_launch"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_real_click_action_denied(self):
        plan = self._base_plan()
        plan["actions"] = [{"action_id": "a1", "type": "real_click", "target_element": "#btn"}]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_telemetry_upload_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["telemetry_upload"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_bridge_temp_plan_is_removed_after_validation(self):
        observed_path = None

        def fake_run_plan(plan_path, rust_bridge):
            nonlocal observed_path
            observed_path = Path(plan_path)
            self.assertTrue(observed_path.exists())
            self.assertTrue(rust_bridge)
            return {"accepted": False}

        with mock.patch.object(cua_adapter._bridge, "_run_plan", side_effect=fake_run_plan):
            self._validate(self._base_plan())

        self.assertIsNotNone(observed_path)
        self.assertFalse(observed_path.exists())

    def test_shell_execution_capability_denied(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["shell_execution"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])


# ------------------------------------------------------------------
# 4: Rust policy gate denies unsafe capabilities
# ------------------------------------------------------------------

class TestRustPolicyGate(unittest.TestCase):
    def _validate(self, plan: dict) -> dict:
        return cua_adapter._validate_trial_plan(plan)

    def _base_plan(self) -> dict:
        return {
            "plan_id": "rust_gate_test",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": [],
            "actions": [],
        }

    def test_rust_gate_denies_browser_capability(self):
        plan = self._base_plan()
        # live_browser is in CUA_TRIAL_BLOCKED_CAPABILITIES (Gate 0) AND maps to
        # "browser" in the Rust gate (Gate 2) — either layer catches it.
        plan["capabilities_required"] = ["live_browser"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])
        if "rust_policy_decision" in result:
            blocked = result["rust_policy_decision"].get("blocked_capabilities", [])
            # Gate 0 preserves the raw name; Gate 2 normalizes to "browser".
            self.assertTrue(
                "browser" in blocked or "live_browser" in blocked,
                msg=f"expected browser capability in blocked: {blocked}",
            )

    def test_rust_gate_denies_account_capability(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["account_login"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_rust_gate_denies_money_capability(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["money"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_rust_gate_denies_secrets_capability(self):
        plan = self._base_plan()
        plan["capabilities_required"] = ["secrets"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])


# ------------------------------------------------------------------
# 5: External URLs and account actions blocked
# ------------------------------------------------------------------

class TestExternalUrlBlocking(unittest.TestCase):
    def _validate(self, plan: dict) -> dict:
        return cua_adapter._validate_trial_plan(plan)

    def _base_plan(self) -> dict:
        return {
            "plan_id": "url_block_test",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": [],
            "actions": [],
        }

    def test_external_https_url_denied(self):
        plan = self._base_plan()
        plan["target_url"] = "https://example.com/account/dashboard"
        plan["capabilities_required"] = ["live_browser", "external_web"]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_file_authority_url_denied(self):
        plan = self._base_plan()
        plan["target_url"] = "file://evil.example/share"
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_account_login_action_denied(self):
        plan = self._base_plan()
        plan["actions"] = [{"action_id": "a1", "type": "login"}]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])

    def test_navigate_url_action_denied(self):
        plan = self._base_plan()
        plan["actions"] = [
            {"action_id": "a1", "type": "navigate_url",
             "value": "https://github.com"}
        ]
        result = self._validate(plan)
        self.assertFalse(result["accepted"])


# ------------------------------------------------------------------
# 6 & 7: Dry-run plan production and dual-gate acceptance
# ------------------------------------------------------------------

class TestTrialPlanProduction(unittest.TestCase):
    def test_build_trial_plan_structure(self):
        plan = cua_adapter._build_trial_plan(CUA_SANDBOX)
        self.assertEqual(plan["target"], "local_sandbox")
        self.assertFalse(plan["auto_submit"])
        self.assertTrue(plan["requires_human_approval"])
        self.assertEqual(plan["capabilities_required"], [])
        self.assertGreaterEqual(len(plan["actions"]), 2)
        action_types = {a["type"] for a in plan["actions"]}
        # All action types must be safe (read_fixture, check_state, generate_report)
        allowed_types = {"read_fixture", "check_state", "generate_report", "inspect_window"}
        self.assertTrue(
            action_types <= allowed_types,
            msg=f"unsafe action types in trial plan: {action_types - allowed_types}",
        )

    def test_trial_plan_uses_local_sandbox_target(self):
        plan = cua_adapter._build_trial_plan(CUA_SANDBOX)
        self.assertTrue(
            plan.get("target_url", "").startswith("file:///"),
            msg=f"trial_url is not a hostless file:// URL: {plan.get('target_url')}",
        )

    def test_safe_trial_plan_accepted_by_dual_gate(self):
        plan = cua_adapter._build_trial_plan(CUA_SANDBOX)
        result = cua_adapter._validate_trial_plan(plan)
        # The observation plan has no blocked capabilities → should be accepted.
        self.assertTrue(result["accepted"], msg=f"dual gate rejected safe plan: {result}")
        self.assertTrue(result.get("adapter_allowed", False))
        self.assertTrue(result.get("rust_allowed", False))

    def test_trial_plan_stays_dry_run(self):
        plan = cua_adapter._build_trial_plan(CUA_SANDBOX)
        result = cua_adapter._validate_trial_plan(plan)
        self.assertTrue(result["accepted"])
        # Bridge result must report dry_run safety invariants
        self.assertFalse(result.get("real_action_performed", True))
        self.assertFalse(result.get("os_input_used", True))


# ------------------------------------------------------------------
# 8: Docker/VM/MCP denied at both gates
# ------------------------------------------------------------------

class TestDockerVmMcpDenial(unittest.TestCase):
    def _validate(self, plan: dict) -> dict:
        return cua_adapter._validate_trial_plan(plan)

    def _obs_plan(self, extra_caps: list) -> dict:
        return {
            "plan_id": "docker_test",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": extra_caps,
            "actions": [],
        }

    def test_docker_blocked(self):
        self.assertFalse(self._validate(self._obs_plan(["docker"]))["accepted"])

    def test_lume_blocked(self):
        self.assertFalse(self._validate(self._obs_plan(["lume"]))["accepted"])

    def test_qemu_blocked(self):
        self.assertFalse(self._validate(self._obs_plan(["qemu"]))["accepted"])

    def test_kasm_blocked(self):
        self.assertFalse(self._validate(self._obs_plan(["kasm"]))["accepted"])

    def test_mcp_blocked(self):
        self.assertFalse(self._validate(self._obs_plan(["mcp"]))["accepted"])


# ------------------------------------------------------------------
# 9: Metadata smoke when sandbox is present
# ------------------------------------------------------------------

class TestMetadataSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox_present = CUA_SANDBOX.exists()

    def setUp(self):
        if not self.sandbox_present:
            self.skipTest("CUA sandbox not present — clone to run metadata smoke tests")

    def test_sandbox_detection_reports_present(self):
        detection = cua_adapter._detect_sandbox(CUA_SANDBOX)
        self.assertTrue(detection["present"])
        self.assertTrue(detection["git_present"])

    def test_sandbox_commit_hash_recorded(self):
        detection = cua_adapter._detect_sandbox(CUA_SANDBOX)
        self.assertIsNotNone(detection.get("commit_hash"))
        self.assertEqual(len(detection["commit_hash"]), 40)

    def test_license_is_mit(self):
        metadata = cua_adapter._read_cua_metadata(CUA_SANDBOX)
        self.assertEqual(metadata["license"], "MIT")
        self.assertTrue(metadata["license_file_present"])

    def test_package_name_read(self):
        metadata = cua_adapter._read_cua_metadata(CUA_SANDBOX)
        self.assertNotEqual(metadata["package_name"], "unknown")

    def test_shell_script_count_nonzero(self):
        metadata = cua_adapter._read_cua_metadata(CUA_SANDBOX)
        self.assertGreater(metadata["shell_script_count"], 0)

    def test_metadata_never_imports_cua_code(self):
        metadata = cua_adapter._read_cua_metadata(CUA_SANDBOX)
        self.assertFalse(metadata["cua_code_imported"])
        self.assertFalse(metadata["cua_code_executed"])

    def test_full_trial_result_structure(self):
        result = cua_adapter._run_trial(sandbox=CUA_SANDBOX)
        self.assertIn("ok", result)
        self.assertIn("cua_sandbox_present", result)
        self.assertIn("cua_metadata", result)
        self.assertIn("trial_plan", result)
        self.assertIn("gate_result", result)
        self.assertIn("accepted", result)
        self.assertIn("safety", result)
        safety = result["safety"]
        self.assertTrue(safety["no_cua_code_imported"])
        self.assertTrue(safety["no_cua_code_executed"])
        self.assertTrue(safety["no_real_os_input"])
        self.assertTrue(safety["no_docker_vm"])
        self.assertTrue(safety["dry_run_only"])

    def test_trial_result_is_accepted(self):
        result = cua_adapter._run_trial(sandbox=CUA_SANDBOX)
        self.assertTrue(result["accepted"])

    def test_pending_human_approval_always_true(self):
        result = cua_adapter._run_trial(sandbox=CUA_SANDBOX)
        self.assertTrue(result["pending_human_approval"])


# ------------------------------------------------------------------
# 10: Check mode works without CUA
# ------------------------------------------------------------------

class TestCheckMode(unittest.TestCase):
    def test_check_mode_ok_without_sandbox(self):
        result = cua_adapter._run_check()
        self.assertTrue(result["ok"])
        self.assertEqual(result["check"], "system_ready")
        self.assertEqual(result["mode"], "dry_run")
        self.assertFalse(result["live_os_input_enabled"])
        self.assertFalse(result["docker_vm_enabled"])
        self.assertFalse(result["live_browser_enabled"])
        self.assertFalse(result["mcp_enabled"])
        self.assertFalse(result["account_login_enabled"])
        self.assertFalse(result["secrets_access_enabled"])
        self.assertFalse(result["auto_submit_enabled"])

    def test_check_mode_safety_block(self):
        result = cua_adapter._run_check()
        safety = result["safety"]
        self.assertTrue(safety["no_cua_code_imported"])
        self.assertTrue(safety["no_cua_code_executed"])
        self.assertTrue(safety["no_real_os_input"])
        self.assertTrue(safety["dry_run_only"])

    def test_blocked_capabilities_list_non_empty(self):
        result = cua_adapter._run_check()
        self.assertGreater(len(result["trial_blocked_capabilities"]), 5)
        self.assertIn("docker", result["trial_blocked_capabilities"])
        self.assertIn("computer_use", result["trial_blocked_capabilities"])
        self.assertIn("mcp", result["trial_blocked_capabilities"])


# ------------------------------------------------------------------
# 11: trial adapter constant / contract checks
# ------------------------------------------------------------------

class TestAdapterContract(unittest.TestCase):
    def test_milestone_is_n6_34a(self):
        self.assertEqual(cua_adapter.MILESTONE, "N+6.34A")

    def test_cua_sandbox_relative_path(self):
        self.assertIn("third_party_runtime_sandbox", cua_adapter.CUA_SANDBOX_RELATIVE)
        self.assertIn("cua", cua_adapter.CUA_SANDBOX_RELATIVE)

    def test_refused_live_actions_non_empty(self):
        self.assertGreater(len(cua_adapter.REFUSED_LIVE_ACTIONS), 5)
        # Check that CUA-specific items are in the list
        combined = " ".join(cua_adapter.REFUSED_LIVE_ACTIONS).lower()
        self.assertIn("docker", combined)
        self.assertIn("cua", combined)
        self.assertIn("telemetry", combined)

    def test_trial_blocked_capabilities_covers_cua_risks(self):
        blocked = cua_adapter.CUA_TRIAL_BLOCKED_CAPABILITIES
        for cap in ("computer_use", "docker", "lume", "mcp", "vm_launch",
                    "shell_execution", "telemetry_upload"):
            self.assertIn(cap, blocked, msg=f"missing: {cap}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
