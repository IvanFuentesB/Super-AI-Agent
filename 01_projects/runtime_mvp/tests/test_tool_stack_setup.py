"""Tests for the Ghoti acceleration tool stack CLI and templates.

Proves the safe posture: status/check return JSON, install-safe dry-run does not
modify the system, MCP templates are all disabled and secret-free, repo intake
dry-run does not clone or execute, and the required docs exist.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_STACK = REPO_ROOT / "03_scripts" / "tool_stack"
CLI = TOOL_STACK / "ghoti_tool_stack.py"
TEMPLATE_DIR = REPO_ROOT / "14_context" / "mcp_connectors" / "config_templates"
SKILLS_REGISTRY = REPO_ROOT / "14_context" / "tool_stack" / "skills_registry.json"

SECRET_MARKERS = ("api_key=", "apikey=", "authorization: bearer", "password=",
                  "secret=", "sk-ant-", "ghp_", "AKIA", "-----begin")
PRIVATE_PATHS = ("c:\\users\\", "c:/users/")


def run_cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(CLI), *args, "--json"],
                          capture_output=True, text=True, cwd=str(REPO_ROOT),
                          timeout=120, shell=False)
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError("no JSON for %s:\n%s\n%s" % (args, proc.stdout[:400], proc.stderr[:400]))


class TestCli(unittest.TestCase):
    def test_status_returns_json(self):
        code, payload = run_cli("--status")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        for key in ("installed_safe_tools", "mcp_templates_ready", "skills_registered",
                    "registry_total", "priority_counts", "blocked_rejected_count"):
            self.assertIn(key, payload)
        self.assertFalse(payload["safety"]["secrets_in_repo"])
        self.assertFalse(payload["safety"]["live_account_actions"])
        self.assertTrue(payload["safety"]["all_mcp_templates_disabled"])

    def test_check_returns_json(self):
        code, payload = run_cli("--check")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertIn("tools", payload)
        self.assertFalse(payload["safety"]["installs_performed"])

    def test_install_safe_dry_run_does_not_modify_system(self):
        code, payload = run_cli("--install-safe", "--dry-run")
        self.assertEqual(code, 0)
        self.assertFalse(payload["system_modified"])
        self.assertFalse(payload["safety"]["installs_performed"])
        self.assertFalse(payload["safety"]["unknown_repos_executed"])

    def test_repo_intake_dry_run_does_not_clone_or_execute(self):
        code, payload = run_cli("--repo-intake", "https://github.com/example/repo", "--dry-run")
        self.assertEqual(code, 0)
        self.assertFalse(payload["cloned"])
        self.assertFalse(payload["executed_anything"])

    def test_repo_intake_rejects_bad_target(self):
        from importlib import util
        spec = util.spec_from_file_location("repo_intake", TOOL_STACK / "repo_intake.py")
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # a local path is not a valid clone target
        result = mod.intake("/etc/passwd", apply=False)
        self.assertFalse(result["ok"])


class TestMcpTemplates(unittest.TestCase):
    def test_templates_exist_and_all_disabled(self):
        templates = sorted(TEMPLATE_DIR.glob("*.template.json"))
        self.assertGreaterEqual(len(templates), 10)
        for t in templates:
            data = json.loads(t.read_text(encoding="utf-8"))
            self.assertFalse(data["enabled"], "%s must be disabled" % t.name)
            self.assertTrue(data["manual_setup_required"], t.name)
            for key in ("name", "purpose", "required_env_vars", "allowed_capabilities",
                        "blocked_capabilities", "safety_notes", "test_command"):
                self.assertIn(key, data, "%s missing %s" % (t.name, key))

    def test_templates_have_no_secrets(self):
        for t in TEMPLATE_DIR.glob("*.template.json"):
            low = t.read_text(encoding="utf-8").lower()
            for marker in SECRET_MARKERS:
                self.assertNotIn(marker, low, "%s in %s" % (marker, t.name))
            for p in PRIVATE_PATHS:
                self.assertNotIn(p, low, "%s in %s" % (p, t.name))


class TestSkillsRegistry(unittest.TestCase):
    def test_registry_loads_and_has_agents(self):
        data = json.loads(SKILLS_REGISTRY.read_text(encoding="utf-8"))
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["agent_count"], 4)
        self.assertGreater(data["skill_count"], 0)
        self.assertFalse(data["safety"]["writes_user_global_skills"])
        for agent, items in data["agents"].items():
            for item in items:
                self.assertIn("manual_required", item)
                self.assertIn("next_action", item)
                self.assertFalse(item["enabled"])


RUST_GUARD_CANDIDATES = [
    REPO_ROOT / "rust" / "target" / "release" / "tool_stack_guard.exe",
    REPO_ROOT / "rust" / "target" / "release" / "tool_stack_guard",
    REPO_ROOT / "rust" / "target" / "debug" / "tool_stack_guard.exe",
    REPO_ROOT / "rust" / "target" / "debug" / "tool_stack_guard",
]


def _rust_binary():
    return next((c for c in RUST_GUARD_CANDIDATES if c.is_file()), None)


class TestRustGuardIntegration(unittest.TestCase):
    def test_check_reports_rust_guard_status(self):
        code, payload = run_cli("--check")
        self.assertEqual(code, 0)
        self.assertIn("rust_tool_stack_guard", payload)
        self.assertIn(payload["rust_tool_stack_guard"], ("available", "missing", "failed"))

    def test_status_reports_rust_guard_status(self):
        _, payload = run_cli("--status")
        self.assertIn("rust_tool_stack_guard", payload)

    def test_rust_guard_validates_real_registry(self):
        binary = _rust_binary()
        if binary is None:
            self.skipTest("tool_stack_guard not built")
        proc = subprocess.run([str(binary), "--check", "--json"],
                              capture_output=True, text=True, cwd=str(REPO_ROOT),
                              timeout=60, shell=False)
        report = json.loads(proc.stdout)
        self.assertTrue(report["ok"], report.get("findings"))
        self.assertEqual(report["blocker_count"], 0)
        self.assertIn("registry", report["fingerprints"])

    def test_rust_guard_fails_closed_on_malformed(self):
        binary = _rust_binary()
        if binary is None:
            self.skipTest("tool_stack_guard not built")
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{ this is not valid json ", encoding="utf-8")
            proc = subprocess.run([str(binary), "--registry", str(bad), "--json"],
                                  capture_output=True, text=True, timeout=60, shell=False)
            self.assertNotEqual(proc.returncode, 0, "must fail closed")
            report = json.loads(proc.stdout)
            self.assertFalse(report["ok"])
            self.assertTrue(report.get("fail_closed"))

    def test_rust_guard_detects_duplicate_and_secret(self):
        binary = _rust_binary()
        if binary is None:
            self.skipTest("tool_stack_guard not built")
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "reg.json"
            tool = {"id": "dup", "name": "T", "category": "repo", "priority": "P1",
                    "owner": "human", "implementation_type": "inspect_first",
                    "risk_level": "low", "value": "v", "source_needed": True,
                    "status": "candidate", "next_action": "x",
                    "notes": "token ghp_abcdef123456"}
            reg.write_text(json.dumps({"tools": [tool, dict(tool)]}), encoding="utf-8")
            proc = subprocess.run([str(binary), "--registry", str(reg), "--json"],
                                  capture_output=True, text=True, timeout=60, shell=False)
            report = json.loads(proc.stdout)
            self.assertFalse(report["ok"])
            codes = {f["code"] for f in report["findings"]}
            self.assertIn("duplicate_id", codes)
            self.assertIn("secret_like_value", codes)


class TestDocsExist(unittest.TestCase):
    def test_required_docs_present(self):
        for rel in ("docs/GHOTI_MCP_SETUP_GUIDE.md",
                    "docs/GHOTI_AGENT_SKILLS_SETUP.md",
                    "docs/GHOTI_REPO_INTAKE_SAFETY.md",
                    "03_scripts/tool_stack/README.md"):
            self.assertTrue((REPO_ROOT / rel).is_file(), "missing %s" % rel)


if __name__ == "__main__":
    unittest.main()
