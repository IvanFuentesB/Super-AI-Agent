# Daily Operator Guide

## What Ghoti is

Ghoti / Super-AI-Agent is a local-first supervised operator control center. It
helps Ivan coordinate local status checks, compact memory, coding workflows,
safe content demos, research plans, and future computer-use tooling from one
truthful dashboard. It is not autonomous, it does not post, and it does not run
live providers or account actions without explicit human approval.

Current main baseline: N+6.0B clean/Gemma install and first local evaluation on
main at `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`.

Current feature/audit lane: N+6.1A adds constrained local model routing with a
repo-bundle hallucination guard. `gemma3:4b` is installed, but Ghoti accepts
Gemma routed output only when it cites known repo bundles/files with
`source_metadata`; otherwise it falls back to `local_demo`.

## Launch

```powershell
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
```

Dashboard URL:

```text
http://127.0.0.1:3210
```

## What to check first

1. Open the dashboard and read Start Here / Daily Operator.
2. Confirm Status Truth says N+6.0B clean on main and N+6.1A guarded routing is
   feature/audit only when that branch is checked out.
3. Confirm Hermes, Ollama/Gemma, Obsidian memory, UI-TARS, adapters, external
   sandbox, public audit, and readiness status are truthful.
4. Confirm Local Model / Easy Worker Lane shows readiness percentage, Gemma
   truth, and `local_demo fallback` availability.
5. Confirm Gemma / Local Model Quality shows Ollama status, Gemma installed
   status, readiness percentage, quality evaluation status, and manual
   latest eval score, and no broad production routing.
6. Confirm Local Model Routing / Guarded Worker shows guard enabled, safe task
   allowlist, last guard result, fallback status, and no command execution from
   model output.
7. Confirm Repo Knowledge / Graphify Lane shows repo knowledge readiness,
   task bundles, latest report index, Graphify roadmap only, no external
   runtime, and no network.
8. Run a smoke check before relying on the dashboard.
9. Review the latest relevant report under `14_context/`.

## Current roadmap priority

The next work is ordered for paid-credit reduction and safer long-task
automation:

1. N+6.1A: constrained Gemma worker routing with a repo-bundle hallucination
   guard. Use known repo-map bundle IDs only, reject invented bundle/file
   claims, require source metadata, and fall back to `local_demo` if the guard
   fails.
2. N+6.2A: Hermes Agent Workflow / Manual Bridge Verification. Use safe probes
   and manual bridge packets only. No tokens, provider setup, Telegram setup,
   live APIs, or browser automation.
3. N+6.3A: Safe Computer-Use Preparation with Gemma, Hermes, UI-TARS
   observation, Browser Harness, and Vercel agent-browser roadmap. Observation
   first; every click/type/live-account action stays human-approved.

Do not start N+6.2A or N+6.3A until N+6.1A passes a clean guard/audit gate.

## Guarded local routing

Use N+6.1A routing only for boring offline text work:

```powershell
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json
```

Allowed tasks are `summarize-latest-report`, `status-paragraph`,
`codex-next-prompt`, `safety-classification`, `context-bundle-summary`,
`next-milestone-outline`, and `report-to-bullets`. The guard rejects invented
repo bundles, unknown source files, URLs, missing `source_metadata`, and any
claim that live APIs, provider setup, Telegram, browser automation, or broad
production routing are enabled.

## Daily commands

```powershell
python 03_scripts/ghoti_product_launcher.py --status --json
python 03_scripts/ghoti_product_launcher.py --smoke --json
python 03_scripts/ghoti_product_launcher.py --context-pack --json
python 03_scripts/ghoti_product_launcher.py --local-worker-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json
python 03_scripts/ghoti_product_launcher.py --gemma-status --json
python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
python 03_scripts/ghoti_product_launcher.py --repo-map --json
python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json
python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json
python 03_scripts/ghoti_context_pack_builder.py --write --json
python 03_scripts/local_model_worker_lane.py --doctor --json
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
python 03_scripts/supervised_content_mvp_runner.py --validate-latest
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/model_council_tool_intake.py --scan --json
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
```

The stop command targets only the launcher-recorded PID. Do not use broad
process kills.

## Latest reports

Most milestone reports live under `14_context/`. Useful starting points:

- `14_context/codex_n5_3a_main_merge_product_finish_local_mvp.md`
- `14_context/codex_n5_3a_product_finish_remote_clean_audit.md`
- `14_context/codex_n5_4a_first_real_operator_usability_pass.md`
- `14_context/codex_n5_4b_main_merge_daily_operator_usability.md`
- `14_context/codex_n5_5b_final_main_local_memory_context_pack.md`
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md`
- audit branch report: `14_context/codex_n5_3b_final_main_full_product_finish.md`

If the newest final-main audit report is not present on `origin/main`, inspect
the pushed audit branch for that milestone.

## Local memory context pack

Use the context pack when you want a small, current handoff for ChatGPT, Codex,
Claude, or Obsidian:

```powershell
python 03_scripts/ghoti_context_pack_builder.py --write --json
```

Generated files live under:

```text
14_context/compact_memory/generated/
```

Start with:

- `ghoti_status_short.md` for a one-paragraph status.
- `ghoti_current_context_pack.md` for a compact full handoff.
- `ghoti_codex_next_prompt.md` for the next safe Codex prompt.
- `ghoti_chatgpt_migration_summary.md` for ChatGPT migration.

See [Local Memory Context Pack Guide](LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md).

## Repo knowledge map

Use the repo knowledge map when you want focused context instead of pasting a
large thread or broad file list:

```powershell
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
python 03_scripts/ghoti_repo_knowledge_map.py --bundle dashboard --json
python 03_scripts/ghoti_repo_knowledge_map.py --bundle next-milestone --json
```

Generated files live under:

```text
14_context/repo_knowledge/generated/
```

Start with `repo_knowledge_map.md`, `latest_reports_index.md`,
`subsystem_index.md`, and `task_bundle_next_milestone.md`. See
[Repo Knowledge Map Guide](REPO_KNOWLEDGE_MAP_GUIDE.md) and
[Graphify Repo Knowledge Roadmap](GRAPHIFY_REPO_KNOWLEDGE_ROADMAP.md).

## Local model easy worker lane

Use this lane for small local/offline tasks that save provider credits:

```powershell
python 03_scripts/local_model_worker_lane.py --status --json
python 03_scripts/local_model_worker_lane.py --doctor --json
python 03_scripts/local_model_worker_lane.py --demo-task status-paragraph --json
python 03_scripts/local_model_worker_lane.py --write-demo-output --json
```

Generated files live under:

```text
14_context/local_worker/generated/
```

Start with `local_worker_status.md`, `status_paragraph.md`, and
`codex_next_prompt_from_context.md`. See
[Local Model / Gemma Setup Guide](LOCAL_MODEL_GEMMA_SETUP_GUIDE.md) and
[Easy Worker Lane Guide](EASY_WORKER_LANE_GUIDE.md).

## Gemma readiness and local quality

Use the Gemma readiness lane to decide whether to stay in `local_demo`, install
a Gemma model manually later, or run a quality evaluation after a human-approved
install:

```powershell
python 03_scripts/gemma_model_readiness.py --status --json
python 03_scripts/gemma_model_readiness.py --doctor --json
python 03_scripts/gemma_model_readiness.py --recommend --json
python 03_scripts/gemma_model_readiness.py --quality-plan --json
python 03_scripts/gemma_model_readiness.py --local-model-eval --json
python 03_scripts/gemma_model_readiness.py --write-evaluation --json
python 03_scripts/gemma_model_readiness.py --write-readiness --json
```

Generated files live under:

```text
14_context/local_model_readiness/generated/
14_context/local_model_evaluation/runs/
```

Start with `gemma_readiness_status.md`, `gemma_install_decision.md`,
`gemma_manual_commands.md`, and `local_task_quality_plan.md`. See
[Human-Approved Gemma Install Log](HUMAN_APPROVED_GEMMA_INSTALL_LOG.md),
[Gemma Model Install Decision](GEMMA_MODEL_INSTALL_DECISION.md) and
[Local Model Quality Evaluation Guide](LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md).

The readiness lane may recommend commands such as `ollama pull gemma3:4b`, but
Ghoti must not run them automatically. Manual approval is required before any
model download, and production routing remains disabled until a later audited
milestone proves quality.

N+6.0A may write a first local evaluation run under
`14_context/local_model_evaluation/runs/`. If `gemma3:4b` is missing, that run is
a controlled fallback. If `gemma3:4b` is installed, it records real local model
outputs and a score, while still keeping production routing disabled.

## local_demo fallback

`local_demo fallback` means Ghoti keeps the workflow local and truthful when a
real local model is unavailable or not trustworthy enough for a task. In N+6.0A,
`gemma3:4b` was installed after explicit human approval and the first local eval
scored 86%, but one repo-bundle task hallucinated. Keep fallback available and
keep production routing disabled until a later audited routing milestone.

## Hermes is currently allowed

Hermes is currently allowed to be checked with safe local status probes only.
Known truth:

- WSL Ubuntu is present.
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0`
- Browser/Playwright is degraded/not claimed unless separately verified.
- Codex provider support inside Hermes is pending/not proven.
- Hermes Agent / Manual Bridge can write local readiness files, a skills index,
  manual checklist, and operator bridge packet under
  `14_context/hermes_workflow/generated/`.

Do not run Hermes setup, provider config, Telegram setup, token flows, or live
APIs from this daily workflow.

See `HERMES_AGENT_WORKFLOW_GUIDE.md`,
`HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md`, `HERMES_SKILLS_INDEX_GUIDE.md`,
and `HERMES_BROWSER_PLAYWRIGHT_REMEDIATION_PLAN.md`.

## UI-TARS is currently allowed

UI-TARS is currently observation-only. Allowed:

- dry-run observation status
- local observation packets
- approval-gated read-only capture in a later audited flow

Not allowed:

- click
- type
- hotkeys
- desktop control
- UI-TARS runtime launch
- external repo code execution

## What must remain manual

- Hermes provider setup
- Telegram connection and tokens
- additional Gemma model pulls or model removal
- broad Gemma production routing outside the N+6.1A guarded safe-task lane
- trusting local model output without source metadata and guard pass/fallback evidence
- Ruflo source/runtime enablement
- external Graphify runtime integration
- browser/Playwright repair and verification
- public release human review
- any live provider, account, posting, money, trading, or legal action

## What not to do

- Do not commit `.env`, API keys, tokens, cookies, browser sessions, local
  credentials, or human private files.
- Do not run bot/captcha/cloak bypass workflows.
- Do not create fake engagement or spam workflows.
- Do not scrape credentials or browser sessions.
- Do not enable autonomous posting.
- Do not enable autonomous money/trading/legal actions.
- Do not wire external repos into runtime without a new audited milestone.
- Do not mutate the primary worktree; no primary worktree mutation except
  read-only inspection.
- Do not run live providers/tokens setup flows.

## Troubleshooting

### dashboard won't start

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --status --json
```

Check whether the state file records a PID and whether the dashboard reports
`dashboard_running=true`.

### port busy

The launcher defaults to port 3210. Run smoke/status first. If the port is used
by something not recorded by the launcher, stop that process manually only after
you identify that it belongs to this workspace.

### WSL/Hermes not found

Use only safe probes:

```powershell
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"
```

Do not run setup or provider config during daily checks.

### Ollama/Gemma missing

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
python 03_scripts/local_memory_compression_bridge.py --status --json
```

If Gemma is missing, expect `local_demo fallback`. That is a safe degraded mode,
not a failure.

### Gemma install decision

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/ghoti_product_launcher.py --gemma-write-readiness --json
```

Inspect `14_context/local_model_readiness/generated/gemma_manual_commands.md`.
The command `ollama pull gemma3:4b` is a human decision, not an automatic Codex
action. Smaller manual options may be listed for fast tests.

### public audit warnings

Run:

```powershell
python 03_scripts/public_repo_security_audit.py --run --json
```

The N+5.4B baseline has 0 blockers and 7 warnings. Warnings still require human
review before any public release claim.

### context pack stale or missing

Run:

```powershell
python 03_scripts/ghoti_context_pack_builder.py --write --json
```

Then refresh the dashboard Local Memory / Context Pack card. The builder is
repo-local and does not call live providers.

### repo knowledge map stale or missing

Run:

```powershell
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
```

Then refresh the dashboard Repo Knowledge / Graphify Lane card. The generated
map is local JSON/Markdown only; it does not run external Graphify, does not
clone repositories, and does not use network.

### generated residue

Some status probes may update generated JSON timestamps. Inspect diffs before
committing. Restore generated probe residue when it is not an intended source
change.

### launcher PID stale

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
python 03_scripts/ghoti_product_launcher.py --status --json
```

The launcher stops only the recorded PID. If status still looks stale, inspect
the state file and process manually; do not kill broad node/python/pwsh process
sets.

## Stop and cleanup

```powershell
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
python 03_scripts/ghoti_product_launcher.py --status --json
git status --short
```

End a daily session with no recorded launcher PID, no unexpected generated
residue, and no primary worktree mutation.
