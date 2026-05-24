# Ghoti Current Context Pack

Generated: `2026-05-24T08:42:12Z`

## Compact Status

Ghoti status: N+5.8B - Hermes Manual Bridge Readiness landed on main at origin/main 6d1a9238d2ca. Launch `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard` then open http://127.0.0.1:3210. Hermes WSL is installed at /home/ai_sandbox/.local/bin/hermes (v0.14.0); browser/Playwright is degraded/not claimed, Codex provider pending/not proven, Telegram manual/no token, no VPS. Ollama available (ollama version is 0.24.0); Gemma model missing; local_demo fallback active. Gemma readiness 45%, mode `local_demo`, quality `pending_real_gemma_install`, no auto-downloads. Obsidian memory, repo bundles, local worker fallback, safety gates, UI-TARS observation-only, adapter dry-runs, and external static sandbox are available. Next recommended milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation.

## Current Main

- Main hash: `6d1a9238d2caa4355e475904c6433310e6cb568b`
- Latest clean milestone: N+5.8B - Hermes Manual Bridge Readiness landed on main
- Current milestone: N+5.9A - Real Gemma Install / Model Availability Decision + Local Task Quality Evaluation
- Next recommended milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation

## Launch

- Launcher command: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard URL: `http://127.0.0.1:3210`
- Context pack command: `python 03_scripts/ghoti_context_pack_builder.py --write --json`
- Repo map command: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Next bundle command: `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`
- Hermes bridge status: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Hermes bridge write: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`
- Gemma readiness status: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Gemma readiness doctor: `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`
- Gemma quality plan: `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`

## What Works Now

- Launcher starts the dashboard.
- Product Control Center is visible.
- Local supervised content demo exists: 8 agents, 100 titles, 100 thumbnails, local preview, no posting.
- Public/security audit gates run locally.
- Model council scan is local-only.
- UI-TARS observation dry-run is available and observation-only.
- Adapter dry-run/status is approval-gated and local-only.
- External sandbox remains static inspection/planning-only.
- Local memory status and fallback are repo-local.
- Repo Knowledge / Graphify Lane creates a local file map, latest report index, and task bundles.
- Hermes Agent / Manual Bridge exposes safe probes, skills index, manual checklist, and bridge packet.
- Gemma / Local Model Quality shows real model availability, manual install decision, and quality evaluation plan.
- Reports live under 14_context/.

## Pending / Manual

- Hermes provider setup.
- Hermes Codex provider verification.
- Telegram connection.
- Real Gemma model availability.
- Ruflo runtime/source availability.
- External Graphify runtime integration.
- Browser/Playwright verification.
- Future audited computer-use click/type.
- Production public release human review.

## Local Model Truth

- Ollama available: true
- Ollama version: ollama version is 0.24.0
- Gemma model found: false
- Gemma status: missing
- Fallback mode: local_demo
- Truth line: Ollama available (ollama version is 0.24.0); Gemma model missing; local_demo fallback active.

## Gemma / Local Model Quality

- Gemma readiness: 45%
- Local worker readiness: 45%
- Gemma installed: false
- Installed model count: 0
- Active local worker mode: `local_demo`
- Recommended manual command: `ollama pull gemma3:4b`
- Quality evaluation status: pending_real_gemma_install
- Status file: `14_context/local_model_readiness/generated/gemma_readiness_status.md`
- Install decision: `14_context/local_model_readiness/generated/gemma_install_decision.md`
- Quality plan: `14_context/local_model_readiness/generated/local_task_quality_plan.md`
- Rubric JSON: `14_context/local_model_readiness/generated/local_task_quality_rubric.json`
- Production routing: disabled
- Safety: no live APIs, no auto-downloads, no `ollama pull` performed by Ghoti, manual approval required before model download.

## Hermes / WSL Truth

- Hermes WSL: installed
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: v0.14.0
- Hermes browser/Playwright: degraded/not claimed unless separately verified
- Codex provider in Hermes: pending/not proven
- Telegram: manual later/no token
- No VPS

## Hermes Agent / Manual Bridge

- Hermes workflow readiness: 58%
- Status file: `14_context/hermes_workflow/generated/hermes_workflow_status.md`
- Skills index: `14_context/hermes_workflow/generated/hermes_skills_index.md`
- Operator bridge packet: `14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md`
- Status command: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Write command: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`
- Hermes setup remains manual later.
- Safe probes only; no live provider setup, no provider config, no Telegram setup, no tokens, no browser automation, no live APIs.

## Obsidian / Local Memory Truth

- Obsidian/local memory: present
- Generated context pack directory: `14_context/compact_memory/generated`
- Obsidian-compatible vault pattern: `14_context/obsidian_vault/`
- Compact memory pattern: `14_context/compact_memory/`
- This context pack is file-based and does not require Obsidian installation.

## Repo Knowledge / Graphify Lane

- Repo knowledge readiness: 55%
- Local repo knowledge map: `14_context/repo_knowledge/generated/repo_knowledge_map.md`
- Repo knowledge JSON: `14_context/repo_knowledge/generated/repo_knowledge_map.json`
- Latest report index: `14_context/repo_knowledge/generated/latest_reports_index.md`
- Best next milestone bundle: `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`
- Copy-paste repo prompt: `14_context/repo_knowledge/generated/codex_next_prompt_graph_context.md`
- Graphify runtime: roadmap only/not wired
- External repo runtime: not wired
- Network: no network
- Generate: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Bundle: `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`

## Operator Lanes

- UI-TARS: observation-only
- Adapter runner: approval-gated/local-only
- External sandbox: static inspection only
- Repo Knowledge / Graphify Lane: local map and task bundles; Graphify runtime roadmap only/not wired
- Hermes Agent / Manual Bridge: safe probes, generated readiness files, and manual setup plan
- Gemma / Local Model Quality: manual install decision and quality evaluation plan; local_demo fallback preserved

## Latest Reports

- `14_context/codex_n5_8b_main_merge_hermes_manual_bridge_readiness.md` (main): CLEAN PASS / N+5.8B MAIN MERGE READY
- `14_context/codex_n5_8a_hermes_agent_workflow_provider_setup_plan_manual_bridge.md` (report): CLEAN PASS / N+5.8A HERMES MANUAL BRIDGE READY
- `14_context/codex_n5_7b_main_merge_repo_knowledge_context_retrieval.md` (main): CLEAN PASS / N+5.7B MAIN MERGE READY
- `14_context/codex_n5_7a_graphify_repo_knowledge_map_context_retrieval.md` (report): CLEAN PASS / N+5.7A REPO KNOWLEDGE MAP CONTEXT RETRIEVAL READY
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md` (main): CLEAN PASS / N+5.6B MAIN MERGE READY
- `14_context/codex_n5_6a_local_model_gemma_setup_truth_easy_worker_lane.md` (report): CLEAN PASS / N+5.6A LOCAL MODEL EASY WORKER LANE READY
- `14_context/codex_n5_5b_main_merge_local_memory_context_pack.md` (main): CLEAN PASS / N+5.5B MAIN MERGE READY
- `14_context/codex_n5_5a_local_memory_obsidian_context_pack_brain_upgrade.md` (report): CLEAN PASS / LOCAL MEMORY CONTEXT PACK READY

## Safety Locks

- No bot/captcha/cloak bypass.
- No fake engagement.
- No spam.
- No credential/session scraping.
- No autonomous posting.
- No autonomous money/trading/legal actions.
- No live providers without human approval.
- No external repo runtime wiring without approval.

## Copy-Paste Codex Prompt

See `14_context/compact_memory/generated/ghoti_codex_next_prompt.md`.

## ChatGPT Migration Summary

See `14_context/compact_memory/generated/ghoti_chatgpt_migration_summary.md`.
