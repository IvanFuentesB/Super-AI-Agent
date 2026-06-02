# Ghoti Status Bridge for Telegram + Hermes (N+6.16A)

This milestone connects the N+6.15A local status brain to the places you actually open
Ghoti - the Telegram status bot, Hermes Desktop/CLI, an Obsidian handoff vault, and local
PowerShell - through one small, local, read-only **status bridge**. It is status-only.
There is no remote control, no `/run`, no live agent launch, no MCP, no live
browser/computer-use, no email or WhatsApp, no auto-send, and no account automation.

## The problem this solves

Two different complaints had the same root cause: every surface was inventing its own
weak status summary.

- **Hermes repeats itself.** Hermes (the local desktop/CLI assistant) keeps giving the
  same generic summary. That is not a mystery: it is given **repetitive prompts** and the
  **local Llama model is limited**, so when it has no fresh, structured status to read it
  falls back to the same boilerplate. The fix is not a bigger prompt; the better memory
  path is a **structured status file and handoff note** that Hermes can read.
- **The Hermes Desktop app is not a smarter brain.** The Hermes Desktop app improves the
  UI and how you launch and use Ghoti. It does not make the model smarter and does not
  improve the model's reasoning or intelligence. Convenience and reasoning are different
  things; this milestone improves the *plumbing*, not the model.
- **Telegram `/status` was hardcoded.** The status-only Telegram bot answered `/status`
  from a small built-in string instead of the real status brain.

## The fix: one status source, many readers

`03_scripts/status_bridge/ghoti_status_bridge.py` reads the status brain once and renders
it for each surface:

- `--json` - the full status packet for tools.
- `--markdown` - the same status as Markdown for Obsidian / a Hermes note.
- `--telegram-safe-json` - a short, sanitized, length-bounded text for a Telegram reply.
- `--write-hermes-handoff` - also write a Hermes-readable handoff note.

So **Hermes, Desktop, Telegram, and PowerShell can all read one status source** instead of
each repeating its own guess. Concretely, **Hermes should read the status bridge and the
handoff note instead of repeating a generic summary**: point Hermes at
`14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md` (written by
`--write-hermes-handoff`) and it has the real `origin/main`, branch, test count, and latest
reports to work from.

## Useful local commands

Generate Ghoti status (full packet):

```
python 03_scripts/status_bridge/ghoti_status_bridge.py --json
```

Write a Hermes-readable handoff note (one status source for Hermes/Obsidian):

```
python 03_scripts/status_bridge/ghoti_status_bridge.py --write-hermes-handoff --json
```

Produce a Telegram-safe status text (sanitized, length-bounded):

```
python 03_scripts/status_bridge/ghoti_status_bridge.py --telegram-safe-json
```

Check the bridge is healthy and safe (file presence, three modes, safety flags):

```
powershell -ExecutionPolicy Bypass -File 03_scripts/status_bridge/check_status_bridge.ps1
```

Check the Telegram bot runtime readiness (no secret needed) and a start dry-run:

```
powershell -ExecutionPolicy Bypass -File 03_scripts/telegram_status_bot/check_telegram_status_bot.ps1 -NoSecretsRequired
powershell -ExecutionPolicy Bypass -File 03_scripts/telegram_status_bot/start_telegram_status_bot.ps1 -DryRun
```

## Telegram `/status` now reads the status brain (opt-in, off by default)

The Telegram bot can answer `/status` from the bridge **only** when the runtime config
sets both `status_bridge_enabled` and `use_status_bridge_for_telegram_status` to true.
Both default false, so out of the box `/status` keeps its deterministic built-in status.
When enabled, the bot imports the bridge as a local module - it adds no new subprocess of
its own, so the bot's only subprocess remains the read-only `git` lookup - and it falls
back to the built-in status if the bridge is unavailable.

The bot command surface is unchanged and remains status-only: `/status`, `/current_task`,
`/latest_claude`, `/latest_codex`, `/help`, and `/flags` are read-only, and the blocked
commands (`/run`, `/send`, `/login`, `/post`, `/buy`, `/trade`, `/delete`, `/mcp`,
`/browser`, `/computer`, `/email`, `/whatsapp`, `/install`, `/clone`, `/shell`, `/exec`,
`/deploy`, `/agent`, `/claude`, `/codex`) stay blocked with no handler. **Telegram stays
status-only: there is no `/run` and no live control.**

## Safety

- **No secrets in the repo.** The bridge needs no Telegram token and no chat id. The bot
  token and the allowed chat id continue to live **outside the repo** and are never
  committed.
- **Local and read-only.** The bridge opens no network connection, calls no external API,
  launches no agent, controls no browser or desktop, sends nothing, installs nothing, and
  runs no third-party code. Its only subprocess is the local, read-only status-brain call,
  made with an argument list (never a shell string, never `Invoke-Expression`).
- **Off by default.** The new feature flags - `status_bridge_enabled`,
  `hermes_status_bridge_enabled`, and `status_bridge_auto_handoff_enabled` - all default
  false in `23_configs/ghoti_feature_flags.example.json`, where only the read-only
  `telegram_status_commands_enabled` toggle defaults true.
- **Approval gates intact.** Nothing here weakens an approval gate. Live control, remote
  command, and agent launch remain future, separately-approved milestones.

## What stays disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS-level
click/type, account login automation, email/WhatsApp drafting, auto-send, external API
calls, installs, Docker/VPS runtime, and third-party code execution are all still disabled
and out of scope for this milestone.
