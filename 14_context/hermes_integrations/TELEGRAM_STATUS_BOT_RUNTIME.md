# Telegram Status Bot Runtime (N+6.10C, status-only)

Status: **runtime pack landed, bot disabled by default.** `telegram_status_bot_enabled`
defaults false; the operator opts in on their own machine. No real token and no real chat
id are in this repo.

This note mirrors the runtime pack under `03_scripts/telegram_status_bot/` and the doc
`docs/GHOTI_N6_10C_TELEGRAM_STATUS_BOT_RUNTIME.md`.

## What it is

A plain Python long-polling bot (standard library + Telegram Bot API) that replies only to
read-only status commands from a single allowed chat id.

- **Allowed:** `/start`, `/status`, `/current_task`, `/latest_claude`, `/latest_codex`,
  `/help`, `/flags`.
- **Blocked:** `/run`, `/send`, `/login`, `/post`, `/buy`, `/trade`, `/delete`, `/mcp`,
  `/browser`, `/computer`, `/email`, `/whatsapp`, `/install`, and more - refused, no handler.

## Secrets outside the repo

The token and the allowed chat id are read from files under the user home
(`~/.ghoti_secrets`), **outside the repo**. The token is never printed, logged, or
committed.

## Why the previous bot did not reply

It did not reply because the **polling process was not running** - **not because Llama was
unsupported**. Status replies need no local model. Hermes/Llama routing arrives later via
approved wrappers, behind its own flags.

## Still disabled

No Ghoti control, no Claude/Codex launch, no MCP, no browser/computer-use, no auto-send,
no arbitrary shell. All gated behind feature flags that default false.
