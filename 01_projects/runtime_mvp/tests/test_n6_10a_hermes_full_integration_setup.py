"""Tests for N+6.10A — Hermes Full Integration Setup Foundation.

These tests lock the read-only/status-only safety behavior of the Hermes
integration setup foundation so it cannot silently regress. They assert (1) every
doc / integration note / handoff / script / report exists, (2) the five new
planning scripts contain no dangerous PowerShell (no arbitrary command execution,
no process launch, no outbound web call, no installs) and emit JSON, (3) at runtime
each script reports the standing ``enabled: false`` safety flags, and (4) no doc
overclaims a capability and no secret pattern is present.
"""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

ROUTER = REPO_ROOT / "03_scripts" / "hermes_router"
DOCS = REPO_ROOT / "docs"
INTEG = REPO_ROOT / "14_context" / "hermes_integrations"
VAULT = REPO_ROOT / "14_context" / "agent_handoff_vault"
HANDOFF = VAULT / "02_Agent_Handoffs" / "NEXT_HERMES_INTEGRATION_TASK.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_10a_hermes_full_integration_setup.md"

# The five new read-only / planning scripts.
SCRIPTS = [
    "hermes_integration_status.ps1",
    "telegram_status_bot_plan.ps1",
    "mcp_read_only_plan.ps1",
    "provider_plugin_inventory.ps1",
    "local_worker_status.ps1",
]

MASTER_DOC = DOCS / "GHOTI_N6_10A_HERMES_FULL_INTEGRATION_SETUP.md"
TELEGRAM_DOC = DOCS / "GHOTI_TELEGRAM_STATUS_BOT_SETUP.md"
MCP_DOC = DOCS / "GHOTI_MCP_READ_ONLY_SETUP.md"
PROVIDER_DOC = DOCS / "GHOTI_HERMES_PROVIDER_PLUGIN_INVENTORY.md"
WORKER_DOC = DOCS / "GHOTI_24_7_LOCAL_WORKER_PLAN.md"
DOC_GUIDES = [MASTER_DOC, TELEGRAM_DOC, MCP_DOC, PROVIDER_DOC, WORKER_DOC]

INTEG_STATUS = INTEG / "HERMES_INTEGRATION_STATUS.md"
INTEG_TELEGRAM = INTEG / "TELEGRAM_STATUS_BOT_PLAN.md"
INTEG_MCP = INTEG / "MCP_READ_ONLY_PLAN.md"
INTEG_PROVIDER = INTEG / "PROVIDER_PLUGIN_INVENTORY.md"
INTEG_ROUTING = INTEG / "LOCAL_MODEL_ROUTING_PLAN.md"
INTEG_EMAIL = INTEG / "EMAIL_WHATSAPP_DRAFT_ONLY_PLAN.md"
INTEG_NOTES = [
    INTEG_STATUS,
    INTEG_TELEGRAM,
    INTEG_MCP,
    INTEG_PROVIDER,
    INTEG_ROUTING,
    INTEG_EMAIL,
]

# Human-facing docs scanned for overclaims and secret patterns.
DOC_FILES = DOC_GUIDES + INTEG_NOTES + [HANDOFF, REPORT]

PS = shutil.which("pwsh") or shutil.which("powershell")

# Tokens that must never appear in a planning script: arbitrary execution, process
# launch, outbound web calls, or installs.
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
# Each is phrased so it cannot be a substring of a truthful *negated* sentence in
# these docs (e.g. "secrets are never stored in the repo" does not contain
# "secrets are stored in the repo"); they only match a real affirmative overclaim.
FALSE_CLAIMS = [
    "telegram is enabled for ghoti",
    "mcp is enabled for ghoti",
    "mcp is installed for ghoti",
    "browser-use is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "email is enabled for ghoti",
    "whatsapp is enabled for ghoti",
    "secrets are stored in the repo",
    "hermes launches claude automatically",
    "hermes launches codex automatically",
    "ghoti is fully autonomous",
    "hermes can run arbitrary commands",
    "the 24/7 worker is enabled",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    """Lowercase and collapse whitespace so a phrase still matches when Markdown
    wrapped it across lines."""
    return " ".join(text.lower().split())


def run_script_json(name, *args):
    """Run a planning script and return (returncode, parsed_json, stderr_text)."""
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROUTER / name), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=120)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class HermesIntegrationStaticTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in DOC_GUIDES + INTEG_NOTES + [HANDOFF, REPORT]:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")
        for script in SCRIPTS:
            self.assertTrue((ROUTER / script).is_file(), msg=f"missing script: {script}")

    def test_scripts_emit_json_and_have_no_dangerous_tokens(self):
        for script in SCRIPTS:
            body = read(ROUTER / script).lower()
            self.assertIn("convertto-json", body, msg=f"{script} does not emit JSON")
            for token in FORBIDDEN_PS_TOKENS:
                self.assertNotIn(token, body, msg=f"{script} contains forbidden token {token!r}")
            self.assertIsNone(re.search(r"\biex\b", body), msg=f"{script} uses the iex alias")

    def test_master_doc_needles(self):
        doc = norm(read(MASTER_DOC))
        for needle in [
            "read-only / status-only foundation",
            "approved wrappers only",
            "no arbitrary command execution",
            "secrets are never stored in the repo, in obsidian, or in prompts",
            "phase 1",
            "phase 7",
        ]:
            self.assertIn(needle, doc, msg=f"master doc missing: {needle!r}")

    def test_telegram_doc_needles(self):
        doc = norm(read(TELEGRAM_DOC))
        for needle in [
            "the first telegram phase is status-only",
            "/status",
            "/run",
            "never in the repo, never in obsidian, never in prompts",
        ]:
            self.assertIn(needle, doc, msg=f"telegram doc missing: {needle!r}")

    def test_mcp_doc_needles(self):
        doc = norm(read(MCP_DOC))
        for needle in [
            "the first mcp phase is read-only and scoped",
            "filesystem read-only",
            "14_context/agent_handoff_vault",
        ]:
            self.assertIn(needle, doc, msg=f"mcp doc missing: {needle!r}")

    def test_provider_doc_needles(self):
        doc = norm(read(PROVIDER_DOC))
        for needle in [
            "a visible plugin does not mean it is approved or enabled",
            "subscription and cloud providers are optional, not extra spend",
            "llama3.1:8b",
            "gemma3:4b",
        ]:
            self.assertIn(needle, doc, msg=f"provider doc missing: {needle!r}")

    def test_worker_doc_needles(self):
        doc = norm(read(WORKER_DOC))
        for needle in [
            "24/7 local worker",
            "planned but not enabled",
            "twenty_four_seven_mode_enabled: false",
        ]:
            self.assertIn(needle, doc, msg=f"worker doc missing: {needle!r}")

    def test_integration_status_note_needles(self):
        note = norm(read(INTEG_STATUS))
        for needle in [
            "approved wrappers only",
            "never runs arbitrary commands",
            "secrets are never stored in the repo, in obsidian, or in prompts",
        ]:
            self.assertIn(needle, note, msg=f"integration status note missing: {needle!r}")

    def test_email_whatsapp_note_needles(self):
        note = norm(read(INTEG_EMAIL))
        for needle in [
            "draft-only",
            "no auto-send",
            "no account login",
            "no email login and no whatsapp login",
        ]:
            self.assertIn(needle, note, msg=f"email/whatsapp note missing: {needle!r}")

    def test_no_overclaims_across_docs(self):
        combined = "\n".join(read(p).lower() for p in DOC_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in DOC_FILES + [ROUTER / s for s in SCRIPTS])
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class HermesIntegrationRuntimeTests(unittest.TestCase):
    def test_integration_status_reports_disabled_flags(self):
        rc, data, err = run_script_json("hermes_integration_status.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["telegram_planned"])
        self.assertTrue(data["mcp_planned"])
        self.assertTrue(data["local_only"])
        for flag in [
            "telegram_enabled",
            "mcp_enabled",
            "provider_keys_required",
            "browser_use_enabled",
            "computer_use_enabled",
            "live_agent_launch_enabled",
            "email_whatsapp_enabled",
            "arbitrary_command_execution_enabled",
            "secrets_in_repo",
        ]:
            self.assertFalse(data[flag], msg=f"{flag} must be False")

    def test_telegram_plan_is_status_only_and_disabled(self):
        rc, data, err = run_script_json("telegram_status_bot_plan.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["status_bot_phase"], "planned_only")
        self.assertFalse(data["enabled"])
        self.assertFalse(data["token_present"])
        self.assertFalse(data["network_used"])
        self.assertTrue(data["requires_human_approval"])
        self.assertTrue(data["local_only"])
        for cmd in ["/status", "/current_task", "/latest_claude", "/latest_codex", "/help"]:
            self.assertIn(cmd, data["allowed_first_commands"], msg=f"missing allowed cmd {cmd}")
        self.assertIn("/run", data["forbidden_commands"])

    def test_mcp_plan_is_read_only_and_not_installed(self):
        rc, data, err = run_script_json("mcp_read_only_plan.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["mcp_phase"], "planned_only")
        self.assertEqual(data["first_mcp"], "filesystem_read_only")
        self.assertFalse(data["enabled"])
        self.assertFalse(data["install_performed"])
        self.assertFalse(data["network_used"])
        self.assertTrue(data["requires_human_approval"])
        self.assertTrue(data["local_only"])
        for path in [
            "14_context/agent_handoff_vault",
            "docs",
            "14_context/tool_intake",
            "14_context/hermes_integrations",
        ]:
            self.assertIn(path, data["allowed_paths"], msg=f"missing allowed path {path}")
        self.assertIn("browser MCP", data["forbidden"])

    def test_provider_inventory_keeps_no_keys(self):
        rc, data, err = run_script_json("provider_plugin_inventory.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["hermes_model"], "llama3.1:8b")
        self.assertEqual(data["cheap_worker_model"], "gemma3:4b")
        self.assertTrue(data["local_only"])
        for flag in [
            "cloud_provider_keys_expected_in_repo",
            "kimi_configured",
            "anthropic_configured",
            "github_configured",
            "browser_plugins_enabled",
        ]:
            self.assertFalse(data[flag], msg=f"{flag} must be False")

    def test_local_worker_is_not_running(self):
        rc, data, err = run_script_json("local_worker_status.ps1")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["local_workers_planned"])
        self.assertTrue(data["local_only"])
        for flag in [
            "gemma_summary_worker_enabled",
            "queue_enabled",
            "scheduled_jobs_enabled",
            "twenty_four_seven_mode_enabled",
            "network_used",
        ]:
            self.assertFalse(data[flag], msg=f"{flag} must be False")


if __name__ == "__main__":
    unittest.main()
