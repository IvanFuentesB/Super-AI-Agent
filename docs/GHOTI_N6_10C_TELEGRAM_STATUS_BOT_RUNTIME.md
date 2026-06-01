# Ghoti N+6.10C - Telegram Status Bot Runtime

## Purpose

Turn the manual GhotiDeepBot experiment into a safe, repo-backed, testable runtime pack.
The goal is a small, auditable Telegram bot that lets the operator check Ghoti's status
from their phone, and nothing more.

## Scope

- A plain Python long-polling bot (`ghoti_telegram_status_bot.py`) using only the Python
  standard library and the Telegram Bot API.
- PowerShell wrappers to set up, start, and health-check the bot.
- Repo example configs for the runtime config and the feature flags.
- The bot answers only read-only status commands from a single allowed chat id.

## Non-goals (explicitly out of scope)

- The bot does **not** control Ghoti.
- It does **not** launch Claude or Codex.
- It does **not** enable MCP, browser-use, or computer-use.
- It does **not** run arbitrary shell, install anything, or clone/run external repos.
- It does **not** send email/WhatsApp, post to social, log in to accounts, or move money.
- It does **not** auto-send; it only replies to approved read-only commands.

## Safety model

- **Secrets live outside the repo.** The bot token and the allowed chat id are read from
  files under the user home (`~/.ghoti_secrets`), never from the repo. The token is never
  printed, never logged, and never placed on a command line.
- **Single allowed chat id.** Messages from any other chat are ignored, and the rejected
  chat id is masked in logs.
- **Status-only command surface.** Allowed commands are read-only. Blocked commands are
  refused with a fixed message; there is no handler that performs them.
- **Global kill switch.** A single `global_kill_switch` flag pauses all status actions.
- **Feature flags default false.** Every risky flag defaults false; only the read-only
  status command toggle defaults true.

## Runtime architecture

1. A PowerShell setup wrapper creates `~/.ghoti_runtime` and `~/.ghoti_secrets`, seeds the
   runtime config and feature flags from the repo examples, and prompts for the token
   (SecureString) and allowed chat id.
2. The start wrapper runs the Python bot in the foreground attached to the window.
3. The Python bot loads the runtime config, reads the token and allowed chat id from the
   outside-repo secret files, reloads the feature flags every poll cycle, long-polls
   `getUpdates`, and replies to allowed commands via `sendMessage`.
4. The check wrapper reports a read-only JSON health summary.

## How this differs from Hermes plugin toggles

The Hermes router has plugin toggles that decide which capabilities are routed to which
local model. This status bot is **independent** of those toggles: it is a standalone
poll loop that needs no plugin enabled, no MCP server, and no model running. Enabling or
disabling a Hermes plugin does not start or stop this bot, and running this bot does not
enable any Hermes plugin.

## Why Llama is not needed for status

Answering `/status` is a fixed read of local repo state (a short SHA, file existence, flag
values). It requires no language model. The previous GhotiDeepBot experiment did not reply
because **this polling process was not running** - **not because Llama was unsupported**.
A plain Python + Telegram Bot API poll loop is sufficient for status replies.

## Future Hermes wrapper routing

Later milestones may let the operator ask richer questions that are summarized by a local
model (e.g. Gemma) or coordinated by Hermes (local llama3.1:8b). That routing will arrive
through approved wrappers, behind their own feature flags, after a separate audited
milestone. It is not part of this pack.

## What remains disabled after this milestone

- `telegram_status_bot_enabled` stays false in the committed example (operator opt-in).
- `telegram_run_commands_enabled`, `telegram_send_commands_enabled` stay false.
- `mcp_enabled`, `mcp_filesystem_read_only_enabled` stay false.
- `live_agent_launch_enabled`, `claude_launch_enabled`, `codex_launch_enabled` stay false.
- `browser_computer_use_enabled` stays false.
- `email_draft_agent_enabled`, `whatsapp_draft_agent_enabled`, `auto_send_enabled` stay false.
- `external_repo_install_enabled`, `affiliate_program_enabled`,
  `dashboard_local_analytics_enabled`, `docker_runtime_enabled`, `vps_runtime_enabled`
  stay false.
