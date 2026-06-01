# Local Worker Queue + Status Brain (N+6.15A)

This directory holds the **data** for Ghoti's first genuinely useful day-to-day
local workflow: a small local worker queue and a status brain. The **code** lives
in `03_scripts/local_worker_queue/`.

The point of N+6.15A is that Ghoti stops being only tests and docs. With one local
command you get the current main/head status, a summary of the latest milestone
report, what is merged vs. pending, computer-use sandbox readiness, repo-intake
progress, a recommended next action, and an optional Obsidian handoff note.

## What is here

- `status_schema_n6_15a.json` — the contract for the status packet produced by
  `ghoti_status_brain.py`.
- `queue_examples/status_summary_task.json` — build the local status packet.
- `queue_examples/computer_use_sandbox_status_task.json` — report confined
  computer-use sandbox readiness using the N+6.14A dry-run only.
- `queue_examples/repo_intake_summary_task.json` — summarize the statically
  inspected computer-use candidate repos (Ruflo, TryCUA / CUA, Browser Harness,
  Vercel agent-browser, UI-TARS).

## How to run

```bash
# One-command local status (no browser, no network, no autonomy):
python 03_scripts/local_worker_queue/ghoti_status_brain.py --json

# Same, and also write the Obsidian handoff note:
python 03_scripts/local_worker_queue/ghoti_status_brain.py --write-handoff --json

# Process a queue task file:
python 03_scripts/local_worker_queue/ghoti_local_worker_queue.py \
  --task 14_context/local_worker_queue/queue_examples/status_summary_task.json --json
```

## Supported vs. blocked task types

Supported (local, read-only): `status_summary`, `computer_use_sandbox_status`,
`repo_intake_summary`.

Blocked by policy (default-deny): `launch_claude`, `launch_codex`, `browser_live`,
`computer_use_live`, `telegram_send`, `email_send`, `whatsapp_send`, `mcp_write`,
`shell_exec`, `install_repo`, `docker_run`. The queue refuses these and reports
`blocked: true` with a reason; it never performs them.

## Safety posture

This is **not** live autonomy, a swarm launcher, live browser/web automation,
Telegram control, MCP, or email/WhatsApp. Everything here is local and offline:
git is used read-only, no external API is called, no account is touched, and no
OS-level click/type happens. Optional summarization uses a **local** Ollama Gemma
model only if it is already installed; if it is not, a deterministic local summary
is used instead. Every risky feature flag defaults to `false`.

## How this becomes useful later (still disabled now)

- **Hermes** can read the generated handoff note
  (`14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md`) instead
  of repeating weak summaries.
- The **Telegram status bot** can later expose this status packet on request. It
  stays disabled by default this milestone.
