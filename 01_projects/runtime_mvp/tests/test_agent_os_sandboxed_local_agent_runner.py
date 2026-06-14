"""Contracts for the first supervised sandboxed local agent process."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUST_MANIFEST = REPO_ROOT / "rust" / "Cargo.toml"
SCRIPT_DIR = REPO_ROOT / "03_scripts" / "agent_os"
AGENT_OS_CLI = SCRIPT_DIR / "ghoti_agent_os.py"
RUNNER = SCRIPT_DIR / "sandboxed_local_agent_runner.py"
WORKER = SCRIPT_DIR / "repo_summary_worker.py"
DOC = REPO_ROOT / "docs" / "GHOTI_SANDBOXED_LOCAL_AGENT_RUNNER.md"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"

sys.path.insert(0, str(SCRIPT_DIR))


class RustGuardMixin:
    @classmethod
    def setUpClass(cls):
        cargo = shutil.which("cargo")
        if not cargo:
            raise unittest.SkipTest("cargo is required for Agent OS guard tests")
        cls.target_dir = Path(tempfile.gettempdir()) / "ghoti_sandboxed_runner_guard_tests"
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


class TestSandboxedRunnerRustGuard(RustGuardMixin, unittest.TestCase):
    def test_guard_allows_only_fixed_worker_contract(self):
        from approval_queue import build_local_worker_request

        request = build_local_worker_request(
            workflow_id="coding-task",
            created_at="2026-06-13T14:00:00Z",
        )
        decision = self.guard(request)
        self.assertTrue(decision["allow"], decision)
        self.assertTrue(decision["safety"]["launches_processes"])
        self.assertTrue(decision["safety"]["allowlisted_local_process"])
        self.assertFalse(decision["safety"]["live_execution"])

        request["payload"]["worker_id"] = "arbitrary-worker"
        denied = self.guard(request)
        self.assertFalse(denied["allow"])
        self.assertIn("worker_not_allowlisted", denied["reasons"])

    def test_guard_denies_dynamic_commands_and_unbounded_worker_runtime(self):
        from approval_queue import build_local_worker_request

        request = build_local_worker_request(
            workflow_id="coding-task",
            created_at="2026-06-13T14:00:00Z",
        )
        request["payload"]["command"] = "whoami"
        dynamic = self.guard(request)
        self.assertFalse(dynamic["allow"])
        self.assertIn("dynamic_process_surface_denied", dynamic["reasons"])

        request["payload"].pop("command")
        request["max_runtime_seconds"] = 31
        unbounded = self.guard(request)
        self.assertFalse(unbounded["allow"])
        self.assertIn("worker_runtime_limit_invalid", unbounded["reasons"])


class TestSandboxedRunnerLifecycle(RustGuardMixin, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp.name) / "repo"
        input_file = (
            self.repo_root
            / "14_context"
            / "compact_memory"
            / "current_working_summary.md"
        )
        input_file.parent.mkdir(parents=True)
        input_file.write_text("# Current truth\n\nLocal supervised Agent OS.\n", encoding="utf-8")
        self.queue_root = self.repo_root / "14_context" / "agent_os" / "approval_queue"

    def tearDown(self):
        self.temp.cleanup()

    def approved_request(self, **kwargs) -> dict:
        from approval_queue import build_local_worker_request

        created_at = kwargs.pop("created_at", "2026-06-13T14:00:00Z")
        request = build_local_worker_request(
            workflow_id="coding-task",
            created_at=created_at,
            **kwargs,
        )
        request["mode"] = "approved_local"
        request["approval_state"] = "approved"
        request["approval_token_hash"] = "a" * 64
        return request

    def test_queue_runs_exactly_one_allowlisted_worker_and_writes_evidence(self):
        from approval_queue import ApprovalQueue, build_local_worker_request

        queue = ApprovalQueue(
            repo_root=self.repo_root,
            queue_root=self.queue_root,
            guard_binary=self.binary,
        )
        request = build_local_worker_request(
            workflow_id="coding-task",
            created_at="2026-06-13T14:00:00Z",
        )
        proposed = queue.propose(request)
        approved = queue.approve(proposed["request_id"])
        executed = queue.execute(proposed["request_id"])

        self.assertTrue(proposed["ok"])
        self.assertTrue(approved["ok"])
        self.assertTrue(executed["ok"], executed)
        self.assertEqual(executed["worker_id"], "repo-summary-worker")
        self.assertEqual(executed["processes_launched"], 1)
        self.assertTrue(executed["local_agent_process_executed"])
        self.assertFalse(executed["live_execution"])
        for key in ("artifact_path", "run_record_path", "evidence_path", "handoff_path"):
            self.assertTrue((self.repo_root / executed[key]).is_file(), key)
        run_record = json.loads(
            (self.repo_root / executed["run_record_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(run_record["exit_reason"], "completed")
        self.assertEqual(run_record["processes_launched"], 1)
        self.assertEqual(
            run_record["request_fingerprint"],
            executed["guard_decision"]["request_fingerprint"],
        )
        self.assertFalse(run_record["network_used"])
        self.assertFalse(run_record["model_output_as_command"])

    def test_runner_requires_positive_rust_decision_and_allows_only_one_active_worker(self):
        from sandboxed_local_agent_runner import execute_allowlisted_worker_request

        first = self.approved_request(
            task="bounded_wait_probe",
            wait_seconds=2,
            max_runtime_seconds=5,
        )
        refused = execute_allowlisted_worker_request(first, self.repo_root, guard_decision={})
        self.assertFalse(refused["ok"])
        self.assertEqual(refused["reason"], "runner_request_refused")

        results: list[dict] = []
        first_guard = self.guard(first)
        thread = threading.Thread(
            target=lambda: results.append(
                execute_allowlisted_worker_request(
                    first, self.repo_root, guard_decision=first_guard
                )
            )
        )
        thread.start()
        active_path = (
            self.repo_root / "14_context" / "agent_os" / "runner_control" / "active_worker.json"
        )
        deadline = time.monotonic() + 5
        while not active_path.is_file() and time.monotonic() < deadline:
            time.sleep(0.05)

        second = self.approved_request(
            task="repo_status_summary",
            created_at="2026-06-13T14:00:01Z",
        )
        blocked = execute_allowlisted_worker_request(
            second, self.repo_root, guard_decision=self.guard(second)
        )
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["reason"], "another_worker_is_active")
        thread.join(timeout=10)
        self.assertFalse(thread.is_alive())

    def test_runner_terminates_timed_out_worker_and_records_failure(self):
        from sandboxed_local_agent_runner import execute_allowlisted_worker_request

        request = self.approved_request(
            task="bounded_wait_probe",
            wait_seconds=2,
            max_runtime_seconds=1,
        )
        result = execute_allowlisted_worker_request(
            request, self.repo_root, guard_decision=self.guard(request)
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "worker_timeout")
        self.assertTrue(result["process_terminated"])
        self.assertEqual(result["processes_launched"], 1)
        run_record = json.loads(
            (self.repo_root / result["run_record_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(run_record["exit_reason"], "timed_out")

    def test_cancel_path_terminates_running_worker(self):
        from sandboxed_local_agent_runner import (
            cancel_worker,
            execute_allowlisted_worker_request,
        )

        request = self.approved_request(
            task="bounded_wait_probe",
            wait_seconds=3,
            max_runtime_seconds=5,
        )
        guard_decision = self.guard(request)
        results: list[dict] = []
        thread = threading.Thread(
            target=lambda: results.append(
                execute_allowlisted_worker_request(
                    request, self.repo_root, guard_decision=guard_decision
                )
            )
        )
        thread.start()
        active_path = (
            self.repo_root / "14_context" / "agent_os" / "runner_control" / "active_worker.json"
        )
        deadline = time.monotonic() + 5
        while not active_path.is_file() and time.monotonic() < deadline:
            time.sleep(0.05)
        cancellation = cancel_worker(request["request_id"], self.repo_root)
        thread.join(timeout=10)

        self.assertTrue(cancellation["ok"])
        self.assertFalse(thread.is_alive())
        self.assertEqual(results[0]["reason"], "worker_cancelled")
        self.assertTrue(results[0]["process_terminated"])


class TestSandboxedRunnerIntegration(unittest.TestCase):
    def test_runner_worker_docs_and_cli_exist(self):
        for path in (RUNNER, WORKER, DOC):
            self.assertTrue(path.is_file(), str(path.relative_to(REPO_ROOT)))
        cli = AGENT_OS_CLI.read_text(encoding="utf-8")
        for command in (
            "--propose-worker-run",
            "--runner-status",
            "--cancel-worker",
            "--full-worker-demo",
        ):
            self.assertIn(command, cli)

    def test_runner_has_one_fixed_process_surface_and_worker_has_none(self):
        runner = RUNNER.read_text(encoding="utf-8")
        worker = WORKER.read_text(encoding="utf-8").lower()
        self.assertIn('"repo-summary-worker"', runner)
        self.assertIn("subprocess.Popen", runner)
        self.assertIn("shell=False", runner)
        self.assertNotIn('payload.get("command")', runner)
        self.assertNotIn('payload.get("args")', runner)
        for forbidden in (
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "playwright",
            "selenium",
            "pyautogui",
            "os.system",
        ):
            self.assertNotIn(forbidden, worker)

    def test_existing_dashboard_exposes_runner_without_duplicate_dashboard(self):
        server = SERVER_JS.read_text(encoding="utf-8")
        index = INDEX_HTML.read_text(encoding="utf-8")
        app = APP_JS.read_text(encoding="utf-8")
        for route in (
            "/api/product-control/agent-os-runner-status",
            "/api/product-control/agent-os-propose-worker-run",
            "/api/product-control/agent-os-cancel-worker",
            "/api/product-control/agent-os-full-worker-demo",
        ):
            self.assertIn(route, server)
        for label in (
            "Sandboxed Local Agent Runner",
            "One allowlisted local worker",
            "No model-output-to-command",
        ):
            self.assertIn(label, index)
        self.assertIn("function refreshAgentOsRunner()", app)


if __name__ == "__main__":
    unittest.main(verbosity=2)
