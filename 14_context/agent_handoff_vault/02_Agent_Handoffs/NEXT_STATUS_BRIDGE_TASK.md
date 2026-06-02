# Next task: Status Bridge for Telegram + Hermes

Status-only handoff note. This describes the next safe, local step around the N+6.16A
status bridge. It authorizes no live control, no remote command, no agent launch, and no
secrets in the repo.

## Where things stand

- The status bridge (`03_scripts/status_bridge/ghoti_status_bridge.py`) renders the
  N+6.15A status brain as `--json`, `--markdown`, and `--telegram-safe-json`, and can write
  a Hermes-readable handoff note with `--write-hermes-handoff`.
- The status-only Telegram bot can read the bridge for `/status` when the runtime config
  opts in (`status_bridge_enabled` + `use_status_bridge_for_telegram_status`, both default
  false). Otherwise it keeps its deterministic built-in status.
- New global feature flags `status_bridge_enabled`, `hermes_status_bridge_enabled`, and
  `status_bridge_auto_handoff_enabled` all default false.

## Useful commands

```
python 03_scripts/status_bridge/ghoti_status_bridge.py --json
python 03_scripts/status_bridge/ghoti_status_bridge.py --write-hermes-handoff --json
python 03_scripts/status_bridge/ghoti_status_bridge.py --telegram-safe-json
powershell -ExecutionPolicy Bypass -File 03_scripts/status_bridge/check_status_bridge.ps1
```

## Suggested next step (when approved)

If you want Hermes to always have fresh state, schedule the **local** handoff write
(`--write-hermes-handoff`) from an approved local wrapper and point Hermes at
`14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`. Keep it local
and read-only; do not add any send, remote, or agent-launch behavior.

## Out of scope / still disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS click/type,
account login, email/WhatsApp, auto-send, external API, installs, and third-party code
execution remain disabled. The Telegram token and chat id stay outside the repo.
