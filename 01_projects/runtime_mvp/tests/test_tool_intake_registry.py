"""Tests for the tool intake registry (14_context/tool_intake/tool_registry.json).

Proves the registry is well-formed and safe: unique ids, valid enums, required
fields, reject items carry a reason, P0 items have an owner + next_action, and no
secret-looking values or private absolute paths leaked in.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "14_context" / "tool_intake" / "tool_registry.json"

PRIORITIES = {"P0", "P1", "P2", "defer", "reject"}
CATEGORIES = {"repo", "mcp", "skill", "business", "local_model", "automation",
              "design", "security", "memory", "analytics", "content", "cad",
              "infrastructure"}
OWNERS = {"claude_code", "codex", "hermes", "chatgpt", "local_model", "human"}
IMPL = {"inspect_first", "install_adapt", "mcp_connector", "prompt_only",
        "obsidian_memory", "business_research", "future_paid_api", "reject"}
RISK = {"low", "medium", "high", "blocked"}
STATUS = {"candidate", "needs_source", "intake_ready", "inspected", "adopt",
          "defer", "reject"}
REQUIRED = ("id", "name", "category", "priority", "owner", "implementation_type",
            "risk_level", "value", "source_needed", "status", "next_action", "notes")
SECRET_MARKERS = ("api_key=", "apikey=", "password=", "secret=", "sk-ant-",
                  "ghp_", "AKIA", "-----begin")


class TestRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.tools = cls.data["tools"]

    def test_loads_and_nonempty(self):
        self.assertGreaterEqual(len(self.tools), 20)

    def test_ids_unique(self):
        ids = [t["id"] for t in self.tools]
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids")

    def test_required_fields_and_enums(self):
        for t in self.tools:
            for field in REQUIRED:
                self.assertIn(field, t, "%s missing %s" % (t.get("id"), field))
            self.assertIn(t["priority"], PRIORITIES, t["id"])
            self.assertIn(t["category"], CATEGORIES, t["id"])
            self.assertIn(t["owner"], OWNERS, t["id"])
            self.assertIn(t["implementation_type"], IMPL, t["id"])
            self.assertIn(t["risk_level"], RISK, t["id"])
            self.assertIn(t["status"], STATUS, t["id"])
            self.assertIsInstance(t["source_needed"], bool)

    def test_reject_items_have_reason(self):
        for t in self.tools:
            if t["priority"] == "reject":
                self.assertEqual(t["implementation_type"], "reject", t["id"])
                self.assertEqual(t["risk_level"], "blocked", t["id"])
                self.assertIn("reason", t["notes"].lower(),
                              "reject item %s must state a reason in notes" % t["id"])

    def test_p0_items_have_owner_and_next_action(self):
        p0 = [t for t in self.tools if t["priority"] == "P0"]
        self.assertGreaterEqual(len(p0), 5)
        for t in p0:
            self.assertIn(t["owner"], OWNERS, t["id"])
            self.assertTrue(t["next_action"].strip(), "%s needs next_action" % t["id"])

    def test_has_each_priority_tier(self):
        present = {t["priority"] for t in self.tools}
        for tier in ("P0", "P1", "P2", "reject"):
            self.assertIn(tier, present, "missing tier %s" % tier)

    def test_no_secrets_or_private_paths(self):
        blob = REGISTRY.read_text(encoding="utf-8").lower()
        for marker in SECRET_MARKERS:
            self.assertNotIn(marker, blob, marker)
        self.assertNotIn("c:\\users\\", blob)
        self.assertNotIn("c:/users/", blob)


if __name__ == "__main__":
    unittest.main()
