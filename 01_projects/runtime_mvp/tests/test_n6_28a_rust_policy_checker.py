"""Tests for N+6.28A - Rust Runtime Policy Checker Prototype."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "rust" / "ghoti_policy_checker" / "Cargo.toml"
MAIN = REPO_ROOT / "rust" / "ghoti_policy_checker" / "src" / "main.rs"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_28A_RUST_POLICY_CHECKER.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_28a_rust_policy_checker.md"


def cargo_run(*args):
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(
        Path(tempfile.gettempdir()) / "ghoti_policy_checker_n6_28a_target"
    )
    completed = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--manifest-path",
            str(MANIFEST),
            "--",
            *args,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )
    return completed, json.loads(completed.stdout)


def run_plan(plan):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        return cargo_run("--input", str(path))


class FilesAndDocsTests(unittest.TestCase):
    def test_required_files_exist(self):
        for path in [MANIFEST, MAIN, DOC, REPORT]:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")

    def test_docs_preserve_prototype_boundary(self):
        body = DOC.read_text(encoding="utf-8").lower()
        self.assertIn("dry-run", body)
        self.assertIn("does not launch agents", body)
        self.assertIn("n+6.27a is not merged", body)
        self.assertIn("python launcher", body)

    def test_report_verdict(self):
        self.assertIn("READY_TO_PUSH", REPORT.read_text(encoding="utf-8"))


class PolicyCheckerCliTests(unittest.TestCase):
    def test_check_is_default_deny(self):
        completed, data = cargo_run("--check")
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertTrue(data["ok"])
        self.assertFalse(data["allowed"])
        self.assertEqual(data["decision"], "deny")
        self.assertTrue(data["safety"]["default_deny"])
        self.assertFalse(data["safety"]["launches_agents"])

    def test_safe_dry_run_plan_is_allowed(self):
        completed, data = run_plan(
            {
                "plan_id": "safe-dry-run",
                "dry_run": True,
                "live_launch": False,
                "requires_human_approval": True,
                "capabilities": ["repo_read", "plan_render", "status_read"],
            }
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertTrue(data["allowed"])
        self.assertEqual(data["decision"], "allow")
        self.assertEqual(data["reasons"], [])

    def test_live_launch_is_denied(self):
        completed, data = run_plan(
            {
                "plan_id": "unsafe-live",
                "dry_run": True,
                "live_launch": True,
                "requires_human_approval": True,
                "capabilities": ["repo_read"],
            }
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertFalse(data["allowed"])
        self.assertIn("live_launch_requested", data["reasons"])

    def test_blocked_capabilities_are_denied(self):
        blocked = [
            "browser",
            "computer_use",
            "mcp",
            "account",
            "money",
            "mass_message",
            "secrets",
        ]
        for capability in blocked:
            with self.subTest(capability=capability):
                completed, data = run_plan(
                    {
                        "plan_id": f"blocked-{capability}",
                        "dry_run": True,
                        "live_launch": False,
                        "requires_human_approval": True,
                        "capabilities": [capability],
                    }
                )
                self.assertEqual(completed.returncode, 0, msg=completed.stderr)
                self.assertFalse(data["allowed"])
                self.assertIn(capability, data["blocked_capabilities"])

    def test_unknown_capability_and_missing_approval_are_denied(self):
        completed, data = run_plan(
            {
                "plan_id": "unknown-no-approval",
                "dry_run": True,
                "live_launch": False,
                "requires_human_approval": False,
                "capabilities": ["future_magic"],
            }
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertFalse(data["allowed"])
        self.assertIn("human_approval_not_required_by_plan", data["reasons"])
        self.assertEqual(data["unknown_capabilities"], ["future_magic"])


class SourceSafetyTests(unittest.TestCase):
    def test_source_has_no_live_execution_surface(self):
        source = MAIN.read_text(encoding="utf-8").lower()
        for forbidden in [
            "std::process::command",
            "subprocess",
            "shell=true",
            "invoke-expression",
            "reqwest",
            "tokio",
            "browser launch",
            "agent launch",
        ]:
            self.assertNotIn(forbidden, source)

    def test_no_swarm_launcher_files_added(self):
        self.assertFalse((REPO_ROOT / "03_scripts" / "swarm_launcher").exists())


if __name__ == "__main__":
    unittest.main()
