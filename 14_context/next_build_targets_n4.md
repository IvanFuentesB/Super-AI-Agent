# Next Build Targets N+4

This file intentionally contains exactly 3 implementation targets.

## Target 1: Dashboard Control Center Reliability

Objective:

Make the current `origin/main` dashboard and runtime supervisor path reliable enough for daily use. The operator should be able to open the dashboard, see supervisor status, approvals, queue state, artifacts, and next action without a 500 error.

Files likely touched:

- `01_projects/runtime_mvp/src/super_ai_agent/models.py`
- `01_projects/runtime_mvp/src/super_ai_agent/storage.py`
- `01_projects/runtime_mvp/src/super_ai_agent/queue.py`
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `03_scripts/check_runtime_mvp.ps1`
- `03_scripts/check_dashboard_mvp.ps1`
- `04_docs/ghoti_control_center.md` or a new daily runbook doc

Files not to touch:

- `21_repos/third_party/`
- `.env`, credentials, tokens, browser sessions, API keys
- `14_context/content_workflows/runs/` unless N+3.65 has already been merged to main
- live account connector files

Implementation steps:

1. Fix the `SupervisorState.ready_to_resume_count` constructor mismatch.
2. Add backward-compatible handling for older `supervisor_state.json` payloads.
3. Make `python -m super_ai_agent.cli init-data`, `status`, `supervisor-status`, and `pending-approvals` green on a clean checkout.
4. Make `/api/supervisor/status` return HTTP 200 with a useful error field only for true runtime failures.
5. Keep dashboard actions local and approval-aware.
6. Add a concise daily operator status panel: current branch, dirty state, pending approvals, blocked tasks, ready-to-resume tasks, latest artifacts, next recommended command.

Tests/validation:

- `python -m super_ai_agent.cli init-data`
- `python -m super_ai_agent.cli status`
- `python -m super_ai_agent.cli supervisor-status`
- `python -m super_ai_agent.cli pending-approvals`
- `powershell -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`
- `powershell -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1`
- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`
- `git diff --check`

Done definition:

All listed validations pass from a clean worktree, and the dashboard supervisor endpoint does not crash.

Safety gates:

- No live posting, emailing, payment, job application, social action, or account mutation.
- Approval queue must not execute public/live actions.
- GitHub write commands remain explicit-approval only.
- No secrets or `.env` reads.

Expected time/risk:

- Time: small to medium.
- Risk: medium, because the runtime state schema and dashboard route are coupled.

Claude Code prompt seed:

```text
N+4.1 Dashboard Control Center Reliability. Work on a clean feature branch from origin/main. Fix the SupervisorState ready_to_resume_count runtime crash and make runtime status, supervisor status, pending approvals, check_runtime_mvp.ps1, and check_dashboard_mvp.ps1 pass. Do not add live actions. Do not touch secrets or external repos. Update docs with the exact daily operator command path. Commit and push only intentional implementation/docs changes.
```

## Target 2: Local Memory and Gemma Draft Compression Bridge

Objective:

Create a practical local memory loop that can compress project context with local Gemma/Ollama when available, write draft summaries only, and make Obsidian/compact memory useful without unsafe canonical overwrites.

Files likely touched:

- `14_context/00_main_memory/`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/status_board.md`
- `03_scripts/` new or existing memory helper script
- `01_projects/runtime_mvp/src/super_ai_agent/providers.py`
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
- `23_configs/provider_profiles.example.json`
- `23_configs/memory_policy.example.yaml`
- `04_docs/memory_architecture.md`

Files not to touch:

- `.env`, credentials, tokens, browser sessions, API keys
- `21_repos/third_party/`
- canonical memory files without an explicit review/promotion flag
- generated logs unless ignored or intentionally documented

Implementation steps:

1. Add a local memory status command that reports compact memory, Obsidian-like notes if present, and latest handoff snapshot.
2. Add a Gemma/Ollama draft compression command that checks `ollama` availability and configured local model.
3. Make dry-run default.
4. Write output only to a draft outbox/log path.
5. Add explicit `--promote-reviewed` or equivalent for canonical updates, but keep it disabled by default.
6. Add dashboard read-only visibility for memory freshness and latest draft summary.

Tests/validation:

- `python -m super_ai_agent.cli memory-status` or equivalent
- `python -m super_ai_agent.cli memory-compress --input 14_context/current_state.md --dry-run`
- `python -m super_ai_agent.cli memory-compress --input 14_context/current_state.md --apply`
- Verify apply writes only draft output, not canonical memory.
- `git diff --check`
- JSON/YAML config validation where applicable.

Done definition:

The operator can generate a local draft compression artifact without consuming Claude/Codex context and without overwriting canonical memory.

Safety gates:

- Local Ollama/Gemma only.
- No automatic model pull.
- No external API.
- Refuse secret-like paths.
- Draft output must be labeled `DRAFT_ONLY` and `HUMAN_REVIEW_REQUIRED`.

Expected time/risk:

- Time: medium.
- Risk: medium, mostly around Windows path handling and avoiding accidental canonical overwrites.

Claude Code prompt seed:

```text
N+4.2 Local Memory and Gemma Draft Compression Bridge. Build a dry-run-first local memory helper on origin/main after N+4.1 is stable. It should inspect memory freshness, call local Ollama/Gemma only if available, write DRAFT_ONLY summaries to an outbox/log path, and never overwrite canonical memory without an explicit reviewed promotion flag. Validate with status, dry-run, apply-to-draft, secret-path refusal, and git diff checks.
```

## Target 3: Supervised Workflow Approval Packet on Main

Objective:

Bring the supervised content MVP proof-packet concept into the main daily operator loop, after the integration branch is merged, and connect it to approval-state visibility without enabling any live/public action.

Files likely touched:

- `03_scripts/supervised_content_mvp_runner.py`
- `03_scripts/ghoti_readiness_check.py`
- `03_scripts/external_repo_implementation_map.py`
- `01_projects/runtime_mvp/src/super_ai_agent/queue.py`
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `14_context/content_workflows/runs/`
- `14_context/obsidian_vault/`
- `23_configs/supervised_content_mvp.example.json`
- `23_configs/ghoti_readiness_check.example.json`

Files not to touch:

- live account connectors
- `.env`, credentials, tokens, browser sessions, API keys
- external repo clone/install/run paths
- public upload/posting integrations

Implementation steps:

1. Ensure N+3.65 supervised content MVP files are merged to main.
2. Add a dashboard read card for latest proof packet, readiness score, and approval gates.
3. Add a runtime approval request generator for the human approval packet, but keep publish action manual-only.
4. Add a CLI command to validate latest proof packet and summarize next manual step.
5. Ensure OpenFang/MoneyPrinter remain Ghoti-native concept mapping only.
6. Ensure LLM Council remains local/demo/fallback by default.

Tests/validation:

- `python 03_scripts/supervised_content_mvp_runner.py --validate-latest`
- `python 03_scripts/ghoti_readiness_check.py --status`
- `python 03_scripts/external_repo_implementation_map.py --status`
- `python -m super_ai_agent.cli pending-approvals`
- dashboard latest supervised workflow endpoint returns 200
- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`
- `git diff --check`

Done definition:

Main can show the latest supervised workflow packet, prove score 100 for the local supervised slice only, show pending human approval gates, and avoid any autonomous/public production claim.

Safety gates:

- No autonomous posting.
- No upload.
- No account login.
- No revenue claim.
- No external API by default.
- No external repo clone/install/run.
- Human approval remains required for any public action.

Expected time/risk:

- Time: medium to large.
- Risk: medium-high because it spans proof artifacts, runtime queue, dashboard, and wording truth.

Claude Code prompt seed:

```text
N+4.3 Supervised Workflow Approval Packet on Main. After N+3.65 is merged to main and N+4.1 runtime status is green, connect the latest supervised content MVP proof packet to dashboard and runtime approval visibility. Do not enable posting, upload, account login, external API, or revenue actions. Validate proof packet, readiness score, approval queue visibility, dashboard route, Node syntax, and git diff checks. Keep all wording clear that 100% means supervised local MVP slice only.
```
