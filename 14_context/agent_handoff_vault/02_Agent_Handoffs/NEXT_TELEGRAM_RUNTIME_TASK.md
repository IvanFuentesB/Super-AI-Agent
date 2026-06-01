# Next Telegram Runtime Task

Source: N+6.10C - Telegram Status Bot Runtime Pack + Feature Flags + Kill Switches +
Runtime Privacy Foundation (status-only runtime landed, bot disabled by default).

## Where we are

The manual GhotiDeepBot experiment is now a repo-backed, testable runtime pack:

- `03_scripts/telegram_status_bot/` - a plain Python long-polling bot (standard library +
  Telegram Bot API) plus PowerShell setup/start/check wrappers and a README.
- `23_configs/ghoti_feature_flags.example.json` - feature flags; every risky flag defaults
  false, only `telegram_status_commands_enabled` defaults true.
- `23_configs/telegram_status_bot.example.json` - runtime config with placeholder paths
  (no real token, no real chat id).
- Docs and integration notes describe the runtime, the flags/kill-switch model, the
  Docker/VPS roadmap (planning only), and the affiliate program (candidate-only).

The bot is status-only: it replies to read-only commands from a single allowed chat id and
nothing else. The token and allowed chat id live OUTSIDE the repo.

## Standing safety (do not weaken)

- No real Telegram token and no real chat id in the repo. No secrets/.env/cookies/auth
  files. The token is never printed, logged, or committed.
- The bot does not control Ghoti, launch Claude/Codex, enable MCP or browser/computer-use,
  run arbitrary shell, auto-send, install anything, or clone/run external repos.
- `telegram_status_bot_enabled` stays false until the operator opts in on their machine.
- `global_kill_switch` pauses status actions immediately.

## Next safe step (each its own approved milestone)

1. Operator opt-in: run setup on the local laptop, store the token and allowed chat id
   outside the repo, start the bot, confirm `/status` replies.
2. Later, behind new flags after an audited milestone: richer answers summarized by a local
   model (Gemma) or coordinated by Hermes (local llama3.1:8b) through approved wrappers -
   still no live account action, no auto-send.
3. Docker (local, reproducible) only after an audited milestone; VPS only when money allows,
   behind auth + HTTPS, after privacy readiness.

## How to verify (read-only)

```powershell
pwsh -ExecutionPolicy Bypass -File 03_scripts\telegram_status_bot\check_telegram_status_bot.ps1 -NoSecretsRequired
```
