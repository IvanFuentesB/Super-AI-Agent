# Ghoti Telegram Status Bot - Setup Guide (Phase 2, status-only)

Status: **planned_only**. Telegram is **not enabled** by this milestone. No bot runs and
**no token exists** in this repo. This guide describes the *future* Phase-2 setup so a
human can enable a **status-only** bot later, under approval.

## The first Telegram phase is status-only

The first Telegram phase is status-only. The bot answers read-only status questions and
nothing else. There is **no `/run`** and no command that sends, deletes, logs in, posts,
buys, or trades.

### Allowed first commands

- `/status` - overall Ghoti/Hermes status
- `/current_task` - the current classified task
- `/latest_claude` - the latest Claude implementation summary
- `/latest_codex` - the latest Codex audit summary
- `/help` - list the allowed commands

### Forbidden commands (not implemented)

`/run`, `/send`, `/delete`, `/login`, `/post`, `/buy`, `/trade`.

## Token-storage rule

A bot token is **never in the repo, never in Obsidian, never in prompts**. Secrets are
never stored in the repo, in Obsidian, or in prompts. A human creates the token
out-of-band; it is supplied at run time only (for example a local environment variable)
and is never committed.

## Setup steps (for the future, approval-gated)

1. A human creates a Telegram bot token out-of-band (not in the repo, Obsidian, or any prompt).
2. The token is provided at run time only and never committed.
3. The bot is wired to the read-only status wrappers and answers status-only commands.
4. No `/run` and no send/delete/login/post/buy/trade command is implemented.
5. Live enablement requires explicit human approval. Until then, `enabled: false`.

## Not enabled now

Telegram is not enabled. No token exists in this repo. `requires_human_approval: true`.
