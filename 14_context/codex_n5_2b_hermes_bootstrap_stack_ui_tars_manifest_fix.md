# Codex N+5.2B: Stack UI-TARS Manifest Fix + Hermes Local Bootstrap Repair

## Branch

- Branch: `feat/ghoti-agent-codex-n5-2b-hermes-bootstrap-stack-ui-tars-manifest-fix`
- Base main: `origin/main` at `f95eca09ccd9afe66f3b7ee6badb439d6c41a613`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\codex_n5_2b_hermes_stack_ui_tars_fix`

## Stack Result

- Merged N+5.0B commit: yes, `cdb8398a5bb71326cbfad01ae6810c62d1db03fd` is an ancestor of `HEAD`
- Merged N+5.2A commit: yes, `5993afa790c07162dc443cfc8eee33c8fb9839e0` is an ancestor of `HEAD`
- Merge order: N+5.0B first, N+5.2A second
- Conflicts: none

## UI-TARS Files Restored

- `03_scripts/ui_tars_observation_adapter.py`: restored
- `02_automation/external_tool_adapters/ui_tars_observation_adapter.py`: restored
- `01_projects/runtime_mvp/tests/test_n5_0a_ui_tars_observation_only_adapter.py`: restored
- Dashboard UI-TARS observation endpoints/cards from N+5.0B: restored through stack merge

## UI-TARS Manifest Contract Result

Committed observation manifest checked:

- `local_only`: true
- `click_enabled`: false
- `type_enabled`: false
- `external_repo_code_executed`: false
- `installs_performed`: false
- `ui_tars_runtime_started`: false
- `desktop_control_enabled`: false
- `live_api_used`: false

Validation:

- `python 03_scripts/ui_tars_observation_adapter.py --status --json`: pass
- `python 03_scripts/ui_tars_observation_adapter.py --dry-run --json`: pass, observation-only status path, no UI-TARS runtime, no click/type/hotkey, no live API
- `python -m unittest 01_projects.runtime_mvp.tests.test_n5_0a_ui_tars_observation_only_adapter -v`: 41 tests passed

## Hermes Result

- `03_scripts/hermes_local_bootstrap.py --status --json`: pass
- `--check-prereqs --json`: pass
- `--print-windows-commands`: pass
- `--download-installer --json`: pass
- `--inspect-installer --json`: pass
- `--write-report --json`: pass
- `--latest --json`: pass
- Installer URL: `https://hermes-agent.nousresearch.com/install.sh`
- Installer SHA-256 observed: `ade99101ec9bde981919a38b4c486123dcc341b5f33fc2e75e22e4e306835299`
- Installer executed: no
- Paid VPS required: no
- Secrets written: no
- Live API used: no

## WSL Ubuntu Status

- WSL distro installed: yes, `Ubuntu`
- Hermes command found: yes, in Ubuntu WSL
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`
- Windows-local Hermes command found: no
- Interactive setup run: no
- Telegram connected: no
- Provider tokens entered: no

## WSL Ubuntu Troubleshooting Wording Result

Added explicit wording to:

- `03_scripts/hermes_local_bootstrap.py --print-windows-commands`
- `docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md`
- `docs/LOCAL_FIRST_NO_VPS_AGENT_STRATEGY.md`
- `README.md`

Required phrases covered:

- `wsl -d Ubuntu`
- `wsl.exe -d Ubuntu`
- If Ubuntu opens but Hermes is not found, the installer was not completed inside Ubuntu
- `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup`
- `source ~/.bashrc`
- `command -v hermes`
- `hermes --help`
- PowerShell `curl` alias solved by `curl.exe`
- Bash from PowerShell can route to WSL
- No paid VPS required
- Telegram setup remains manual later

## Codex Provider Support Result

- Codex provider support: pending / not verified
- Truth rule: Codex is preferred if Hermes supports it, but support is not claimed until verified by local Hermes help/config docs or a non-interactive provider command.
- The downloaded installer text mentions Codex, but no local Hermes provider command was used to confirm support.

## Telegram Manual Setup Result

- Telegram setup remains later/manual.
- No Telegram bot token or chat ID was committed, printed, or used.
- `.env.example` contains placeholders only.

## Public Readiness Result

- `public_repo_security_audit.py --status --json`: pass
- `public_repo_security_audit.py --run --json`: pass
- `public_repo_security_audit.py --write-report --json`: pass
- Total checks: 150
- Passed checks: 142
- Failed checks: 0
- Warning checks: 8
- `safe_to_make_public`: true
- Blockers: 0
- Note: inherited historical Claude co-author trailers from the stacked N+5.0 branch are surfaced as a human-review warning; this branch does not rewrite that history.

## Model Council Result

- `model_council_tool_intake.py --status --json`: pass
- `model_council_tool_intake.py --scan --json`: pass
- `model_council_tool_intake.py --write-report --json`: pass
- Registry entries verified: Hermes Agent, Codex, Gemma/Ollama, Graphify, agent-browser, browser-harness, Claude skills, ChatGPT/OpenAI, Claude Code, Supabase, Vercel, Stripe, Postgres, OpenWA, Insforge, Picoclaw, robotics references
- Cloak/browser bot-detection entry: present and `BLOCKED`
- Runtime wiring enabled: false
- Live API used: false

## Tests Result

- `git diff --check`: pass, line-ending warnings only
- `git show --check --stat HEAD`: pass
- Python regression tests: 382 tests passed, 0 failed
- N+5.2A tests: 12 passed
- N+5.0 UI-TARS tests: 41 passed
- N+4.9A: 37 passed
- N+4.8A: 35 passed
- N+4.7A: 25 passed
- N+4.6A: 33 passed
- N+4.5A: 68 passed
- N+4.4D: 18 passed
- N+4.4C: 16 passed
- N+4.4B: 17 passed
- N+4.4A: 20 passed
- N+4.3A: 15 passed
- N+4.2A: 26 passed
- N+4.1 reliability with `PYTHONPATH`: 19 passed

## Runtime / Dashboard Checks

- `approved_adapter_runner.py --status --json`: pass
- `external_tool_sandbox_manager.py --status --json`: pass
- `ghoti_product_launcher.py --status --json`: pass
- `parallel_agent_relay.py --status --json`: pass
- `local_memory_compression_bridge.py --json`: pass
- `repo_skill_plugin_intake.py --validate-config`: pass
- `ghoti_readiness_check.py --status`: pass, readiness remains 100
- `supervised_content_mvp_runner.py --validate-latest`: pass
- `node --check 01_projects/dashboard_mvp/server.js`: pass
- `node --check 01_projects/dashboard_mvp/public/app.js`: pass
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`: pass
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1`: pass when run by itself. A previous parallel run raced on `runtime_data/tasks.json`, then the sequential rerun passed.

## Cleanup Result

- Restored validator drift in `14_context/external_tools/external_tool_sandbox_status.json`.
- Removed transient validation run outputs from adapter execution, agent relay, compact memory, desktop handoff, external tool approval packets, Obsidian export, and generated UI-TARS run folders.
- No broad process kill was performed.
- No lingering process tied to the N+5.2B worktree was found.

## Safety Summary

- No main push.
- No force push.
- No history rewrite.
- No paid VPS setup.
- No provider/Telegram/API secrets written.
- No live provider APIs connected.
- No UI-TARS runtime started.
- No external repo code executed.
- No desktop click/type/hotkey enabled through UI-TARS.
- Telegram remains manual and approval-gated.

## Final Verdict

IMPLEMENTED_AND_PUSHED
