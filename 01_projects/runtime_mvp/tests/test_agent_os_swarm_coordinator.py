"""Tests for the Agent OS swarm coordinator (control plane).

Pure-function tests (determinism, allowlists, dependency order, ownership
overlap, blocked capabilities) always run. Queue-integration tests (queue-next
creates an approval request not an execution, one-worker lock, full planning
demo) run against an isolated temp queue and the real Rust guard; they skip if
cargo is unavailable. Also asserts the dashboard wiring and that no duplicate
systems were introduced.
"""

from __future__ import annotations

import copy
import importlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_OS_DIR = REPO_ROOT / "03_scripts" / "agent_os"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
sys.path.insert(0, str(AGENT_OS_DIR))

import approval_queue  # noqa: E402
import swarm_coordinator as sc  # noqa: E402

SWARM_IDS = ["coding-task-swarm-plan", "content-pipeline-swarm-plan",
             "business-research-swarm-plan"]


class TestPlanBuilding(unittest.TestCase):
    def test_known_workflows_build_ok(self):
        for wf in SWARM_IDS:
            plan = sc.build_plan(wf, created_at="20260614T000000Z")
            self.assertTrue(plan["ok"], wf)
            self.assertTrue(plan["plan_id"].startswith("swarm-"))
            self.assertTrue(plan["single_worker_lock"])
            self.assertFalse(plan["safety"]["parallel_execution"])

    def test_plan_is_deterministic(self):
        a = sc.build_plan("coding-task-swarm-plan", created_at="20260614T000000Z")
        b = sc.build_plan("coding-task-swarm-plan", created_at="20260614T999999Z")
        self.assertEqual(a["plan_id"], b["plan_id"])
        self.assertEqual(a["fingerprint"], b["fingerprint"])

    def test_unknown_workflow_rejected(self):
        plan = sc.build_plan("does-not-exist")
        self.assertFalse(plan["ok"])

    def test_only_known_workers_allowed(self):
        bad = copy.deepcopy(sc.SWARM_WORKFLOWS["coding-task-swarm-plan"])
        bad["steps"][0]["worker_id"] = "rogue-worker"
        with _temp_workflow(sc, "bad-worker-plan", bad):
            plan = sc.build_plan("bad-worker-plan")
            self.assertFalse(plan["ok"])
            self.assertTrue(any("unknown worker" in e for e in plan["errors"]))

    def test_blocked_capability_rejected(self):
        bad = copy.deepcopy(sc.SWARM_WORKFLOWS["coding-task-swarm-plan"])
        bad["steps"][0]["capabilities"] = ["repo_read", "browser"]
        with _temp_workflow(sc, "bad-cap-plan", bad):
            plan = sc.build_plan("bad-cap-plan")
            self.assertFalse(plan["ok"])
            self.assertTrue(any("blocked capability" in e for e in plan["errors"]))

    def test_money_account_capabilities_rejected(self):
        for cap in ("money", "account", "computer_use"):
            bad = copy.deepcopy(sc.SWARM_WORKFLOWS["business-research-swarm-plan"])
            bad["steps"][0]["capabilities"] = ["repo_read", cap]
            with _temp_workflow(sc, "cap-%s-plan" % cap, bad):
                plan = sc.build_plan("cap-%s-plan" % cap)
                self.assertFalse(plan["ok"], cap)

    def test_forward_dependency_rejected(self):
        bad = copy.deepcopy(sc.SWARM_WORKFLOWS["coding-task-swarm-plan"])
        bad["steps"][0]["dependencies"] = [3]  # step 1 depends on later step 3
        with _temp_workflow(sc, "bad-dep-plan", bad):
            plan = sc.build_plan("bad-dep-plan")
            self.assertFalse(plan["ok"])
            self.assertTrue(any("dependency" in e for e in plan["errors"]))

    def test_ownership_overlap_blocks_step(self):
        bad = copy.deepcopy(sc.SWARM_WORKFLOWS["coding-task-swarm-plan"])
        # Make steps 1 and 2 independent but share an owned folder.
        bad["steps"][1]["dependencies"] = []
        bad["steps"][1]["owned_files"] = bad["steps"][0]["owned_files"]
        bad["steps"][2]["dependencies"] = []
        with _temp_workflow(sc, "overlap-plan", bad):
            plan = sc.build_plan("overlap-plan")
            self.assertTrue(plan["ok"])
            statuses = [s["status"] for s in plan["steps"]]
            self.assertIn("blocked", statuses)


class TestDependencyScheduling(unittest.TestCase):
    def test_first_runnable_has_no_unmet_deps(self):
        plan = sc.build_plan("coding-task-swarm-plan", created_at="20260614T000000Z")
        step = sc.next_runnable_step(plan)
        self.assertIsNotNone(step)
        self.assertEqual(step["step"], 1)
        self.assertEqual(step["dependencies"], [])

    def test_dependent_step_not_runnable_until_dep_executed(self):
        plan = sc.build_plan("coding-task-swarm-plan", created_at="20260614T000000Z")
        # Step 2 depends on 1; with 1 still planned, runnable is step 1, not 2.
        self.assertEqual(sc.next_runnable_step(plan)["step"], 1)
        plan["steps"][0]["status"] = "executed"
        self.assertEqual(sc.next_runnable_step(plan)["step"], 2)


class RustGuardMixin:
    @classmethod
    def setUpClass(cls):
        if shutil.which("cargo") is None:
            raise unittest.SkipTest("cargo required for swarm queue tests")


class TestQueueIntegration(RustGuardMixin, unittest.TestCase):
    """Runs against the real (gitignored) repo dirs + real Rust guard, cleaning
    up the exact plan/request/evidence files each test creates."""

    def setUp(self):
        self.queue_root = REPO_ROOT / "14_context" / "agent_os" / "approval_queue"
        self._orig_queue = sc._queue
        self._created_requests: list[str] = []
        self._created_plan_ids: set[str] = set()
        self._created_files: list[Path] = []
        outer = self

        def _factory():
            q = approval_queue.ApprovalQueue()
            orig_propose = q.propose

            def _tracked(req):
                res = orig_propose(req)
                if res.get("request_id"):
                    outer._created_requests.append(res["request_id"])
                return res
            q.propose = _tracked
            return q
        sc._queue = _factory

    def _fresh_plan(self, workflow):
        """Write a plan, starting from a clean slate for that deterministic id."""
        plan_id = sc.build_plan(workflow, created_at="20260614T000000Z")["plan_id"]
        for suffix in (".json", ".md"):
            f = sc.SWARM_PLANS_DIR / (plan_id + suffix)
            if f.exists():
                f.unlink()
        plan = sc.write_plan(workflow, created_at="20260614T000000Z")
        self._created_plan_ids.add(plan["plan_id"])
        return plan

    def tearDown(self):
        sc._queue = self._orig_queue
        for plan_id in self._created_plan_ids:
            for suffix in (".json", ".md"):
                f = sc.SWARM_PLANS_DIR / (plan_id + suffix)
                if f.exists():
                    f.unlink()
        for rid in self._created_requests:
            for state in ("pending", "approved", "executed", "rejected", "failed"):
                f = self.queue_root / state / ("%s.json" % rid)
                if f.exists():
                    f.unlink()
        for f in self._created_files:
            if f.exists():
                f.unlink()

    def test_queue_next_creates_approval_request_not_execution(self):
        plan = self._fresh_plan("coding-task-swarm-plan")
        result = sc.queue_next_step(plan["plan_id"])
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["queued_step"], 1)
        self.assertTrue(result["request_id"].startswith("req-"))
        self.assertFalse(result["executed"])
        state, _ = approval_queue.ApprovalQueue()._find(result["request_id"])
        self.assertEqual(state, "pending")

    def test_only_one_step_queued_at_a_time(self):
        plan = self._fresh_plan("content-pipeline-swarm-plan")
        first = sc.queue_next_step(plan["plan_id"])
        self.assertTrue(first["ok"])
        second = sc.queue_next_step(plan["plan_id"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["reason"], "one_worker_lock")

    def test_full_swarm_planning_demo_creates_evidence(self):
        # Start clean for all three deterministic plan ids (remove any stale
        # plan files so the demo builds fresh, unqueued plans).
        for wf in SWARM_IDS:
            plan_id = sc.build_plan(wf, created_at="20260614T000000Z")["plan_id"]
            self._created_plan_ids.add(plan_id)
            for suffix in (".json", ".md"):
                f = sc.SWARM_PLANS_DIR / (plan_id + suffix)
                if f.exists():
                    f.unlink()
        payload = sc.full_swarm_planning_demo()
        self.assertTrue(payload["ok"], payload)
        md = REPO_ROOT / payload["evidence_path"]
        js = REPO_ROOT / payload["evidence_json_path"]
        self._created_files += [md, js]
        for entry in payload["plans"]:
            self._created_plan_ids.add(entry["plan_id"])
        self.assertTrue(md.is_file())
        self.assertTrue(js.is_file())
        self.assertFalse(payload["live_execution"])


class TestDashboardWiring(unittest.TestCase):
    def setUp(self):
        self.server = SERVER_JS.read_text(encoding="utf-8")
        self.index = INDEX_HTML.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")

    def test_server_swarm_endpoints_present(self):
        for route in ("agent-os-swarm-status", "agent-os-swarm-plans",
                      "agent-os-plan-swarm", "agent-os-queue-next-swarm-step",
                      "agent-os-full-swarm-planning-demo"):
            self.assertIn("/api/product-control/%s" % route, self.server)
        self.assertIn("AGENT_OS_SWARM_IDS", self.server)

    def test_index_and_app_swarm_controls_present(self):
        self.assertIn('id="agentos-swarm-card"', self.index)
        self.assertIn('id="agentos-swarm-plan"', self.index)
        self.assertIn("function agentOsSwarmPlan", self.app)
        self.assertIn("agentOsSwarmQueueNext", self.app)


class TestNoDuplicateSystems(unittest.TestCase):
    def test_coordinator_reuses_approval_queue(self):
        source = (AGENT_OS_DIR / "swarm_coordinator.py").read_text(encoding="utf-8")
        self.assertIn("import approval_queue", source)
        # It must not redefine a queue or an executor of its own.
        self.assertNotIn("class ApprovalQueue", source)
        self.assertNotIn("def execute_approved_request", source)

    def test_no_duplicate_subsystem_refs(self):
        source = (AGENT_OS_DIR / "swarm_coordinator.py").read_text(encoding="utf-8")
        for token in ("context_memory", "agent_command_center", "14_context/memory/"):
            self.assertNotIn(token, source)


class _temp_workflow:
    """Context manager: temporarily register a workflow spec for validation."""

    def __init__(self, module, name, spec):
        self.module = module
        self.name = name
        self.spec = spec

    def __enter__(self):
        self.module.SWARM_WORKFLOWS[self.name] = self.spec
        return self

    def __exit__(self, *exc):
        self.module.SWARM_WORKFLOWS.pop(self.name, None)
        return False


if __name__ == "__main__":
    unittest.main()
