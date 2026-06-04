"""Tests for N+6.20A - Approved-Window Copy/Paste Harness (+ AGENTS.md, plans).

These tests lock the safety and behavior of the approved-window paste harness in
03_scripts/approved_window_paste/ and the supporting docs. They assert (1) every file
exists, (2) the detector emits JSON, (3) the paste wrapper dry-run emits JSON and
pastes nothing, (4) PasteApproved refuses without an allowlist match, (5) the scripts
press no Enter key, click no mouse, use no shell string, and use no PowerShell
expression invocation, (6) no secret/token/chat-id pattern is committed, (7) the
feature flags default false with only telegram_status_commands_enabled true, (8)
AGENTS.md exists and is concise, (9) the Agent Arena plan is simulation-first, and (10)
the report carries a skills/plugin section.
"""

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

AGENTS = REPO_ROOT / "AGENTS.md"

DOCS = REPO_ROOT / "docs"
DOC_HARNESS = DOCS / "GHOTI_N6_20A_APPROVED_WINDOW_COPY_PASTE_HARNESS.md"
DOC_ECC = DOCS / "GHOTI_ECC_AGENT_WORKFLOW_UPGRADE_PLAN.md"
DOC_GBRAIN = DOCS / "GHOTI_GBRAIN_MEMORY_UPGRADE_PLAN.md"
DOC_ECC_VS = DOCS / "GHOTI_ECC_INTENDED_USE_VS_GHOTI_ADAPTATION.md"
DOC_ARENA = DOCS / "GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md"

CTX_DIR = REPO_ROOT / "14_context" / "approved_window_paste"
CTX_README = CTX_DIR / "README.md"
APPROVED_WINDOWS = CTX_DIR / "approved_windows.example.json"
PASTE_SCHEMA = CTX_DIR / "paste_status_schema.json"
DROP_README = CTX_DIR / "manual_output_drop" / "README.md"

SCRIPT_DIR = REPO_ROOT / "03_scripts" / "approved_window_paste"
DETECTOR = SCRIPT_DIR / "ghoti_approved_window_detector.ps1"
PASTE = SCRIPT_DIR / "ghoti_approved_clipboard_paste.ps1"
PASTE_STATUS = SCRIPT_DIR / "ghoti_paste_status.py"
CHECK = SCRIPT_DIR / "check_approved_window_paste.ps1"
SUMMARY = SCRIPT_DIR / "write_manual_output_summary.py"

HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_APPROVED_WINDOW_PASTE_TASK.md")
REPORT = REPO_ROOT / "14_context" / "claude_n6_20a_approved_window_copy_paste_harness.md"
FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

OUTBOX_GITKEEP = REPO_ROOT / "14_context" / "overnight_operator" / "outbox" / ".gitkeep"

PS_SCRIPTS = [DETECTOR, PASTE, CHECK]
PY_SCRIPTS = [PASTE_STATUS, SUMMARY]
ALL_SCRIPTS = PS_SCRIPTS + PY_SCRIPTS

ALL_FILES = [
    AGENTS, DOC_HARNESS, DOC_ECC, DOC_GBRAIN, DOC_ECC_VS, DOC_ARENA,
    CTX_README, APPROVED_WINDOWS, PASTE_SCHEMA, DROP_README,
    DETECTOR, PASTE, PASTE_STATUS, CHECK, SUMMARY,
    HANDOFF, REPORT, FLAGS,
]

TEXT_FILES = [
    AGENTS, DOC_HARNESS, DOC_ECC, DOC_GBRAIN, DOC_ECC_VS, DOC_ARENA,
    CTX_README, APPROVED_WINDOWS, PASTE_SCHEMA, DROP_README,
    DETECTOR, PASTE, PASTE_STATUS, CHECK, SUMMARY, HANDOFF, REPORT,
]

NEW_FLAGS = [
    "approved_window_detection_enabled",
    "manual_output_drop_enabled",
    "ecc_agent_workflow_upgrade_enabled",
    "gbrain_memory_upgrade_enabled",
    "agent_arena_simulator_enabled",
    "unattended_live_agent_loop_enabled",
]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")

# OS-input primitives (actual invocations), written so prose like "press Enter" or
# "clicks_coordinates" never matches.
ENTER_RE = re.compile(r"\bSendKeys\b|\{ENTER\}|\bkeybd_event\b|\bVK_RETURN\b|\.SendWait\(", re.IGNORECASE)
CLICK_RE = re.compile(r"\bmouse_event\b|\bSetCursorPos\b|\.Click\(|\bSendInput\b|\bleft_click\b", re.IGNORECASE)

PS = shutil.which("pwsh") or shutil.which("powershell")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def run_py(script, *args, timeout=120):
    proc = subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, json.loads(proc.stdout), proc.stderr


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=300)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class SourceSafetyTests(unittest.TestCase):
    def test_scripts_press_no_enter_key(self):
        for path in ALL_SCRIPTS:
            self.assertIsNone(ENTER_RE.search(read(path)), msg=f"{path.name} sends an Enter key")

    def test_scripts_click_no_mouse(self):
        for path in ALL_SCRIPTS:
            self.assertIsNone(CLICK_RE.search(read(path)), msg=f"{path.name} performs a mouse click")

    def test_scripts_have_no_shell_true(self):
        for path in ALL_SCRIPTS:
            self.assertNotIn("shell=True", read(path), msg=f"{path.name} uses shell=True")

    def test_ps_scripts_have_no_expression_invocation(self):
        for path in PS_SCRIPTS:
            code = re.sub(r"#.*", "", re.sub(r"<#.*?#>", "", read(path), flags=re.DOTALL))
            self.assertNotIn("invoke-expression", code.lower(), msg=f"{path.name} uses Invoke-Expression")
            self.assertIsNone(re.search(r"(?i)(?:^|[\s|;(])iex(?:[\s|;)]|$)", code),
                              msg=f"{path.name} uses the iex alias")


class SecretScanTests(unittest.TestCase):
    def test_no_token_or_chat_id(self):
        for path in TEXT_FILES:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9]{20,}")
        self.assertNotRegex(combined, r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")


class FeatureFlagTests(unittest.TestCase):
    def setUp(self):
        self.flags = json.loads(read(FLAGS))

    def test_new_flags_present_and_false(self):
        for name in NEW_FLAGS:
            self.assertIn(name, self.flags, msg=f"missing flag {name}")
            self.assertFalse(self.flags[name], msg=f"{name} must default false")

    def test_only_status_commands_flag_true(self):
        enabled = sorted(k for k, v in self.flags.items() if v is True)
        self.assertEqual(enabled, ["telegram_status_commands_enabled"])


class DocsContentTests(unittest.TestCase):
    def test_agents_md_concise(self):
        self.assertTrue(AGENTS.is_file())
        lines = read(AGENTS).splitlines()
        self.assertLess(len(lines), 130, msg="AGENTS.md should stay concise")
        body = norm(read(AGENTS))
        self.assertIn("no ai attribution", body)
        self.assertIn("feature branch only", body)

    def test_harness_doc_says_no_live_app_control(self):
        doc = norm(read(DOC_HARNESS))
        self.assertIn("no live app control", doc)
        self.assertIn("does not control apps", doc)

    def test_agent_arena_is_simulation_first(self):
        doc = norm(read(DOC_ARENA))
        self.assertIn("simulation-first", doc)
        self.assertIn("simulate swarms before live swarms", doc)
        self.assertIn("n+6.21a", doc)

    def test_report_has_skills_plugin_section(self):
        report = read(REPORT).lower()
        self.assertIn("skills", report)
        self.assertIn("plugin", report)


class PythonToolTests(unittest.TestCase):
    def test_paste_status_json(self):
        rc, data, err = run_py(PASTE_STATUS, "--json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["risky_flags_default_false"])
        self.assertTrue(data["only_status_commands_flag_enabled"])
        self.assertFalse(data["approved_window_paste_enabled"])
        self.assertFalse(data["auto_submit_enabled"])

    def test_manual_output_summary_json(self):
        rc, data, err = run_py(SUMMARY, "--json")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertIsInstance(data["dropped_count"], int)
        self.assertFalse(data["safety"]["runs_commands"])


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class PowerShellHarnessTests(unittest.TestCase):
    def test_detector_emits_json(self):
        rc, data, err = run_ps_json(DETECTOR)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertIn("window_count", data)
        self.assertFalse(data["safety"]["presses_enter"])
        self.assertFalse(data["safety"]["clicks_coordinates"])

    def test_paste_dry_run_does_not_paste(self):
        rc, data, err = run_ps_json(PASTE, "-InputFile", str(OUTBOX_GITKEEP), "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertEqual(data["mode"], "dry_run")
        self.assertFalse(data["copied"])
        self.assertFalse(data["pasted"])
        self.assertFalse(data["submitted"])

    def test_paste_approved_refuses_without_match(self):
        rc, data, err = run_ps_json(PASTE, "-InputFile", str(OUTBOX_GITKEEP),
                                    "-PasteApproved", "-TargetWindow", "definitely_not_approved_zzz")
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["ok"])
        self.assertFalse(data["pasted"])
        self.assertFalse(data["submitted"])
        self.assertIn(data["approved_match"], (None, "", "null"))

    def test_check_emits_safe_json(self):
        rc, data, err = run_ps_json(CHECK)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["detector_works"])
        self.assertTrue(data["paste_dry_run_works"])
        self.assertTrue(data["paste_approved_refuses_without_match"])
        self.assertTrue(data["risky_flags_default_false"])
        self.assertTrue(data["only_status_commands_flag_enabled"])
        self.assertTrue(data["ok"])


if __name__ == "__main__":
    unittest.main()
