"""Contracts for the second deterministic Agent OS worker and runner hardening."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "03_scripts" / "agent_os"
RUST_MANIFEST = REPO_ROOT / "rust" / "Cargo.toml"
LOCAL_MODEL_WORKER = SCRIPT_DIR / "local_model_summary_classification_worker.py"
RUNNER = SCRIPT_DIR / "sandboxed_local_agent_runner.py"
CLI = SCRIPT_DIR / "ghoti_agent_os.py"
SERVER = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
EXPECTED_REGISTRY_FINGERPRINT = (
    "13e24b9f2aa491b79517f612ae92f35766d548a2e3881685beeccbe245c09f3a"
)

sys.path.insert(0, str(SCRIPT_DIR))


class RustGuardMixin:
    @classmethod
    def setUpClass(cls):
        cargo = shutil.which("cargo")
        if not cargo:
            raise unittest.SkipTest("cargo is required for Agent OS guard tests")
        cls.target_dir = Path(tempfile.gettempdir()) / "ghoti_two_worker_guard_tests"
        env = os.environ.copy()
        env["CARGO_TARGET_DIR"] = str(cls.target_dir)
        subprocess.run(
            [
                cargo,
                "build",
                "--quiet",
                "--manifest-path",
                str(RUST_MANIFEST),
                "--bin",
                "agent_os_guard",
            ],
            cwd=REPO_ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
        cls.binary = cls.target_dir / "debug" / (
            "agent_os_guard.exe" if os.name == "nt" else "agent_os_guard"
        )

    def guard(self, request: dict) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            request_path = Path(temp_dir) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            result = subprocess.run(
                [
                    str(self.binary),
                    "validate",
                    "--request",
                    str(request_path),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)


class TestTwoWorkerRegistry(RustGuardMixin, unittest.TestCase):
    def test_registry_contains_exactly_two_fixed_workers_and_stable_fingerprint(self):
        import sandboxed_local_agent_runner as runner

        self.assertEqual(
            set(runner.WORKER_REGISTRY),
            {
                "repo-summary-worker",
                "local-model-summary-classification-worker",
            },
        )
        self.assertEqual(runner.WORKER_REGISTRY_FINGERPRINT, EXPECTED_REGISTRY_FINGERPRINT)
        for specification in runner.WORKER_REGISTRY.values():
            self.assertEqual(specification["fixed_args"], ("--json",))
            self.assertTrue(specification["entrypoint"].is_file())

    def test_rust_guard_requires_known_worker_and_registry_fingerprint(self):
        from approval_queue import build_local_worker_request

        request = build_local_worker_request(
            workflow_id="local-model-summary-classification",
            created_at="2026-06-14T10:00:00Z",
        )
        self.assertEqual(
            request["payload"]["worker_id"],
            "local-model-summary-classification-worker",
        )
        self.assertEqual(request["payload"]["task"], "summary_classification")
        self.assertEqual(
            request["payload"]["worker_registry_fingerprint"],
            EXPECTED_REGISTRY_FINGERPRINT,
        )
        self.assertTrue(self.guard(request)["allow"])

        invalid = copy.deepcopy(request)
        invalid["payload"]["worker_registry_fingerprint"] = "wrong"
        denied = self.guard(invalid)
        self.assertFalse(denied["allow"])
        self.assertIn("worker_registry_fingerprint_invalid", denied["reasons"])

    def test_guard_denies_path_escape_and_forbidden_capability_for_model_worker(self):
        from approval_queue import build_local_worker_request

        request = build_local_worker_request(
            workflow_id="local-model-summary-classification",
            created_at="2026-06-14T10:00:00Z",
        )
        request["input_paths"] = ["../private.txt"]
        escaped = self.guard(request)
        self.assertFalse(escaped["allow"])
        self.assertIn("invalid_input_path", escaped["reasons"])

        request = build_local_worker_request(
            workflow_id="local-model-summary-classification",
            created_at="2026-06-14T10:00:01Z",
        )
        request["requested_capabilities"].append("browser")
        forbidden = self.guard(request)
        self.assertFalse(forbidden["allow"])
        self.assertIn("blocked_capability", forbidden["reasons"])


class TestLocalModelWorkerLifecycle(RustGuardMixin, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp.name) / "repo"
        source = (
            self.repo_root
            / "14_context"
            / "compact_memory"
            / "current_working_summary.md"
        )
        source.parent.mkdir(parents=True)
        source.write_text(
            "# Current truth\n\n"
            "Rust guard and approval queue are active. Browser and accounts remain blocked.\n",
            encoding="utf-8",
        )
        self.queue_root = self.repo_root / "14_context" / "agent_os" / "approval_queue"

    def tearDown(self):
        self.temp.cleanup()

    def _run(self, workflow_id: str, *, task: str | None = None) -> dict:
        from approval_queue import ApprovalQueue, build_local_worker_request

        queue = ApprovalQueue(
            repo_root=self.repo_root,
            queue_root=self.queue_root,
            guard_binary=self.binary,
        )
        request = build_local_worker_request(
            workflow_id=workflow_id,
            task=task,
            created_at="2026-06-14T10:00:00Z",
        )
        proposed = queue.propose(request)
        self.assertTrue(proposed["ok"], proposed)
        approved = queue.approve(proposed["request_id"])
        self.assertTrue(approved["ok"], approved)
        return queue.execute(proposed["request_id"])

    def test_local_model_worker_runs_safe_fallback_and_writes_structured_artifact(self):
        result = self._run("local-model-summary-classification")
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["worker_id"], "local-model-summary-classification-worker")
        self.assertEqual(result["processes_launched"], 1)
        self.assertFalse(result["network_used"])
        self.assertFalse(result["provider_api_used"])
        self.assertEqual(result["model_mode"], "deterministic_local_fallback")

        artifact = (self.repo_root / result["artifact_path"]).read_text(encoding="utf-8")
        for heading in (
            "## Summary",
            "## Classification tags",
            "## Source pointers",
            "## Confidence and uncertainty",
            "## Next suggested handoff target",
        ):
            self.assertIn(heading, artifact)
        run_record = json.loads(
            (self.repo_root / result["run_record_path"]).read_text(encoding="utf-8")
        )
        metadata = run_record["worker_result_metadata"]
        self.assertTrue(metadata["classification_tags"])
        self.assertIn(metadata["next_handoff_target"], {"Claude", "Codex", "Hermes", "Human"})
        self.assertEqual(metadata["model_mode"], "deterministic_local_fallback")

    def test_oversized_worker_output_fails_closed_and_logs_are_capped(self):
        import sandboxed_local_agent_runner as runner

        result = self._run("coding-task", task="bounded_log_probe")
        self.assertFalse(result["ok"], result)
        self.assertEqual(result["reason"], "worker_output_too_large")
        run_record = json.loads(
            (self.repo_root / result["run_record_path"]).read_text(encoding="utf-8")
        )
        self.assertTrue(run_record["stdout_log"]["truncated"])
        self.assertLessEqual(
            run_record["stdout_log"]["captured_bytes"],
            runner.MAX_CAPTURE_BYTES,
        )
        self.assertLessEqual(
            run_record["stderr_log"]["captured_bytes"],
            runner.MAX_CAPTURE_BYTES,
        )


class TestTwoWorkerIntegration(unittest.TestCase):
    def test_local_model_worker_has_no_process_network_or_provider_surface(self):
        self.assertTrue(LOCAL_MODEL_WORKER.is_file())
        source = LOCAL_MODEL_WORKER.read_text(encoding="utf-8").lower()
        for forbidden in (
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "httpx",
            "playwright",
            "selenium",
            "pyautogui",
            "api_key",
        ):
            self.assertNotIn(forbidden, source)

    def test_cli_dashboard_docs_and_no_duplicate_systems(self):
        cli = CLI.read_text(encoding="utf-8")
        server = SERVER.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertIn("--full-local-model-worker-demo", cli)
        self.assertIn("/api/product-control/agent-os-full-local-model-worker-demo", server)
        self.assertIn("Latest local-model summary/classification", index)
        self.assertIn("latest_local_model_state", app)
        for relative in (
            "docs/GHOTI_SANDBOXED_LOCAL_AGENT_RUNNER.md",
            "docs/GHOTI_LOCAL_MODEL_WORKER.md",
            "docs/GHOTI_CURRENT_PRODUCT_STATUS.md",
            "docs/GHOTI_ROADMAP_TO_FULL_COMPUTER_USE.md",
        ):
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)
        for duplicate in (
            "03_scripts/context_memory",
            "03_scripts/agent_command_center",
            "14_context/memory",
        ):
            self.assertFalse((REPO_ROOT / duplicate).exists(), duplicate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
