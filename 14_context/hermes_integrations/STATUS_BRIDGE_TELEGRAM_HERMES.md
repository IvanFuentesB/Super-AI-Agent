# Hermes integration note: Status Bridge for Telegram + Hermes (N+6.16A)

Status-only. This note tells Hermes (the local desktop/CLI assistant) how to read one
real status source instead of repeating a generic summary. Nothing here gives Hermes,
the Desktop app, or Telegram any control over Ghoti.

## Read one source, stop repeating yourself

Hermes repeats itself because it is given repetitive prompts and the local Llama model is
limited; with no fresh, structured status to read it falls back to boilerplate. The better
memory path is a structured status file and handoff note. **Hermes should read the status
bridge and the handoff note instead of repeating a generic summary.**

- Full status packet (for tools / parsing):
  `python 03_scripts/status_bridge/ghoti_status_bridge.py --json`
- Markdown status (for an Obsidian pane or a prompt context block):
  `python 03_scripts/status_bridge/ghoti_status_bridge.py --markdown`
- Write the Hermes-readable handoff note, then read it:
  `python 03_scripts/status_bridge/ghoti_status_bridge.py --write-hermes-handoff --json`
  -> `14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`

The handoff note carries the real `origin/main`, current branch, n6 test count, the latest
Claude report, the latest Codex audit, and the next recommended action - the facts Hermes
needs so it does not guess.

## Desktop is a better door, not a bigger brain

The Hermes Desktop app improves the UI and how you launch and use Ghoti. It does not make
the model smarter and does not improve the model's reasoning or intelligence. Use Desktop
for convenience; use the status bridge and handoff note for accurate state.

## Telegram stays status-only

Telegram `/status` can read this same bridge when the runtime config opts in
(`status_bridge_enabled` + `use_status_bridge_for_telegram_status`, both default false),
and otherwise keeps its deterministic built-in status. Telegram stays status-only: there
is no `/run` and no live control, and the bot token and chat id live outside the repo.

## Safety

Local and read-only: no Telegram token or chat id in the repo, no network, no external
API, no agent launch, no MCP, no browser/computer-use, no OS click/type, no email or
WhatsApp, no auto-send, no installs, no third-party code execution. Approval gates are
unchanged.
