import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "safe_computer_use_observation_harness.py"
FIXTURE = REPO_ROOT / "14_context" / "computer_use" / "fixtures" / "apple_mac_compare_fixture.json"
README = REPO_ROOT / "14_context" / "computer_use" / "README_SAFE_OBSERVATION_HARNESS.md"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_5_SAFE_COMPUTER_USE_OBSERVATION_HARNESS.md"


class SafeComputerUseObservationHarnessTests(unittest.TestCase):
    def run_harness(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--fixture",
                str(FIXTURE),
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_required_files_exist(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertTrue(FIXTURE.is_file())
        self.assertTrue(README.is_file())
        self.assertTrue(DOC.is_file())

    def test_harness_outputs_safe_json(self):
        data = self.run_harness()
        self.assertTrue(data["ok"])
        self.assertEqual(data["scenario_id"], "apple-mac-compare-local-fixture")
        self.assertTrue(data["required_human_approval"])
        self.assertTrue(data["requires_human_approval"])
        self.assertEqual(data["safety_verdict"], "OBSERVATION_ONLY_REQUIRES_HUMAN_APPROVAL")
        self.assertIn("summarize_fixture", data["allowed_actions_now"])
        self.assertIn("propose_plan", data["allowed_actions_now"])
        self.assertIn("Mock Mac mini", data["detected_entities"]["products"])

    def test_output_does_not_claim_live_browser_or_click_type(self):
        data = self.run_harness()
        flags = data["safety_flags"]
        self.assertTrue(flags["local_only"])
        self.assertTrue(flags["observation_only"])
        for key in [
            "browser_opened",
            "live_browser_executed",
            "chrome_opened",
            "live_site_visited",
            "clicked_or_typed",
            "click_enabled",
            "type_enabled",
            "live_network_used",
            "live_api_used",
            "external_telemetry_enabled",
        ]:
            self.assertFalse(flags[key], msg=f"{key} must stay false")

    def test_forbidden_actions_are_explicit(self):
        data = self.run_harness()
        forbidden = set(data["forbidden_actions"])
        for action in [
            "click",
            "type",
            "login",
            "cart",
            "purchase",
            "captcha_bypass",
            "cookie_bypass",
            "browser_launch",
            "network_request",
        ]:
            self.assertIn(action, forbidden)

    def test_docs_state_observation_only_and_boundaries(self):
        combined = (README.read_text(encoding="utf-8") + "\n" + DOC.read_text(encoding="utf-8")).lower()
        for needle in [
            "observation-only",
            "local fixture",
            "no live browser",
            "no chrome",
            "no click/type",
            "no accounts",
            "login",
            "cart",
            "purchase",
            "captcha",
            "cookie",
            "bypass",
            "human approval",
        ]:
            self.assertIn(needle, combined)

    def test_script_uses_no_browser_network_or_telemetry_libraries(self):
        text = SCRIPT.read_text(encoding="utf-8").lower()
        for forbidden in [
            "subprocess",
            "requests",
            "httpx",
            "selenium",
            "playwright",
            "webbrowser",
            "urllib",
            "opentelemetry",
            "analytics",
            "socket",
        ]:
            self.assertNotIn(forbidden, text)

    def test_invalid_fixture_exits_nonzero(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--fixture",
                str(REPO_ROOT / "does_not_exist.json"),
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertFalse(data["ok"])


if __name__ == "__main__":
    unittest.main()
