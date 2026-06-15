"""Focused tests for the Codex and Hermes productivity prompt packs."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PRODUCTIVITY = REPO_ROOT / "23_configs" / "assistant_productivity"
PROMPTS = REPO_ROOT / "14_context" / "assistant_productivity"


class TestCodexProductivity(unittest.TestCase):
    def test_codex_required_prompt_protocols_exist(self):
        text = (PROMPTS / "codex_ready_prompts.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "merge gate",
            "rust validator audit",
            "mcp audit",
            "repo-intake audit",
            "public repo safety audit",
            "token-saving audit",
            "parallel branch audit",
            "continue a claude code branch",
            "no-overlap implementation",
            "github pr review",
            "finish incomplete claude branch protocol",
        ):
            self.assertIn(phrase, text)

    def test_codex_skills_and_safety(self):
        data = json.loads((PRODUCTIVITY / "codex_productivity.example.json").read_text(encoding="utf-8"))
        for skill in (
            "karpathy-guidelines",
            "context-engineering",
            "verification-loop",
            "parallel-execution-optimizer",
            "codex-merge-gate",
            "safe-repo-intake",
            "token-saving-audit",
        ):
            self.assertIn(skill, data["available_skills"])
        self.assertFalse(data["safety"]["push_main"])
        self.assertTrue(data["safety"]["human_approval_required"])


class TestHermesProductivity(unittest.TestCase):
    def test_hermes_is_summary_only(self):
        data = json.loads((PRODUCTIVITY / "hermes_productivity.example.json").read_text(encoding="utf-8"))
        self.assertFalse(data["execution_enabled"])
        self.assertFalse(data["live_actions"])
        self.assertIn("command_execution", data["blocked_outputs"])
        self.assertIn("account_action", data["blocked_outputs"])

    def test_hermes_required_prompts_exist(self):
        text = (PROMPTS / "hermes_ready_prompts.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "daily ghoti control-room summary",
            "summarize claude code report",
            "summarize codex audit",
            "summarize mcp status",
            "summarize tool-stack status",
            "summarize ruflo status",
            "top five next actions",
            "create handoff and detect conflicts",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
