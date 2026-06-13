"""Contract tests for the Agent OS guard and suggestion-only local worker trial."""

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
GUARD_MANIFEST = REPO_ROOT / "rust" / "agent_os_guard" / "Cargo.toml"
HARNESS = REPO_ROOT / "03_scripts" / "agent_os" / "local_worker_trial.py"
CONTEXT_ROOT = REPO_ROOT / "14_context" / "agent_os"
DOC = REPO_ROOT / "docs" / "GHOTI_AGENT_OS_GUARD_AND_LOCAL_WORKER_TRIAL.md"
WORKFLOWS = {
    "coding-task-plan",
    "content-video-plan",
    "business-research-plan",
    "email-draft-plan",
    "automation-plan",
}
TEST_OUTPUT_ROOT = Path(tempfile.gettempdir()) / "ghoti_agent_os_tests"


def _test_output_dir():
    TEST_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=TEST_OUTPUT_ROOT)


def _request(**overrides):
    request = {
        "schema_version": "1.0",
        "action_id": "content-video-plan",
        "mode": "suggestion",
        "requested_capabilities": [
            "repo_read",
            "plan_render",
            "repo_write_trial",
            "run_record_write",
            "handoff_write",
        ],
        "input_paths": ["14_context/compact_memory/current_working_summary.md"],
        "output_paths": [
            "14_context/agent_os/trials/example_content_video_plan.md",
            "14_context/agent_os/runs/example_content_video_plan_run.json",
            "14_context/agent_os/handoffs/example_content_video_plan_handoff.md",
        ],
        "locked_paths": [],
        "max_runtime_seconds": 30,
        "approval_token": None,
    }
    request.update(overrides)
    return request


class TestRequiredFiles(unittest.TestCase):
    def test_required_files_exist(self):
        expected = [
            GUARD_MANIFEST,
            REPO_ROOT / "rust" / "agent_os_guard" / "src" / "main.rs",
            HARNESS,
            CONTEXT_ROOT / "README.md",
            CONTEXT_ROOT / "requests" / "example_worker_request.json",
            CONTEXT_ROOT / "trials" / "README.md",
            CONTEXT_ROOT / "runs" / "README.md",
            CONTEXT_ROOT / "handoffs" / "README.md",
            DOC,
        ]
        for path in expected:
            self.assertTrue(path.is_file(), msg=f"missing: {path.relative_to(REPO_ROOT)}")

    def test_guard_is_workspace_member(self):
        self.assertIn(
            '"agent_os_guard"',
            RUST_MANIFEST.read_text(encoding="utf-8"),
        )


class TestAgentOsGuardCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cargo = shutil.which("cargo")
        if not cargo:
            raise unittest.SkipTest("cargo is required for Agent OS guard tests")
        cls.target_dir = Path(tempfile.gettempdir()) / "ghoti_agent_os_guard_tests"
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

    def _decision(self, request):
        with tempfile.TemporaryDirectory() as temp_dir:
            request_path = Path(temp_dir) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            result = subprocess.run(
                [str(self.binary), "--request", str(request_path), "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        return json.loads(result.stdout)

    def test_safe_suggestion_is_allowed_deterministically(self):
        first = self._decision(_request())
        second = self._decision(_request())
        self.assertTrue(first["allow"])
        self.assertEqual(first["decision"], "allowed")
        self.assertEqual(first, second)
        self.assertFalse(first["approval_required"])
        self.assertFalse(first["approval_present"])
        self.assertTrue(first["safety"]["default_deny"])
        self.assertFalse(first["safety"]["network_used"])
        self.assertFalse(first["safety"]["writes_files"])
        self.assertFalse(first["safety"]["live_execution"])

    def test_unknown_action_is_denied(self):
        result = self._decision(_request(action_id="unknown-worker"))
        self.assertFalse(result["allow"])
        self.assertIn("unknown_action", result["reasons"])

    def test_dangerous_and_unknown_capabilities_are_denied(self):
        result = self._decision(
            _request(
                requested_capabilities=[
                    "repo_read",
                    "browser",
                    "account",
                    "payment",
                    "computer_use",
                    "future_magic",
                ]
            )
        )
        self.assertFalse(result["allow"])
        self.assertEqual(
            result["denied_capabilities"],
            ["account", "browser", "computer_use", "future_magic", "payment"],
        )

    def test_absolute_parent_and_external_output_paths_are_denied(self):
        for output_path in (
            "D:/outside.md",
            "../outside.md",
            "/tmp/outside.md",
            "docs/outside.md",
        ):
            with self.subTest(output_path=output_path):
                result = self._decision(_request(output_paths=[output_path]))
                self.assertFalse(result["allow"])
                self.assertIn("invalid_output_path", result["reasons"])

    def test_locked_path_overlap_is_denied(self):
        result = self._decision(
            _request(locked_paths=["14_context/agent_os/trials"])
        )
        self.assertFalse(result["allow"])
        self.assertIn("locked_path_conflict", result["reasons"])

    def test_approved_local_requires_approval(self):
        denied = self._decision(_request(mode="approved_local"))
        allowed = self._decision(
            _request(mode="approved_local", approval_token="human-approved")
        )
        self.assertFalse(denied["allow"])
        self.assertTrue(denied["approval_required"])
        self.assertIn("approval_required", denied["reasons"])
        self.assertTrue(allowed["allow"])
        self.assertTrue(allowed["approval_required"])
        self.assertTrue(allowed["approval_present"])
        self.assertNotIn("human-approved", json.dumps(allowed))


class TestLocalWorkerTrial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if HARNESS.parent.exists():
            sys.path.insert(0, str(HARNESS.parent))

    def _load_harness(self):
        import local_worker_trial  # noqa: PLC0415

        return local_worker_trial

    def test_harness_check_is_safe_and_lists_all_workflows(self):
        result = self._load_harness().run_check()
        self.assertTrue(result["ok"])
        self.assertEqual(set(result["workflows"]), WORKFLOWS)
        self.assertEqual(result["modes_executed"], ["simulation", "suggestion"])
        self.assertFalse(result["live_execution"])
        self.assertFalse(result["browser_enabled"])
        self.assertFalse(result["computer_use_enabled"])
        self.assertFalse(result["model_output_as_command"])

    def test_suggestion_writes_only_plan_run_and_handoff(self):
        with _test_output_dir() as temp_dir:
            result = self._load_harness().run_workflow(
                "content-video-plan",
                "suggestion",
                output_root=Path(temp_dir),
            )
            files = sorted(
                str(path.relative_to(temp_dir)).replace("\\", "/")
                for path in Path(temp_dir).rglob("*")
                if path.is_file()
            )
            self.assertEqual(
                files,
                [
                    "handoffs/content-video-plan_handoff.md",
                    "runs/content-video-plan_run.json",
                    "trials/content-video-plan.md",
                ],
            )
            self.assertTrue(result["ok"])
            self.assertTrue(result["guard_decision"]["allow"])
            self.assertFalse(result["live_execution"])
            self.assertTrue(result["suggestion_only"])

    def test_approved_local_is_never_executed_by_harness(self):
        with _test_output_dir() as temp_dir:
            result = self._load_harness().run_workflow(
                "coding-task-plan",
                "approved_local",
                output_root=Path(temp_dir),
                approval_token="present-but-not-executed",
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["worker_executed"])
            self.assertIn("approved_local_not_executed", result["reasons"])
            self.assertEqual(list(Path(temp_dir).rglob("*")), [])

    def test_guard_denial_writes_only_a_denied_run_record(self):
        with _test_output_dir() as temp_dir:
            result = self._load_harness().run_workflow(
                "automation-plan",
                "suggestion",
                output_root=Path(temp_dir),
                request_overrides={"requested_capabilities": ["browser"]},
            )
            files = [
                path.relative_to(temp_dir).as_posix()
                for path in Path(temp_dir).rglob("*")
                if path.is_file()
            ]
            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "denied")
            self.assertFalse(result["worker_executed"])
            self.assertEqual(files, ["runs/automation-plan_run.json"])
            record = json.loads((Path(temp_dir) / files[0]).read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "denied")
            self.assertFalse(record["live_execution"])

    def test_arbitrary_output_root_is_rejected(self):
        outside = Path(tempfile.gettempdir()) / "outside_agent_os_test_root"
        result = self._load_harness().run_workflow(
            "coding-task-plan",
            "suggestion",
            output_root=outside,
        )
        self.assertFalse(result["ok"])
        self.assertFalse(result["worker_executed"])
        self.assertIn("output_root_not_allowed", result["reasons"])

    def test_source_has_no_live_or_shell_execution_surface(self):
        source = HARNESS.read_text(encoding="utf-8").lower()
        forbidden = [
            "shell=true",
            "pyautogui",
            "selenium",
            "playwright",
            "pynput",
            "os.system",
            "invoke-expression",
        ]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_cli_example_trial_writes_repo_local_examples(self):
        result = subprocess.run(
            [
                sys.executable,
                str(HARNESS),
                "--workflow",
                "content-video-plan",
                "--mode",
                "suggestion",
                "--json",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["live_execution"])
        self.assertTrue((CONTEXT_ROOT / "trials" / "content-video-plan.md").is_file())
        self.assertTrue((CONTEXT_ROOT / "runs" / "content-video-plan_run.json").is_file())
        self.assertTrue(
            (CONTEXT_ROOT / "handoffs" / "content-video-plan_handoff.md").is_file()
        )


class TestPublicSafeContracts(unittest.TestCase):
    def test_contracts_are_public_safe(self):
        paths = [
            CONTEXT_ROOT / "README.md",
            CONTEXT_ROOT / "requests" / "example_worker_request.json",
            DOC,
        ]
        forbidden = ["C:\\Users\\", "C:/Users/", "/home/", "api_key", "password"]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"{token} found in {path.name}")

    def test_docs_state_suggestion_only_and_default_deny(self):
        text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "default-deny",
            "suggestion-only",
            "no browser",
            "no account",
            "model output",
        ):
            self.assertIn(phrase, text)

    def test_docs_explain_agent_os_integration_path(self):
        text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "claude",
            "codex",
            "hermes",
            "shared memory",
            "future swarms",
            "future computer-use",
            "command-center",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
