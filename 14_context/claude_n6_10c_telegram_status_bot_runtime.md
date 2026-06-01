# N+6.10C - Telegram Status Bot Runtime Pack + Feature Flags + Kill Switches

## Summary

Turned the manual GhotiDeepBot experiment into a safe, repo-backed, testable runtime
pack. The bot is **status-only**: it long-polls the Telegram Bot API and replies only to
read-only status commands from a single allowed chat id. It does not control Ghoti, launch
Claude/Codex, enable MCP or browser/computer-use, run arbitrary shell, auto-send, install
anything, or run external repo code. Every risky capability sits behind a feature flag that
defaults false, with a global kill switch that overrides them all.

## Branch / base / dependency

- **Branch:** `feat/ghoti-agent-claude-n6-10c-telegram-status-bot-runtime`
- **Base used:** `origin/main` at `fbd64d6ebe03527107ba8f5000d84770c6cc7753`
  (the feature branch was created from the N+6.10A tip `f10b2f6`, then fast-forwarded onto
  current `origin/main`, which already contains N+6.10A).
- **Depends on N+6.10A:** Yes - but N+6.10A is **already merged into `origin/main`**
  (merge commit `9c8f052 merge(ghoti): land Hermes integration setup foundation`), so this
  pack builds directly on main. No separate unmerged dependency remains.

## Files created (17)

Runtime scripts (`03_scripts/telegram_status_bot/`):
- `ghoti_telegram_status_bot.py` - status-only Python poll loop (standard library only)
- `setup_telegram_status_bot.ps1` - one-time setup (SecureString token prompt, outside-repo secrets)
- `start_telegram_status_bot.ps1` - foreground start (`-DryRun` prints would-run + JSON)
- `check_telegram_status_bot.ps1` - read-only JSON health/safety check
- `README.md` - operator guide

Configs (`23_configs/`):
- `ghoti_feature_flags.example.json` - 19 flags, only `telegram_status_commands_enabled` true
- `telegram_status_bot.example.json` - runtime config with placeholder outside-repo paths

Docs (`docs/`):
- `GHOTI_N6_10C_TELEGRAM_STATUS_BOT_RUNTIME.md`
- `GHOTI_FEATURE_FLAGS_AND_KILL_SWITCHES.md`
- `GHOTI_DOCKER_VPS_RUNTIME_ROADMAP.md`

Integration notes (`14_context/hermes_integrations/`):
- `TELEGRAM_STATUS_BOT_RUNTIME.md`
- `FEATURE_FLAGS_AND_KILL_SWITCHES.md`
- `TELEGRAM_AFFILIATE_PROGRAM_CANDIDATE.md`
- `DOCKER_VPS_RUNTIME_ROADMAP.md`

Handoff + test + report:
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_TELEGRAM_RUNTIME_TASK.md`
- `01_projects/runtime_mvp/tests/test_n6_10c_telegram_status_bot_runtime.py`
- `14_context/claude_n6_10c_telegram_status_bot_runtime.md` (this report)

## Setup scripts

- **setup** creates `~/.ghoti_runtime` and `~/.ghoti_secrets` outside the repo, seeds the
  runtime config + feature flags from the repo examples, and prompts for the token (read as
  a `SecureString`, never printed) and the allowed chat id. It writes no repo files and
  reports `secrets_printed: false`, `repo_modified: false`.
- **start** runs the Python bot in the foreground attached to the window; the token is never
  placed on the command line (`token_in_command_line: false`). `-DryRun` prints the would-run
  command + a JSON status and does not poll.
- **check** is read-only and reports a JSON safety summary (file existence only, never secret
  values, plus the standing safety flags).

## Feature flags

19 flags in `ghoti_feature_flags.example.json`. Only `telegram_status_commands_enabled`
defaults **true** (read-only status replies are not risky). Every other flag defaults
**false**, including `telegram_status_bot_enabled` (operator opt-in), `telegram_run_commands_enabled`,
`telegram_send_commands_enabled`, `mcp_enabled`, `mcp_filesystem_read_only_enabled`,
`live_agent_launch_enabled`, `claude_launch_enabled`, `codex_launch_enabled`,
`browser_computer_use_enabled`, `email_draft_agent_enabled`, `whatsapp_draft_agent_enabled`,
`auto_send_enabled`, `external_repo_install_enabled`, `affiliate_program_enabled`,
`dashboard_local_analytics_enabled`, `docker_runtime_enabled`, `vps_runtime_enabled`, and the
`global_kill_switch`.

## Kill switch behavior

When `global_kill_switch` is true, the running bot (which reloads flags every poll cycle)
pauses all status actions and answers only `/help` and `/flags`; every other command returns
"Global kill switch is active. Status bot actions are paused." Setting it back to false
resumes status replies on the next cycle.

## Telegram runtime behavior

- Reads the token and allowed chat id from outside-repo secret files; never prints, logs, or
  commits them. The token-bearing API URL is never logged (only the method name + an error
  class/code on failure).
- Ignores any message whose chat id is not the single allowed chat id (the rejected id is
  masked in logs).
- Allowed (read-only): `/start`, `/status`, `/current_task`, `/latest_claude`,
  `/latest_codex`, `/help`, `/flags`.
- Blocked (refused, no handler): `/run`, `/send`, `/login`, `/post`, `/buy`, `/trade`,
  `/delete`, `/mcp`, `/browser`, `/computer`, `/email`, `/whatsapp`, `/install`, `/clone`,
  `/shell`, `/exec`, `/deploy`, `/agent`, `/claude`, `/codex`.
- `/status` reports `live_launch_enabled: false`, `telegram_control_enabled: false`,
  `mcp_enabled: false`, `browser_computer_use_enabled: false`, `auto_send_enabled: false`.
- The only subprocess call is a read-only `git rev-parse --short origin/main`; there is no
  `shell=True`, no `os.system`, no agent launch, and no external package import.

## Why the previous bot did not reply

It did not reply because this **polling process was not running** - not because a local
model (Llama) was unsupported. A plain Python + Telegram Bot API poll loop is sufficient for
status replies. Hermes/Llama routing arrives later via approved wrappers, behind their own
flags.

## Docker / VPS note

Planning only; **not enabled**. `docker_runtime_enabled` and `vps_runtime_enabled` default
false. Order: local laptop first; local Docker later (Compose only after an audited
milestone); VPS later when money allows, behind auth + HTTPS, after privacy readiness. Prefer
open-source / self-hosted.

## Affiliate note

**Candidate-only. Not enabled.** `affiliate_program_enabled` defaults false. Any future
affiliate work must be legal and TOS-aware with no spam, no fake engagement, no auto-mass
messaging, no deceptive referrals, no unauthorized scraping, no auto-send, and human approval
for campaigns.

## Validation

- `git diff --check` (staged): clean - no whitespace errors.
- `git show --check --stat HEAD`: clean after commit.
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py"`:
  146 tests, all passing (n6_10c module contributes 35).
- `python -m unittest discover ... -p "test_n6_10c_telegram_status_bot_runtime.py"`:
  35 tests, OK.
- `check_telegram_status_bot.ps1 -NoSecretsRequired`: `ok: true`,
  `risky_flags_default_false: true`, `no_mcp/no_browser_computer_use/no_auto_send/no_live_agent_launch: true`.
- `start_telegram_status_bot.ps1 -DryRun`: `ok: true`, `dry_run: true`, `status_only: true`,
  `token_in_command_line: false` (no poll loop started).
- `public_repo_security_audit.py --run --json`: `failed_checks: 0`, `blocking_findings: []`.
- `ghoti_product_launcher.py` status/context-pack/repo-map: ran read-only; any generated
  artifact restored, none committed.

## Safety verdict

All hard rules held. No real Telegram token and no real chat id are committed (the externally
mentioned operator chat id is explicitly absent and asserted absent by a test). No secrets,
`.env`, cookies, or auth files in the repo. No Telegram plugin enablement, no MCP install/runtime,
no browser/computer-use, no live Claude/Codex launch, no arbitrary shell, no email/WhatsApp
login, no auto-send, no external repo clone/install/run, no social posting, no money movement.
The implementation is surgical: 17 new files, no edits to existing code.

## What is still NOT enabled

- The bot itself (`telegram_status_bot_enabled` false) until the operator opts in on their
  machine.
- Any Telegram run/send command, MCP, browser/computer-use, live agent launch, email/WhatsApp
  drafts, auto-send, external repo install, affiliate program, dashboard analytics, Docker, VPS.
- Hermes/Llama routing for richer answers (a later, separately audited milestone).

## Codex audit target branch

`audit/ghoti-agent-codex-n6-10c-telegram-status-bot-runtime`
