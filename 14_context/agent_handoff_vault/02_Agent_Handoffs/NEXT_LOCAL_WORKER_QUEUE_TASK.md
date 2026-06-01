# Next Local Worker Queue Task

Source: N+6.15A - Useful Local Worker Queue + Ghoti Status Brain (local read-only
workflow landed).

## Where we are

The first genuinely useful local workflow is in place. One command,
`python 03_scripts/local_worker_queue/ghoti_status_brain.py --json`, produces a
status packet (origin/main head, latest Claude/Codex reports, n6 test count,
computer-use sandbox dry-run readiness, repo-intake progress, Hermes/Telegram
posture, and a next recommended action). With `--write-handoff` it also writes
`14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md`. The local
worker queue (`ghoti_local_worker_queue.py`) runs the safe task types
`status_summary`, `computer_use_sandbox_status`, and `repo_intake_summary`, and
blocks everything else by default-deny. Everything is local, offline, and
read-only.

## Standing safety (do not weaken)

- No live autonomy, no agent launch (Claude/Codex), no swarm.
- No live browser/website automation, no OS-level click/type, no desktop control.
- No Telegram control, no MCP writes, no email/WhatsApp, no auto-send.
- No installs, no Docker runtime, no third-party repository code execution.
- No external API, no account login, no secrets/tokens in the repo or prompts.
- `subprocess` is argument-list only; no shell string, no `Invoke-Expression`.
- Optional Gemma summarization is local Ollama only, with a deterministic fallback.

## Next safe step (needs human approval)

1. Add a **read-only** Hermes step that loads
   `04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md` and uses it as the coordinator status,
   instead of repeating weaker hand-written summaries. Keep
   `hermes_memory_writer_enabled` `false` until a human approves it.
2. Teach the existing status-only Telegram bot to surface this status packet on a
   read-only command. Keep `telegram_status_bridge_enabled` `false` until approved;
   only `telegram_status_commands_enabled` stays enabled.

## After that (later, each its own approved milestone)

Scheduled local summaries (queue + timer, no live action) ->
local Gemma quality evaluation on the summaries ->
draft-only outbound (no auto-send) ->
live computer-use only after the observation harness and an audited
limited-action harness are both approved.
