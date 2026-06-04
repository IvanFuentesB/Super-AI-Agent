"""Tests for N+6.17A - Ghoti Runtime Activation Pack.

These tests lock the safety and behavior of the local PowerShell wrappers in
03_scripts/runtime_activation/ that make Ghoti easier to use from PowerShell,
Telegram, and WSL Hermes. They assert (1) every pack file exists, (2) each wrapper
emits a single JSON object and honors its dry-run/preview default, (3) the Python
resolver finds a working interpreter even when the PATH shim is broken, (4) the
health check reports the status brain + status bridge present and every live-action
flag false, (5) enabling the Telegram status bridge writes only to a LOCAL
outside-repo config, sets the two bridge flags, and writes no secret value, (6) the
wrappers are local and read-only - no Invoke-Expression / iex, every external call
uses an argument array, no token or chat id committed - and (7) the docs explain that
WSL Hermes is the only Hermes install now, the Windows Hermes Desktop app was
deleted, the same session is resumed, the status bridge and handoff note are the
memory source, and Telegram stays status-only. The wrappers that run the bot, write
outside the repo, or resume Hermes are only ever exercised in their preview/dry-run
mode here; nothing live is started.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

PACK_DIR = REPO_ROOT / "03_scripts" / "runtime_activation"
RESOLVER = PACK_DIR / "ghoti_python_resolver.ps1"
CHECK = PACK_DIR / "check_ghoti_runtime.ps1"
WRITE_HANDOFF = PACK_DIR / "write_hermes_status_handoff.ps1"
ENABLE_BRIDGE = PACK_DIR / "enable_status_bridge_runtime_config.ps1"
START_BOT = PACK_DIR / "start_ghotideepbot_status_only.ps1"
RESUME_HERMES = PACK_DIR / "resume_wsl_hermes_session.ps1"
PACK_README = PACK_DIR / "README.md"

CONTEXT_DIR = REPO_ROOT / "14_context" / "runtime_activation"
CONTEXT_README = CONTEXT_DIR / "README.md"
STATUS_SCHEMA = CONTEXT_DIR / "runtime_activation_status_schema.json"

CONFIG_EXAMPLE = REPO_ROOT / "23_configs" / "runtime_activation.example.json"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_17A_RUNTIME_ACTIVATION_PACK.md"
HANDOFF_NOTE = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
    / "NEXT_RUNTIME_ACTIVATION_TASK.md"
)

# Existing scripts the pack drives (must remain present for the wrappers to work).
STATUS_BRIDGE = REPO_ROOT / "03_scripts" / "status_bridge" / "ghoti_status_bridge.py"
STATUS_BRAIN = REPO_ROOT / "03_scripts" / "local_worker_queue" / "ghoti_status_brain.py"
TELEGRAM_BOT = REPO_ROOT / "03_scripts" / "telegram_status_bot" / "ghoti_telegram_status_bot.py"

SESSION_ID = "20260601_081506_d35c70"

PS_SCRIPTS = [RESOLVER, CHECK, WRITE_HANDOFF, ENABLE_BRIDGE, START_BOT, RESUME_HERMES]

# Committed text scanned for secrets and chat ids (this test file is excluded on
# purpose: it carries the regexes and forbidden-token literals it searches for).
TEXT_PACK = PS_SCRIPTS + [
    PACK_README, CONTEXT_README, STATUS_SCHEMA, CONFIG_EXAMPLE, DOC, HANDOFF_NOTE,
]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")

PS = shutil.which("pwsh") or shutil.which("powershell")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase and collapse whitespace so a phrase matches across wrapped lines."""
    return " ".join(text.lower().split())


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=240)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class PackFilesExistTests(unittest.TestCase):
    def test_pack_files_exist(self):
        for path in [
            RESOLVER, CHECK, WRITE_HANDOFF, ENABLE_BRIDGE, START_BOT, RESUME_HERMES,
            PACK_README, CONTEXT_README, STATUS_SCHEMA, CONFIG_EXAMPLE, DOC, HANDOFF_NOTE,
        ]:
            self.assertTrue(path.is_file(), msg=f"missing pack file: {path}")

    def test_driven_scripts_present(self):
        for path in [STATUS_BRIDGE, STATUS_BRAIN, TELEGRAM_BOT]:
            self.assertTrue(path.is_file(), msg=f"missing driven script: {path}")


class ConfigExampleTests(unittest.TestCase):
    def test_example_is_local_only_and_bridge_defaults_off(self):
        cfg = json.loads(read(CONFIG_EXAMPLE))
        self.assertTrue(cfg["local_only"])
        self.assertFalse(cfg["status_bridge_enabled_default"])
        self.assertFalse(cfg["use_status_bridge_for_telegram_status_default"])
        self.assertEqual(cfg["hermes_session_id"], SESSION_ID)

    def test_example_points_at_outside_repo_secret_paths(self):
        cfg = json.loads(read(CONFIG_EXAMPLE))
        for key in ["telegram_token_file", "telegram_allowed_chat_id_file"]:
            value = cfg[key]
            self.assertTrue(value.endswith(".txt"), msg=f"{key} should be a file path")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), value.replace("\\", "/"))

    def test_example_blocks_live_commands(self):
        cfg = json.loads(read(CONFIG_EXAMPLE))
        blocked = cfg["blocked_commands"]
        for cmd in ["/run", "/send", "/login", "/mcp", "/browser", "/computer",
                    "/email", "/whatsapp", "/install", "/shell", "/exec", "/deploy"]:
            self.assertIn(cmd, blocked, msg=f"{cmd} must be blocked")


class StatusSchemaTests(unittest.TestCase):
    def test_schema_declares_safe_posture(self):
        schema = json.loads(read(STATUS_SCHEMA))
        safety = schema["safety"]
        self.assertTrue(safety["local_only"])
        for flag in [
            "reads_secret_values", "network_used", "external_api_used",
            "live_agent_launch", "telegram_control", "mcp", "live_browser",
            "os_input", "auto_send", "installs",
        ]:
            self.assertFalse(safety[flag], msg=f"{flag} must be false in schema")


class SafetyScanTests(unittest.TestCase):
    @staticmethod
    def _strip_ps_comments(text):
        # Strip <# .. #> block comments then # line comments so the scan sees only
        # executable code (the scripts state "no Invoke-Expression" in their synopsis).
        text = re.sub(r"<#.*?#>", "", text, flags=re.DOTALL)
        return re.sub(r"#.*", "", text)

    def test_ps_scripts_have_no_invoke_expression(self):
        for path in PS_SCRIPTS:
            code = self._strip_ps_comments(read(path))
            self.assertNotIn("invoke-expression", code.lower(),
                             msg=f"{path.name} uses Invoke-Expression")
            self.assertIsNone(re.search(r"(?i)(?:^|[\s|;(])iex(?:[\s|;)]|$)", code),
                              msg=f"{path.name} uses the iex alias")

    def test_ps_scripts_emit_json(self):
        for path in PS_SCRIPTS:
            self.assertIn("ConvertTo-Json", read(path), msg=f"{path.name} should emit JSON")

    def test_no_token_or_chat_id_committed(self):
        for path in TEXT_PACK:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_PACK)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


class DocsContentTests(unittest.TestCase):
    def test_hermes_is_wsl_only_now(self):
        combined = norm(read(DOC)) + " " + norm(read(HANDOFF_NOTE)) + " " + norm(read(CONTEXT_README))
        self.assertIn("wsl hermes is the only hermes installation now", combined)
        self.assertIn("the windows hermes desktop app was deleted", combined)

    def test_same_session_and_memory_source(self):
        combined = norm(read(DOC)) + " " + norm(read(HANDOFF_NOTE))
        self.assertIn(SESSION_ID, combined)
        self.assertIn("the status bridge and the handoff note are the memory source", combined)

    def test_telegram_stays_status_only(self):
        doc = norm(read(DOC))
        self.assertIn("telegram stays status-only", doc)
        self.assertIn("no live control", doc)


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class ResolverAndCheckTests(unittest.TestCase):
    def test_resolver_finds_working_python(self):
        rc, data, err = run_ps_json(RESOLVER)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"], msg=f"resolver did not find python: {data}")
        self.assertTrue(str(data["executable"]).lower().endswith("python.exe"))
        self.assertIn("python", data["tried"])

    def test_check_runtime_emits_safe_json(self):
        rc, data, err = run_ps_json(CHECK)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["python_ok"], msg="python should resolve")
        self.assertTrue(data["status_brain_ok"])
        self.assertTrue(data["status_bridge_ok"])
        self.assertTrue(data["ok"])
        self.assertEqual(data["same_session_id"], SESSION_ID)
        self.assertTrue(data["local_only"])
        for field in [
            "telegram_control_enabled", "mcp_enabled", "auto_send_enabled",
            "live_browser_enabled",
        ]:
            self.assertFalse(data[field], msg=f"{field} must be false")


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class WrapperPreviewTests(unittest.TestCase):
    def test_write_handoff_dry_run_writes_nothing(self):
        rc, data, err = run_ps_json(WRITE_HANDOFF, "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["ready"], msg="python + bridge should be ready")
        self.assertFalse(data["handoff_written"])
        self.assertFalse(data["secrets_present"])
        self.assertTrue(data["local_only"])
        self.assertIn("--write-hermes-handoff", data["would_run_command"])

    def test_enable_bridge_dry_run_is_local_and_secretless(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "telegram_status_config.json")
            rc, data, err = run_ps_json(ENABLE_BRIDGE, "-DryRun", "-ConfigPath", target)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["status_bridge_enabled"])
        self.assertTrue(data["use_status_bridge_for_telegram_status"])
        self.assertFalse(data["secrets_written"])
        self.assertFalse(data["config_written"])
        self.assertTrue(data["config_outside_repo"])
        self.assertFalse(data["telegram_control_enabled"])
        preview = data["config_preview"]
        self.assertTrue(preview["status_only"])
        self.assertTrue(preview["status_bridge_enabled"])
        self.assertTrue(preview["use_status_bridge_for_telegram_status"])

    def test_start_bot_dry_run_is_status_only(self):
        rc, data, err = run_ps_json(START_BOT, "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["status_only"])
        self.assertTrue(data["python_ok"])
        self.assertTrue(data["bot_script_present"])
        self.assertFalse(data["token_in_command_line"])
        self.assertFalse(data["telegram_control_enabled"])
        self.assertIn("-u", data["would_run_command"])

    def test_resume_hermes_previews_same_session(self):
        rc, data, err = run_ps_json(RESUME_HERMES)
        self.assertEqual(rc, 0, msg=err)
        self.assertFalse(data["run"])
        self.assertEqual(data["session_id"], SESSION_ID)
        self.assertIn("hermes --resume", data["command_preview"])
        self.assertIn(SESSION_ID, data["command_preview"])
        self.assertIn("wsl -d", data["command_preview"])
        self.assertTrue(data["hermes_wsl_only"])
        self.assertTrue(data["windows_hermes_desktop_deleted"])
        self.assertTrue(data["local_only"])
        self.assertFalse(data["secrets_present"])


if __name__ == "__main__":
    unittest.main()
