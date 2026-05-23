# N+5.7B Main Merge - Repo Knowledge Context Retrieval

Generated: 2026-05-23

## Verdict

CLEAN PASS / N+5.7B MAIN MERGE READY

N+5.7A was merged into the main merge gate through the audited branch and validated cleanly. The branch is ready to push to `origin/main`.

## Branches And Commits

- Starting `origin/main`: `c9413108006d920e0110413d3d5e195b504489c1`
- Merged feature branch: `feat/ghoti-agent-codex-n5-7a-graphify-repo-knowledge-map-context-retrieval`
- Feature commit: `b32b80e8f90f86c4ae4fb2a6626e5c0bcf474f6c`
- Merged audit branch: `audit/ghoti-agent-codex-n5-7a-graphify-repo-knowledge-map-context-retrieval`
- Audit commit: `c9afca649524f13f70f4e4e809e7e20c120569db`
- Merge-gate branch: `merge/ghoti-agent-codex-n5-7b-main-repo-knowledge-context-retrieval`
- Merge validation marker: `09683d6f859a7aab2fbab1e694d16c919c956485`
- Final merge HEAD: this report commit

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- N+4 tests: 329 OK
- N+5 tests: 85 OK
- Total tests: 414 OK
- `python 03_scripts/ghoti_product_launcher.py --smoke --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`: PASS
- `python 03_scripts/ghoti_repo_knowledge_map.py --status --json`: PASS
- `python 03_scripts/ghoti_repo_knowledge_map.py --write --json`: PASS
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle next-milestone --json`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 blockers, 7 warnings
- `python 03_scripts/model_council_tool_intake.py --scan --json`: PASS
- `python 03_scripts/hermes_local_bootstrap.py --status --json`: PASS
- `python 03_scripts/local_memory_compression_bridge.py --status --json`: PASS
- `python 03_scripts/local_model_worker_lane.py --status --json`: PASS
- `python 03_scripts/ui_tars_observation_adapter.py --dry-run --json`: PASS
- `python 03_scripts/approved_adapter_runner.py --status --json`: PASS
- `python 03_scripts/external_tool_sandbox_manager.py --status --json`: PASS
- `python 03_scripts/supervised_content_mvp_runner.py --validate-latest`: PASS
- `node --check 01_projects/dashboard_mvp/server.js`: PASS
- `node --check 01_projects/dashboard_mvp/public/app.js`: PASS
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`: PASS
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1`: PASS with resource-guard test environment forcing terminal-open to the safe blocked path

Note: the unmodified dashboard checker twice reached the guarded desktop `open_allowed_app` endpoint and the local desktop environment timed out/reset while trying to open or focus a terminal. The repo's existing resource-guard test variables were used for the final dashboard checker run so the terminal-open branch blocked safely instead of attempting desktop manipulation.

## Repo Knowledge Status

- Repo knowledge readiness: 55%.
- Status paragraph: "Repo knowledge readiness: 55%. Local file map and task bundles are available. Graphify runtime: roadmap only/not wired; no external repo runtime; no network."
- Graphify runtime: roadmap only/not wired.
- External repo runtime: none.
- Network use: none.

## Generated Repo Knowledge Files

- `14_context/repo_knowledge/generated/repo_knowledge_map.json`
- `14_context/repo_knowledge/generated/repo_knowledge_map.md`
- `14_context/repo_knowledge/generated/latest_reports_index.md`
- `14_context/repo_knowledge/generated/subsystem_index.md`
- `14_context/repo_knowledge/generated/codex_next_prompt_graph_context.md`
- `14_context/repo_knowledge/generated/chatgpt_repo_context_summary.md`

## Generated Task Bundles

- `14_context/repo_knowledge/generated/task_bundle_audit_main.md`
- `14_context/repo_knowledge/generated/task_bundle_dashboard.md`
- `14_context/repo_knowledge/generated/task_bundle_local_memory.md`
- `14_context/repo_knowledge/generated/task_bundle_local_model_worker.md`
- `14_context/repo_knowledge/generated/task_bundle_hermes.md`
- `14_context/repo_knowledge/generated/task_bundle_content_workflow.md`
- `14_context/repo_knowledge/generated/task_bundle_safety.md`
- `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`

## Operator Commands

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Local worker: `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- Repo map: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Repo bundle: `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`

## Current Truth

- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version: Hermes Agent v0.14.0 (2026.5.16).
- Hermes browser/Playwright: degraded/not claimed.
- Hermes Codex provider: pending/not proven.
- Telegram: manual later/no token.
- No VPS.
- Ollama installed: `ollama version is 0.24.0`.
- Gemma missing.
- Active worker mode: `local_demo` fallback.
- UI-TARS observation-only.
- Adapter runner approval-gated/local-only.
- External sandbox static inspection only.

## Cleanup

- Validation-only generated timestamp/status drift was restored before writing this report.
- No broad process kills were used.
- No primary worktree mutation was performed.
- Dashboard checker used the repo's resource-guard test path for terminal-open safety.

## Human Status

Human status: Ghoti is about 80% complete toward the bigger local-first agent OS vision. The local MVP is stable and usable. Current capabilities are audited dashboard control, compact memory/context packs, local worker fallback, repo knowledge map/task bundles, safe content demo, UI-TARS observation dry-runs, adapter dry-runs, and public/security gates. The main gaps are real Gemma model tasks, provider switching, Hermes workflow/provider bridge, full Graphify/runtime retrieval, and audited future computer-use click/type workflows. Confidence: high because the N+5.7B merge gate passed 414 tests plus product, safety, dashboard, and local-only probes.
