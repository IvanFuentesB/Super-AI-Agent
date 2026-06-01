# N+6.10A - Hermes Full Integration Setup Foundation (implementation report)

Status: **IMPLEMENTED** - safe setup foundation only. This milestone prepares Hermes for a
set of future integrations (a Telegram status bot, a read-only MCP, a provider/plugin
inventory, local model routing, future Claude/Codex launch wrappers, future email/WhatsApp
draft-only agents, and a future 24/7 local worker mode) as **planning and read-only status
only**. It enables **no** live capability.

## Lane facts

- **Branch:** `feat/ghoti-agent-claude-n6-10a-hermes-full-integration-setup`
- **Worktree:** `.claude/worktrees/n6_10a_hermes_full_integration_setup` (repo-contained)
- **Base main:** `6cf426b` (N+6.7C). Later `origin/main` is neither depended on nor pushed.
- **Author/committer:** repo identity only; no AI attribution in commit metadata.

## What this milestone is (and is not)

This is a **read-only / status-only foundation**. Every new script reports JSON and makes no
change to the world: no network call, no install, no launch, no secret access, and **no
arbitrary command execution**. Every integration is described with a clear `enabled: false`
flag and an explicit approval gate.

- Telegram is **not enabled**; no bot runs and **no token exists** in this repo.
- MCP is **not installed** and **not enabled**; no MCP server is started.
- Browser-use and computer-use are **not enabled**.
- No provider keys are required; the repo holds **no secrets and no provider keys**.
- Hermes **does not launch Claude or Codex**; launch wrappers remain a later dry-run design.
- Email and WhatsApp are **draft-only** designs with **no auto-send** and no account login.
- The 24/7 local worker mode is **planned but not enabled**.

**Secrets are never stored in the repo, in Obsidian, or in prompts.** Any future token, key,
or credential is supplied at run time only and is never committed.

## Files added (19)

Docs (5) under `docs/`: `GHOTI_N6_10A_HERMES_FULL_INTEGRATION_SETUP.md`,
`GHOTI_TELEGRAM_STATUS_BOT_SETUP.md`, `GHOTI_MCP_READ_ONLY_SETUP.md`,
`GHOTI_HERMES_PROVIDER_PLUGIN_INVENTORY.md`, `GHOTI_24_7_LOCAL_WORKER_PLAN.md`.

Integration notes (6) under `14_context/hermes_integrations/`: `HERMES_INTEGRATION_STATUS.md`,
`TELEGRAM_STATUS_BOT_PLAN.md`, `MCP_READ_ONLY_PLAN.md`, `PROVIDER_PLUGIN_INVENTORY.md`,
`LOCAL_MODEL_ROUTING_PLAN.md`, `EMAIL_WHATSAPP_DRAFT_ONLY_PLAN.md`.

Handoff (1): `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_HERMES_INTEGRATION_TASK.md`.

Scripts (5) under `03_scripts/hermes_router/`: `hermes_integration_status.ps1`,
`telegram_status_bot_plan.ps1`, `mcp_read_only_plan.ps1`, `provider_plugin_inventory.ps1`,
`local_worker_status.ps1`. Each is read-only/planning, emits JSON, needs no secret, and
returns clear `enabled: false` flags.

Test (1): `01_projects/runtime_mvp/tests/test_n6_10a_hermes_full_integration_setup.py`.
Report (1): this file.

## Setup phases (phased, approval-gated)

1. **Phase 1 (this milestone):** read-only / status-only foundation. No tokens, no live integrations.
2. **Phase 2:** a status-only Telegram bot (`/status`, `/current_task`, `/latest_claude`, `/latest_codex`, `/help`); no `/run`.
3. **Phase 3:** a read-only, scoped filesystem MCP (vault, docs, tool_intake, hermes_integrations).
4. **Phase 4:** a local Gemma summary worker over queue files; disabled until approved.
5. **Phase 5:** Claude/Codex launch wrappers, designed dry-run first; live launch is approval-gated.
6. **Phase 6:** email/WhatsApp draft-only agents with no auto-send and no login credentials in the repo.
7. **Phase 7:** browser/computer-use last, only after an observation harness and an audited limited-action harness.

## Script smoke results

All five scripts ran via `powershell -ExecutionPolicy Bypass -File ...` and emitted valid JSON.

| Script | Key reported flags |
|--------|--------------------|
| `hermes_integration_status.ps1` | telegram_enabled=false, mcp_enabled=false, browser_use_enabled=false, computer_use_enabled=false, live_agent_launch_enabled=false, email_whatsapp_enabled=false, arbitrary_command_execution_enabled=false, secrets_in_repo=false, local_only=true |
| `telegram_status_bot_plan.ps1` | status_bot_phase=planned_only, enabled=false, token_present=false, network_used=false, requires_human_approval=true, local_only=true |
| `mcp_read_only_plan.ps1` | mcp_phase=planned_only, first_mcp=filesystem_read_only, enabled=false, install_performed=false, network_used=false, requires_human_approval=true, local_only=true |
| `provider_plugin_inventory.ps1` | hermes_model=llama3.1:8b, cheap_worker_model=gemma3:4b, cloud_provider_keys_expected_in_repo=false, kimi_configured=false, anthropic_configured=false, github_configured=false, browser_plugins_enabled=false, local_only=true |
| `local_worker_status.ps1` | local_workers_planned=true, gemma_summary_worker_enabled=false, queue_enabled=false, scheduled_jobs_enabled=false, twenty_four_seven_mode_enabled=false, network_used=false, local_only=true |

## Validation results

- `git diff --check`: clean (no whitespace errors).
- N+6.10A tests: `test_n6_10a_hermes_full_integration_setup` - 16 passed, 0 failed.
- Full N+6 suite: `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py"` - 93 passed, 0 failed.
- Public-repo security audit: `python 03_scripts/public_repo_security_audit.py --run --json` - 0 failed checks; no new blocking findings versus baseline.
- Generated validation residue (if any) was restored; only the 19 intended files remain staged.

## Safety verdict

- No live Telegram, no real token, no MCP install, no real provider auth.
- No secrets, `.env`, tokens, cookies, or auth files in the repo, in Obsidian, or in prompts.
- No browser-use, no computer-use, no account login, no email/WhatsApp login.
- No external repo clone/install/run, no arbitrary command execution.
- No auto-sent email or message. Hermes does not launch Claude or Codex.
- `main` is untouched; only the feature branch is pushed.

## What is still NOT enabled

Live Telegram, real tokens, MCP install/runtime, real provider auth, browser-use,
computer-use, account/email/WhatsApp login, auto-send, autonomous Claude/Codex launch, the
24/7 worker, queues, and scheduled jobs all remain disabled and approval-gated.

## Direct safety answers

- Telegram enabled? No (`telegram_enabled: false`; no token in repo).
- MCP installed/enabled? No (`mcp_enabled: false`, `install_performed: false`).
- Provider keys in repo? No (`cloud_provider_keys_expected_in_repo: false`, `secrets_in_repo: false`).
- Browser/computer-use enabled? No.
- Did Hermes launch Claude or Codex? No (`live_agent_launch_enabled: false`).
- Auto-send email/WhatsApp? No (`email_whatsapp_enabled: false`, draft-only design).
- Arbitrary command execution? No (`arbitrary_command_execution_enabled: false`).
- Approval gates intact? Yes; every phase past Phase 1 requires explicit human approval.

## Codex audit target

Audit branch: `feat/ghoti-agent-claude-n6-10a-hermes-full-integration-setup` (this same feature branch).

## Final verdict

IMPLEMENTED_AND_PUSHED - read-only/status-only foundation; no live capability enabled.
