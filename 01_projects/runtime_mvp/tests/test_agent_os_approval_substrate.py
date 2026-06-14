"""Contracts for the supervised Agent OS approved-execution substrate."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUST_MANIFEST = REPO_ROOT / "rust" / "Cargo.toml"
SCRIPT_DIR = REPO_ROOT / "03_scripts" / "agent_os"
CONTRACT = (
    REPO_ROOT
    / "14_context"
    / "agent_os"
    / "contracts"
    / "action_request.schema.example.json"
)
APPROVED_EXECUTOR = SCRIPT_DIR / "approved_executor.py"
DOC = REPO_ROOT / "docs" / "GHOTI_APPROVED_EXECUTION_SUBSTRATE.md"
AGENT_OS_CLI = SCRIPT_DIR / "ghoti_agent_os.py"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"

sys.path.insert(0, str(SCRIPT_DIR))


def _request(**overrides):
    request = {
        "schema": "ghoti_action_request/1",
        "request_id": "req-test-001",
        "created_at": "2026-06-13T12:00:00Z",
        "created_by": "agent-os-worker",
        "workflow_id": "coding-task",
        "action_id": "write_workflow_plan",
        "mode": "suggestion",
        "approval_state": "pending",
        "requested_capabilities": [
            "agent_os.read_memory",
            "agent_os.write_repo_local",
        ],
        "input_paths": ["14_context/compact_memory/current_working_summary.md"],
        "output_paths": [
            "14_context/agent_os/workflows/approved_req-test-001.md",
            "14_context/agent_os/runs/approved_req-test-001.json",
        ],
        "owned_files": [
            "14_context/agent_os/workflows/approved_req-test-001.md",
            "14_context/agent_os/runs/approved_req-test-001.json",
        ],
        "locked_paths": [],
        "max_runtime_seconds": 30,
        "approval_token_hash": None,
        "summary": "Write one bounded local workflow plan.",
        "risk_note": "Text artifact only; no shell, network, browser, or account action.",
        "payload": {
            "kind": "write_text_artifact",
            "artifact_path": "14_context/agent_os/workflows/approved_req-test-001.md",
            "title": "Approved workflow plan",
            "content": "# Approved workflow plan\n\nLocal artifact only.\n",
        },
    }
    request.update(overrides)
    return request


class RustGuardMixin:
    @classmethod
    def setUpClass(cls):
        cargo = shutil.which("cargo")
        if not cargo:
            raise unittest.SkipTest("cargo is required for Agent OS guard tests")
        cls.target_dir = Path(tempfile.gettempdir()) / "ghoti_agent_os_approval_guard_tests"
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

    def guard(self, command: str, request: dict) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            request_path = Path(temp_dir) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            result = subprocess.run(
                [
                    str(self.binary),
                    command,
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


class TestApprovedActionRustGuard(RustGuardMixin, unittest.TestCase):
    def test_new_suggestion_contract_is_allowed_and_fingerprint_is_stable(self):
        first = self.guard("validate", _request())
        second = self.guard("validate", _request())
        fingerprint = self.guard("fingerprint", _request())
        self.assertTrue(first["allow"])
        self.assertEqual(first["schema"], "ghoti_guard_decision/1")
        self.assertEqual(first["request_id"], "req-test-001")
        self.assertEqual(first["request_fingerprint"], second["request_fingerprint"])
        self.assertEqual(first["request_fingerprint"], fingerprint["request_fingerprint"])
        self.assertFalse(first["approval_required"])
        self.assertFalse(first["safety"]["live_execution"])

    def test_approved_local_requires_valid_hash(self):
        denied = self.guard(
            "validate",
            _request(mode="approved_local", approval_state="approved"),
        )
        malformed = self.guard(
            "validate",
            _request(
                mode="approved_local",
                approval_state="approved",
                approval_token_hash="not-a-valid-hash",
            ),
        )
        allowed = self.guard(
            "validate",
            _request(
                mode="approved_local",
                approval_state="approved",
                approval_token_hash="a" * 64,
            ),
        )
        self.assertFalse(denied["allow"])
        self.assertIn("approval_required", denied["reasons"])
        self.assertFalse(malformed["allow"])
        self.assertIn("approval_token_hash_invalid", malformed["reasons"])
        self.assertTrue(allowed["allow"])
        self.assertTrue(allowed["approval_present"])
        self.assertNotIn("a" * 64, json.dumps(allowed))

    def test_forbidden_capability_paths_and_ownership_conflict_are_denied(self):
        dangerous = self.guard(
            "validate",
            _request(requested_capabilities=["agent_os.write_repo_local", "browser"]),
        )
        absolute = self.guard(
            "validate",
            _request(output_paths=["D:/outside.md"]),
        )
        escaped = self.guard(
            "validate",
            _request(output_paths=["../outside.md"]),
        )
        external = self.guard(
            "validate",
            _request(output_paths=["docs/outside.md"]),
        )
        conflict = self.guard(
            "validate",
            _request(locked_paths=["14_context/agent_os/workflows"]),
        )
        self.assertIn("blocked_capability", dangerous["reasons"])
        self.assertIn("invalid_output_path", absolute["reasons"])
        self.assertIn("invalid_output_path", escaped["reasons"])
        self.assertIn("invalid_output_path", external["reasons"])
        self.assertIn("locked_path_conflict", conflict["reasons"])
        self.assertGreater(len(conflict["ownership_conflicts"]), 0)


class TestApprovalQueueContracts(RustGuardMixin, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp.name) / "repo"
        self.repo_root.mkdir()
        self.queue_root = self.repo_root / "14_context" / "agent_os" / "approval_queue"

    def tearDown(self):
        self.temp.cleanup()

    def test_propose_approve_execute_writes_only_bounded_artifacts(self):
        from approval_queue import ApprovalQueue, build_action_request

        request = build_action_request(
            workflow_id="coding-task",
            action_id="write_workflow_plan",
            artifact_path="14_context/agent_os/workflows/test_plan.md",
            content="# Test plan\n",
            created_at="2026-06-13T12:00:00Z",
        )
        queue = ApprovalQueue(
            repo_root=self.repo_root,
            queue_root=self.queue_root,
            guard_binary=self.binary,
        )
        proposed = queue.propose(request)
        self.assertTrue(proposed["ok"])
        self.assertEqual(proposed["approval_state"], "pending")
        self.assertEqual(queue.status()["counts"]["pending"], 1)

        approved = queue.approve(proposed["request_id"])
        self.assertTrue(approved["ok"])
        self.assertEqual(approved["approval_state"], "approved")

        executed = queue.execute(proposed["request_id"])
        self.assertTrue(executed["ok"])
        self.assertEqual(executed["approval_state"], "executed")
        self.assertTrue((self.repo_root / "14_context/agent_os/workflows/test_plan.md").is_file())
        self.assertTrue((self.repo_root / executed["run_record_path"]).is_file())
        self.assertTrue((self.repo_root / executed["evidence_path"]).is_file())
        self.assertTrue((self.repo_root / executed["handoff_path"]).is_file())
        self.assertEqual(queue.status()["counts"]["executed"], 1)

    def test_reject_moves_request_and_denied_guard_never_queues(self):
        from approval_queue import ApprovalQueue, build_action_request

        queue = ApprovalQueue(
            repo_root=self.repo_root,
            queue_root=self.queue_root,
            guard_binary=self.binary,
        )
        request = build_action_request(
            workflow_id="coding-task",
            action_id="write_workflow_plan",
            artifact_path="14_context/agent_os/workflows/reject.md",
            content="# Reject fixture\n",
            created_at="2026-06-13T12:00:00Z",
        )
        proposed = queue.propose(request)
        rejected = queue.reject(proposed["request_id"], reason="human declined")
        self.assertTrue(rejected["ok"])
        self.assertEqual(rejected["approval_state"], "rejected")

        request["requested_capabilities"] = ["browser"]
        denied = queue.propose(request)
        self.assertFalse(denied["ok"])
        self.assertEqual(denied["approval_state"], "denied")
        self.assertEqual(queue.status()["counts"]["pending"], 0)


class TestApprovedExecutionHygiene(unittest.TestCase):
    def test_contract_docs_and_executor_exist(self):
        for path in (CONTRACT, APPROVED_EXECUTOR, DOC):
            self.assertTrue(path.is_file(), str(path.relative_to(REPO_ROOT)))

    def test_executor_has_no_shell_network_or_process_surface(self):
        source = APPROVED_EXECUTOR.read_text(encoding="utf-8").lower()
        for forbidden in (
            "subprocess",
            "shell=true",
            "os." + "system",
            "urllib",
            "requests",
            "socket",
            "playwright",
            "selenium",
            "pyautogui",
        ):
            self.assertNotIn(forbidden, source)

    def test_command_center_exposes_approval_commands(self):
        source = AGENT_OS_CLI.read_text(encoding="utf-8")
        for command in (
            "--propose-action",
            "--list-approvals",
            "--approve-action",
            "--reject-action",
            "--execute-approved",
            "--approval-status",
            "--full-approved-demo",
        ):
            self.assertIn(command, source)

    def test_full_approved_demo_cli_creates_evidence(self):
        result = subprocess.run(
            [sys.executable, str(AGENT_OS_CLI), "--full-approved-demo", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["approved_local_execution"])
        self.assertFalse(payload["live_execution"])
        self.assertTrue((REPO_ROOT / payload["evidence_path"]).is_file())
        self.assertTrue((REPO_ROOT / payload["artifact_path"]).is_file())

    def test_dashboard_exposes_bounded_approval_queue(self):
        server = SERVER_JS.read_text(encoding="utf-8")
        index = INDEX_HTML.read_text(encoding="utf-8")
        app = APP_JS.read_text(encoding="utf-8")
        for route in (
            "/api/product-control/agent-os-approvals",
            "/api/product-control/agent-os-propose-action",
            "/api/product-control/agent-os-approve-action",
            "/api/product-control/agent-os-reject-action",
            "/api/product-control/agent-os-execute-approved",
            "/api/product-control/agent-os-full-approved-demo",
        ):
            self.assertIn(route, server)
        for label in (
            "Approved Execution Queue",
            "Human approval required",
            "External/live execution remains blocked",
        ):
            self.assertIn(label, index)
        self.assertIn("function refreshAgentOsApprovals()", app)


if __name__ == "__main__":
    unittest.main(verbosity=2)
