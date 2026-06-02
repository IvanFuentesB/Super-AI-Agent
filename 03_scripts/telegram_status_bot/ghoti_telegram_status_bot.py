#!/usr/bin/env python3
"""GhotiDeepBot - status-only Telegram bot runtime (N+6.10C).

Status-only. This bot long-polls the Telegram Bot API and replies ONLY to a small
set of read-only status commands sent from a single allowed chat id. It does not
control Ghoti, does not launch Claude or Codex, does not enable MCP or
browser/computer-use, runs no arbitrary shell, and never sends anything except
replies to approved read-only commands.

Secrets (the bot token and the allowed chat id) live OUTSIDE the repo and are never
printed, logged, or committed. Python standard library only - no external packages,
no pip install, no requests dependency.

The previous GhotiDeepBot experiment did not reply because this polling process was
not running - not because a local model (Llama) was unsupported. Llama is not needed
to answer /status; that future Hermes routing arrives later through approved wrappers.
"""

import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BOT_NAME = "GhotiDeepBot"
STARTUP_MESSAGE = "GhotiDeepBot is online. Send /status."

# Default runtime/secret locations - all OUTSIDE the repo. A runtime config file may
# override these paths; the repo itself never holds the token or the allowed chat id.
HOME = Path.home()
DEFAULT_CONFIG_PATH = HOME / ".ghoti_runtime" / "telegram_status_config.json"
DEFAULT_TOKEN_FILE = HOME / ".ghoti_secrets" / "telegram_bot_token.txt"
DEFAULT_ALLOWED_CHAT_ID_FILE = HOME / ".ghoti_secrets" / "telegram_allowed_chat_id.txt"
DEFAULT_FEATURE_FLAGS_FILE = HOME / ".ghoti_runtime" / "ghoti_feature_flags.json"
DEFAULT_POLL_TIMEOUT = 25
DEFAULT_PREVIEW_LIMIT = 3500
# Optional, off by default: the local read-only status bridge (N+6.16A). When the
# runtime config explicitly opts in, /status can read a sanitized status summary from
# this local module. It is imported lazily only when enabled and never adds a new
# subprocess here, so the bot's only subprocess remains the read-only git lookup.
DEFAULT_STATUS_BRIDGE_TIMEOUT = 20
DEFAULT_STATUS_BRIDGE_REL = "03_scripts/status_bridge/ghoti_status_bridge.py"

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"

# Read-only status commands the bot may answer.
ALLOWED_COMMANDS = [
    "/start",
    "/status",
    "/current_task",
    "/latest_claude",
    "/latest_codex",
    "/help",
    "/flags",
]

# Commands that are always refused. The presence of this list never makes any of
# them live; there is no handler that performs these actions.
BLOCKED_COMMANDS = [
    "/run",
    "/send",
    "/login",
    "/post",
    "/buy",
    "/trade",
    "/delete",
    "/mcp",
    "/browser",
    "/computer",
    "/email",
    "/whatsapp",
    "/install",
    "/clone",
    "/shell",
    "/exec",
    "/deploy",
    "/agent",
    "/claude",
    "/codex",
]

BLOCKED_REPLY = (
    "Blocked. GhotiDeepBot is status-only. This command requires a future approved "
    "milestone and human approval."
)

KILL_SWITCH_REPLY = "Global kill switch is active. Status bot actions are paused."

# Bounded-preview source files (relative to repo_root).
CURRENT_TASK_REL = "14_context/agent_handoff_vault/02_Agent_Handoffs/CURRENT_TASK.md"
LATEST_CLAUDE_REL = "14_context/agent_handoff_vault/04_Logs/CLAUDE_LAST_RUN.md"
LATEST_CODEX_REL = "14_context/agent_handoff_vault/04_Logs/CODEX_LAST_AUDIT.md"

# Safe defaults: every risky flag is false; only status commands default on.
SAFE_DEFAULT_FLAGS = {
    "global_kill_switch": False,
    "telegram_status_bot_enabled": False,
    "telegram_status_commands_enabled": True,
    "telegram_run_commands_enabled": False,
    "telegram_send_commands_enabled": False,
    "mcp_enabled": False,
    "mcp_filesystem_read_only_enabled": False,
    "live_agent_launch_enabled": False,
    "claude_launch_enabled": False,
    "codex_launch_enabled": False,
    "browser_computer_use_enabled": False,
    "email_draft_agent_enabled": False,
    "whatsapp_draft_agent_enabled": False,
    "auto_send_enabled": False,
    "external_repo_install_enabled": False,
    "affiliate_program_enabled": False,
    "dashboard_local_analytics_enabled": False,
    "docker_runtime_enabled": False,
    "vps_runtime_enabled": False,
}


def log(message):
    """Print a timestamped console line. Never pass a secret to this function."""
    print("[{0}] {1}".format(time.strftime("%Y-%m-%d %H:%M:%S"), message), flush=True)


def _bool_str(value):
    return "true" if bool(value) else "false"


def load_json_file(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except (ValueError, OSError):
        return default


def read_secret_file(path):
    """Read a single-line secret (token or chat id). Returns None if missing or
    empty. The value is never printed or logged anywhere in this module."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = handle.read().strip()
        return value or None
    except (FileNotFoundError, OSError):
        return None


def _default_repo_root():
    # <repo>/03_scripts/telegram_status_bot/ghoti_telegram_status_bot.py
    return Path(__file__).resolve().parents[2]


def load_config(config_path):
    cfg = load_json_file(config_path, default={}) or {}
    return {
        "repo_root": cfg.get("repo_root") or str(_default_repo_root()),
        "token_file": cfg.get("token_file") or str(DEFAULT_TOKEN_FILE),
        "allowed_chat_id_file": cfg.get("allowed_chat_id_file") or str(DEFAULT_ALLOWED_CHAT_ID_FILE),
        "feature_flags_file": cfg.get("feature_flags_file") or str(DEFAULT_FEATURE_FLAGS_FILE),
        "poll_timeout_seconds": int(cfg.get("poll_timeout_seconds") or DEFAULT_POLL_TIMEOUT),
        "message_preview_limit": int(cfg.get("message_preview_limit") or DEFAULT_PREVIEW_LIMIT),
        "status_only": bool(cfg.get("status_only", True)),
        "status_bridge_enabled": bool(cfg.get("status_bridge_enabled", False)),
        "status_bridge_script_path": cfg.get("status_bridge_script_path") or DEFAULT_STATUS_BRIDGE_REL,
        "status_bridge_timeout_seconds": int(cfg.get("status_bridge_timeout_seconds") or DEFAULT_STATUS_BRIDGE_TIMEOUT),
        "use_status_bridge_for_telegram_status": bool(cfg.get("use_status_bridge_for_telegram_status", False)),
    }


def load_flags(path):
    flags = load_json_file(path, default=None)
    merged = dict(SAFE_DEFAULT_FLAGS)
    if isinstance(flags, dict):
        for key, value in flags.items():
            if isinstance(value, bool):
                merged[key] = value
    return merged


def _api_call(token, method, params=None, timeout=30):
    """Call the Telegram Bot API. The token is embedded in the URL path and is never
    logged; on error only the method name and an error class/code are reported."""
    url = TELEGRAM_API_BASE.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode("utf-8") if params else None
    request = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        log("Telegram API HTTP error on {0}: {1}".format(method, getattr(exc, "code", "?")))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log("Telegram API error on {0}: {1}".format(method, exc.__class__.__name__))
    return None


def get_updates(token, offset, timeout):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    result = _api_call(token, "getUpdates", params, timeout=timeout + 10)
    if not result or not result.get("ok"):
        return []
    return result.get("result", [])


def send_message(token, chat_id, text):
    result = _api_call(token, "sendMessage", {"chat_id": chat_id, "text": text})
    return bool(result and result.get("ok"))


def git_short_sha(repo_root):
    """Read-only: best-effort short SHA of origin/main. No shell, no writes."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "origin/main"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unavailable"


def bounded_preview(repo_root, rel_path, limit):
    base = Path(repo_root).resolve()
    target = (base / rel_path).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return "(unavailable: path outside repo root)"
    if not target.is_file():
        return "(no file yet at {0})".format(rel_path)
    try:
        text = target.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return "(unavailable: could not read {0})".format(rel_path)
    if len(text) > limit:
        text = text[:limit] + "\n... (truncated)"
    return text or "(empty)"


def build_status(config, flags, token_loaded, allowed_chat_configured):
    return "\n".join([
        "{0} status-only online".format(BOT_NAME),
        "repo_root: {0}".format(config["repo_root"]),
        "origin_main: {0}".format(git_short_sha(config["repo_root"])),
        "live_launch_enabled: false",
        "telegram_control_enabled: false",
        "mcp_enabled: false",
        "browser_computer_use_enabled: false",
        "auto_send_enabled: false",
        "global_kill_switch: {0}".format(_bool_str(flags.get("global_kill_switch", False))),
        "feature_flags_path: {0}".format(config["feature_flags_file"]),
        "token_loaded: {0}".format(_bool_str(token_loaded)),
        "allowed_chat_configured: {0}".format(_bool_str(allowed_chat_configured)),
    ])


def build_help():
    return "\n".join([
        "{0} is status-only.".format(BOT_NAME),
        "Allowed commands: " + ", ".join(ALLOWED_COMMANDS),
        "Blocked commands: " + ", ".join(BLOCKED_COMMANDS),
        "Blocked commands need a future approved milestone and human approval.",
    ])


def build_flags(flags):
    lines = ["{0} feature flags (safe view):".format(BOT_NAME)]
    for key in sorted(flags):
        lines.append("{0}: {1}".format(key, _bool_str(flags[key])))
    return "\n".join(lines)


def _status_via_bridge(config):
    """Return a sanitized status text from the local status bridge, or None.

    This only does anything when the runtime config explicitly opts in with BOTH
    ``status_bridge_enabled`` and ``use_status_bridge_for_telegram_status``. Both
    default false, so the bot stays on the deterministic ``build_status`` unless the
    operator turns the bridge on. The bridge is imported lazily as a local module
    (never a new subprocess from this file), and any failure returns None so the
    caller falls back to the deterministic status. No network or secret is touched
    here; the bridge itself is local and read-only."""
    if not (config.get("status_bridge_enabled")
            and config.get("use_status_bridge_for_telegram_status")):
        return None
    repo_root = config.get("repo_root") or str(_default_repo_root())
    rel = config.get("status_bridge_script_path") or DEFAULT_STATUS_BRIDGE_REL
    try:
        bridge_dir = str((Path(repo_root) / rel).resolve().parent)
        if bridge_dir not in sys.path:
            sys.path.insert(0, bridge_dir)
        import ghoti_status_bridge  # local read-only status bridge module
        timeout = int(config.get("status_bridge_timeout_seconds")
                      or DEFAULT_STATUS_BRIDGE_TIMEOUT)
        text = ghoti_status_bridge.telegram_safe_status_text(timeout=timeout)
        return text or None
    except Exception:
        return None


def parse_command(text):
    if not text:
        return ""
    head = text.strip().split()[0].lower()
    if "@" in head:
        head = head.split("@", 1)[0]
    return head


def handle_command(text, config, flags, token_loaded, allowed_chat_configured):
    """Return the reply string for a message, or None to stay silent."""
    cmd = parse_command(text)
    if not cmd.startswith("/"):
        return None
    if bool(flags.get("global_kill_switch", False)) and cmd not in ("/help", "/flags"):
        return KILL_SWITCH_REPLY
    if cmd == "/start":
        return build_status(config, flags, token_loaded, allowed_chat_configured) + "\n\n" + build_help()
    if cmd == "/status":
        bridge_text = _status_via_bridge(config)
        if bridge_text:
            return bridge_text
        return build_status(config, flags, token_loaded, allowed_chat_configured)
    if cmd == "/help":
        return build_help()
    if cmd == "/flags":
        return build_flags(flags)
    if cmd == "/current_task":
        return bounded_preview(config["repo_root"], CURRENT_TASK_REL, config["message_preview_limit"])
    if cmd == "/latest_claude":
        return bounded_preview(config["repo_root"], LATEST_CLAUDE_REL, config["message_preview_limit"])
    if cmd == "/latest_codex":
        return bounded_preview(config["repo_root"], LATEST_CODEX_REL, config["message_preview_limit"])
    if cmd in BLOCKED_COMMANDS:
        return BLOCKED_REPLY
    return "Unknown command. Send /help for the allowed status commands."


def run(config_path=DEFAULT_CONFIG_PATH):
    config = load_config(config_path)
    flags = load_flags(config["feature_flags_file"])
    token = read_secret_file(config["token_file"])
    allowed_chat_id = read_secret_file(config["allowed_chat_id_file"])
    token_loaded = token is not None
    allowed_chat_configured = allowed_chat_id is not None

    log("{0} starting (status-only).".format(BOT_NAME))
    log("repo_root: {0}".format(config["repo_root"]))
    log("token_loaded: {0}".format(_bool_str(token_loaded)))
    log("allowed_chat_configured: {0}".format(_bool_str(allowed_chat_configured)))
    log("global_kill_switch: {0}".format(_bool_str(flags.get("global_kill_switch", False))))

    if not token_loaded:
        log("No token file found. Run setup first (see README). Exiting.")
        return 1
    if not allowed_chat_configured:
        log("No allowed chat id configured. Refusing to talk to anyone. Exiting.")
        return 1

    if send_message(token, allowed_chat_id, STARTUP_MESSAGE):
        log("Startup message sent.")
    else:
        log("Could not send startup message; will keep polling.")

    log("Polling for updates. Keep this window open - the bot stops if this process stops.")
    offset = None
    while True:
        flags = load_flags(config["feature_flags_file"])
        for update in get_updates(token, offset, config["poll_timeout_seconds"]):
            offset = update.get("update_id", 0) + 1
            message = update.get("message") or update.get("edited_message")
            if not message:
                continue
            chat_id = str(message.get("chat", {}).get("id", ""))
            if chat_id != allowed_chat_id:
                log("Ignored a message from an unauthorized chat (id masked).")
                continue
            reply = handle_command(
                message.get("text", ""), config, flags, token_loaded, allowed_chat_configured
            )
            if reply:
                send_message(token, chat_id, reply)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    config_path = DEFAULT_CONFIG_PATH
    if "--config" in argv:
        idx = argv.index("--config")
        if idx + 1 < len(argv):
            config_path = Path(argv[idx + 1])
    try:
        return run(config_path)
    except KeyboardInterrupt:
        log("Stopped by Ctrl+C. The bot is no longer running.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
