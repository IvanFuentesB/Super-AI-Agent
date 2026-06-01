# Telegram Status Bot Plan (Phase 2, planned_only)

Status: **planned_only**. Telegram is **not enabled**; no token exists in this repo. This
note mirrors `telegram_status_bot_plan.ps1`.

## The first Telegram phase is status-only

The bot answers status-only commands and nothing else.

- **Allowed first commands:** `/status`, `/current_task`, `/latest_claude`,
  `/latest_codex`, `/help`.
- **Forbidden commands:** `/run`, `/send`, `/delete`, `/login`, `/post`, `/buy`, `/trade`.

## Token-storage rule

The token is **never in repo, never in Obsidian, never in prompts**. It is supplied at
run time only and never committed.

## Flags

`enabled: false`. `requires_human_approval: true`. `token_present: false`.
`network_used: false`.
