"""
test_n6_29a_computer_use_repo_backed_adapter.py

Unit tests for ghoti_computer_use_adapter.py (N+6.29A).
Pure stdlib; no real OS actions; dry-run only.
"""

import json
import sys
import unittest
from pathlib import Path

# Make the adapter importable from the scripts directory
_SCRIPTS_ROOT = Path(__file__).parent.parent.parent.parent / "03_scripts"
sys.path.insert(0, str(_SCRIPTS_ROOT / "computer_use_adapter"))

import ghoti_computer_use_adapter as adapter


class TestConstants(unittest.TestCase):
    def test_allowed_targets_non_empty(self):
        self.assertIn("local_sandbox", adapter.ALLOWED_TARGETS)
        self.assertIn("approved_window", adapter.ALLOWED_TARGETS)

    def test_blocked_action_types_non_empty(self):
        self.assertIn("real_click", adapter.BLOCKED_ACTION_TYPES)
        self.assertIn("real_type", adapter.BLOCKED_ACTION_TYPES)
        self.assertIn("login", adapter.BLOCKED_ACTION_TYPES)
        self.assertIn("navigate_url", adapter.BLOCKED_ACTION_TYPES)
        self.assertIn("launch_docker", adapter.BLOCKED_ACTION_TYPES)
        self.assertIn("mcp_setup", adapter.BLOCKED_ACTION_TYPES)

    def test_allowed_action_types_non_empty(self):
        self.assertIn("read_fixture", adapter.ALLOWED_ACTION_TYPES)
        self.assertIn("check_state", adapter.ALLOWED_ACTION_TYPES)
        self.assertIn("dry_run_click", adapter.ALLOWED_ACTION_TYPES)
        self.assertIn("generate_report", adapter.ALLOWED_ACTION_TYPES)

    def test_blocked_and_allowed_disjoint(self):
        overlap = adapter.BLOCKED_ACTION_TYPES & adapter.ALLOWED_ACTION_TYPES
        self.assertEqual(overlap, frozenset(), f"Overlap: {overlap}")

    def test_refused_live_actions_non_empty(self):
        self.assertGreater(len(adapter.REFUSED_LIVE_ACTIONS), 5)


class TestCheckTarget(unittest.TestCase):
    def test_local_sandbox_allowed(self):
        reasons = adapter._check_target({"target": "local_sandbox"})
        self.assertEqual(reasons, [])

    def test_approved_window_allowed(self):
        reasons = adapter._check_target({"target": "approved_window"})
        self.assertEqual(reasons, [])

    def test_external_target_blocked(self):
        reasons = adapter._check_target({"target": "live_browser"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("live_browser", reasons[0])

    def test_missing_target_blocked(self):
        reasons = adapter._check_target({})
        self.assertEqual(len(reasons), 1)


class TestCheckUrl(unittest.TestCase):
    def test_file_url_hostless_allowed(self):
        # file:///path (empty authority) is a local fixture reference
        reasons = adapter._check_url({"target_url": "file:///sandbox/page.html"})
        self.assertEqual(reasons, [])

    def test_file_url_hostless_windows_allowed(self):
        reasons = adapter._check_url({"target_url": "file:///C:/fixtures/test.html"})
        self.assertEqual(reasons, [])

    def test_file_authority_evil_blocked(self):
        # file://evil.example/share has a non-empty authority
        reasons = adapter._check_url({"target_url": "file://evil.example/share"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("evil.example", reasons[0])

    def test_file_authority_localhost_blocked(self):
        # file://localhost/path has authority "localhost" and must be blocked;
        # the adapter only allows hostless file:/// URLs
        reasons = adapter._check_url({"target_url": "file://localhost/share"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("localhost", reasons[0])

    def test_localhost_allowed(self):
        reasons = adapter._check_url({"target_url": "http://localhost:3210"})
        self.assertEqual(reasons, [])

    def test_127_allowed(self):
        reasons = adapter._check_url({"target_url": "http://127.0.0.1:8080"})
        self.assertEqual(reasons, [])

    def test_external_https_blocked(self):
        reasons = adapter._check_url({"target_url": "https://example.com/dashboard"})
        self.assertEqual(len(reasons), 1)

    def test_empty_url_allowed(self):
        reasons = adapter._check_url({})
        self.assertEqual(reasons, [])

    # --- deceptive-hostname regression tests ---

    def test_deceptive_localhost_prefix_blocked(self):
        # "localhost.evil.example" starts with "localhost" but is not local
        reasons = adapter._check_url({"target_url": "http://localhost.evil.example/account"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("localhost.evil.example", reasons[0])

    def test_deceptive_127_prefix_blocked(self):
        # "127.0.0.1.evil.example" starts with "127.0.0.1" but is not local
        reasons = adapter._check_url({"target_url": "http://127.0.0.1.evil.example/login"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("127.0.0.1.evil.example", reasons[0])

    def test_deceptive_localhost_https_blocked(self):
        reasons = adapter._check_url({"target_url": "https://localhost.attacker.test/steal"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("localhost.attacker.test", reasons[0])

    def test_deceptive_127_https_blocked(self):
        reasons = adapter._check_url({"target_url": "https://127.0.0.1.attacker.test/evil"})
        self.assertEqual(len(reasons), 1)
        self.assertIn("127.0.0.1.attacker.test", reasons[0])

    def test_blocked_scheme_blocked(self):
        reasons = adapter._check_url({"target_url": "ftp://localhost/something"})
        self.assertEqual(len(reasons), 1)

    def test_https_localhost_still_allowed(self):
        reasons = adapter._check_url({"target_url": "https://localhost:8443/dashboard"})
        self.assertEqual(reasons, [])

    def test_ipv6_loopback_allowed(self):
        reasons = adapter._check_url({"target_url": "http://[::1]:3210/"})
        self.assertEqual(reasons, [])


class TestCheckAutoSubmit(unittest.TestCase):
    def test_false_ok(self):
        self.assertEqual(adapter._check_auto_submit({"auto_submit": False}), [])

    def test_missing_ok(self):
        self.assertEqual(adapter._check_auto_submit({}), [])

    def test_true_blocked(self):
        reasons = adapter._check_auto_submit({"auto_submit": True})
        self.assertEqual(len(reasons), 1)
        self.assertIn("auto_submit", reasons[0])


class TestCheckHumanApproval(unittest.TestCase):
    def test_true_ok(self):
        self.assertEqual(
            adapter._check_human_approval({"requires_human_approval": True}), []
        )

    def test_false_blocked(self):
        reasons = adapter._check_human_approval({"requires_human_approval": False})
        self.assertEqual(len(reasons), 1)

    def test_missing_blocked(self):
        reasons = adapter._check_human_approval({})
        self.assertEqual(len(reasons), 1)


class TestCheckCapabilities(unittest.TestCase):
    def test_empty_ok(self):
        self.assertEqual(
            adapter._check_capabilities({"capabilities_required": []}), []
        )

    def test_no_field_ok(self):
        self.assertEqual(adapter._check_capabilities({}), [])

    def test_live_browser_blocked(self):
        reasons = adapter._check_capabilities(
            {"capabilities_required": ["live_browser"]}
        )
        self.assertEqual(len(reasons), 1)
        self.assertIn("live_browser", reasons[0])

    def test_multiple_blocked(self):
        reasons = adapter._check_capabilities(
            {"capabilities_required": ["live_browser", "docker", "mcp"]}
        )
        self.assertEqual(len(reasons), 3)


class TestCheckActions(unittest.TestCase):
    def _make_plan(self, actions):
        return {
            "target": "local_sandbox",
            "auto_submit": False,
            "requires_human_approval": True,
            "actions": actions,
        }

    def test_allowed_action_passes(self):
        reasons, dry_runs = adapter._check_actions(
            self._make_plan([
                {"action_id": "a1", "type": "read_fixture", "target_element": None}
            ])
        )
        self.assertEqual(reasons, [])
        self.assertEqual(len(dry_runs), 1)
        self.assertFalse(dry_runs[0]["real_action_performed"])
        self.assertFalse(dry_runs[0]["real_click_performed"])
        self.assertFalse(dry_runs[0]["real_type_performed"])
        self.assertFalse(dry_runs[0]["os_input_used"])

    def test_blocked_action_type(self):
        reasons, dry_runs = adapter._check_actions(
            self._make_plan([
                {"action_id": "b1", "type": "real_click", "target_element": "#btn"}
            ])
        )
        self.assertEqual(len(reasons), 1)
        self.assertIn("real_click", reasons[0])
        self.assertEqual(dry_runs, [])

    def test_unknown_action_type_blocked(self):
        reasons, _ = adapter._check_actions(
            self._make_plan([
                {"action_id": "u1", "type": "teleport_mouse", "target_element": None}
            ])
        )
        self.assertEqual(len(reasons), 1)
        self.assertIn("teleport_mouse", reasons[0])

    def test_secret_value_blocked(self):
        reasons, _ = adapter._check_actions(
            self._make_plan([
                {
                    "action_id": "s1",
                    "type": "dry_run_type",
                    "target_element": "#input",
                    "value": "my_api_token_abc123",
                }
            ])
        )
        self.assertEqual(len(reasons), 1)
        self.assertIn("secret", reasons[0].lower())

    def test_secret_field_name_blocked(self):
        reasons, _ = adapter._check_actions(
            self._make_plan([
                {
                    "action_id": "sf1",
                    "type": "dry_run_type",
                    "target_element": "#input",
                    "password": "hunter2",
                }
            ])
        )
        self.assertEqual(len(reasons), 1)

    def test_multiple_actions_mixed(self):
        reasons, dry_runs = adapter._check_actions(
            self._make_plan([
                {"action_id": "ok1", "type": "read_fixture"},
                {"action_id": "bad1", "type": "login"},
                {"action_id": "ok2", "type": "check_state", "target_element": "#x"},
            ])
        )
        self.assertEqual(len(reasons), 1)
        self.assertIn("login", reasons[0])
        self.assertEqual(len(dry_runs), 2)


class TestValidatePlan(unittest.TestCase):
    def _good_plan(self):
        return {
            "plan_id": "test_001",
            "milestone": "N+6.29A",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": [],
            "actions": [
                {"action_id": "a1", "type": "read_fixture", "target_element": None}
            ],
        }

    def test_good_plan_allowed(self):
        status, reasons, dry_runs = adapter._validate_plan(self._good_plan())
        self.assertEqual(status, "allowed")
        self.assertEqual(reasons, [])
        self.assertEqual(len(dry_runs), 1)

    def test_blocked_target(self):
        plan = self._good_plan()
        plan["target"] = "external_browser"
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked")
        self.assertGreater(len(reasons), 0)

    def test_blocked_url(self):
        plan = self._good_plan()
        plan["target_url"] = "https://evil.com"
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked")
        self.assertGreater(len(reasons), 0)

    def test_auto_submit_blocked(self):
        plan = self._good_plan()
        plan["auto_submit"] = True
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked")

    def test_missing_human_approval_blocked(self):
        plan = self._good_plan()
        plan["requires_human_approval"] = False
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked")


class TestRunPlan(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()

    def _write_plan(self, plan: dict) -> str:
        import os
        path = os.path.join(self._tmpdir, "plan.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f)
        return path

    def test_allowed_plan_result(self):
        plan = {
            "plan_id": "test_run_001",
            "milestone": "N+6.29A",
            "target": "local_sandbox",
            "target_url": "file:///sandbox/page.html",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": [],
            "actions": [
                {"action_id": "a1", "type": "read_fixture", "target_element": None}
            ],
        }
        result = adapter._run_plan(self._write_plan(plan))
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "allowed")
        self.assertEqual(result["mode"], "dry_run")
        self.assertFalse(result["real_action_performed"])
        self.assertFalse(result["real_click_performed"])
        self.assertFalse(result["real_type_performed"])
        self.assertFalse(result["os_input_used"])
        self.assertFalse(result["secrets_accessed"])
        self.assertFalse(result["auto_submit_performed"])
        self.assertIsNone(result["approval_token"])
        self.assertFalse(result["rust_policy_bridge_ready"])
        self.assertTrue(result["arena_status"]["simulation"])
        self.assertFalse(result["arena_status"]["live_execution"])
        self.assertFalse(result["arena_status"]["live_computer_use_enabled"])
        self.assertTrue(result["safety"]["dry_run_only"])
        self.assertTrue(result["safety"]["no_real_os_input"])
        self.assertFalse(result["safety"]["real_action_performed"])

    def test_blocked_plan_result(self):
        plan = {
            "plan_id": "test_run_block_001",
            "milestone": "N+6.29A",
            "target": "external_site",
            "auto_submit": False,
            "requires_human_approval": True,
            "capabilities_required": ["live_browser"],
            "actions": [
                {"action_id": "b1", "type": "real_click", "target_element": "#btn"}
            ],
        }
        result = adapter._run_plan(self._write_plan(plan))
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked")
        self.assertGreater(len(result["blocked_reasons"]), 0)
        self.assertFalse(result["real_action_performed"])
        self.assertFalse(result["os_input_used"])

    def test_invalid_json_returns_error(self):
        import os
        path = os.path.join(self._tmpdir, "bad.json")
        with open(path, "w") as f:
            f.write("not valid json {{")
        result = adapter._run_plan(path)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "error")

    def test_missing_file_returns_error(self):
        result = adapter._run_plan("/nonexistent/path/plan.json")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "error")


class TestRunCheck(unittest.TestCase):
    def test_check_fields(self):
        result = adapter._run_check()
        self.assertTrue(result["ok"])
        self.assertEqual(result["milestone"], "N+6.29A")
        self.assertEqual(result["mode"], "dry_run")
        self.assertFalse(result["computer_use_enabled"])
        self.assertFalse(result["live_browser_enabled"])
        self.assertFalse(result["real_os_input_enabled"])
        self.assertFalse(result["auto_submit_enabled"])
        self.assertFalse(result["docker_enabled"])
        self.assertFalse(result["mcp_enabled"])
        self.assertFalse(result["secrets_access_enabled"])
        self.assertFalse(result["rust_policy_bridge_ready"])
        self.assertIn("n6_27a_dependency", result)
        self.assertIn("n6_28b_dependency", result)
        self.assertIn("merged", result["n6_27a_dependency"])
        self.assertFalse(result["safety"]["real_action_performed"])
        self.assertTrue(result["safety"]["dry_run_only"])

    def test_check_result_json_serializable(self):
        result = adapter._run_check()
        serialized = json.dumps(result)
        self.assertIsInstance(serialized, str)

    def test_allowed_targets_in_check(self):
        result = adapter._run_check()
        self.assertIn("local_sandbox", result["allowed_targets"])
        self.assertIn("approved_window", result["allowed_targets"])

    def test_refused_live_actions_in_check(self):
        result = adapter._run_check()
        self.assertGreater(len(result["refused_live_actions"]), 5)


class TestExampleFixtures(unittest.TestCase):
    """Validate the bundled example JSON fixtures against the adapter."""

    _EXAMPLES = Path(__file__).parent.parent.parent.parent / "14_context" / "computer_use_adapter" / "examples"

    def test_dry_run_local_fixture_action_allowed(self):
        fixture = self._EXAMPLES / "dry_run_local_fixture_action.json"
        if not fixture.exists():
            self.skipTest("fixture not found")
        import tempfile
        plan = json.loads(fixture.read_text(encoding="utf-8"))
        result = adapter._validate_plan(plan)
        status, reasons, dry_runs = result
        self.assertEqual(status, "allowed", f"Expected allowed; blocked: {reasons}")
        self.assertGreater(len(dry_runs), 0)

    def test_blocked_external_website_action_blocked(self):
        fixture = self._EXAMPLES / "blocked_external_website_action.json"
        if not fixture.exists():
            self.skipTest("fixture not found")
        plan = json.loads(fixture.read_text(encoding="utf-8"))
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked", f"Expected blocked; got {status}")
        self.assertGreater(len(reasons), 0)

    def test_blocked_secret_input_action_blocked(self):
        fixture = self._EXAMPLES / "blocked_secret_input_action.json"
        if not fixture.exists():
            self.skipTest("fixture not found")
        plan = json.loads(fixture.read_text(encoding="utf-8"))
        status, reasons, _ = adapter._validate_plan(plan)
        self.assertEqual(status, "blocked", f"Expected blocked; got {status}")
        self.assertGreater(len(reasons), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
