# N+6.10A - Hermes Full Integration Setup Foundation

Status: IMPLEMENTED (safe setup foundation only). This milestone prepares Hermes for a
set of future integrations - a Telegram status bot, a read-only MCP, a provider/plugin
inventory, local model routing, future Claude/Codex launch wrappers, future
email/WhatsApp draft-only agents, and a future 24/7 local worker mode - **as planning
and read-only status only**. It enables **no** live capability.

Author lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Base: origin/main `6cf426b` (N+6.7C). Date: 2026-05-31.

## 1. What this milestone is (and is not)

This is a **read-only / status-only foundation**. Every new script reports JSON and
makes no change to the world: no network call, no install, no launch, no secret access,
and **no arbitrary command execution**. Every integration below is described with a
clear `enabled: false` flag and an explicit approval gate.

- Telegram is **not enabled**. No bot runs and **no token exists** in this repo.
- MCP is **not installed** and **not enabled**. No MCP server is started.
- Browser-use and computer-use are **not enabled**.
- No provider keys are required; the repo holds **no secrets and no provider keys**.
- Hermes **does not launch Claude or Codex**; launch wrappers remain a later, dry-run design.
- Email and WhatsApp are **draft-only** designs with **no auto-send** and no account login.
- The 24/7 local worker mode is **planned but not enabled**.

**Secrets are never stored in the repo, in Obsidian, or in prompts.** Any future token,
key, or credential is supplied at run time only and is never committed.

## 2. Setup order (phased, approval-gated)

**Phase 1 (now): read-only / status-only foundation.** No tokens, no live integrations.
The five new `hermes_router` scripts report JSON status/plan only.

**Phase 2: Telegram status bot only.** First commands are status-only - `/status`,
`/current_task`, `/latest_claude`, `/latest_codex`, `/help`. There is **no `/run`** and
no send/delete/login/post/buy/trade. The first Telegram phase is status-only.

**Phase 3: filesystem MCP, read-only.** A read-only filesystem MCP scoped to
`14_context/agent_handoff_vault`, `docs`, `14_context/tool_intake`, and
`14_context/hermes_integrations`. No write MCP, no browser MCP, no account/social MCP,
no unrestricted root filesystem MCP.

**Phase 4: local Gemma summary worker.** Queue files and scheduled summaries run by a
local Gemma worker. No live account actions. Stays disabled until approved.

**Phase 5: Claude/Codex launch wrappers (dry-run first).** Launch wrappers are designed
dry-run; live launch is approval-gated. Hermes does not launch Claude or Codex in this
milestone.

**Phase 6: email/WhatsApp draft-only.** Draft-only agents with **no auto-send**, no login
credentials in the repo, no mass replies, and no deleting/archiving/moving messages
without approval.

**Phase 7: browser/computer-use (last).** Only after the observation harness, approval
gates, and an audited limited-action harness are in place. Not part of this milestone.

## 3. Files added

Docs (5): this file, `GHOTI_TELEGRAM_STATUS_BOT_SETUP.md`, `GHOTI_MCP_READ_ONLY_SETUP.md`,
`GHOTI_HERMES_PROVIDER_PLUGIN_INVENTORY.md`, `GHOTI_24_7_LOCAL_WORKER_PLAN.md`.

Integration notes (6) under `14_context/hermes_integrations/`:
`HERMES_INTEGRATION_STATUS.md`, `TELEGRAM_STATUS_BOT_PLAN.md`, `MCP_READ_ONLY_PLAN.md`,
`PROVIDER_PLUGIN_INVENTORY.md`, `LOCAL_MODEL_ROUTING_PLAN.md`,
`EMAIL_WHATSAPP_DRAFT_ONLY_PLAN.md`.

Handoff (1): `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_HERMES_INTEGRATION_TASK.md`.

Scripts (5) under `03_scripts/hermes_router/`: `hermes_integration_status.ps1`,
`telegram_status_bot_plan.ps1`, `mcp_read_only_plan.ps1`, `provider_plugin_inventory.ps1`,
`local_worker_status.ps1`. Each is read-only/planning, emits JSON, needs no secret, and
returns clear `enabled: false` flags.

Test (1): `01_projects/runtime_mvp/tests/test_n6_10a_hermes_full_integration_setup.py`.
Report (1): `14_context/claude_n6_10a_hermes_full_integration_setup.md`.

## 4. Script contract (all five)

All scripts are read-only/status/planning by default, emit a single JSON object, require
no secrets, install nothing, run no live Telegram or MCP, open no browser/computer-use,
call no external APIs, never launch Claude or Codex, and **never run arbitrary commands**.
They build on the existing wrapper style in `03_scripts/hermes_router/`: Hermes runs
**approved wrappers only**.

## 5. What is explicitly NOT enabled by this milestone

- No live Telegram, no real token, no MCP install, no real provider auth.
- No secrets, `.env`, tokens, cookies, or auth files in the repo.
- No browser-use, no computer-use, no account login, no email/WhatsApp login.
- No external repo clone/install/run, no arbitrary command execution.
- No auto-sent email or message. `main` is untouched; only the feature branch is pushed.
