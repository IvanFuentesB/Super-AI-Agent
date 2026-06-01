# Next Hermes Integration Task

Source: N+6.10A - Hermes Full Integration Setup Foundation (read-only foundation landed).

## Where we are

Phase 1 is done: a read-only/status-only integration foundation. Five new
`03_scripts/hermes_router/` scripts report JSON status/plans; six
`14_context/hermes_integrations/` notes and five `docs/` guides describe the phased,
approval-gated path. Nothing live is enabled.

## Standing safety (do not weaken)

- No live Telegram, no token in repo, no MCP install, no real provider auth.
- No secrets/.env/tokens/cookies/auth files in the repo, Obsidian, or prompts.
- No browser-use, no computer-use, no account login, no email/WhatsApp login.
- No auto-send. Hermes does not launch Claude or Codex. No arbitrary command execution.

## Next safe step (Phase 2, needs human approval)

1. Design a **status-only** Telegram bot that answers `/status`, `/current_task`,
   `/latest_claude`, `/latest_codex`, `/help` and nothing else (no `/run`).
2. Keep the token out of the repo, Obsidian, and prompts; supply it at run time only.
3. Wire the bot to the existing read-only wrappers; keep `enabled: false` until a human
   approves live enablement.

## After that (later, each its own approved milestone)

Phase 3 read-only scoped filesystem MCP -> Phase 4 local Gemma summary worker (queue +
scheduled summaries, no live account action) -> Phase 5 Claude/Codex launch wrappers
(dry-run first, then approval-gated) -> Phase 6 email/WhatsApp draft-only (no auto-send) ->
Phase 7 browser/computer-use only after the observation harness and an audited
limited-action harness.
