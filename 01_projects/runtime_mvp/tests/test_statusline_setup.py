"""Honesty and safety tests for the Claude Code statusline intake."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "23_configs" / "assistant_productivity" / "claude_code_productivity.example.json"
DOC = REPO_ROOT / "docs" / "GHOTI_CLAUDE_CODE_STATUSLINE_SETUP.md"


class TestStatuslineSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.statusline = cls.data["statusline"]
        cls.doc = DOC.read_text(encoding="utf-8").lower()

    def test_verified_source_is_recorded(self):
        self.assertEqual(self.statusline["source_url"], "https://github.com/sirmalloc/ccstatusline")
        self.assertEqual(self.statusline["package"], "ccstatusline")
        self.assertEqual(self.statusline["pinned_version"], "2.2.21")
        self.assertEqual(self.statusline["license"], "MIT")
        self.assertTrue(self.statusline["source_revision_inspected"])

    def test_no_install_or_global_write_claim(self):
        self.assertFalse(self.statusline["installed"])
        self.assertTrue(self.statusline["manual_setup_required"])
        self.assertTrue(self.statusline["backup_required"])
        self.assertFalse(self.data["safety"]["global_config_write_allowed"])
        self.assertFalse(self.data["safety"]["hooks_enabled"])

    def test_credit_claim_is_honest(self):
        self.assertFalse(self.statusline["exact_credits_supported"])
        self.assertFalse(self.statusline["claims_exact_credits"])
        self.assertFalse(self.statusline["usage_api_enabled"])
        self.assertIn("cannot promise a", self.doc)
        self.assertIn("universal exact", self.doc)
        self.assertIn("session/weekly usage", self.doc)

    def test_optional_sensitive_signals_disabled(self):
        disabled = self.statusline["optional_sensitive_signals_disabled"]
        self.assertIn("claude_account_email", disabled)
        self.assertIn("usage_api", disabled)
        self.assertIn("extra_usage_remaining", disabled)


if __name__ == "__main__":
    unittest.main()
