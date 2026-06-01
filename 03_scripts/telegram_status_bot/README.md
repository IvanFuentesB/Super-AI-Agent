# GhotiDeepBot - Telegram Status Bot Runtime (N+6.10C)

This is a **status-only** Telegram bot. It long-polls the Telegram Bot API and replies
ONLY to a small set of read-only status commands from a single allowed chat id. It does
not control Ghoti, does not launch Claude or Codex, does not enable MCP or
browser/computer-use, runs no arbitrary shell, and never sends anything except replies
to approved read-only commands.

## Where the secrets live (outside the repo)

- The bot **token is outside the repo**: `C:\Users\<you>\.ghoti_secrets\telegram_bot_token.txt`
- The **allowed chat id is outside the repo**: `C:\Users\<you>\.ghoti_secrets\telegram_allowed_chat_id.txt`
- Runtime config + feature flags live under `C:\Users\<you>\.ghoti_runtime\`

Nothing in this repo holds a real token or a real chat id. The token is never printed,
never logged, and never placed on a command line.

## Keep the window open

The bot runs in the foreground attached to the PowerShell window that starts it.
**Keep that window open.** If the window closes or the process stops, the bot stops and
will not reply. This is the single most common cause of "the bot is not answering."

## Why the previous bot did not reply

The earlier GhotiDeepBot experiment did not reply because **this polling process was not
running** - not because a local model (Llama) was unsupported. A plain Python + Telegram
Bot API poll loop is all that is needed to answer `/status`. Hermes/Llama is **not
required** for basic status replies; that routing arrives later through approved wrappers.

## No plugin toggles required

You do **not** need to enable any Telegram plugin, MCP server, browser/computer-use, or
any agent launch to run this status bot. None of those are touched here.

## Allowed commands (read-only)

`/start`, `/status`, `/current_task`, `/latest_claude`, `/latest_codex`, `/help`, `/flags`

## Blocked commands (always refused)

`/run`, `/send`, `/login`, `/post`, `/buy`, `/trade`, `/delete`, `/mcp`, `/browser`,
`/computer`, `/email`, `/whatsapp`, `/install`, `/clone`, `/shell`, `/exec`, `/deploy`,
`/agent`, `/claude`, `/codex`

Blocked commands are refused with a fixed message; there is no handler that performs them.
They would each require a future approved milestone and explicit human approval.

## How to run setup (one time)

```powershell
pwsh -ExecutionPolicy Bypass -File 03_scripts\telegram_status_bot\setup_telegram_status_bot.ps1
```

This creates `~/.ghoti_runtime` and `~/.ghoti_secrets` outside the repo, seeds the runtime
config and feature flags from the repo examples, then prompts you (input hidden) for the
bot token and for the allowed chat id. The token is read as a SecureString and is never
printed.

## How to start

```powershell
pwsh -ExecutionPolicy Bypass -File 03_scripts\telegram_status_bot\start_telegram_status_bot.ps1
```

Use `-DryRun` to print what would run (and a JSON status) without starting the poll loop.

## How to stop

Press `Ctrl+C` in the window, or close the window. The bot stops immediately.

## How to rotate the token

1. Stop the bot (`Ctrl+C`).
2. Create a new token in Telegram's @BotFather and revoke the old one.
3. Overwrite `~/.ghoti_secrets\telegram_bot_token.txt` with the new token (one line), or
   delete that file and re-run setup.
4. Start the bot again.

## How to activate the kill switch

Edit `~/.ghoti_runtime\ghoti_feature_flags.json` and set `"global_kill_switch": true`.
The running bot reloads flags every poll cycle; once the kill switch is on it pauses all
status actions and only answers `/help` and `/flags`. Set it back to `false` to resume.

## How to check status (read-only)

```powershell
pwsh -ExecutionPolicy Bypass -File 03_scripts\telegram_status_bot\check_telegram_status_bot.ps1 -NoSecretsRequired
```

This prints a JSON health summary: which scripts/configs exist, whether the secret files
are present (existence only, never their values), and that the risky feature flags are
still defaulted false. It changes nothing.
