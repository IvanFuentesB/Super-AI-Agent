# Ghoti Repo Knowledge Map

Generated: `2026-05-23T12:40:07Z`

Repo knowledge readiness: 55%. Local file map and task bundles are available. Graphify runtime: roadmap only/not wired; no external repo runtime; no network.

- Main hash: `c9413108006d920e0110413d3d5e195b504489c1`
- Latest clean milestone: N+5.6B - Local Model Easy Worker Lane landed on main
- Current milestone: N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval
- Next recommended milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness
- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Repo map command: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Graphify runtime: roadmap only/not wired
- no external repo runtime
- no network

## Important Files

- `README.md` [docs/operator guides]: First file Ivan or GitHub visitors read before running Ghoti.
- `03_scripts/ghoti_product_launcher.py` [launcher]: Daily operator entry point and safest command surface.
- `03_scripts/ghoti_context_pack_builder.py` [local memory/context packs]: Main token-saving continuity tool.
- `03_scripts/local_memory_compression_bridge.py` [local memory/context packs]: Keeps durable memory visible without live providers.
- `03_scripts/local_model_worker_lane.py` [local model/easy worker]: Current credit-saving worker lane with local_demo fallback.
- `03_scripts/hermes_local_bootstrap.py` [Hermes/WSL]: Hermes is a planned local agent layer, but setup/provider actions remain manual.
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
- `docs/EASY_WORKER_LANE_GUIDE.md` [local model/easy worker]: Documents safe credit-saving local tasks.
- `docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md` [Hermes/WSL]: Important next human/manual milestone context.
- `docs/COMPUTER_USE_ROADMAP.md` [UI-TARS/computer-use]: Keeps click/type/autonomy future-gated.
- `docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md` [future Graphify roadmap]: Connects repo knowledge with the broader token-saving roadmap.
- `docs/BLOCKED_UNSAFE_AUTOMATION.md` [public/security audit]: Canonical list of blocked automation categories.
- `14_context/compact_memory/generated/ghoti_current_context_pack.md` [local memory/context packs]: Short current-state handoff source.
- `14_context/local_worker/generated/local_worker_status.md` [local model/easy worker]: Shows Ollama/Gemma/local_demo readiness.
- `01_projects/runtime_mvp/tests/test_n5_6a_local_model_easy_worker_lane.py` [tests]: Best current pattern for JSON script, launcher, docs, and dashboard checks.
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md` [reports/14_context]: CLEAN PASS / N+5.6B MAIN MERGE READY
- `14_context/codex_n5_6a_local_model_gemma_setup_truth_easy_worker_lane.md` [reports/14_context]: CLEAN PASS / N+5.6A LOCAL MODEL EASY WORKER LANE READY
- `14_context/codex_n5_5b_main_merge_local_memory_context_pack.md` [reports/14_context]: CLEAN PASS / N+5.5B MAIN MERGE READY
- `14_context/codex_n5_5a_local_memory_obsidian_context_pack_brain_upgrade.md` [reports/14_context]: CLEAN PASS / LOCAL MEMORY CONTEXT PACK READY
- `14_context/codex_n5_4b_main_merge_daily_operator_usability.md` [reports/14_context]: CLEAN PASS / N+5.4A DAILY OPERATOR USABILITY MERGE READY
- `14_context/codex_n5_4a_first_real_operator_usability_pass.md` [reports/14_context]: CLEAN PASS / DAILY OPERATOR USABILITY READY
- `14_context/codex_n5_3a_product_finish_remote_clean_audit.md` [reports/14_context]: CLEAN PASS for local-first supervised MVP merge gating. No blocker was found that prevents merging N+5.3A to `main`.
- `14_context/codex_n5_3a_main_merge_product_finish_local_mvp.md` [reports/14_context]: CLEAN PASS. The N+5.3A Product Control Center work is suitable for `main` as a local-first supervised MVP. No blocker was found in tests, dashboard checks, public audit, model council scan, Hermes status, local memory status, dry-runs, or s
- `14_context/codex_n5_2b_hermes_bootstrap_stack_ui_tars_manifest_fix.md` [reports/14_context]: verdict not detected
- `14_context/codex_n5_2a_hermes_local_bootstrap_public_readiness_model_provider.md` [reports/14_context]: verdict not detected

## Task Bundles

- `audit-main` -> `14_context/repo_knowledge/generated/task_bundle_audit_main.md`
- `dashboard` -> `14_context/repo_knowledge/generated/task_bundle_dashboard.md`
- `local-memory` -> `14_context/repo_knowledge/generated/task_bundle_local_memory.md`
- `local-model-worker` -> `14_context/repo_knowledge/generated/task_bundle_local_model_worker.md`
- `hermes` -> `14_context/repo_knowledge/generated/task_bundle_hermes.md`
- `content-workflow` -> `14_context/repo_knowledge/generated/task_bundle_content_workflow.md`
- `safety` -> `14_context/repo_knowledge/generated/task_bundle_safety.md`
- `next-milestone` -> `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`

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
