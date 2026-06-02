"""Tests for N+6.16A - Status Bridge for Telegram + Hermes Desktop/CLI.

These tests lock the safety and behavior of the local, read-only status bridge that
turns the N+6.15A status brain into shapes Telegram, Hermes, Obsidian, and PowerShell
can read. They assert (1) every pack file exists, (2) the bridge produces JSON,
Markdown, and Telegram-safe output and can write a Hermes handoff note, (3) the Telegram
bot has the opt-in status-bridge integration and stays status-only with blocked commands
refused, (4) the new global flags default false with only the read-only status toggle
true and the bot config gains the bridge keys, (5) the bridge is local and read-only -
no shell string, no Invoke-Expression, no network/external API, no MCP/browser/email/
WhatsApp/auto-send, no token or chat id committed, and (6) the docs explain that the
Desktop app improves the UI but not the model's intelligence and that Hermes should read
the bridge/handoff instead of repeating a generic summary. A guarded test runs the
PowerShell health check and asserts its JSON safety fields.
"""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

BRIDGE_DIR = REPO_ROOT / "03_scripts" / "status_bridge"
BRIDGE = BRIDGE_DIR / "ghoti_status_bridge.py"
BRIDGE_CHECK = BRIDGE_DIR / "check_status_bridge.ps1"
BRIDGE_README = BRIDGE_DIR / "README.md"

BOT_DIR = REPO_ROOT / "03_scripts" / "telegram_status_bot"
PY_BOT = BOT_DIR / "ghoti_telegram_status_bot.py"

STATUS_BRAIN = REPO_ROOT / "03_scripts" / "local_worker_queue" / "ghoti_status_brain.py"

CONFIGS = REPO_ROOT / "23_configs"
FLAGS_EXAMPLE = CONFIGS / "ghoti_feature_flags.example.json"
BOT_CONFIG = CONFIGS / "telegram_status_bot.example.json"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_16A_STATUS_BRIDGE_TELEGRAM_HERMES.md"
HERMES_NOTE = REPO_ROOT / "14_context" / "hermes_integrations" / "STATUS_BRIDGE_TELEGRAM_HERMES.md"
HANDOFF_NOTE = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
    / "NEXT_STATUS_BRIDGE_TASK.md"
)
EXAMPLE_OUT = REPO_ROOT / "14_context" / "local_worker_queue" / "status_bridge_example_output.json"
HANDOFF_LOG = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "04_Logs"
    / "HERMES_STATUS_BRIDGE_LAST_RUN.md"
)

PS = shutil.which("pwsh") or shutil.which("powershell")

# The three flags this milestone adds; all must default false.
NEW_FLAGS = [
    "status_bridge_enabled",
    "hermes_status_bridge_enabled",
    "status_bridge_auto_handoff_enabled",
]
TRUE_BY_DEFAULT = "telegram_status_commands_enabled"

# A representative slice of commands that must remain blocked with no handler.
BLOCKED_SAMPLE = [
    "/run", "/send", "/login", "/mcp", "/browser", "/computer", "/email",
    "/whatsapp", "/install", "/clone", "/shell", "/exec", "/agent", "/claude", "/codex",
]

# Committed text scanned for secrets and chat ids.
TEXT_PACK = [
    BRIDGE, BRIDGE_CHECK, BRIDGE_README, PY_BOT, BOT_CONFIG, FLAGS_EXAMPLE,
    DOC, HERMES_NOTE, HANDOFF_NOTE, EXAMPLE_OUT,
]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")

# Network / external-API / live-control tokens that must never appear in the bridge.
BRIDGE_FORBIDDEN = [
    "import urllib", "import requests", "import socket", "import http",
    "urlopen", "httpx", "openai", "anthropic", "selenium", "playwright",
    "smtplib", "os.system", "subprocess.popen", "shell=true",
]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase and collapse whitespace so a phrase matches across wrapped lines."""
    return " ".join(text.lower().split())


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(BRIDGE), *args],
        capture_output=True, text=True, timeout=90,
    )


def load_bot_module():
    spec = importlib.util.spec_from_file_location("ghoti_telegram_status_bot", str(PY_BOT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The bot is pure standard library with no import-time side effects.
BOT = load_bot_module()


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=240)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class PackFilesExistTests(unittest.TestCase):
    def test_bridge_pack_exists(self):
        for path in [BRIDGE, BRIDGE_CHECK, BRIDGE_README, STATUS_BRAIN, PY_BOT]:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")

    def test_configs_exist(self):
        for path in [FLAGS_EXAMPLE, BOT_CONFIG]:
            self.assertTrue(path.is_file(), msg=f"missing config: {path}")

    def test_docs_and_notes_exist(self):
        for path in [DOC, HERMES_NOTE, HANDOFF_NOTE, EXAMPLE_OUT]:
            self.assertTrue(path.is_file(), msg=f"missing doc/note: {path}")


class BridgeCliTests(unittest.TestCase):
    def test_json_mode_ok(self):
        proc = run_cli("--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["milestone"], "N+6.16A")
        self.assertIn(data["source"], ("status_brain", "fallback"))
        self.assertIn("packet", data)

    def test_markdown_mode_renders(self):
        proc = run_cli("--markdown")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("Ghoti Status Bridge", proc.stdout)
        self.assertIn("## Safety", proc.stdout)

    def test_telegram_safe_json_is_sanitized(self):
        proc = run_cli("--telegram-safe-json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertFalse(data["secrets_present"])
        text = data["telegram_safe_text"]
        self.assertLessEqual(len(text), 3500)
        for line in [
            "telegram_control_enabled: false",
            "mcp_enabled: false",
            "browser_computer_use_enabled: false",
            "auto_send_enabled: false",
        ]:
            self.assertIn(line, text, msg=f"telegram-safe text missing {line!r}")

    def test_bridge_safety_flags_all_safe(self):
        data = json.loads(run_cli("--json").stdout)
        for scope in (data["safety"], data["packet"]["safety"]):
            for flag in [
                "live_browser_used", "os_input_used", "external_api_used",
                "telegram_control_used", "mcp_used", "auto_send_used",
                "network_used", "secrets_read",
            ]:
                self.assertFalse(scope.get(flag, False), msg=f"{flag} must be false")
            self.assertTrue(scope.get("local_only"))

    def test_write_hermes_handoff_writes_file(self):
        proc = run_cli("--write-hermes-handoff", "--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["hermes_handoff_written"])
        self.assertEqual(
            data["hermes_handoff_path"],
            "14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md",
        )
        self.assertTrue(HANDOFF_LOG.is_file(), msg="handoff note not written")
        self.assertIn("Ghoti Status Bridge", read(HANDOFF_LOG))


class BotIntegrationTests(unittest.TestCase):
    def _cfg(self, **extra):
        cfg = {
            "repo_root": str(REPO_ROOT),
            "feature_flags_file": str(FLAGS_EXAMPLE),
            "message_preview_limit": 3500,
        }
        cfg.update(extra)
        return cfg

    def test_bot_source_has_bridge_integration(self):
        src = read(PY_BOT)
        for marker in [
            "_status_via_bridge",
            "ghoti_status_bridge",
            "use_status_bridge_for_telegram_status",
            "status_bridge_enabled",
        ]:
            self.assertIn(marker, src, msg=f"bot missing integration marker {marker!r}")
        self.assertTrue(hasattr(BOT, "_status_via_bridge"))

    def test_status_default_off_uses_builtin(self):
        # Without the opt-in keys, /status keeps the deterministic built-in status.
        flags = dict(BOT.SAFE_DEFAULT_FLAGS)
        reply = BOT.handle_command("/status", self._cfg(), flags, True, True)
        self.assertIn("GhotiDeepBot status-only online", reply)

    def test_status_uses_bridge_when_enabled(self):
        flags = dict(BOT.SAFE_DEFAULT_FLAGS)
        cfg = self._cfg(
            status_bridge_enabled=True,
            use_status_bridge_for_telegram_status=True,
            status_bridge_script_path="03_scripts/status_bridge/ghoti_status_bridge.py",
            status_bridge_timeout_seconds=60,
        )
        reply = BOT.handle_command("/status", cfg, flags, True, True)
        self.assertIn("Ghoti status", reply)
        self.assertIn("telegram_control_enabled: false", reply)
        self.assertNotIn("GhotiDeepBot status-only online", reply)

    def test_blocked_commands_still_blocked(self):
        flags = dict(BOT.SAFE_DEFAULT_FLAGS)
        for cmd in BLOCKED_SAMPLE:
            self.assertEqual(
                BOT.handle_command(cmd, self._cfg(), flags, True, True),
                BOT.BLOCKED_REPLY,
                msg=f"{cmd} must remain blocked",
            )

    def test_kill_switch_still_first(self):
        flags = dict(BOT.SAFE_DEFAULT_FLAGS)
        flags["global_kill_switch"] = True
        cfg = self._cfg(
            status_bridge_enabled=True,
            use_status_bridge_for_telegram_status=True,
        )
        self.assertEqual(
            BOT.handle_command("/status", cfg, flags, True, True), BOT.KILL_SWITCH_REPLY
        )

    def test_bot_adds_no_new_subprocess(self):
        # The n6.10c invariant: the bot's only subprocess is the read-only git lookup.
        self.assertEqual(read(PY_BOT).count("subprocess.run("), 1)


class ConfigTests(unittest.TestCase):
    def test_flags_example_single_true_and_new_flags_false(self):
        flags = json.loads(read(FLAGS_EXAMPLE))
        true_keys = [k for k, v in flags.items() if v is True]
        self.assertEqual(true_keys, [TRUE_BY_DEFAULT], msg=f"unexpected true flags: {true_keys}")
        for name in NEW_FLAGS + ["telegram_status_bridge_enabled"]:
            self.assertIn(name, flags, msg=f"flags example missing {name!r}")
            self.assertFalse(flags[name], msg=f"{name} must default false")
        for value in flags.values():
            self.assertIsInstance(value, bool)

    def test_bot_config_has_bridge_keys(self):
        cfg = json.loads(read(BOT_CONFIG))
        self.assertTrue(cfg["status_only"])
        self.assertFalse(cfg["status_bridge_enabled"])
        self.assertFalse(cfg["use_status_bridge_for_telegram_status"])
        self.assertIsInstance(cfg["status_bridge_timeout_seconds"], int)
        self.assertIn("status_bridge", cfg["status_bridge_script_path"])


class SafetyScanTests(unittest.TestCase):
    def test_bridge_is_local_and_read_only(self):
        low = read(BRIDGE).lower()
        for token in BRIDGE_FORBIDDEN:
            self.assertNotIn(token, low, msg=f"bridge must not contain {token!r}")
        self.assertIsNone(re.search(r"\beval\(", read(BRIDGE)))
        self.assertIsNone(re.search(r"\bexec\(", read(BRIDGE)))

    def test_bridge_uses_arg_list_not_shell(self):
        src = read(BRIDGE)
        self.assertIn("subprocess.run(", src)
        self.assertNotIn("shell=True", src)

    def test_no_invoke_expression_in_ps_checks(self):
        for path in [BRIDGE_CHECK]:
            self.assertNotIn("invoke-expression", read(path).lower())

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
    def test_desktop_improves_ui_not_intelligence(self):
        combined = norm(read(DOC)) + " " + norm(read(HERMES_NOTE))
        self.assertIn("improves the ui", combined)
        self.assertIn("does not make the model smarter", combined)

    def test_hermes_should_read_bridge_not_repeat(self):
        combined = norm(read(DOC)) + " " + norm(read(HERMES_NOTE))
        self.assertIn("instead of repeating a generic summary", combined)
        self.assertIn("read the status bridge and the handoff note", combined)

    def test_telegram_stays_status_only(self):
        doc = norm(read(DOC))
        self.assertIn("telegram stays status-only", doc)
        self.assertIn("no live control", doc)


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class PsCheckTests(unittest.TestCase):
    def test_check_emits_safe_json(self):
        rc, data, err = run_ps_json(BRIDGE_CHECK)
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["check"], "status_bridge")
        for field in [
            "status_bridge_exists", "status_brain_exists", "telegram_bot_exists",
            "handoff_dir_exists", "no_token_required", "local_only",
            "risky_flags_default_false",
        ]:
            self.assertTrue(data[field], msg=f"{field} must be true")
        for field in [
            "telegram_control_enabled", "live_agent_launch_enabled", "mcp_enabled",
            "live_browser_enabled", "auto_send_enabled",
        ]:
            self.assertFalse(data[field], msg=f"{field} must be false")


if __name__ == "__main__":
    unittest.main()
