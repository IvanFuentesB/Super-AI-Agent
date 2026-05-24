# Ghoti Repo Knowledge Map

Generated: `2026-05-24T18:40:40Z`

Repo knowledge readiness: 55%. Local file map and task bundles are available. Graphify runtime: roadmap only/not wired; no external repo runtime; no network.

- Main hash: `20e1dce1e89f15a337054864560b95b82233877c`
- Latest clean milestone: N+5.9B - Gemma Readiness / Local Quality Plan landed on main
- Current milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation
- Next recommended milestone: N+6.1A - Constrained Gemma Worker Routing + Repo-Bundle Hallucination Guard
- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Repo map command: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Hermes bridge command: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Gemma status command: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Gemma quality command: `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`
- Gemma readiness files: `14_context/local_model_readiness/generated/`
- Local model eval runs: `14_context/local_model_evaluation/runs/`
- Gemma production routing: disabled
- Graphify runtime: roadmap only/not wired
- no external repo runtime
- no network

## Important Files

- `README.md` [docs/operator guides]: First file Ivan or GitHub visitors read before running Ghoti.
- `03_scripts/ghoti_product_launcher.py` [launcher]: Daily operator entry point and safest command surface.
- `03_scripts/ghoti_context_pack_builder.py` [local memory/context packs]: Main token-saving continuity tool.
- `03_scripts/local_memory_compression_bridge.py` [local memory/context packs]: Keeps durable memory visible without live providers.
- `03_scripts/local_model_worker_lane.py` [local model/easy worker]: Current credit-saving worker lane with local_demo fallback.
- `03_scripts/gemma_model_readiness.py` [local model/easy worker]: N+6.0A preflight and local model evaluation layer without provider setup or production routing.
- `03_scripts/hermes_local_bootstrap.py` [Hermes/WSL]: Hermes is a planned local agent layer, but setup/provider actions remain manual.
- `03_scripts/hermes_agent_workflow_bridge.py` [Hermes/WSL]: Makes Hermes useful and inspectable while keeping provider setup, Telegram, tokens, and browser automation manual later.
- `03_scripts/ui_tars_observation_adapter.py` [UI-TARS/computer-use]: Preserves computer-use research without click/type control.
- `03_scripts/approved_adapter_runner.py` [adapter/external sandbox]: Keeps integrations dry-run/local unless explicitly approved.
- `03_scripts/external_tool_sandbox_manager.py` [adapter/external sandbox]: Prevents uncontrolled external repo runtime wiring.
- `03_scripts/public_repo_security_audit.py` [public/security audit]: Finds blockers before public polish or main pushes.
- `03_scripts/model_council_tool_intake.py` [public/security audit]: Tracks provider/tool readiness without enabling unsafe automation.
- `03_scripts/supervised_content_mvp_runner.py` [supervised content demo]: Demonstrates supervised content workflow without posting.
- `01_projects/dashboard_mvp/server.js` [dashboard]: Backend for the Product Control Center and operator cards.
- `01_projects/dashboard_mvp/public/index.html` [dashboard]: First-screen truth surface for daily use.
- `01_projects/dashboard_mvp/public/app.js` [dashboard]: Connects UI cards to local-only status endpoints.
- `01_projects/dashboard_mvp/public/styles.css` [dashboard]: Keeps the operator console usable and scannable.
- `docs/DAILY_OPERATOR_GUIDE.md` [docs/operator guides]: Turns milestone work into repeatable human workflow.
- `docs/CODEX_ONLY_WORKFLOW.md` [docs/operator guides]: Keeps future Codex work isolated and auditable.
- `docs/LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md` [local memory/context packs]: Explains token-saving context handoff.
- `docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md` [local model/easy worker]: Shows how to unlock real local model work later without auto-downloads.
- `docs/GEMMA_MODEL_INSTALL_DECISION.md` [local model/easy worker]: Helps Ivan choose 4B, 1B, 270M, or stay local_demo.
- `docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md` [local model/easy worker]: Keeps the one-model approval separate from future routing or provider setup.
- `docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md` [local model/easy worker]: Keeps real Gemma quality separate from local_demo fallback plumbing.
- `docs/EASY_WORKER_LANE_GUIDE.md` [local model/easy worker]: Documents safe credit-saving local tasks.
- `docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md` [Hermes/WSL]: Important next human/manual milestone context.
- `docs/HERMES_AGENT_WORKFLOW_GUIDE.md` [Hermes/WSL]: Explains safe probes, generated readiness files, and manual later boundaries.
- `docs/HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md` [Hermes/WSL]: Keeps provider setup out of Codex automation and behind explicit approval.
- `docs/COMPUTER_USE_ROADMAP.md` [UI-TARS/computer-use]: Keeps click/type/autonomy future-gated.
- `docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md` [future Graphify roadmap]: Connects repo knowledge with the broader token-saving roadmap.
- `docs/BLOCKED_UNSAFE_AUTOMATION.md` [public/security audit]: Canonical list of blocked automation categories.
- `14_context/compact_memory/generated/ghoti_current_context_pack.md` [local memory/context packs]: Short current-state handoff source.
- `14_context/local_worker/generated/local_worker_status.md` [local model/easy worker]: Shows Ollama/Gemma/local_demo readiness.
- `14_context/hermes_workflow/generated/hermes_workflow_status.md` [Hermes/WSL]: Shows Hermes installed/version/skills truth and manual later boundaries.
- `01_projects/runtime_mvp/tests/test_n5_6a_local_model_easy_worker_lane.py` [tests]: Best current pattern for JSON script, launcher, docs, and dashboard checks.
- `14_context/codex_n6_0a_roadmap_priority_hermes_computer_use_update.md` [reports/14_context]: verdict not detected
- `14_context/codex_n5_9b_main_merge_gemma_readiness_local_quality_plan.md` [reports/14_context]: CLEAN PASS / N+5.9B MAIN MERGE READY
- `14_context/codex_n5_9a_gemma_model_availability_local_task_quality_evaluation.md` [reports/14_context]: CLEAN PASS / N+5.9A GEMMA READINESS AND LOCAL QUALITY PLAN READY
- `14_context/codex_n5_8b_main_merge_hermes_manual_bridge_readiness.md` [reports/14_context]: CLEAN PASS / N+5.8B MAIN MERGE READY
- `14_context/codex_n5_8a_hermes_agent_workflow_provider_setup_plan_manual_bridge.md` [reports/14_context]: CLEAN PASS / N+5.8A HERMES MANUAL BRIDGE READY
- `14_context/codex_n5_7b_main_merge_repo_knowledge_context_retrieval.md` [reports/14_context]: CLEAN PASS / N+5.7B MAIN MERGE READY
- `14_context/codex_n5_7a_graphify_repo_knowledge_map_context_retrieval.md` [reports/14_context]: CLEAN PASS / N+5.7A REPO KNOWLEDGE MAP CONTEXT RETRIEVAL READY
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md` [reports/14_context]: CLEAN PASS / N+5.6B MAIN MERGE READY
- `14_context/codex_n5_6a_local_model_gemma_setup_truth_easy_worker_lane.md` [reports/14_context]: CLEAN PASS / N+5.6A LOCAL MODEL EASY WORKER LANE READY
- `14_context/codex_n5_5b_main_merge_local_memory_context_pack.md` [reports/14_context]: CLEAN PASS / N+5.5B MAIN MERGE READY

## Task Bundles

- `audit-main` -> `14_context/repo_knowledge/generated/task_bundle_audit_main.md`
- `dashboard` -> `14_context/repo_knowledge/generated/task_bundle_dashboard.md`
- `local-memory` -> `14_context/repo_knowledge/generated/task_bundle_local_memory.md`
- `local-model-worker` -> `14_context/repo_knowledge/generated/task_bundle_local_model_worker.md`
- `hermes` -> `14_context/repo_knowledge/generated/task_bundle_hermes.md`
- `content-workflow` -> `14_context/repo_knowledge/generated/task_bundle_content_workflow.md`
- `safety` -> `14_context/repo_knowledge/generated/task_bundle_safety.md`
- `next-milestone` -> `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`

## Roadmap Priority

- N+6.1A - Constrained Gemma worker routing for boring/simple local tasks, with known repo-bundle IDs only and fallback on guard failure.
- N+6.2A - Hermes Agent Workflow / Manual Bridge Verification for faster supervised task execution; safe probes only, no tokens, no provider setup.
- N+6.3A - Safe Computer-Use Preparation with Gemma + Hermes + UI-TARS observation + Browser Harness/Vercel agent-browser roadmap; observation first, human approval for every click/type/live-account action.

Hermes and safe computer-use are the next high-value lanes for long,
boring supervised tasks, but only after the constrained Gemma routing
guard is clean. No provider setup, live APIs, Telegram setup,
uncontrolled click/type, or browser automation is enabled here.

## Safety Boundaries

- no live APIs
- no provider setup or token flows
- no posting or account actions
- no money, trading, or legal actions
- no bot, captcha, or cloak bypass
- no external repo runtime wiring
- no network
- UI-TARS observation-only
- Hermes setup, provider config, Telegram, and tokens remain manual later
