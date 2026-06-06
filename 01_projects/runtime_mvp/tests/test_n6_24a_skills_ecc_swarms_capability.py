"""Tests for N+6.24A - Skills / ECC / Swarms Capability Upgrade + Swarm Repo Intake.

Static, planning-only milestone. These tests assert (1) every file exists, (2) the skills
docs actually explain skills vs agents vs commands vs hooks, Codex AGENTS.md vs skills,
Hermes skills/memory, and ECC = Everything Claude Code (not elliptic curve) with the
adapt-not-install rationale and the separate-profile test, (3) the swarm intake JSON is
valid, static-only, has the required swarm candidates and new backlog items, every row
carries the required fields, and source_url is null whenever source_needed is true (no
fabricated URLs), (4) the memory-palace lane is PAO/tier-1-last and gates device capture,
(5) the main doc and capability map carry the safe progression, and (6) no secret, token,
chat-id, video-downloader token, bot-bypass phrase, or real local path / username is
committed. Flagged literals are assembled at runtime so this file never contains them.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

SKILLS = REPO_ROOT / "14_context" / "skills"
MAP = SKILLS / "SKILLS_CAPABILITY_MAP_N6_24A.md"
CLAUDE_D = SKILLS / "CLAUDE_SKILLS_AND_AGENTS_N6_24A.md"
CODEX_D = SKILLS / "CODEX_AGENTS_AND_SKILLS_N6_24A.md"
HERMES_D = SKILLS / "HERMES_SKILLS_AND_MEMORY_N6_24A.md"
ECC_D = SKILLS / "ECC_EVERYTHING_CLAUDE_CODE_N6_24A.md"

TI = REPO_ROOT / "14_context" / "tool_intake"
SWARM_MD = TI / "swarm_launcher_repo_intake_n6_24a.md"
SWARM_JSON = TI / "swarm_launcher_repo_intake_n6_24a.json"
PALACE = TI / "memory_palace_pao_app_lane_n6_24a.md"

HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_SKILLS_SWARMS_TASK.md")
MAIN_DOC = REPO_ROOT / "docs" / "GHOTI_N6_24A_SKILLS_ECC_SWARMS_CAPABILITY.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_24a_skills_ecc_swarms_capability.md"

ALL_FILES = [MAP, CLAUDE_D, CODEX_D, HERMES_D, ECC_D, SWARM_MD, SWARM_JSON, PALACE,
             HANDOFF, MAIN_DOC, REPORT]
TEXT_FILES = ALL_FILES  # all are text (md/json)

PROGRESSION_STAGES = ["trace ingestion", "static repo intake", "controlled launcher",
                      "approved-window bridge", "supervised overnight loop"]

REQUIRED_FIELDS = ["name", "slug", "category", "source_url", "source_confidence",
                   "source_needed", "safety_gate", "notes"]

REQUIRED_NAMES = ["clawteam", "am-will/swarms", "multiswarm", "ecc", "subagent",
                  "codex skill", "cobalt", "pake", "ideogram", "panopticore",
                  "quant mind", "zero by vercel", "claude mem", "sentry search",
                  "aiengineer", "rag", "memory palace"]

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


class SkillsDocsTests(unittest.TestCase):
    def test_claude_doc_four_blocks(self):
        body = norm(read(CLAUDE_D))
        for word in ["skill", "agent", "command", "hook"]:
            self.assertIn(word, body, msg=f"Claude doc missing '{word}'")

    def test_codex_doc_agents_md_vs_skills(self):
        body = norm(read(CODEX_D))
        self.assertIn("agents.md", body)
        self.assertIn("skill", body)
        self.assertIn("agent-launching", body)

    def test_hermes_doc_skills_and_memory(self):
        body = norm(read(HERMES_D))
        self.assertIn("wrapper", body)
        self.assertIn("memory", body)

    def test_ecc_doc_meaning_and_rationale(self):
        body = norm(read(ECC_D))
        self.assertIn("everything claude code", body)
        self.assertIn("elliptic curve", body)  # explicitly disambiguated as NOT this
        self.assertIn("separate", body)
        self.assertTrue("adapt" in body or "install" in body)

    def test_capability_map_progression_and_blocks(self):
        body = norm(read(MAP))
        for stage in PROGRESSION_STAGES:
            self.assertIn(stage, body, msg=f"capability map missing stage '{stage}'")
        for word in ["skill", "agent", "command", "hook"]:
            self.assertIn(word, body)


class MainDocTests(unittest.TestCase):
    def test_main_doc_static_only_and_progression(self):
        body = norm(read(MAIN_DOC))
        self.assertIn("static intake and planning only", body)
        self.assertIn("everything claude code", body)
        self.assertIn("swarm", body)
        for stage in PROGRESSION_STAGES:
            self.assertIn(stage, body, msg=f"main doc missing stage '{stage}'")


class SwarmJsonTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(read(SWARM_JSON))
        self.rows = self.data["swarm_candidates"] + self.data["new_backlog_items"]

    def test_static_only_flags(self):
        for flag in ["static_intake_only", "no_install", "no_execution", "no_clone",
                     "no_live_agent_launch"]:
            self.assertTrue(self.data[flag], msg=f"flag {flag} must be true")

    def test_rows_have_required_fields(self):
        self.assertGreaterEqual(len(self.data["swarm_candidates"]), 6)
        self.assertGreaterEqual(len(self.data["new_backlog_items"]), 12)
        for row in self.rows:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, row, msg=f"{row.get('slug')} missing {field}")

    def test_no_fabricated_url_when_source_needed(self):
        for row in self.rows:
            if row["source_needed"]:
                self.assertIsNone(row["source_url"],
                                  msg=f"{row['slug']} source_needed but has url")

    def test_required_candidates_present(self):
        names = " ".join(r["name"] for r in self.rows).lower()
        for needed in REQUIRED_NAMES:
            self.assertIn(needed, names, msg=f"missing required item: {needed}")

    def test_memory_palace_item_is_tier_last(self):
        palace = [r for r in self.rows if r["slug"] == "memory_palace_pao_app"]
        self.assertEqual(len(palace), 1)
        self.assertEqual(palace[0]["tier"], "tier1_last")


class MemoryPalaceLaneTests(unittest.TestCase):
    def test_pao_and_gating(self):
        body = norm(read(PALACE))
        self.assertIn("pao", body)
        self.assertIn("memory palace", body)
        self.assertIn("lidar", body)
        self.assertIn("gated", body)
        self.assertTrue("tier-1-last" in body or "build last" in body)


class HandoffTests(unittest.TestCase):
    def test_handoff_points_to_controlled_launcher(self):
        body = norm(read(HANDOFF))
        self.assertIn("controlled launcher", body)
        self.assertIn("dry-run", body)


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
        body = read(SWARM_JSON).lower()
        for phrase in ["captcha" + " bypass", "bot detection" + " bypass",
                       "cloak browser" + " bypass", "anti-bot" + " bypass"]:
            self.assertNotIn(phrase, body)


class NoLocalPathLeakTests(unittest.TestCase):
    """Committed N+6.24A files must carry no real local path / username. Forbidden tokens
    are assembled at runtime so this file never contains them literally."""

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
