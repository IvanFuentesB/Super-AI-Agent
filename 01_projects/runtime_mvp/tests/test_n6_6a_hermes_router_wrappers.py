"""Tests for N+6.6A — Hermes Soul + Router Wrapper Foundation.

These tests lock the safety behavior of the Hermes router wrappers so it cannot
silently regress. They assert (1) the soul/status/policy/coordinator memory files
exist and carry the agreed roles + safety language, (2) the wrappers exist and
contain no dangerous PowerShell (no arbitrary command execution, no process launch,
no outbound web call, no installs), (3) at runtime the wrappers default to
dry-run/read-only and report the standing safety flags, and (4) no doc overclaims a
capability and no secret pattern is present.
"""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

VAULT = REPO_ROOT / "14_context" / "agent_handoff_vault"
ROUTER = REPO_ROOT / "03_scripts" / "hermes_router"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_6A_HERMES_ROUTER_WRAPPERS.md"

SOUL = VAULT / "HERMES_SOUL.md"
STATUS = VAULT / "HERMES_CURRENT_STATUS.md"
POLICY = VAULT / "HERMES_ROUTER_POLICY.md"
COORD = VAULT / "04_Logs" / "HERMES_COORDINATOR_SUMMARY.md"
README = ROUTER / "README.md"

WRAPPERS = [
    "read_current_task.ps1",
    "write_handoff_note.ps1",
    "prepare_claude_prompt.ps1",
    "prepare_codex_audit.ps1",
    "collect_agent_outputs.ps1",
    "run_gemma_summary.ps1",
    "hermes_router_status.ps1",
]

MEMORY_FILES = [SOUL, STATUS, POLICY, COORD]
# Human-facing docs scanned for overclaims and secret patterns.
DOC_FILES = [SOUL, STATUS, POLICY, COORD, DOC, README]

PS = shutil.which("pwsh") or shutil.which("powershell")

# Tokens that must never appear in a wrapper: arbitrary execution, process launch,
# outbound web calls, or installs.
FORBIDDEN_PS_TOKENS = [
    "invoke-expression",
    "start-process",
    "invoke-webrequest",
    "invoke-restmethod",
    "webclient",
    "start-bitstransfer",
    "install-module",
    "install-package",
    "winget",
    "npm install",
    "pip install",
]

# Distinctive affirmative overclaims that must never appear in a planning/doc file.
# These are phrased so they cannot be a substring of a truthful *negated* sentence
# (e.g. "no telegram, browser/computer-use, or mcp is enabled") — they only match a
# real affirmative overclaim.
FALSE_CLAIMS = [
    "telegram is enabled for ghoti",
    "browser is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "computer use is enabled for ghoti",
    "mcp is enabled for ghoti",
    "mcp is installed for ghoti",
    "ghoti is fully autonomous",
    "hermes is fully autonomous",
    "wrappers run arbitrary commands",
    "hermes can run arbitrary commands",
    "agents are launched automatically",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    """Lowercase and collapse whitespace so a phrase still matches when Markdown
    wrapped it across lines."""
    return " ".join(text.lower().split())


def run_wrapper_json(name, *args):
    """Run a wrapper and return (returncode, parsed_json, stderr_text)."""
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROUTER / name), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=120)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class HermesRouterFoundationTests(unittest.TestCase):
    def test_memory_files_exist(self):
        for path in MEMORY_FILES:
            self.assertTrue(path.is_file(), msg=f"missing memory file: {path}")

    def test_wrappers_and_docs_exist(self):
        for wrapper in WRAPPERS:
            self.assertTrue((ROUTER / wrapper).is_file(), msg=f"missing wrapper: {wrapper}")
        self.assertTrue(DOC.is_file(), msg=f"missing doc: {DOC}")
        self.assertTrue(README.is_file(), msg=f"missing README: {README}")

    def test_wrappers_have_no_dangerous_tokens(self):
        for wrapper in WRAPPERS:
            body = read(ROUTER / wrapper).lower()
            for token in FORBIDDEN_PS_TOKENS:
                self.assertNotIn(token, body, msg=f"{wrapper} contains forbidden token {token!r}")
            self.assertIsNone(re.search(r"\biex\b", body), msg=f"{wrapper} uses the iex alias")

    def test_soul_states_roles_and_safety(self):
        soul = norm(read(SOUL))
        for needle in [
            "local coordinator and memory writer",
            "chatgpt is the main architect and planner",
            "must not pretend to be the smartest brain",
            "approved wrappers only",
            "arbitrary command",
            "human approval",
            "never stores secrets",
            "not enabled",
        ]:
            self.assertIn(needle, soul, msg=f"HERMES_SOUL.md missing: {needle!r}")

    def test_status_states_truth(self):
        status = norm(read(STATUS))
        for needle in [
            "n+6.4b is on",
            "do not claim n+6.5a is merged",
            "wrapper foundation",
            "llama3.1:8b",
            "gemma",
            "not enabled",
            "not installed",
        ]:
            self.assertIn(needle, status, msg=f"HERMES_CURRENT_STATUS.md missing: {needle!r}")

    def test_policy_states_routing_and_lifecycle(self):
        policy = norm(read(POLICY))
        for needle in [
            "chatgpt",
            "claude code",
            "codex",
            "gemma",
            "human",
            "blocked",
            "human_decision",
            "approved wrappers",
            "arbitrary command",
        ]:
            self.assertIn(needle, policy, msg=f"HERMES_ROUTER_POLICY.md missing: {needle!r}")

    def test_doc_states_wrappers_only_and_not_enabled(self):
        doc = norm(read(DOC))
        for needle in [
            "approved wrappers only",
            "arbitrary command",
            "no telegram",
            "no browser/computer-use",
            "no mcp installed",
        ]:
            self.assertIn(needle, doc, msg=f"doc missing: {needle!r}")

    def test_no_overclaims_across_docs(self):
        combined = "\n".join(read(p).lower() for p in DOC_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in DOC_FILES + [ROUTER / w for w in WRAPPERS])
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class HermesRouterRuntimeTests(unittest.TestCase):
    def test_status_wrapper_reports_safe_flags(self):
        rc, data, err = run_wrapper_json("hermes_router_status.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["wrappers_present_count"], len(WRAPPERS))
        for flag in [
            "live_launch_enabled",
            "browser_use_enabled",
            "computer_use_enabled",
            "telegram_enabled",
            "mcp_enabled",
            "arbitrary_command_execution_enabled",
        ]:
            self.assertFalse(data[flag], msg=f"{flag} must be False")
        self.assertTrue(data["dry_run_default"])
        self.assertTrue(data["local_only"])

    def test_read_current_task_returns_json(self):
        rc, data, err = run_wrapper_json("read_current_task.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertFalse(data["live_action"])
        self.assertTrue(data["task_exists"])

    def test_write_handoff_note_cannot_traverse(self):
        rc, data, err = run_wrapper_json(
            "write_handoff_note.ps1",
            "-Title", r"..\..\..\Windows\System32\evil:note",
            "-Body", "traversal probe",
        )
        self.assertEqual(rc, 0, msg=err)
        # Default is dry-run: nothing is written, but the safe target is computed.
        self.assertFalse(data["wrote"], msg="dry-run must not write")
        self.assertTrue(data["under_logs"], msg="target must resolve inside 04_Logs")
        name = data["safe_filename"]
        for bad in ["..", "/", "\\", ":"]:
            self.assertNotIn(bad, name, msg=f"sanitized filename leaked {bad!r}: {name!r}")

    def test_prepare_claude_prompt_does_not_launch(self):
        rc, data, err = run_wrapper_json("prepare_claude_prompt.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["launches_claude"])
        self.assertFalse(data["wrote"], msg="dry-run default must not write")

    def test_prepare_codex_audit_does_not_launch(self):
        rc, data, err = run_wrapper_json("prepare_codex_audit.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["launches_codex"])
        self.assertFalse(data["wrote"], msg="dry-run default must not write")

    def test_run_gemma_summary_makes_no_network_call(self):
        rc, data, err = run_wrapper_json("run_gemma_summary.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["local_model_call_implemented"])
        self.assertFalse(data["network_used"])
        self.assertEqual(data["mode"], "dry_run")

    def test_collect_agent_outputs_is_read_only(self):
        rc, data, err = run_wrapper_json("collect_agent_outputs.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["llm_used"])
        self.assertFalse(data["network_used"])
        self.assertFalse(data["live_action"])


if __name__ == "__main__":
    unittest.main()
