"""
test_n6_35a_plug_and_play_agent_systems_trial.py — N+6.35A test suite (≥17 tests).

Covers:
- Inventory loading and repo classification
- Engine selection logic (claude_swarm, am_will_swarms, clawteam, blocked engines)
- Model routing (Opus, Sonnet, Codex, Hermes, DeepSeek)
- Dry-run plan production
- Arena status shape (simulation=true, live_execution=false)
- Hooks-blocked refusal
- Globally blocked capabilities
- Dual-gate validation (pre-filter + N+6.33A adapter)
- Check mode
- Safety invariants
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the planner module is importable
_SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "03_scripts" / "agent_systems_trial"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import ghoti_agent_systems_trial as _planner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _inventory_path() -> Path:
    return _repo_root() / "14_context" / "agent_systems_trial" / "agent_systems_inventory_n6_35a.json"


def _load_inventory() -> list[dict]:
    return _planner._load_inventory(_inventory_path())


def _task_spec(task_type: str = "swarm_coordination", complexity: str = "medium",
               task_id: str = "test-01", **extra) -> dict:
    return {"task_id": task_id, "task_type": task_type, "complexity": complexity, **extra}


def _write_task_spec(spec: dict) -> str:
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(spec, tf)
    tf.close()
    return tf.name


# ---------------------------------------------------------------------------
# 1. Inventory
# ---------------------------------------------------------------------------

class TestInventory(unittest.TestCase):
    def test_inventory_loads(self):
        inv = _load_inventory()
        self.assertIsInstance(inv, list)
        self.assertGreater(len(inv), 0)

    def test_inventory_has_seven_repos(self):
        inv = _load_inventory()
        self.assertEqual(len(inv), 7)

    def test_inventory_ids(self):
        inv = _load_inventory()
        ids = {r["id"] for r in inv}
        expected = {
            "claude_swarm", "am_will_swarms", "clawteam",
            "ruflo", "ecc", "paperclip", "hermes_paperclip_adapter",
        }
        self.assertEqual(ids, expected)

    def test_verdicts_present(self):
        inv = _load_inventory()
        for repo in inv:
            self.assertIn("verdict", repo, f"Missing verdict for {repo['id']}")

    def test_claude_swarm_most_ready(self):
        inv = _load_inventory()
        cs = next(r for r in inv if r["id"] == "claude_swarm")
        self.assertEqual(cs["verdict"], "MOST_READY")

    def test_am_will_swarms_second_ready(self):
        inv = _load_inventory()
        aw = next(r for r in inv if r["id"] == "am_will_swarms")
        self.assertEqual(aw["verdict"], "SECOND_READY")

    def test_hooks_engines_blocked(self):
        inv = _load_inventory()
        for repo in inv:
            if "hooks" in repo.get("blocked_capabilities", []):
                self.assertIn(repo["verdict"], {"ADAPT_LATER", "GOVERNANCE_PATTERNS_ONLY"})


# ---------------------------------------------------------------------------
# 2. Engine selection
# ---------------------------------------------------------------------------

class TestEngineSelection(unittest.TestCase):
    def setUp(self):
        self.inventory = _load_inventory()

    def test_swarm_coordination_selects_claude_swarm(self):
        spec = _task_spec("swarm_coordination")
        result = _planner._select_engine(spec, self.inventory)
        self.assertEqual(result["selected"], "claude_swarm")

    def test_parallel_tasks_selects_am_will_swarms(self):
        spec = _task_spec("parallel_tasks")
        result = _planner._select_engine(spec, self.inventory)
        self.assertEqual(result["selected"], "am_will_swarms")

    def test_cli_batch_selects_clawteam(self):
        spec = _task_spec("cli_batch")
        result = _planner._select_engine(spec, self.inventory)
        self.assertEqual(result["selected"], "clawteam")

    def test_unknown_task_type_falls_back(self):
        spec = _task_spec("unknown_xyz_task")
        result = _planner._select_engine(spec, self.inventory)
        self.assertIn(result["selected"], {"claude_swarm", "am_will_swarms", "clawteam"})

    def test_ruflo_not_selected_directly(self):
        # ruflo is ADAPT_LATER — should never be returned as selected engine
        spec = _task_spec("swarm_coordination")
        result = _planner._select_engine(spec, self.inventory)
        self.assertNotEqual(result["selected"], "ruflo")

    def test_ecc_not_selected_directly(self):
        spec = _task_spec("swarm_coordination")
        result = _planner._select_engine(spec, self.inventory)
        self.assertNotEqual(result["selected"], "ecc")

    def test_paperclip_not_selected_directly(self):
        spec = _task_spec("swarm_coordination")
        result = _planner._select_engine(spec, self.inventory)
        self.assertNotEqual(result["selected"], "paperclip")


# ---------------------------------------------------------------------------
# 3. Model routing
# ---------------------------------------------------------------------------

class TestModelRouting(unittest.TestCase):
    def setUp(self):
        self.inventory = _load_inventory()

    def _engine(self, task_type: str) -> dict:
        return _planner._select_engine(_task_spec(task_type), self.inventory)

    def test_high_complexity_routes_opus(self):
        spec = _task_spec("swarm_coordination", complexity="high")
        engine = self._engine("swarm_coordination")
        route = _planner._route_model(spec, engine)
        self.assertEqual(route["routing_key"], "complex_integration")
        self.assertIn("opus", route["model"])

    def test_low_complexity_routes_sonnet(self):
        spec = _task_spec("code_fix", complexity="low")
        engine = self._engine("code_fix")
        route = _planner._route_model(spec, engine)
        self.assertEqual(route["routing_key"], "small_fix")
        self.assertIn("sonnet", route["model"])

    def test_merge_gate_routes_codex(self):
        spec = _task_spec("merge_gate")
        engine = self._engine("merge_gate")
        route = _planner._route_model(spec, engine)
        self.assertEqual(route["routing_key"], "merge_gate")
        self.assertIn("codex", route["model"])

    def test_summary_routes_deepseek(self):
        spec = _task_spec("summary")
        engine = self._engine("summary")
        route = _planner._route_model(spec, engine)
        self.assertEqual(route["routing_key"], "summary")
        self.assertIn("deepseek", route["model"])

    def test_coordination_routes_hermes(self):
        spec = _task_spec("swarm_coordination", requires_coordination=True)
        engine = self._engine("swarm_coordination")
        route = _planner._route_model(spec, engine)
        self.assertEqual(route["routing_key"], "coordination")
        self.assertIn("hermes", route["model"])

    def test_model_route_has_tier(self):
        spec = _task_spec("swarm_coordination", complexity="high")
        engine = self._engine("swarm_coordination")
        route = _planner._route_model(spec, engine)
        self.assertIn("tier", route)
        self.assertIn("reason", route)


# ---------------------------------------------------------------------------
# 4. Dry-run plan production
# ---------------------------------------------------------------------------

class TestPlanProduction(unittest.TestCase):
    def setUp(self):
        self.inventory = _load_inventory()
        spec = _task_spec("swarm_coordination")
        self.engine = _planner._select_engine(spec, self.inventory)
        self.model_route = _planner._route_model(spec, self.engine)
        self.plan = _planner._build_execution_plan(spec, self.engine, self.model_route)

    def test_plan_is_dry_run(self):
        self.assertTrue(self.plan["dry_run"])

    def test_plan_live_launch_false(self):
        self.assertFalse(self.plan["live_launch"])

    def test_plan_requires_human_approval(self):
        self.assertTrue(self.plan["requires_human_approval"])

    def test_plan_capabilities_are_safe(self):
        for cap in self.plan["capabilities"]:
            self.assertNotIn(cap, _planner._GLOBALLY_BLOCKED,
                             f"Unsafe capability in plan: {cap}")

    def test_plan_actions_are_dry_run(self):
        for action in self.plan["actions"]:
            self.assertTrue(action["dry_run"], f"Action not dry_run: {action}")


# ---------------------------------------------------------------------------
# 5. Arena status shape
# ---------------------------------------------------------------------------

class TestArenaStatus(unittest.TestCase):
    def _check_mode_result(self) -> dict:
        return _planner._run_check()

    def test_safety_block_simulation_true(self):
        result = self._check_mode_result()
        self.assertTrue(result["safety_block"]["simulation"])

    def test_safety_block_live_execution_false(self):
        result = self._check_mode_result()
        self.assertFalse(result["safety_block"]["live_execution"])

    def test_safety_block_live_computer_use_false(self):
        result = self._check_mode_result()
        self.assertFalse(result["safety_block"]["live_computer_use_enabled"])

    def test_safety_block_hooks_disabled(self):
        result = self._check_mode_result()
        self.assertFalse(result["safety_block"]["hooks_enabled"])

    def test_safety_block_third_party_not_executed(self):
        result = self._check_mode_result()
        self.assertFalse(result["safety_block"]["third_party_code_executed"])
        self.assertFalse(result["safety_block"]["third_party_code_imported"])


# ---------------------------------------------------------------------------
# 6. Hooks-blocked refusal
# ---------------------------------------------------------------------------

class TestHooksBlocked(unittest.TestCase):
    def _run(self, spec: dict) -> dict:
        tmp = _write_task_spec(spec)
        try:
            return _planner._run_trial(Path(tmp))
        finally:
            os.unlink(tmp)

    def test_hooks_capability_refused(self):
        spec = _task_spec("swarm_coordination", capabilities=["hooks"])
        result = self._run(spec)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "hooks_requested")

    def test_enable_hooks_action_refused(self):
        spec = _task_spec("swarm_coordination", actions=["enable_hooks"])
        result = self._run(spec)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "hooks_requested")

    def test_pretooluse_refused(self):
        spec = _task_spec("swarm_coordination", actions=["PreToolUse"])
        result = self._run(spec)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "hooks_requested")


# ---------------------------------------------------------------------------
# 7. Globally blocked capabilities pre-filter
# ---------------------------------------------------------------------------

class TestGloballyBlockedPreFilter(unittest.TestCase):
    def test_globally_blocked_set_non_empty(self):
        self.assertGreater(len(_planner._GLOBALLY_BLOCKED), 0)

    def test_docker_is_blocked(self):
        self.assertIn("docker", _planner._GLOBALLY_BLOCKED)

    def test_mcp_is_blocked(self):
        self.assertIn("mcp", _planner._GLOBALLY_BLOCKED)

    def test_live_launch_is_blocked(self):
        self.assertIn("live_launch", _planner._GLOBALLY_BLOCKED)

    def test_hooks_is_blocked(self):
        self.assertIn("hooks", _planner._GLOBALLY_BLOCKED)

    def test_secrets_is_blocked(self):
        self.assertIn("secrets", _planner._GLOBALLY_BLOCKED)


# ---------------------------------------------------------------------------
# 8. Check mode
# ---------------------------------------------------------------------------

class TestCheckMode(unittest.TestCase):
    def test_check_ok(self):
        result = _planner._run_check()
        self.assertTrue(result["ok"])

    def test_check_milestone(self):
        result = _planner._run_check()
        self.assertEqual(result["milestone"], "N+6.35A")

    def test_check_has_inventory_count(self):
        result = _planner._run_check()
        self.assertIn("repos_in_inventory", result)
        self.assertGreaterEqual(result["repos_in_inventory"], 7)

    def test_check_has_globally_blocked_list(self):
        result = _planner._run_check()
        self.assertIn("globally_blocked_capabilities", result)
        self.assertIn("docker", result["globally_blocked_capabilities"])


# ---------------------------------------------------------------------------
# 9. Full trial run (swarm_coordination)
# ---------------------------------------------------------------------------

class TestFullTrialRun(unittest.TestCase):
    def _run(self, spec: dict) -> dict:
        tmp = _write_task_spec(spec)
        try:
            return _planner._run_trial(Path(tmp))
        finally:
            os.unlink(tmp)

    def test_swarm_coordination_trial_accepted(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertTrue(result.get("accepted", False),
                        f"Expected accepted=True, got: {result}")

    def test_trial_result_has_safety_block(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertIn("safety_block", result)

    def test_trial_safety_block_simulation_true(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertTrue(result["safety_block"]["simulation"])

    def test_trial_result_has_engine_selection(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertIn("engine_selection", result)
        self.assertEqual(result["engine_selection"]["selected"], "claude_swarm")

    def test_trial_result_has_model_routing(self):
        spec = _task_spec("swarm_coordination", complexity="high")
        result = self._run(spec)
        self.assertIn("model_routing", result)
        self.assertIn("tier", result["model_routing"])

    def test_trial_result_has_execution_plan(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertIn("execution_plan", result)
        self.assertTrue(result["execution_plan"]["dry_run"])

    def test_trial_milestone_correct(self):
        spec = _task_spec("swarm_coordination")
        result = self._run(spec)
        self.assertEqual(result["milestone"], "N+6.35A")


# ---------------------------------------------------------------------------
# 10. Adapter source safety
# ---------------------------------------------------------------------------

class TestAdapterSourceSafety(unittest.TestCase):
    def test_planner_does_not_import_third_party_engines(self):
        import ast, inspect
        src = inspect.getsource(_planner)
        tree = ast.parse(src)
        forbidden = {"ruflo", "ecc", "paperclip", "clawteam", "claude_swarm",
                     "am_will_swarms", "hermes_paperclip"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in getattr(node, "names", []):
                    name = alias.name or ""
                    self.assertFalse(
                        any(f in name for f in forbidden),
                        f"Planner imports third-party engine code: {name}",
                    )

    def test_planner_no_subprocess_calls(self):
        import ast, inspect
        src = inspect.getsource(_planner)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in ("run", "call", "Popen"):
                    if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                        self.fail("Planner uses subprocess to launch external processes")


if __name__ == "__main__":
    unittest.main()
