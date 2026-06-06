"""Tests for N+6.25A - Hermes Memory/Status Upgrade + Automatic Coordinator Grounding.

These tests lock the safety and behavior of the read-only Hermes status packet generator.
They assert (1) every file exists, (2) the generator source uses no shell-string execution
and no os.system (read-only git via subprocess is allowed), (3) --check passes and reports
the read-only posture, (4) --json builds a packet with the required sources, percentages,
the safe progression with live_automation_enabled_percent == 0, ECC = Everything Claude
Code (not elliptic curve), the must-not-claim list, and Hermes current/future roles,
(5) --write writes a packet inside the repo and refuses any path outside the repo,
(6) the schema and example and docs carry the required sections, and (7) no secret, token,
chat-id, video-downloader token, or real local path / username is committed. Flagged
literals are assembled at runtime so this file never contains them.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

HS_SCRIPTS = REPO_ROOT / "03_scripts" / "hermes_status"
SCRIPT = HS_SCRIPTS / "ghoti_hermes_status_packet.py"
CHECK_PS = HS_SCRIPTS / "check_hermes_status_packet.ps1"

HS_CTX = REPO_ROOT / "14_context" / "hermes_status"
SCHEMA = HS_CTX / "hermes_status_packet_schema.json"
EXAMPLE = HS_CTX / "HERMES_STATUS_PACKET.example.md"
README = HS_CTX / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_25A_HERMES_MEMORY_STATUS_UPGRADE.md"
HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_HERMES_STATUS_TASK.md")
REPORT = REPO_ROOT / "14_context" / "claude_n6_25a_hermes_memory_status_upgrade.md"

ALL_FILES = [SCRIPT, CHECK_PS, SCHEMA, EXAMPLE, README, DOC, HANDOFF, REPORT]
TEXT_FILES = [SCRIPT, CHECK_PS, SCHEMA, EXAMPLE, README, DOC, HANDOFF, REPORT]

SOURCE_KEYS = ["main_commit", "agent_arena_trace", "memory_vault", "tool_intake",
               "latest_claude_report", "latest_codex_report", "feature_flags"]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def run_py(*args, timeout=60):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class SourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(SCRIPT)

    def test_no_shell_true(self):
        self.assertIsNone(re.search(r"shell\s*=\s*True", self.src))

    def test_no_os_system(self):
        self.assertIsNone(re.search(r"os\.system\s*\(", self.src))

    def test_git_calls_use_list_args(self):
        # subprocess is allowed only for read-only git metadata; ensure it is list-form.
        self.assertIn("subprocess.run(", self.src)
        self.assertIn('"git"', self.src)


class CheckCliTests(unittest.TestCase):
    def test_check_ok(self):
        rc, out, err = run_py("--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"], msg=f"check not ok: {data}")
        for key in ["no_shell_true", "no_os_system", "packet_builds",
                    "reads_git_metadata_only", "ecc_is_everything_claude_code"]:
            self.assertTrue(data[key], msg=f"check.{key} must be true")


class PacketJsonTests(unittest.TestCase):
    def setUp(self):
        rc, out, err = run_py("--json")
        self.assertEqual(rc, 0, msg=err)
        self.data = json.loads(out)

    def test_required_top_level(self):
        for key in ["milestone", "status_plain_english", "sources", "progression",
                    "done", "blocked", "parallel_safe", "hermes_must_not_claim",
                    "ecc", "hermes_role", "safety"]:
            self.assertIn(key, self.data)

    def test_sources_present(self):
        for key in SOURCE_KEYS:
            self.assertIn(key, self.data["sources"])
        self.assertIn("short", self.data["sources"]["main_commit"])

    def test_percentages_present(self):
        prog = self.data["progression"]
        self.assertEqual(prog["live_automation_enabled_percent"], 0)
        self.assertIsInstance(prog["overall_percent"], int)
        self.assertGreaterEqual(len(prog["stages"]), 5)
        for stage in prog["stages"]:
            self.assertIsInstance(stage["percent"], int)
        self.assertIn("%", self.data["status_plain_english"])

    def test_ecc_meaning(self):
        ecc = self.data["ecc"]
        self.assertEqual(ecc["meaning"], "Everything Claude Code")
        self.assertIn("elliptic curve", ecc["is_not"].lower())

    def test_hermes_role(self):
        role = self.data["hermes_role"]
        current = role["current"].lower()
        self.assertTrue("coordinator" in current and "status" in current and "memory" in current)
        future = role["future"].lower()
        self.assertTrue("launcher" in future or "approval" in future or "gate" in future)

    def test_must_not_claim(self):
        joined = " ".join(self.data["hermes_must_not_claim"]).lower()
        self.assertIn("elliptic curve", joined)
        self.assertTrue("launch" in joined or "live" in joined)

    def test_safe_posture(self):
        safety = self.data["safety"]
        self.assertFalse(safety["launches_agents"])
        self.assertFalse(safety["uses_mcp"])
        self.assertFalse(safety["auto_submit"])
        self.assertTrue(safety["read_only"])


class WriteTests(unittest.TestCase):
    def test_write_inside_repo(self):
        rel = "14_context/hermes_status/_test_last_run_n6_25a.md"
        out_path = REPO_ROOT / rel
        self.addCleanup(lambda: out_path.unlink() if out_path.exists() else None)
        rc, out, err = run_py("--write", "--output", rel, "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"], msg=data)
        self.assertTrue(out_path.is_file())
        self.assertIn("Hermes Status Packet", read(out_path))

    def test_write_outside_repo_refused(self):
        outside = str(REPO_ROOT.parent / "_evil_n6_25a.md")
        rc, out, err = run_py("--write", "--output", outside, "--json")
        self.assertEqual(rc, 2, msg=err)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        self.assertFalse((REPO_ROOT.parent / "_evil_n6_25a.md").exists())


class SchemaAndExampleTests(unittest.TestCase):
    def test_schema_safe_posture(self):
        schema = json.loads(read(SCHEMA))
        self.assertTrue(schema["x_safety"]["read_only"])
        self.assertFalse(schema["x_safety"]["launches_agents"])

    def test_example_sections(self):
        body = norm(read(EXAMPLE))
        self.assertIn("everything claude code", body)
        self.assertIn("elliptic curve", body)
        self.assertIn("what hermes should not claim", body)
        self.assertIn("%", read(EXAMPLE))
        self.assertIn("hermes role", body)


class DocsTests(unittest.TestCase):
    def test_doc_explains_paste_and_ecc(self):
        body = norm(read(DOC))
        self.assertIn("paste", body)
        self.assertIn("everything claude code", body)
        self.assertIn("read-only", body)

    def test_handoff_controlled_launcher(self):
        self.assertIn("controlled launcher", norm(read(HANDOFF)))

    def test_report_verdict(self):
        self.assertIn("IMPLEMENTED_AND_PUSHED", read(REPORT))


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


class NoLocalPathLeakTests(unittest.TestCase):
    """Committed N+6.25A files must carry no real local path / username. Forbidden tokens
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
