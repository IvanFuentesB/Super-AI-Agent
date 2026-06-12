"""N+6.44A local agent command-center simulation contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "agent_command_center" / "ghoti_agent_command_center.py"
CHECK_PS = REPO_ROOT / "03_scripts" / "agent_command_center" / "check_agent_command_center.ps1"
START_PS = REPO_ROOT / "03_scripts" / "agent_command_center" / "start_agent_command_center.ps1"
FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"
CTX = REPO_ROOT / "14_context" / "agent_command_center"
SCENARIOS = CTX / "scenarios"
GENERATED = CTX / "generated"
STATIC = REPO_ROOT / "03_scripts" / "agent_command_center" / "static"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_44A_LOCAL_AGENT_COMMAND_CENTER_SIMULATION.md"
README = CTX / "README.md"

EXPECTED_FILES = [
    SCRIPT,
    CHECK_PS,
    START_PS,
    README,
    DOC,
    SCENARIOS / "content_revenue_research.json",
    SCENARIOS / "ecommerce_product_research.json",
    SCENARIOS / "code_maintenance_swarm.json",
    GENERATED / "command_center_status.json",
    GENERATED / "content_revenue_paperclip_preview.json",
    GENERATED / "content_revenue_arena_simulation.json",
    STATIC / "index.html",
    STATIC / "app.js",
    STATIC / "styles.css",
]


def run_cli(*args: str) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {}
    return proc.returncode, payload, proc.stderr


class FilesAndSourceSafetyTests(unittest.TestCase):
    def test_expected_files_exist(self):
        for path in EXPECTED_FILES:
            self.assertTrue(path.is_file(), msg=f"missing: {path}")

    def test_command_center_has_no_process_network_or_live_input_surface(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            "import subprocess",
            "os.system(",
            "shell=True",
            "Invoke-Expression",
            "requests.",
            "httpx.",
            "selenium",
            "playwright",
            "pyautogui",
            "SendKeys",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIsNone(re.search(r"\bPopen\s*\(|\bexec\s*\(|\beval\s*\(", source))


class StatusAndMemoryTests(unittest.TestCase):
    def test_check_is_safe_and_simulation_only(self):
        rc, data, err = run_cli("--check")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["local_only"])
        self.assertTrue(data["simulation"])
        self.assertFalse(data["live_execution"])
        self.assertFalse(data["live_agent_launch"])
        self.assertFalse(data["mouse_click_enabled"])
        self.assertFalse(data["keyboard_input_enabled"])
        self.assertFalse(data["account_actions_enabled"])
        self.assertFalse(data["money_actions_enabled"])
        self.assertFalse(data["posting_enabled"])

    def test_status_integrates_verified_memory_and_repo_patterns(self):
        rc, data, err = run_cli("--status")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        memory = data["memory"]
        self.assertEqual(memory["verified_sources"], 12)
        self.assertEqual(memory["engine"], "deterministic_local_feature_hash_v1")
        self.assertTrue(memory["search_aid_only"])
        systems = data["agent_systems"]
        self.assertEqual(systems["paperclip"]["mode"], "planning_preview_only")
        self.assertFalse(systems["paperclip"]["live_company_launch"])
        self.assertIn("claude_swarm", systems["repo_patterns"])

    def test_health_reports_loopback_get_only_dashboard(self):
        rc, data, err = run_cli("--health")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["binds_loopback_only"])
        self.assertTrue(data["get_only"])
        self.assertFalse(data["has_post_routes"])
        self.assertFalse(data["live_execution"])

    def test_memory_query_returns_source_pointers_not_source_text(self):
        rc, data, err = run_cli("--memory-query", "coordinator planner memory writer")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertGreater(len(data["results"]), 0)
        for result in data["results"]:
            self.assertTrue(result["hash_verified"])
            self.assertIn("source_path", result)
            self.assertNotIn("source_text", result)
            self.assertFalse(result["canonical_truth"])


class ScenarioSimulationTests(unittest.TestCase):
    def _scenario(self, scenario_id: str) -> dict:
        rc, data, err = run_cli("--scenario", scenario_id)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"], msg=data)
        return data

    def test_content_revenue_scenario_is_research_and_draft_only(self):
        data = self._scenario("content-revenue-research")
        self.assertEqual(data["business_lane"], "content_revenue_research")
        self.assertIn("human_approver", data["roles"])
        self.assertFalse(data["safety"]["posting_enabled"])
        self.assertFalse(data["safety"]["account_actions_enabled"])
        self.assertFalse(data["safety"]["money_actions_enabled"])
        self.assertIn("human approval", " ".join(data["approval_gates"]).lower())

    def test_ecommerce_scenario_cannot_open_store_buy_or_run_ads(self):
        data = self._scenario("ecommerce-product-research")
        joined = " ".join(data["blocked_actions"]).lower()
        for phrase in ("store login", "purchase", "ad spend", "supplier contact"):
            self.assertIn(phrase, joined)
        self.assertEqual(data["business_lane"], "ecommerce_product_research")
        self.assertFalse(data["safety"]["live_execution"])

    def test_code_scenario_has_non_overlapping_owned_files(self):
        data = self._scenario("code-maintenance-swarm")
        self.assertTrue(data["ownership"]["one_owner_per_path"])
        self.assertEqual(data["ownership"]["conflicts"], [])
        self.assertGreaterEqual(len(data["waves"]), 2)

    def test_agent_arena_shape_is_simulation_only(self):
        rc, data, err = run_cli("--arena-preview", "content-revenue-research")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["simulation"])
        self.assertFalse(data["live_execution"])
        self.assertGreaterEqual(len(data["agents"]), 5)
        self.assertGreater(len(data["queue"]), 0)

    def test_paperclip_preview_is_not_a_live_company(self):
        rc, data, err = run_cli("--paperclip-preview", "content-revenue-research")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["mode"], "paperclip_compatible_planning_preview")
        self.assertFalse(data["live_company_created"])
        self.assertFalse(data["docker_used"])
        self.assertFalse(data["external_repo_executed"])
        self.assertTrue(data["human_approval_required"])


class ScenarioAndDocsSafetyTests(unittest.TestCase):
    def test_scenarios_block_live_and_high_risk_actions(self):
        blocked_required = {
            "live agent launch",
            "mouse click",
            "keyboard input",
            "account login",
            "purchase",
            "payment",
            "auto-submit",
            "live posting",
        }
        for path in SCENARIOS.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            blocked = {item.lower() for item in data["blocked_actions"]}
            self.assertTrue(blocked_required.issubset(blocked), msg=path.name)
            self.assertTrue(data["simulation"])
            self.assertFalse(data["live_execution"])

    def test_docs_are_honest_about_money_and_computer_use(self):
        text = (README.read_text(encoding="utf-8") + DOC.read_text(encoding="utf-8")).lower()
        self.assertIn("does not guarantee income", text)
        self.assertIn("simulation", text)
        self.assertIn("paperclip", text)
        self.assertIn("obsidian", text)
        self.assertIn("full computer-use remains blocked", text)

    def test_committed_files_have_no_private_absolute_paths(self):
        slash = "/"
        backslash = chr(92)
        forbidden = [
            "C:" + backslash + "Users" + backslash,
            "C:" + slash + "Users" + slash,
            slash + "mnt" + slash + "c" + slash + "Users" + slash,
            "ai" + "_sandbox",
        ]
        for path in EXPECTED_FILES:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"{token!r} in {path}")

    def test_generated_packets_are_small(self):
        for path in GENERATED.glob("*.json"):
            self.assertLess(path.stat().st_size, 100_000, msg=path.name)

    def test_command_center_feature_flags_default_false(self):
        flags = json.loads(FLAGS.read_text(encoding="utf-8"))
        for name in (
            "local_agent_command_center_enabled",
            "local_agent_command_center_live_launch_enabled",
            "paperclip_live_company_launch_enabled",
            "supervised_business_scenarios_enabled",
        ):
            self.assertIn(name, flags)
            self.assertFalse(flags[name])

    def test_visual_command_center_has_no_external_assets_or_forms(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        assets = "\n".join(path.read_text(encoding="utf-8") for path in STATIC.glob("*.*"))
        self.assertIn("Ghoti Agent Command Center", html)
        self.assertNotIn("<form", html.lower())
        self.assertNotRegex(assets, r"https?://|//cdn\.|unpkg|jsdelivr|cdnjs")

    def test_server_has_no_post_or_external_bind_escape_hatch(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"def\s+do_POST")
        self.assertNotIn("allow_nonlocal", source)
        rc, data, err = run_cli("--serve", "--host", "0.0.0.0")
        self.assertNotEqual(rc, 0, msg=err)
        self.assertFalse(data["ok"])
        self.assertTrue(data["binds_loopback_only"])


if __name__ == "__main__":
    unittest.main()
