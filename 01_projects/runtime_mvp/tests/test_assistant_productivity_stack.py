"""Safety and completeness tests for the assistant productivity stack."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_ROOT = REPO_ROOT / "23_configs"
PRODUCTIVITY = CONFIG_ROOT / "assistant_productivity"
MCP = CONFIG_ROOT / "mcp"
SKILLS = CONFIG_ROOT / "skills"

CONFIGS = [
    PRODUCTIVITY / "codex_productivity.example.json",
    PRODUCTIVITY / "hermes_productivity.example.json",
    PRODUCTIVITY / "claude_code_productivity.example.json",
    PRODUCTIVITY / "chatgpt_cowork_productivity.example.json",
    PRODUCTIVITY / "routines.example.json",
    PRODUCTIVITY / "ruflo_productivity.example.json",
    SKILLS / "claude_code_skills.example.json",
    MCP / "codex_mcp_strategy.example.json",
    MCP / "hermes_mcp_strategy.example.json",
    MCP / "chatgpt_cowork_connectors.example.json",
]
DOCS = [
    "docs/GHOTI_CODEX_PRODUCTIVITY_SETUP.md",
    "docs/GHOTI_HERMES_PRODUCTIVITY_SETUP.md",
    "docs/GHOTI_CLAUDE_CODE_PRODUCTIVITY_SETUP.md",
    "docs/GHOTI_CLAUDE_CODE_STATUSLINE_SETUP.md",
    "docs/GHOTI_CHATGPT_COWORK_PRODUCTIVITY_SETUP.md",
    "docs/GHOTI_ASSISTANT_ROUTINES_AND_AUTOMATIONS.md",
    "docs/GHOTI_CODEX_HERMES_MCP_STRATEGY.md",
    "docs/GHOTI_RUFLO_PRODUCTIVITY_SETUP.md",
]
SECRET_MARKERS = (
    "api_key=",
    "apikey=",
    "authorization: bearer",
    "password=",
    "secret=",
    "sk-ant-",
    "ghp_",
    "-----begin",
)
PRIVATE_PATHS = ("c:\\users\\", "c:/users/", "/mnt/c/users/")


class TestProductivityConfigs(unittest.TestCase):
    def test_all_expected_json_loads(self):
        self.assertEqual(len(CONFIGS), 10)
        for path in CONFIGS:
            self.assertTrue(path.is_file(), path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("schema", data, path)
            self.assertFalse(data.get("live_actions", False), path)

    def test_routines_are_prompt_only_and_disabled(self):
        data = json.loads((PRODUCTIVITY / "routines.example.json").read_text(encoding="utf-8"))
        self.assertFalse(data["scheduler_enabled"])
        for routine in data["routines"]:
            self.assertFalse(routine["enabled"], routine["id"])
            self.assertFalse(routine["live_actions"], routine["id"])
            self.assertEqual(routine["mode"], "prompt_only", routine["id"])

    def test_credentialed_connectors_disabled(self):
        for path in (
            PRODUCTIVITY / "chatgpt_cowork_productivity.example.json",
            MCP / "chatgpt_cowork_connectors.example.json",
        ):
            data = json.loads(path.read_text(encoding="utf-8"))
            connectors = data.get("connectors", data.get("current_operator_reported_connectors", []))
            for connector in connectors:
                if connector.get("credentialed"):
                    self.assertFalse(connector["enabled"], connector["id"])

    def test_ruflo_pack_stays_planning_only(self):
        data = json.loads((PRODUCTIVITY / "ruflo_productivity.example.json").read_text(encoding="utf-8"))
        self.assertFalse(data["enabled"])
        self.assertTrue(data["syntax_uncertain"])
        self.assertIn("open_ended_swarm", data["blocked_use"])
        self.assertIn("live_agent_launch", data["blocked_use"])

    def test_chatgpt_pack_has_artifact_plan(self):
        data = json.loads((PRODUCTIVITY / "chatgpt_cowork_productivity.example.json").read_text(encoding="utf-8"))
        self.assertIn("morning_dashboard", data["artifacts"])
        self.assertIn("ghoti_command_dashboard", data["artifacts"])
        self.assertIn("github", data["desired_future_connectors"])
        self.assertIn("notion", data["desired_future_connectors"])

    def test_docs_exist(self):
        for relative in DOCS:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_no_secrets_or_private_paths_in_productivity_files(self):
        paths = CONFIGS + [REPO_ROOT / relative for relative in DOCS]
        paths += list((REPO_ROOT / "14_context" / "assistant_productivity").glob("*.md"))
        for path in paths:
            text = path.read_text(encoding="utf-8").lower()
            for marker in SECRET_MARKERS:
                self.assertNotIn(marker, text, f"{marker} in {path}")
            for marker in PRIVATE_PATHS:
                self.assertNotIn(marker, text, f"{marker} in {path}")

    def test_rust_guard_is_available(self):
        workspace = (REPO_ROOT / "rust" / "Cargo.toml").read_text(encoding="utf-8")
        self.assertIn('"assistant_productivity_guard"', workspace)
        self.assertTrue((REPO_ROOT / "rust" / "assistant_productivity_guard" / "src" / "main.rs").is_file())


if __name__ == "__main__":
    unittest.main()
