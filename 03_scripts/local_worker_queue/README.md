# Local Worker Queue + Status Brain scripts (N+6.15A)

The first genuinely useful day-to-day local Ghoti workflow. One local command
turns the repo into a concise status packet (and an optional Obsidian handoff
note). Everything here is local, offline, and read-only.

## Scripts

- `ghoti_status_brain.py` - builds the local status packet: origin/main head and
  recent commits, latest Claude/Codex milestone reports, n6 test count,
  computer-use sandbox readiness (dry-run only), repo-intake progress, Hermes and
  Telegram posture, and a concrete next recommended action. Optionally writes an
  Obsidian handoff note and can summarize with a local Ollama Gemma model.
- `ghoti_local_worker_queue.py` - processes one local queue task JSON file. It
  supports a small set of safe read-only task types and refuses everything else.
- `check_local_worker_queue.ps1` - emits a JSON status of files, flags, and the
  safe posture.

## Run

```bash
# One-command local status (no browser, no network, no autonomy):
python 03_scripts/local_worker_queue/ghoti_status_brain.py --json

# Also write the Obsidian handoff note:
python 03_scripts/local_worker_queue/ghoti_status_brain.py --write-handoff --json

# Include the confined computer-use sandbox dry-run (no browser launch):
python 03_scripts/local_worker_queue/ghoti_status_brain.py \
  --include-computer-use-sandbox --json

# Summarize with a local Gemma model if one is installed (falls back otherwise):
python 03_scripts/local_worker_queue/ghoti_status_brain.py \
  --use-gemma-if-available --json

# Process a queue task file:
python 03_scripts/local_worker_queue/ghoti_local_worker_queue.py \
  --task 14_context/local_worker_queue/queue_examples/status_summary_task.json --json

powershell -ExecutionPolicy Bypass -File \
  03_scripts/local_worker_queue/check_local_worker_queue.ps1
```

## Task types

Supported (local, read-only): `status_summary`, `computer_use_sandbox_status`,
`repo_intake_summary`.

Blocked by default-deny policy (never performed): `launch_claude`,
`launch_codex`, `browser_live`, `computer_use_live`, `telegram_send`,
`email_send`, `whatsapp_send`, `mcp_write`, `shell_exec`, `install_repo`,
`docker_run`, and any unrecognized type.

## Safety

Git is used read-only (`rev-parse`, `log`, `status`, `branch --show-current`).
`subprocess` is always called with an argument list, never via a shell string. No
internet, no GitHub CLI, no external API, no account, no Telegram control, no
MCP, no email/WhatsApp, no auto-send, no live browser, and no OS-level
click/type. Optional summarization uses a local Ollama Gemma model only if it is
already installed; otherwise a deterministic local summary is used. The data
files and the schema live under `14_context/local_worker_queue/`.

## How this becomes useful later (still disabled now)

- Hermes can later read the generated handoff note
  (`14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md`)
  instead of repeating weak summaries.
- The Telegram status bot can later expose this status packet on request; it
  stays disabled by default this milestone.
