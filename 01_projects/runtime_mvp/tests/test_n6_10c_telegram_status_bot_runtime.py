"""Tests for N+6.10C - Telegram Status Bot Runtime Pack + Feature Flags + Kill Switches.

These tests lock the safety behavior of the status-only Telegram bot so it cannot
silently regress. They assert (1) every pack file exists (scripts, configs, docs,
notes, handoff, report), (2) the feature flags example defaults every risky flag
false with only the read-only status toggle true, (3) the bot's command surface is
status-only - allowed commands are read-only and blocked commands are refused with no
handler, (4) the kill switch pauses status actions, (5) no real bot token pattern and
no real chat id are committed, (6) the Python bot runs no arbitrary shell and launches
no agent, (7) setup reads the token as a SecureString and never prints it, (8) the
docs/notes carry the agreed safety language, and (9) the read-only check wrapper and
the start -DryRun wrapper emit JSON without polling. A final guarded test runs the
public-repo security audit and asserts zero failed checks.
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

BOT_DIR = REPO_ROOT / "03_scripts" / "telegram_status_bot"
PY_BOT = BOT_DIR / "ghoti_telegram_status_bot.py"
SETUP = BOT_DIR / "setup_telegram_status_bot.ps1"
START = BOT_DIR / "start_telegram_status_bot.ps1"
CHECK = BOT_DIR / "check_telegram_status_bot.ps1"
BOT_README = BOT_DIR / "README.md"

CONFIGS = REPO_ROOT / "23_configs"
FLAGS_EXAMPLE = CONFIGS / "ghoti_feature_flags.example.json"
CONFIG_EXAMPLE = CONFIGS / "telegram_status_bot.example.json"

DOCS = REPO_ROOT / "docs"
DOC_RUNTIME = DOCS / "GHOTI_N6_10C_TELEGRAM_STATUS_BOT_RUNTIME.md"
DOC_FLAGS = DOCS / "GHOTI_FEATURE_FLAGS_AND_KILL_SWITCHES.md"
DOC_DOCKER = DOCS / "GHOTI_DOCKER_VPS_RUNTIME_ROADMAP.md"

NOTES = REPO_ROOT / "14_context" / "hermes_integrations"
NOTE_RUNTIME = NOTES / "TELEGRAM_STATUS_BOT_RUNTIME.md"
NOTE_FLAGS = NOTES / "FEATURE_FLAGS_AND_KILL_SWITCHES.md"
NOTE_AFFILIATE = NOTES / "TELEGRAM_AFFILIATE_PROGRAM_CANDIDATE.md"
NOTE_DOCKER = NOTES / "DOCKER_VPS_RUNTIME_ROADMAP.md"

HANDOFF = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
    / "NEXT_TELEGRAM_RUNTIME_TASK.md"
)
REPORT = REPO_ROOT / "14_context" / "claude_n6_10c_telegram_status_bot_runtime.md"

AUDIT = REPO_ROOT / "03_scripts" / "public_repo_security_audit.py"

PS = shutil.which("pwsh") or shutil.which("powershell")

# The 19 feature flags the example must declare; only the status toggle defaults true.
ALL_FLAGS = [
    "global_kill_switch",
    "telegram_status_bot_enabled",
    "telegram_status_commands_enabled",
    "telegram_run_commands_enabled",
    "telegram_send_commands_enabled",
    "mcp_enabled",
    "mcp_filesystem_read_only_enabled",
    "live_agent_launch_enabled",
    "claude_launch_enabled",
    "codex_launch_enabled",
    "browser_computer_use_enabled",
    "email_draft_agent_enabled",
    "whatsapp_draft_agent_enabled",
    "auto_send_enabled",
    "external_repo_install_enabled",
    "affiliate_program_enabled",
    "dashboard_local_analytics_enabled",
    "docker_runtime_enabled",
    "vps_runtime_enabled",
]
TRUE_BY_DEFAULT = "telegram_status_commands_enabled"

# Commands that must be in the blocked list and must never have a handler.
REQUIRED_BLOCKED = [
    "/run", "/send", "/login", "/post", "/buy", "/trade", "/delete",
    "/mcp", "/browser", "/computer", "/email", "/whatsapp", "/install",
]

# Real chat ids must never be committed. Use a shape-based guard instead of
# storing a remembered private identifier in the test itself.
CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")

# All committed text in this pack - scanned for secrets, tokens, and the chat id.
PACK_TEXT_FILES = [
    PY_BOT, SETUP, START, CHECK, BOT_README,
    FLAGS_EXAMPLE, CONFIG_EXAMPLE,
    DOC_RUNTIME, DOC_FLAGS, DOC_DOCKER,
    NOTE_RUNTIME, NOTE_FLAGS, NOTE_AFFILIATE, NOTE_DOCKER,
    HANDOFF, REPORT,
]

# Distinctive affirmative overclaims that must never appear. Each is phrased so it
# cannot be a substring of a truthful *negated* sentence in the pack.
FALSE_CLAIMS = [
    "telegram is enabled for ghoti",
    "browser is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "mcp is enabled for ghoti",
    "the bot controls ghoti",
    "the bot launches claude",
    "the bot launches codex",
    "auto-send is enabled for ghoti",
    "ghoti is fully autonomous",
]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase and collapse whitespace so a phrase matches even when Markdown
    wrapped it across lines."""
    return " ".join(text.lower().split())


def load_bot_module():
    spec = importlib.util.spec_from_file_location("ghoti_telegram_status_bot", str(PY_BOT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Imported once: the bot is pure standard library and has no import-time side effects
# (run() is only reached via the __main__ guard).
BOT = load_bot_module()


def sample_config():
    return {
        "repo_root": str(REPO_ROOT),
        "token_file": "unused-in-test",
        "allowed_chat_id_file": "unused-in-test",
        "feature_flags_file": str(FLAGS_EXAMPLE),
        "poll_timeout_seconds": 25,
        "message_preview_limit": 3500,
        "status_only": True,
    }


def run_ps_json(path, *args):
    cmd = [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=120)
    out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, json.loads(out), err


class PackFilesExistTests(unittest.TestCase):
    def test_runtime_scripts_exist(self):
        for path in [PY_BOT, SETUP, START, CHECK, BOT_README]:
            self.assertTrue(path.is_file(), msg=f"missing runtime file: {path}")

    def test_configs_exist(self):
        for path in [FLAGS_EXAMPLE, CONFIG_EXAMPLE]:
            self.assertTrue(path.is_file(), msg=f"missing config: {path}")

    def test_docs_exist(self):
        for path in [DOC_RUNTIME, DOC_FLAGS, DOC_DOCKER]:
            self.assertTrue(path.is_file(), msg=f"missing doc: {path}")

    def test_notes_exist(self):
        for path in [NOTE_RUNTIME, NOTE_FLAGS, NOTE_AFFILIATE, NOTE_DOCKER]:
            self.assertTrue(path.is_file(), msg=f"missing integration note: {path}")

    def test_handoff_and_report_exist(self):
        for path in [HANDOFF, REPORT]:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class FeatureFlagsExampleTests(unittest.TestCase):
    def setUp(self):
        self.flags = json.loads(read(FLAGS_EXAMPLE))

    def test_all_required_flags_present(self):
        for name in ALL_FLAGS:
            self.assertIn(name, self.flags, msg=f"flags example missing {name!r}")

    def test_global_kill_switch_present_and_false(self):
        self.assertIn("global_kill_switch", self.flags)
        self.assertFalse(self.flags["global_kill_switch"])

    def test_only_status_commands_default_true(self):
        for name, value in self.flags.items():
            self.assertIsInstance(value, bool, msg=f"{name} must be a bool")
            if name == TRUE_BY_DEFAULT:
                self.assertTrue(value, msg=f"{name} should default true")
            else:
                self.assertFalse(value, msg=f"risky flag {name} must default false")


class BotCommandSurfaceTests(unittest.TestCase):
    def test_blocked_commands_listed(self):
        for cmd in REQUIRED_BLOCKED:
            self.assertIn(cmd, BOT.BLOCKED_COMMANDS, msg=f"{cmd} must be blocked")

    def test_allowed_commands_are_read_only(self):
        for cmd in BOT.ALLOWED_COMMANDS:
            self.assertNotIn(cmd, BOT.BLOCKED_COMMANDS)
        self.assertIn("/status", BOT.ALLOWED_COMMANDS)
        self.assertIn("/help", BOT.ALLOWED_COMMANDS)

    def test_safe_default_flags_only_status_true(self):
        for name, value in BOT.SAFE_DEFAULT_FLAGS.items():
            if name == TRUE_BY_DEFAULT:
                self.assertTrue(value)
            else:
                self.assertFalse(value, msg=f"{name} must default false")

    def test_parse_command_strips_botname_and_args(self):
        self.assertEqual(BOT.parse_command("/STATUS@GhotiDeepBot extra"), "/status")
        self.assertEqual(BOT.parse_command("  /Help  "), "/help")
        self.assertEqual(BOT.parse_command("not a command"), "not")

    def test_blocked_commands_return_blocked_reply(self):
        cfg, flags = sample_config(), dict(BOT.SAFE_DEFAULT_FLAGS)
        for cmd in BOT.BLOCKED_COMMANDS:
            reply = BOT.handle_command(cmd, cfg, flags, False, False)
            self.assertEqual(reply, BOT.BLOCKED_REPLY, msg=f"{cmd} not blocked")

    def test_no_live_agent_launch_via_commands(self):
        # /run, /claude, /codex, /mcp, /browser, /computer must be inert refusals.
        cfg, flags = sample_config(), dict(BOT.SAFE_DEFAULT_FLAGS)
        for cmd in ["/run", "/claude", "/codex", "/mcp", "/browser", "/computer"]:
            self.assertEqual(BOT.handle_command(cmd, cfg, flags, True, True), BOT.BLOCKED_REPLY)

    def test_status_reports_disabled_capabilities(self):
        cfg, flags = sample_config(), dict(BOT.SAFE_DEFAULT_FLAGS)
        status = BOT.handle_command("/status", cfg, flags, True, True)
        for line in [
            "live_launch_enabled: false",
            "telegram_control_enabled: false",
            "mcp_enabled: false",
            "browser_computer_use_enabled: false",
            "auto_send_enabled: false",
        ]:
            self.assertIn(line, status, msg=f"/status missing {line!r}")

    def test_kill_switch_pauses_status_actions(self):
        cfg = sample_config()
        kill = dict(BOT.SAFE_DEFAULT_FLAGS)
        kill["global_kill_switch"] = True
        self.assertEqual(
            BOT.handle_command("/status", cfg, kill, True, True), BOT.KILL_SWITCH_REPLY
        )
        # /help and /flags still answer so the operator can see why it is paused.
        self.assertNotEqual(
            BOT.handle_command("/help", cfg, kill, True, True), BOT.KILL_SWITCH_REPLY
        )
        self.assertNotEqual(
            BOT.handle_command("/flags", cfg, kill, True, True), BOT.KILL_SWITCH_REPLY
        )

    def test_unknown_command_is_safe(self):
        cfg, flags = sample_config(), dict(BOT.SAFE_DEFAULT_FLAGS)
        reply = BOT.handle_command("/wat", cfg, flags, True, True)
        self.assertIn("Unknown command", reply)


class PythonBotSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(PY_BOT)
        self.low = self.src.lower()

    def test_no_arbitrary_shell(self):
        self.assertNotIn("shell=true", self.low)
        self.assertNotIn("os.system", self.low)
        self.assertNotIn("subprocess.popen", self.low)
        self.assertIsNone(re.search(r"\beval\(", self.src))
        self.assertIsNone(re.search(r"\bexec\(", self.src))

    def test_subprocess_only_runs_readonly_git(self):
        # The single subprocess call is the read-only git short-SHA lookup; nothing
        # else launches a process. (We assert structure, not docstring wording - the
        # module's prose truthfully says "no pip install".)
        self.assertIn('"git", "-C"', self.src)
        self.assertIn("rev-parse", self.src)
        self.assertEqual(self.src.count("subprocess.run("), 1)
        self.assertNotIn("subprocess.call(", self.src)
        self.assertNotIn("subprocess.popen", self.low)
        self.assertNotIn("os.startfile", self.low)

    def test_no_external_package_import(self):
        self.assertNotIn("import requests", self.low)
        self.assertNotIn("import telegram", self.low)


class SetupScriptSafetyTests(unittest.TestCase):
    def setUp(self):
        self.low = read(SETUP).lower()

    def test_setup_uses_securestring(self):
        self.assertIn("-assecurestring", self.low)
        self.assertIn("securestringtobstr", self.low)
        self.assertIn("zerofreebstr", self.low)

    def test_setup_never_prints_token(self):
        self.assertNotIn("write-host $plain", self.low)
        self.assertNotIn("write-host $secure", self.low)
        self.assertNotIn("write-output $plain", self.low)


class DocsContentTests(unittest.TestCase):
    def test_token_is_outside_the_repo(self):
        for path in [BOT_README, DOC_RUNTIME, NOTE_RUNTIME]:
            self.assertIn("outside the repo", norm(read(path)), msg=f"{path.name}")

    def test_previous_no_reply_was_runtime_not_llama(self):
        combined = norm(read(BOT_README)) + " " + norm(read(DOC_RUNTIME)) + " " + norm(read(NOTE_RUNTIME))
        self.assertIn("was not running", combined)
        self.assertIn("not because llama", combined)
        self.assertIn("polling process", combined)

    def test_affiliate_is_candidate_only_no_spam(self):
        note = norm(read(NOTE_AFFILIATE))
        for needle in ["candidate-only", "not enabled", "no spam", "no fake engagement", "no auto-mass"]:
            self.assertIn(needle, note, msg=f"affiliate note missing {needle!r}")

    def test_docker_vps_planned_not_enabled(self):
        combined = norm(read(DOC_DOCKER)) + " " + norm(read(NOTE_DOCKER))
        for needle in ["not enabled", "docker", "vps", "when money allows", "audited milestone"]:
            self.assertIn(needle, combined, msg=f"docker/vps roadmap missing {needle!r}")

    def test_no_overclaims(self):
        combined = "\n".join(read(p).lower() for p in PACK_TEXT_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")


class SecretAndPrivacyTests(unittest.TestCase):
    def test_no_real_chat_id_committed(self):
        for path in PACK_TEXT_FILES:
            self.assertIsNone(CHAT_ID_RE.search(read(path)), msg=f"chat-id-like value leaked in {path.name}")

    def test_no_bot_token_pattern(self):
        token_re = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
        for path in PACK_TEXT_FILES:
            self.assertIsNone(token_re.search(read(path)), msg=f"token-like pattern in {path.name}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in PACK_TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_no_dotenv_in_pack(self):
        self.assertFalse((BOT_DIR / ".env").exists())
        self.assertFalse((CONFIGS / ".env").exists())

    def test_config_example_points_outside_repo(self):
        cfg = json.loads(read(CONFIG_EXAMPLE))
        self.assertIn(".ghoti_secrets", cfg["token_file"])
        self.assertIn(".ghoti_secrets", cfg["allowed_chat_id_file"])
        self.assertIn(".ghoti_runtime", cfg["feature_flags_file"])
        self.assertTrue(cfg["status_only"])


@unittest.skipUnless(PS, "PowerShell (pwsh/powershell) not available")
class WrapperRuntimeTests(unittest.TestCase):
    def test_check_wrapper_reports_safe_flags(self):
        rc, data, err = run_ps_json(CHECK, "-NoSecretsRequired")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertEqual(data["wrapper"], "check_telegram_status_bot")
        self.assertTrue(data["python_script_exists"])
        self.assertTrue(data["risky_flags_default_false"])
        self.assertFalse(data["telegram_status_bot_enabled"])
        self.assertFalse(data["global_kill_switch"])
        for flag in ["no_live_agent_launch", "no_mcp", "no_browser_computer_use", "no_auto_send"]:
            self.assertTrue(data[flag], msg=f"{flag} must be true")

    def test_start_dryrun_emits_json_without_polling(self):
        rc, data, err = run_ps_json(START, "-DryRun")
        self.assertEqual(rc, 0, msg=err)
        self.assertTrue(data["ok"])
        self.assertTrue(data["dry_run"])
        self.assertTrue(data["status_only"])
        self.assertFalse(data["token_in_command_line"])


@unittest.skipUnless(AUDIT.is_file(), "public_repo_security_audit.py not present")
class SecurityAuditGateTests(unittest.TestCase):
    def test_security_audit_zero_failed(self):
        proc = subprocess.run(
            [sys.executable, str(AUDIT), "--run", "--json"],
            capture_output=True, timeout=300,
        )
        out = proc.stdout.decode("utf-8-sig", errors="replace")
        start, end = out.find("{"), out.rfind("}")
        self.assertNotEqual(start, -1, msg="audit produced no JSON")
        data = json.loads(out[start:end + 1])
        self.assertEqual(data["failed_checks"], 0, msg=f"audit failed checks: {data.get('failed_checks')}")
        self.assertEqual(data["blocking_findings"], [], msg="audit reported blocking findings")


if __name__ == "__main__":
    unittest.main()
