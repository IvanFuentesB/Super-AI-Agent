"""Integration contract for the command center and Rust Agent OS guard."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_OS_DIR = REPO_ROOT / "03_scripts" / "agent_os"
AGENT_OS = AGENT_OS_DIR / "ghoti_agent_os.py"
BRIDGE = AGENT_OS_DIR / "agent_os_guard_bridge.py"
DATA_WRITER = AGENT_OS_DIR / "data_only_writer.py"
README = REPO_ROOT / "14_context" / "agent_os" / "README.md"


def load_agent_os():
    sys.path.insert(0, str(AGENT_OS_DIR))
    spec = importlib.util.spec_from_file_location("ghoti_agent_os_integrated", AGENT_OS)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestGuardIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent_os = load_agent_os()

    def test_status_exposes_default_deny_guard_truth(self):
        status = self.agent_os.cmd_status()
        guard = status["agent_os_guard"]
        self.assertTrue(guard["available"])
        self.assertTrue(guard["safe_suggestion_allowed"])
        self.assertTrue(guard["dangerous_capability_denied"])
        self.assertTrue(guard["default_deny"])
        self.assertFalse(guard["live_execution"])
        self.assertFalse(guard["approved_local_execution_enabled"])
        self.assertNotIn("approval_token", json.dumps(guard))

    def test_guard_check_records_prove_allow_and_deny_paths(self):
        import agent_os_guard_bridge

        checks = {
            check["name"]: check
            for check in agent_os_guard_bridge.guard_check_records()
        }
        self.assertTrue(checks["agent_os_guard_allows_safe_suggestion"]["ok"])
        self.assertTrue(checks["agent_os_guard_denies_browser_capability"]["ok"])

    def test_command_center_worker_stays_suggestion_only(self):
        status = self.agent_os.cmd_status()
        self.assertEqual(status["worker"]["mode"], "suggestion_only")
        self.assertFalse(status["agent_os_guard"]["approved_local_execution_enabled"])
        self.assertTrue(status["safety_flags"]["no_live_actions"])

    def test_guard_status_cli_returns_json(self):
        result = subprocess.run(
            [sys.executable, str(AGENT_OS), "--guard-status", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "guard-status")
        self.assertTrue(payload["available"])
        self.assertFalse(payload["live_execution"])


class TestIntegrationHygiene(unittest.TestCase):
    def test_bridge_exists_and_has_no_live_execution_surface(self):
        self.assertTrue(BRIDGE.is_file())
        source = BRIDGE.read_text(encoding="utf-8").lower()
        for forbidden in (
            "shell=true",
            "pyautogui",
            "selenium",
            "playwright",
            "pynput",
            "os.system",
            "invoke-expression",
            "approval_token=",
        ):
            self.assertNotIn(forbidden, source)

    def test_combined_readme_documents_both_contracts(self):
        text = README.read_text(encoding="utf-8").lower()
        for phrase in (
            "integrated command center",
            "rust guard",
            "suggestion-only",
            "deny-by-default",
            "never execute",
            "raw approval values are never copied",
        ):
            self.assertIn(phrase, text)

    def test_command_center_uses_fixed_data_only_write_fallback(self):
        self.assertTrue(DATA_WRITER.is_file())
        source = DATA_WRITER.read_text(encoding="utf-8").lower()
        self.assertIn('["node", "-e", _node_write_script', source)
        for forbidden in (
            "shell=true",
            "os.system",
            "invoke-expression",
            "eval(",
            "exec(",
            "process.argv[3]",
        ):
            self.assertNotIn(forbidden, source)

        import local_worker

        result = local_worker._write_text(
            local_worker.RUNS_DIR / "integration_write_probe.json",
            '{"probe": true}\n',
        )
        self.assertTrue(result["written"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
