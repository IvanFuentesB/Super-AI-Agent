# Ghoti Status Bridge (N+6.16A)

One local, read-only entry point that turns the N+6.15A status brain into the shapes
the places you actually open Ghoti can read: Telegram, Hermes Desktop/CLI, an Obsidian
handoff vault, and local PowerShell. It is **status-only**. It does not control Ghoti,
launch any agent, enable MCP, drive a browser or the desktop, send anything, install
anything, run third-party code, or call any external API.

## Why this exists

The status brain (`03_scripts/local_worker_queue/ghoti_status_brain.py`) already knows
the real state: `origin/main`, the current branch, the n6 test count, the latest Claude
report, the latest Codex audit, and what stays disabled. The bridge takes that one source
of truth and renders it for each surface, so Telegram `/status`, a Hermes handoff note,
and a PowerShell health check can all read the **same** status instead of each inventing
its own weaker summary.

## Commands

```
python 03_scripts/status_bridge/ghoti_status_bridge.py --json
python 03_scripts/status_bridge/ghoti_status_bridge.py --markdown
python 03_scripts/status_bridge/ghoti_status_bridge.py --telegram-safe-json
python 03_scripts/status_bridge/ghoti_status_bridge.py --write-hermes-handoff --json
```

| Flag | Output |
|------|--------|
| `--json` | The full status packet (brain packet plus a `source` tag) as JSON. |
| `--markdown` | The same status rendered as Markdown for Obsidian / a Hermes note. |
| `--telegram-safe-json` | A short, sanitized, length-bounded text safe to post in a Telegram reply, wrapped in a small JSON envelope. |
| `--write-hermes-handoff` | Also write the Hermes-readable handoff note (only with this explicit flag). |
| `--use-gemma-if-available` | Forward the local-Gemma flag to the brain. Off by default; the brain uses its deterministic summary otherwise. |
| `--timeout N` | Status-brain subprocess timeout in seconds (default 20). |

The Hermes handoff note is written to
`14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`, and only when
`--write-hermes-handoff` is passed.

## How it stays safe

- It calls the local status brain as a read-only subprocess using an **argument list
  only** - never a shell string, never `Invoke-Expression`. There is a timeout, and if the
  brain is missing or fails the bridge returns a deterministic local fallback packet.
- It needs **no Telegram token and no chat id**, opens no network connection, calls no
  external API, launches no agent, and controls no browser or desktop.
- Gemma is **off by default**. The local Gemma summary only runs when the caller passes
  `--use-gemma-if-available`, which is forwarded to the brain.
- Output is scrubbed for secret-shaped substrings and stripped of non-printable
  characters before it is ever shaped for Telegram.

## How the Telegram bot uses it (opt-in, off by default)

The status-only Telegram bot (`03_scripts/telegram_status_bot/ghoti_telegram_status_bot.py`)
can answer `/status` from this bridge **only** when the runtime config sets both
`status_bridge_enabled` and `use_status_bridge_for_telegram_status` to true. Both default
false, so out of the box `/status` keeps its deterministic built-in status. When enabled,
the bot imports the bridge as a local module (it adds no new subprocess of its own) and
falls back to the built-in status if the bridge is unavailable. Telegram stays
status-only: there is no `/run` and no live control.

## Health check

```
powershell -ExecutionPolicy Bypass -File 03_scripts/status_bridge/check_status_bridge.ps1
```

Emits one JSON object confirming the bridge, the status brain, and the Telegram bot
scripts exist, that the handoff log directory is present, that the three bridge modes
produce output, that no token is required, and that the risky feature flags default false.
