# CLEAN PASS / N+5.8A HERMES MANUAL BRIDGE READY

## Branches And Commits

- Starting main hash: `84e880e7c3f774580a5e4ac340acd497af3027ee`
- N+5.7B main merge: complete; `origin/main` is `84e880e7c3f774580a5e4ac340acd497af3027ee`
- N+5.7B final main audit branch: `audit/ghoti-agent-codex-n5-7b-final-main-repo-knowledge-context-retrieval`
- N+5.7B final main audit commit: `d704dbd9a1d71b58d759dd812d5445fd1efbaa50`
- N+5.8A feature branch: `feat/ghoti-agent-codex-n5-8a-hermes-agent-workflow-provider-setup-plan-manual-bridge`
- N+5.8A feature commit: `b930261832f06eab6544fca64de39b3cc708e742`
- N+5.8A audit branch: `audit/ghoti-agent-codex-n5-8a-hermes-agent-workflow-provider-setup-plan-manual-bridge`
- N+5.8A audit base before this report: `919d796e33f038a06ac4dca1453f8832ab6725ea`
- N+5.8A merge policy: feature and audit are pushed for review; N+5.8A is not merged to main in this run.

## Files Changed

- Added Hermes bridge script: `03_scripts/hermes_agent_workflow_bridge.py`
- Added N+5.8 tests: `01_projects/runtime_mvp/tests/test_n5_8a_hermes_agent_manual_bridge.py`
- Added launcher commands: `--hermes-bridge-status --json`, `--hermes-bridge-write --json`
- Added dashboard card and local endpoints for `Hermes Agent / Manual Bridge`
- Updated context pack and repo knowledge outputs to reference Hermes bridge readiness
- Added generated Hermes readiness artifacts under `14_context/hermes_workflow/generated/`
- Added docs: `docs/HERMES_AGENT_WORKFLOW_GUIDE.md`, `docs/HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md`, `docs/HERMES_SKILLS_INDEX_GUIDE.md`, `docs/HERMES_BROWSER_PLAYWRIGHT_REMEDIATION_PLAN.md`
- Updated README and operator workflow docs to keep Hermes truth visible and manual-only.

## Generated Hermes Workflow Files

- `14_context/hermes_workflow/generated/hermes_workflow_status.json`
- `14_context/hermes_workflow/generated/hermes_workflow_status.md`
- `14_context/hermes_workflow/generated/hermes_skills_index.json`
- `14_context/hermes_workflow/generated/hermes_skills_index.md`
- `14_context/hermes_workflow/generated/hermes_manual_setup_checklist.md`
- `14_context/hermes_workflow/generated/hermes_safe_next_steps.md`
- `14_context/hermes_workflow/generated/hermes_codex_provider_plan.md`
- `14_context/hermes_workflow/generated/hermes_telegram_manual_plan.md`
- `14_context/hermes_workflow/generated/hermes_browser_playwright_remediation_plan.md`
- `14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md`

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 90 OK
- Total runtime tests: 419 OK
- Launcher smoke: PASS
- Context pack: PASS
- Local worker status: PASS
- Repo map and Hermes repo bundle: PASS
- Hermes bridge status, doctor, skills index, write-readiness: PASS
- Public audit: PASS, 150 checks, 0 blockers, 8 warnings requiring human review
- Model council scan: PASS
- Hermes local bootstrap status: PASS
- Local memory status: PASS
- Local model worker status: PASS
- UI-TARS dry-run: PASS, observation-only
- Approved adapter runner status: PASS, approval-gated/local-only
- External sandbox status: PASS, static inspection only
- Supervised content demo latest validation: PASS
- Node syntax checks for dashboard server and app: PASS
- Runtime PowerShell check with repo-supported desktop fixtures/resource guard: PASS
- Dashboard PowerShell check with repo-supported desktop fixtures/resource guard: PASS after solo rerun
- Local dashboard HTTP/DOM labels: PASS
- Safe WSL Hermes probes: PASS

The exact PowerShell desktop checks timed out in this desktop session before returning a failure. The same repo checks passed with the repo-supported deterministic fixtures and resource-guard variables, which avoids real terminal hotkeys and uncontrolled desktop interaction. This is recorded as an environment limitation, not a code blocker.

## Dashboard Evidence

The local dashboard was started with:

`python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`

URL:

`http://127.0.0.1:3210`

The audit verified these DOM labels over localhost:

- `Hermes Agent / Manual Bridge`
- `readiness percentage`
- `Codex provider pending/not proven`
- `Telegram manual`
- `browser/Playwright degraded`
- `no live provider setup`
- `safe probes only`

The launcher stopped recorded PID `25144` only.

## Hermes WSL Truth

- Hermes WSL status: installed
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`
- Safe probe path output: `/home/ai_sandbox/.local/bin/hermes`
- Safe probe version output includes: `Project: /home/ai_sandbox/.hermes/hermes-agent`, `Python: 3.11.15`, `OpenAI SDK: 2.24.0`
- Hermes bridge parsed skills count: 78 from the first safe `skills list` window
- WSL skills footer: `0 hub-installed, 84 builtin, 0 local - 84 enabled, 0 disabled`
- Important detected skills include `codex`, `claude-code`, `hermes-agent`, `native-mcp`, `obsidian`, `github`, `plan`, `test-driven-development`, and `youtube-content`
- Hermes browser/Playwright status: degraded/not claimed
- Hermes Codex provider support: pending/not proven
- Telegram: manual later/no token
- Provider setup: manual later
- No VPS: true

## Safety Review

- No Hermes setup was run.
- No provider configuration was run.
- No Telegram setup was run.
- No tokens or credentials were read or written.
- No live APIs were called.
- No browser automation was run beyond local dashboard HTTP/DOM validation.
- UI-TARS remains observation-only.
- Adapter runner remains approval-gated/local-only.
- External sandbox remains static inspection/planning-only.
- No bot, captcha, or cloak bypass was added.
- No autonomous posting, account actions, money movement, trading, or legal actions were enabled.
- No `ollama pull` or model download was run.

## Commands

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Local worker: `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- Repo map: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Repo bundle: `python 03_scripts/ghoti_product_launcher.py --repo-bundle hermes --json`
- Hermes bridge status: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Hermes bridge write: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`
- Direct Hermes bridge status: `python 03_scripts/hermes_agent_workflow_bridge.py --status --json`
- Direct Hermes bridge write: `python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json`

## Current Status

- Hermes bridge readiness: 58%
- Repo knowledge readiness: 55%
- Local worker readiness: 45%
- Ollama status: installed, `ollama version is 0.24.0`
- Gemma status: missing
- Active local worker mode: `local_demo` fallback
- Public readiness: 150 checks, 0 blockers, 8 warnings requiring human review

Human status: Ghoti is about 82% complete toward the bigger local-first agent OS vision. The local MVP is stable and usable. Current capabilities are launcher/dashboard operation, context packs, local_demo worker lane, repo knowledge bundles, Hermes manual bridge readiness, public/security audits, model council scan, UI-TARS observation-only dry-runs, adapter dry-runs, external sandbox status, and local supervised content demo. The main gaps are real Gemma model task quality, provider switching, Hermes Codex provider verification, Telegram, browser/Playwright remediation, audited future click/type computer-use, and production/public human review. Confidence: high because N+5.7B is merged and audited on main, N+5.8A passes the local audit gate, and all live setup surfaces remain manual or blocked.

## What Improved

- Hermes now has a safe bridge lane with status, doctor, skills index, manual setup plan, and generated readiness artifacts.
- The dashboard shows Hermes as an installed WSL component while keeping provider setup, Telegram, and browser/Playwright manual/unproven.
- Launcher commands expose Hermes bridge status and readiness generation without invoking setup.
- Context packs and repo bundles now point to Hermes bridge files and safe next steps.
- Docs separate what is installed now from what is manual later and what remains blocked.

## What Remains

- Human-approved Hermes provider setup and Codex provider verification.
- Human-approved Telegram setup with tokens kept out of git.
- Browser/Playwright remediation and verification.
- Real Gemma install/model availability decision and local task quality evaluation.
- Future audited computer-use click/type milestone, if ever approved.
- Continued public/GitHub human review before broader release.

## Cleanup

- Local dashboard was stopped through the launcher using the recorded PID only.
- Generated validation residue was restored before this audit report was added.
- No broad process kill was used.
- No primary worktree files were modified.

## Final Verdict

CLEAN PASS / N+5.8A HERMES MANUAL BRIDGE READY
