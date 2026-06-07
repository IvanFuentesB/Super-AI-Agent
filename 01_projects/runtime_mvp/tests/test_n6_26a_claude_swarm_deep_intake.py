"""Tests for N+6.26A - Claude Swarm / Agent-Team / ClawTeam / am-will-swarms Deep Intake.

Static research/planning milestone. These tests assert (1) every file exists, (2) the
surfaces JSON is static-only, lists the official and community swarm surfaces with the
required fields and no fabricated URL when source_needed, (3) the docs distinguish
Claude-side vs Ghoti-side, correct '/batch' to '/bg', describe agent teams / dynamic
workflows / ClawTeam / am-will-swarms, give a safe separate-profile test order, and a
future Ghoti controlled-launcher path, (4) ECC = Everything Claude Code is disambiguated
from elliptic curve cryptography, and (5) no secret, token, chat-id, video-downloader
token, bot-bypass phrase, or real local path / username is committed. Flagged literals are
assembled at runtime so this file never contains them.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

TI = REPO_ROOT / "14_context" / "tool_intake"
SURFACES_JSON = TI / "claude_swarm_surfaces_n6_26a.json"
SURFACES_MD = TI / "claude_swarm_surfaces_n6_26a.md"
OFFICIAL_MD = TI / "official_claude_agent_teams_n6_26a.md"
CLAWTEAM_MD = TI / "clawteam_deep_intake_n6_26a.md"
AMWILL_MD = TI / "am_will_swarms_deep_intake_n6_26a.md"
ECC_MD = TI / "ecc_claude_swarm_profile_n6_26a.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_26A_CLAUDE_SWARM_DEEP_INTAKE.md"
HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_CLAUDE_SWARM_TASK.md")
REPORT = REPO_ROOT / "14_context" / "claude_n6_26a_claude_swarm_deep_intake.md"

ALL_FILES = [SURFACES_JSON, SURFACES_MD, OFFICIAL_MD, CLAWTEAM_MD, AMWILL_MD, ECC_MD,
             DOC, HANDOFF, REPORT]
TEXT_FILES = ALL_FILES

REQUIRED_FIELDS = ["surface", "can_launch_real_agents", "ghoti_default_status",
                   "test_in_separate_profile", "source_url", "source_confidence",
                   "source_needed", "notes"]

REQUIRED_OFFICIAL = ["subagents", "agent view", "agent teams", "dynamic workflows",
                     "batch", "skills", "hooks", "worktrees"]
REQUIRED_COMMUNITY = ["ecc", "clawteam", "am-will/swarms", "claude-swarm", "kyegomez"]

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


class SurfacesJsonTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(read(SURFACES_JSON))
        self.rows = self.data["official_claude_surfaces"] + self.data["community_surfaces"]

    def test_static_only_flags(self):
        for flag in ["static_intake_only", "no_install", "no_clone", "no_execution",
                     "no_live_agent_launch", "no_agent_teams_enabled",
                     "no_dynamic_workflows_enabled", "no_hooks_enabled"]:
            self.assertTrue(self.data[flag], msg=f"flag {flag} must be true")

    def test_rows_have_required_fields(self):
        self.assertGreaterEqual(len(self.data["official_claude_surfaces"]), 7)
        self.assertGreaterEqual(len(self.data["community_surfaces"]), 4)
        for row in self.rows:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, row, msg=f"{row.get('surface')} missing {field}")

    def test_no_fabricated_url_when_source_needed(self):
        for row in self.rows:
            if row["source_needed"]:
                self.assertIsNone(row["source_url"],
                                  msg=f"{row['surface']} source_needed but has url")

    def test_required_official_surfaces(self):
        names = " ".join(r["surface"] for r in self.data["official_claude_surfaces"]).lower()
        for needed in REQUIRED_OFFICIAL:
            self.assertIn(needed, names, msg=f"missing official surface: {needed}")

    def test_required_community_surfaces(self):
        names = " ".join(r.get("repo", "") + " " + r["surface"]
                         for r in self.data["community_surfaces"]).lower()
        for needed in REQUIRED_COMMUNITY:
            self.assertIn(needed, names, msg=f"missing community surface: {needed}")


class DocsContentTests(unittest.TestCase):
    def test_surfaces_md_sides_and_tokens(self):
        body = norm(read(SURFACES_MD))
        self.assertIn("claude-side", body)
        self.assertIn("ghoti-side", body)
        self.assertIn("what costs more tokens", body)
        self.assertIn("/bg", body)

    def test_official_md_features(self):
        body = norm(read(OFFICIAL_MD))
        self.assertIn("agent teams", body)
        self.assertIn("dynamic workflows", body)
        self.assertIn("/bg", body)
        self.assertIn("experimental_agent_teams", body)

    def test_batch_correction(self):
        body = norm(read(DOC))
        self.assertIn("/batch", body)
        self.assertIn("/bg", body)

    def test_clawteam_doc(self):
        body = norm(read(CLAWTEAM_MD))
        self.assertIn("hkuds/clawteam", body)
        self.assertIn("should_stay_disabled", body)

    def test_amwill_doc_distinct_from_kyegomez(self):
        body = norm(read(AMWILL_MD))
        self.assertIn("am-will/swarms", body)
        self.assertIn("kyegomez/swarms", body)
        self.assertIn("parallel-task", body)

    def test_ecc_profile_test_order(self):
        body = norm(read(ECC_MD))
        self.assertIn("separate", body)
        self.assertIn("safe test order", body)
        self.assertIn("everything claude code", body)
        self.assertIn("elliptic curve", body)

    def test_main_doc_sections(self):
        body = norm(read(DOC))
        self.assertIn("official claude swarm summary", body)
        self.assertIn("community swarm repo summary", body)
        self.assertIn("safe test order", body)
        self.assertIn("future path for the ghoti controlled launcher", body)
        self.assertIn("everything claude code", body)

    def test_handoff_controlled_launcher(self):
        body = norm(read(HANDOFF))
        self.assertIn("controlled launcher", body)
        self.assertIn("dry-run", body)

    def test_report_verdict(self):
        self.assertIn("IMPLEMENTED_AND_PUSHED", read(REPORT))


class EccDisambiguationTests(unittest.TestCase):
    def test_ecc_not_elliptic_in_key_docs(self):
        for path in [ECC_MD, DOC, SURFACES_MD]:
            body = norm(read(path))
            self.assertIn("everything claude code", body, msg=f"{path.name}")
            self.assertIn("elliptic curve", body, msg=f"{path.name}")


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
        body = read(SURFACES_JSON).lower()
        for phrase in ["captcha" + " bypass", "bot detection" + " bypass",
                       "cloak browser" + " bypass", "anti-bot" + " bypass"]:
            self.assertNotIn(phrase, body)


class NoLocalPathLeakTests(unittest.TestCase):
    """Committed N+6.26A files must carry no real local path / username. Forbidden tokens
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
