# Ghoti N+6.15A — Useful Local Worker Queue + Ghoti Status Brain

## What this milestone adds

N+6.15A is the point where Ghoti stops being only tests and docs and becomes
genuinely useful day-to-day. With **one local command** you get a concise picture
of the project and a recommended next action — built entirely from local, offline,
read-only data.

```bash
python 03_scripts/local_worker_queue/ghoti_status_brain.py --json
```

That single command answers:

- current `origin/main` head and the last few commits,
- a summary of the latest milestone report (Claude and Codex),
- how many `n6` tests exist,
- whether the confined computer-use sandbox is dry-run ready,
- how the computer-use repo intake is progressing,
- the current Hermes and Telegram posture,
- a concrete **next recommended action**.

Add `--write-handoff` and the same run also writes an Obsidian handoff note that a
later Hermes step can read instead of re-deriving a weaker summary.

## The two pieces

- **`ghoti_status_brain.py`** — builds the status packet (see
  `14_context/local_worker_queue/status_schema_n6_15a.json` for the contract).
  Git is used read-only only (`rev-parse`, `log`, `status`, `branch
  --show-current`). It can optionally run the confined sandbox **dry-run** and can
  optionally summarize with a local Gemma model.
- **`ghoti_local_worker_queue.py`** — processes one local queue task JSON file. It
  supports a small set of safe, read-only task types and refuses everything else
  by default.

The example queue tasks live under
`14_context/local_worker_queue/queue_examples/`: a daily status summary, a
computer-use sandbox readiness check (dry-run only), and a computer-use repo
intake summary.

## It uses real progress, not planning-only

The status brain reports against work Ghoti has actually done: it reads the
committed milestone reports, reflects the N+6.14A confined computer-use sandbox
runner readiness (via its safe dry-run), and summarizes the statically inspected
computer-use candidate repos (Ruflo, TryCUA / CUA, Browser Harness, Vercel
agent-browser, and UI-TARS). It is a status view over real repo-intake and
computer-use progress, not a planning-only document.

## Optional local Gemma summarization

If `--use-gemma-if-available` is passed, the brain checks for a local Ollama
install and a `gemma3:4b` model. If both are present it asks the **local** model
to compress the status into a few bullet points; the prompt contains only the
non-secret local status summary. If Ollama or the model is not present — or the
call fails or times out — the brain uses a deterministic local summary instead.
Repo contents are never sent to an external API, and no model is downloaded or
installed by this milestone.

## How this becomes useful later (still disabled now)

- **Hermes** can read the generated handoff note
  (`14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md`) so the
  coordinator stops repeating weak, hand-written summaries.
- The **Telegram status bot** can later expose this status packet on request. It
  stays disabled by default this milestone; only `telegram_status_commands_enabled`
  remains the single enabled flag in the example config.

## How it stays safe

- **Not live autonomy.** This is not a swarm launcher and starts no agents. The
  queue blocks `launch_claude`, `launch_codex`, and any unrecognized task type by
  default-deny.
- **Local and offline.** No internet, no GitHub CLI, no external API, no account
  login, and no secrets are read. Git is read-only.
- **No live browser / no OS input.** The computer-use task only ever runs the
  N+6.14A confined sandbox **dry-run**, which launches no browser and performs no
  DOM action. The brain never moves a mouse, never presses a key, and never
  controls the desktop.
- **No Telegram control, no MCP, no email/WhatsApp, no auto-send.** Those task
  types are blocked.
- **No shell execution.** `subprocess` is always invoked with an argument list;
  no shell string is ever used and there is no `Invoke-Expression`.
- **No installs, no Docker.** `install_repo` and `docker_run` are blocked and
  nothing is installed.
- **Disabled by default.** Six dedicated feature flags
  (`local_worker_queue_enabled`, `local_status_brain_enabled`,
  `local_gemma_summary_enabled`, `auto_schedule_worker_enabled`,
  `telegram_status_bridge_enabled`, `hermes_memory_writer_enabled`) all default to
  `false`; the global kill switch still overrides everything.

## What remains disabled

Live autonomy and agent launching; live website navigation and live browser
automation; OS-level mouse/keyboard input and desktop control; Telegram control
and message sending; MCP writes; email and WhatsApp; auto-send; arbitrary shell
execution; running third-party repository code; dependency installation; Docker
runtime; and any outbound API or account action. Every risky feature flag defaults
to `false`.

## Next step

`N+6.15B` (merge gate) or the next milestone can wire the Telegram status bot and
a Hermes memory step to **read** this status packet and handoff note, still under
separate review, before any live action is considered. Until then the queue stays
local, offline, and read-only.
