"""
test_n6_33a_rust_policy_bridge_computer_use.py

N+6.33A — Rust policy bridge ↔ computer-use dry-run adapter.

Proves the SECOND gate: a computer-use dry-run plan is only "accepted" when the
Python adapter AND the ghoti_policy_checker decision both allow it. The policy
decision is mirrored deterministically in Python (no toolchain needed); when a
Rust toolchain is present, an optional test cross-checks the real cargo binary
against the mirror.

Required proof cases (all dry-run, no real OS action):
  1. safe local dry-run plan  -> adapter allowed AND rust policy allow -> accepted
  2. live launch              -> denied (both gates)
  3. external URL             -> denied (both gates)
  4. secret input             -> denied (both gates)
  5. file:// authority        -> denied (both gates)

Pure stdlib; no real OS actions; the cargo cross-check is skipped when Rust is
not installed.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS_ROOT = Path(__file__).parent.parent.parent.parent / "03_scripts"
sys.path.insert(0, str(_SCRIPTS_ROOT / "computer_use_adapter"))

import ghoti_computer_use_adapter as adapter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]


# ------------------------------------------------------------------
# Plan fixtures (dry-run only)
# ------------------------------------------------------------------

def _safe_local_plan() -> dict:
    return {
        "plan_id": "n6_33a_safe_local",
        "target": "local_sandbox",
        "target_url": "file:///14_context/computer_use/sandbox/page.html",
        "auto_submit": False,
        "requires_human_approval": True,
        "capabilities_required": [],
        "actions": [
            {"action_id": "a1", "type": "read_fixture",
             "value": "14_context/computer_use/sandbox/obs.json"},
            {"action_id": "a2", "type": "check_state",
             "target_element": "#status"},
            {"action_id": "a3", "type": "dry_run_click",
             "target_element": "#btn"},
        ],
    }


def _live_launch_plan() -> dict:
    plan = _safe_local_plan()
    plan["plan_id"] = "n6_33a_live_launch"
    # A blocked, live action type — a real OS click.
    plan["actions"] = [
        {"action_id": "b1", "type": "real_click", "target_element": "#login"},
    ]
    return plan


def _external_url_plan() -> dict:
    plan = _safe_local_plan()
    plan["plan_id"] = "n6_33a_external_url"
    plan["target"] = "approved_window"
    plan["target_url"] = "https://example.com/account/dashboard"
    plan["capabilities_required"] = ["live_browser", "external_web"]
    plan["actions"] = [
        {"action_id": "c1", "type": "navigate_url",
         "value": "https://example.com/account/dashboard"},
    ]
    return plan


def _secret_input_plan() -> dict:
    plan = _safe_local_plan()
    plan["plan_id"] = "n6_33a_secret_input"
    plan["actions"] = [
        {"action_id": "d1", "type": "dry_run_type",
         "target_element": "#field", "value": "my password is hunter2"},
    ]
    return plan


def _file_authority_plan() -> dict:
    plan = _safe_local_plan()
    plan["plan_id"] = "n6_33a_file_authority"
    plan["target_url"] = "file://evil.example/share"
    return plan


def _unknown_capability_plan() -> dict:
    # A capability the Python adapter does NOT block (it is not in
    # BLOCKED_CAPABILITIES), so Gate 1 alone would let it through. The Rust
    # policy gate marks it "unknown" and denies it — demonstrating the second
    # gate catches what the adapter alone would miss (default-deny holds).
    plan = _safe_local_plan()
    plan["plan_id"] = "n6_33a_unknown_capability"
    plan["capabilities_required"] = ["telemetry_upload"]
    return plan


def _write(plan: dict) -> str:
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(plan, fh)
    fh.close()
    return fh.name


# ------------------------------------------------------------------
# Dual-gate proof cases
# ------------------------------------------------------------------

class TestDualGateAcceptance(unittest.TestCase):
    def _run(self, plan: dict) -> dict:
        return adapter._run_plan(_write(plan), rust_bridge=True)

    def test_safe_local_dry_run_accepted_by_both(self):
        result = self._run(_safe_local_plan())
        self.assertEqual(result["status"], "allowed")
        self.assertTrue(result["adapter_allowed"])
        self.assertTrue(result["rust_allowed"])
        self.assertTrue(result["accepted"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["rust_policy_decision"]["decision"], "allow")

    def test_live_launch_denied_by_both(self):
        result = self._run(_live_launch_plan())
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["adapter_allowed"])
        self.assertFalse(result["rust_allowed"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["ok"])
        self.assertIn(
            "live_launch_requested",
            result["rust_policy_decision"]["reasons"],
        )

    def test_external_url_denied_by_both(self):
        result = self._run(_external_url_plan())
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["accepted"])
        self.assertFalse(result["rust_allowed"])
        self.assertIn(
            "blocked_capability_requested",
            result["rust_policy_decision"]["reasons"],
        )
        self.assertIn("browser", result["rust_policy_decision"]["blocked_capabilities"])

    def test_secret_input_denied_by_both(self):
        result = self._run(_secret_input_plan())
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["accepted"])
        self.assertFalse(result["rust_allowed"])
        self.assertIn("secrets", result["rust_policy_decision"]["blocked_capabilities"])

    def test_file_authority_denied_by_both(self):
        result = self._run(_file_authority_plan())
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["accepted"])
        self.assertFalse(result["rust_allowed"])
        self.assertIn("browser", result["rust_policy_decision"]["blocked_capabilities"])

    def test_unknown_capability_denied_by_rust_gate(self):
        # Gate 1 (adapter) allows it; Gate 2 (Rust policy) denies it as unknown.
        # The combined decision must be NOT accepted — the second gate adds value.
        result = self._run(_unknown_capability_plan())
        self.assertEqual(result["status"], "allowed")
        self.assertTrue(result["adapter_allowed"])
        self.assertFalse(result["rust_allowed"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["ok"])
        self.assertIn(
            "unknown_capability_requested",
            result["rust_policy_decision"]["reasons"],
        )
        self.assertIn(
            "telemetry_upload",
            result["rust_policy_decision"]["unknown_capabilities"],
        )


# ------------------------------------------------------------------
# Bridge is opt-in: baseline N+6.29A behavior is preserved
# ------------------------------------------------------------------

class TestBridgeIsOptIn(unittest.TestCase):
    def test_default_run_plan_has_no_bridge(self):
        result = adapter._run_plan(_write(_safe_local_plan()))
        self.assertFalse(result["rust_policy_bridge_ready"])
        self.assertNotIn("rust_policy_decision", result)
        self.assertNotIn("accepted", result)

    def test_default_run_check_has_no_bridge(self):
        result = adapter._run_check()
        self.assertFalse(result["rust_policy_bridge_ready"])
        self.assertNotIn("rust_default_deny_decision", result)

    def test_check_with_bridge_default_denies_empty_plan(self):
        result = adapter._run_check(rust_bridge=True)
        self.assertTrue(result["rust_policy_bridge_ready"])
        self.assertEqual(
            result["rust_default_deny_decision"]["decision"], "deny"
        )


# ------------------------------------------------------------------
# Plan -> swarm-plan mapping and mirror logic
# ------------------------------------------------------------------

class TestPlanToSwarmPlan(unittest.TestCase):
    def test_safe_plan_maps_to_empty_caps_no_live_launch(self):
        sp = adapter._plan_to_swarm_plan(_safe_local_plan())
        self.assertTrue(sp["dry_run"])
        self.assertFalse(sp["live_launch"])
        self.assertTrue(sp["requires_human_approval"])
        self.assertEqual(sp["capabilities"], [])

    def test_blocked_action_sets_live_launch(self):
        sp = adapter._plan_to_swarm_plan(_live_launch_plan())
        self.assertTrue(sp["live_launch"])
        self.assertIn("computer_use", sp["capabilities"])

    def test_external_url_adds_browser_capability(self):
        sp = adapter._plan_to_swarm_plan(_external_url_plan())
        self.assertIn("browser", sp["capabilities"])
        self.assertTrue(sp["live_launch"])

    def test_secret_value_adds_secrets_capability(self):
        sp = adapter._plan_to_swarm_plan(_secret_input_plan())
        self.assertIn("secrets", sp["capabilities"])

    def test_file_authority_adds_browser_capability(self):
        sp = adapter._plan_to_swarm_plan(_file_authority_plan())
        self.assertIn("browser", sp["capabilities"])
        self.assertTrue(sp["live_launch"])


class TestMirrorMatchesRustSemantics(unittest.TestCase):
    def test_empty_plan_default_deny(self):
        decision = adapter._mirror_rust_policy_decision({})
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("dry_run_required", decision["reasons"])

    def test_safe_plan_allowed(self):
        sp = {
            "plan_id": "safe",
            "dry_run": True,
            "live_launch": False,
            "requires_human_approval": True,
            "capabilities": ["repo_read", "plan_render"],
        }
        decision = adapter._mirror_rust_policy_decision(sp)
        self.assertTrue(decision["allowed"])
        self.assertEqual(decision["decision"], "allow")

    def test_blocked_and_unknown_capabilities(self):
        sp = {
            "plan_id": "x",
            "dry_run": True,
            "live_launch": False,
            "requires_human_approval": True,
            "capabilities": ["money", "future_magic"],
        }
        decision = adapter._mirror_rust_policy_decision(sp)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["blocked_capabilities"], ["money"])
        self.assertEqual(decision["unknown_capabilities"], ["future_magic"])

    def test_capability_normalization(self):
        sp = {
            "dry_run": True,
            "requires_human_approval": True,
            "capabilities": ["Mass-Message", "  COMPUTER USE "],
        }
        decision = adapter._mirror_rust_policy_decision(sp)
        self.assertIn("mass_message", decision["blocked_capabilities"])
        self.assertIn("computer_use", decision["blocked_capabilities"])


# ------------------------------------------------------------------
# Safety: the bridge never enables live execution
# ------------------------------------------------------------------

class TestBridgeStaysDryRun(unittest.TestCase):
    def test_accepted_plan_still_reports_no_real_action(self):
        result = adapter._run_plan(_write(_safe_local_plan()), rust_bridge=True)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["real_action_performed"])
        self.assertFalse(result["os_input_used"])
        self.assertTrue(result["safety"]["dry_run_only"])
        self.assertEqual(result["mode"], "dry_run")
        self.assertTrue(result["rust_swarm_plan_input"]["dry_run"])

    def test_arena_status_never_live(self):
        result = adapter._run_plan(_write(_safe_local_plan()), rust_bridge=True)
        self.assertFalse(result["arena_status"]["live_execution"])
        self.assertFalse(result["arena_status"]["live_computer_use_enabled"])

    def test_adapter_source_has_no_unsafe_calls(self):
        """The adapter must not contain real OS-input / browser-driver imports."""
        src = (
            _SCRIPTS_ROOT / "computer_use_adapter" / "ghoti_computer_use_adapter.py"
        ).read_text(encoding="utf-8")
        for forbidden in ("pyautogui", "selenium", "playwright", "pynput",
                          "shell=True"):
            self.assertNotIn(forbidden, src, msg=f"forbidden token: {forbidden}")


# ------------------------------------------------------------------
# Optional cross-check against the real cargo binary
# ------------------------------------------------------------------

class TestRustCargoCrossCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cargo = shutil.which("cargo")
        cls.manifest = REPO_ROOT / "rust" / "ghoti_policy_checker" / "Cargo.toml"

    def setUp(self):
        if not self.cargo:
            self.skipTest("cargo not installed")
        if not self.manifest.exists():
            self.skipTest("policy checker manifest missing")

    def _cargo_decision(self, swarm_plan: dict) -> dict:
        return adapter._invoke_rust_policy_checker(swarm_plan, str(self.manifest))

    def test_unapproved_manifest_is_refused_without_invoking_cargo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            unapproved = Path(temp_dir) / "Cargo.toml"
            unapproved.write_text("[package]\nname = \"unapproved\"\n", encoding="utf-8")
            with mock.patch.object(adapter.subprocess, "run") as run:
                result = adapter._invoke_rust_policy_checker(
                    adapter._plan_to_swarm_plan(_safe_local_plan()),
                    str(unapproved),
                )
        self.assertFalse(result["available"])
        self.assertIn("not the approved Ghoti manifest", result["note"])
        run.assert_not_called()

    def test_cargo_agrees_with_mirror_for_each_case(self):
        for builder in (
            _safe_local_plan, _live_launch_plan, _external_url_plan,
            _secret_input_plan, _file_authority_plan, _unknown_capability_plan,
        ):
            plan = builder()
            swarm_plan = adapter._plan_to_swarm_plan(plan)
            mirror = adapter._mirror_rust_policy_decision(swarm_plan)
            cli = self._cargo_decision(swarm_plan)
            if not cli.get("available"):
                self.skipTest("cargo policy checker unavailable")
            self.assertEqual(
                cli["decision"], mirror["decision"],
                msg=f"mismatch for {plan['plan_id']}: cli={cli} mirror={mirror}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
