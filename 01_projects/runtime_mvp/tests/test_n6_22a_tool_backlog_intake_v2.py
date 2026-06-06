"""Tests for N+6.22A - Tool Backlog Intake v2 + Repo Memory Vault v1.

Static, planning-only milestone. These tests assert (1) every file exists, (2) the
memory vault structure is present with the no-sensitive-data rule, (3) the inventory
JSON is valid and every tool carries the required fields, a known category, and a known
safety gate, with source_url null whenever source_needed is true, (4) the priority map
has Tier 1 / Tier 2 / blocked sections and the safety matrix names the three gates, (5)
the docs are static-intake-only and the Rust lane defers Rust, and (6) no secret, token,
chat-id, video-downloader token, or bot-bypass phrase is committed. Flagged literals are
assembled at runtime so this test file never contains them.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

MEMORY = REPO_ROOT / "14_context" / "memory_vault"
VAULT_README = MEMORY / "README.md"
VAULT_INDEX = MEMORY / "INDEX.md"
VAULT_GITKEEPS = [
    MEMORY / "lists" / ".gitkeep",
    MEMORY / "preferences" / ".gitkeep",
    MEMORY / "tool_backlog" / ".gitkeep",
    MEMORY / "project_notes" / ".gitkeep",
]
VAULT_CHECKLIST = MEMORY / "templates" / "checklist.md"
VAULT_TOOLNOTE = MEMORY / "templates" / "tool_note.md"
VAULT_DOC = REPO_ROOT / "docs" / "GHOTI_REPO_MEMORY_VAULT.md"

TI = REPO_ROOT / "14_context" / "tool_intake"
INV_MD = TI / "tool_backlog_inventory_n6_22a.md"
INV_JSON = TI / "tool_backlog_inventory_n6_22a.json"
PRIORITY = TI / "tool_priority_map_n6_22a.md"
SAFETY = TI / "tool_safety_gate_matrix_n6_22a.md"
PAPERCLIP = TI / "paperclip_tier1_intake_n6_22a.md"
AWESOME = TI / "awesome_llm_apps_tier1_intake_n6_22a.md"
CODEGRAPH = TI / "code_graph_lane_n6_22a.md"
MONEY = TI / "money_automation_lane_n6_22a.md"
PROVIDER = TI / "model_provider_lane_n6_22a.md"
RUST = TI / "rust_runtime_lane_n6_22a.md"

MAIN_DOC = REPO_ROOT / "docs" / "GHOTI_N6_22A_TOOL_BACKLOG_INTAKE_V2.md"
HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_TOOL_INTAKE_V2_TASK.md")
REPORT = REPO_ROOT / "14_context" / "claude_n6_22a_tool_backlog_intake_v2.md"

ALL_FILES = [
    VAULT_README, VAULT_INDEX, VAULT_CHECKLIST, VAULT_TOOLNOTE, VAULT_DOC,
    INV_MD, INV_JSON, PRIORITY, SAFETY, PAPERCLIP, AWESOME, CODEGRAPH, MONEY,
    PROVIDER, RUST, MAIN_DOC, HANDOFF, REPORT,
] + VAULT_GITKEEPS

TEXT_FILES = [
    VAULT_README, VAULT_INDEX, VAULT_CHECKLIST, VAULT_TOOLNOTE, VAULT_DOC,
    INV_MD, INV_JSON, PRIORITY, SAFETY, PAPERCLIP, AWESOME, CODEGRAPH, MONEY,
    PROVIDER, RUST, MAIN_DOC, HANDOFF, REPORT,
]

CATEGORIES = {
    "coding_brain_code_graph", "agent_skills_swarms", "automation_money",
    "documents_content", "apps_products", "apis_model_routing",
}
REQUIRED_FIELDS = ["name", "slug", "tier", "category", "source_url",
                   "source_confidence", "source_needed", "safety_gate"]
GATES = {"tier1_static_inspect", "tier2_later", "blocked_careful"}

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class MemoryVaultTests(unittest.TestCase):
    def test_structure(self):
        self.assertTrue(VAULT_README.is_file())
        self.assertTrue(VAULT_INDEX.is_file())
        for gk in VAULT_GITKEEPS:
            self.assertTrue(gk.is_file(), msg=f"missing {gk}")
        self.assertTrue(VAULT_CHECKLIST.is_file())
        self.assertTrue(VAULT_TOOLNOTE.is_file())

    def test_no_sensitive_data_rule(self):
        body = norm(read(VAULT_README))
        self.assertIn("no secrets", body)
        self.assertIn("sensitive personal data", body)


class InventoryJsonTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(read(INV_JSON))

    def test_static_only_flags(self):
        self.assertTrue(self.data["static_intake_only"])
        self.assertTrue(self.data["no_install"])
        self.assertTrue(self.data["no_execution"])

    def test_tools_have_required_fields(self):
        tools = self.data["tools"]
        self.assertGreaterEqual(len(tools), 25)
        for tool in tools:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, tool, msg=f"{tool.get('name')} missing {field}")
            self.assertIn(tool["category"], CATEGORIES, msg=tool.get("name"))
            self.assertIn(tool["safety_gate"], GATES, msg=tool.get("name"))
            if tool["source_needed"]:
                self.assertIsNone(tool["source_url"], msg=f"{tool['name']} source_needed but has url")

    def test_tier1_items_present(self):
        names = " ".join(t["name"] for t in self.data["tools"]).lower()
        for needed in ["awesome-llm-apps", "ruflo", "paperclip", "markitdown",
                       "tesseract", "n8n", "firecrawl"]:
            self.assertIn(needed, names, msg=f"missing Tier 1 item {needed}")

    def test_some_source_needed(self):
        self.assertTrue(any(t["source_needed"] for t in self.data["tools"]))


class PriorityAndSafetyTests(unittest.TestCase):
    def test_priority_sections(self):
        body = read(PRIORITY).lower()
        self.assertIn("tier 1", body)
        self.assertIn("tier 2", body)
        self.assertIn("blocked", body)

    def test_safety_gates_named(self):
        body = read(SAFETY)
        for gate in GATES:
            self.assertIn(gate, body)


class DocsContentTests(unittest.TestCase):
    def test_main_doc_static_only(self):
        self.assertIn("static intake and planning only", norm(read(MAIN_DOC)))

    def test_rust_lane_defers_rust(self):
        body = norm(read(RUST))
        self.assertIn("do not introduce rust now", body)
        self.assertIn("rust is not needed", body)

    def test_report_exists(self):
        self.assertTrue(REPORT.is_file())


class SecretAndFlaggedTokenTests(unittest.TestCase):
    def test_no_token_or_chat_id(self):
        for path in TEXT_FILES:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9]{20,}")
        self.assertNotRegex(combined, r"-----BEGIN [A-Z ]+-----")

    def test_no_video_downloader_token(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotIn("yt" + "-" + "dlp", combined)
        self.assertNotIn("youtube" + "-" + "dl", combined)

    def test_json_has_no_bot_bypass_phrases(self):
        body = read(INV_JSON).lower()
        for phrase in ["captcha" + " bypass", "bot detection" + " bypass",
                       "cloak browser" + " bypass", "anti-bot" + " bypass"]:
            self.assertNotIn(phrase, body)


class NoLocalPathLeakTests(unittest.TestCase):
    """Regression: committed N+6.22A docs must carry no real local path / username.

    The forbidden tokens are assembled at runtime so this test file never contains them
    literally (and therefore never trips the leak scan itself).
    """

    def test_no_real_local_path_leak(self):
        bslash = chr(92)
        forbidden = [
            "ai" + "_sandbox",
            "Nav" + "if",
            "C:" + bslash + "Users" + bslash,
            "C:" + "/Users/",
            "/mnt/" + "c/Users/",
            "Documents" + bslash + "AI_Managed_Only",
        ]
        for path in TEXT_FILES:
            text = read(path)
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"local path/username leak in {path.name}")


if __name__ == "__main__":
    unittest.main()
