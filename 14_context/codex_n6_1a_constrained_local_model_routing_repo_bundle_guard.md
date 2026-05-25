CLEAN PASS / N+6.1A CONSTRAINED LOCAL MODEL ROUTING GUARD READY

Branch:
- Feature: feat/ghoti-agent-codex-n6-1a-constrained-local-model-routing-repo-bundle-guard
- Starting main: 1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6
- Audit branch: pending until clean audit worktree merge
- Main merge: not performed in this run

Scope:
- Added guarded local model routing for a narrow safe-task lane.
- Added repo-bundle/source output guard to prevent invented repo bundles, fake file claims, missing source metadata, URLs, and live API claims.
- Added dashboard, launcher, context pack, repo map, docs, and tests for N+6.1A.
- Added future safe computer-use Apple comparison test plan as documentation only. No browser control was executed.

Hallucination Fix:
- N+6.0A caught Gemma inventing `StableLM-DanceDiffusion` and citing an external GitHub URL during the repo-bundle identification task.
- N+6.1A adds `03_scripts/local_model_output_guard.py`.
- Guard self-test rejects `StableLM-DanceDiffusion` as an invented/unsupported bundle.
- Guard self-test rejects unknown source files such as `docs/DOES_NOT_EXIST.md`.
- Routed output must include `source_metadata` with known `bundle_ids`, known `file_paths`, `local_only=true`, and `live_api_used=false`.

Safe Task Allowlist:
- summarize-latest-report
- status-paragraph
- codex-next-prompt
- safety-classification
- context-bundle-summary
- next-milestone-outline
- report-to-bullets

Blocked Routed Tasks:
- code editing
- shell commands
- browser actions
- API actions
- posting
- money/trading/legal decisions
- credential/session handling
- unsupported file claims
- live account operations

Routing Status:
- Local model routing readiness: 82%
- Gemma installed: yes, `gemma3:4b`
- Active route preference: `ollama_gemma_guarded`
- Guard enabled: true
- Source metadata required: true
- Production routing enabled: false
- Fallback available: true
- Latest routing run: `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo`
- Demo guard statuses: pass, pass, pass
- Demo fallback used: false
- `status-paragraph` route task passed guard with known bundles `next-milestone` and `local-model-worker`.

Generated Files:
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/00_routing_manifest.json`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/01_task_inputs.json`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/02_gemma_outputs.md`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/03_guard_results.json`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/04_fallback_outputs.md`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/05_final_outputs.md`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/06_quality_review.md`
- `14_context/local_worker/routing_runs/20260525T091510Z_guarded_routing_demo/07_next_steps.md`
- `14_context/repo_knowledge/generated/task_bundle_local_model_routing.md`

Dashboard:
- Added card: Local Model Routing / Guarded Worker
- Shows Gemma installed, active model, routing safe-task status, guard status, bundle allowlist source, fallback status, latest routing run path, safe task list, and blocked execution/browser/API behavior.

Launcher Commands:
- `python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json`
- `python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json`
- `python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json`

Core Operator Commands:
- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Local worker: `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- Gemma status: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Local eval: `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`
- Repo map: `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- Hermes bridge: `python 03_scripts/hermes_agent_workflow_bridge.py --status --json`

Validation:
- `git diff --check`: PASS
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 14 OK
- Total runtime tests: 440 OK
- Launcher smoke: PASS
- Context pack generation: PASS
- Local worker status/demo: PASS
- Gemma status: PASS
- Local model eval: PASS, cached real eval score 86%
- Routing status: PASS
- Route task `status-paragraph`: PASS
- Routing demo: PASS
- Output guard self-test: PASS
- Hermes bridge status: PASS
- Hermes local bootstrap status: PASS
- Repo map status and launcher repo-map: PASS
- Repo bundle next-milestone: PASS
- Local memory status: PASS
- Public repo security audit: 150 checks, 0 blockers, 7 warnings requiring human review
- Model council scan: PASS
- UI-TARS dry-run: PASS, observation-only
- Approved adapter runner status: PASS, approval-gated/local-only
- External sandbox status: PASS, static inspection only
- Supervised content demo validate-latest: PASS
- Node syntax checks: PASS
- Runtime PowerShell check: PASS
- Dashboard PowerShell check: first run hit a local transport interruption during a desktop hotkey check; rerun with repo-supported resource-guard fixture passed.

Public/Safety Truth:
- No live APIs used.
- No provider setup performed.
- No Telegram setup performed.
- No browser automation performed.
- No extra model pulls performed.
- No commands executed from model output.
- No files edited from model output.
- UI-TARS remains observation-only.
- Adapter runner remains approval-gated/local-only.
- External sandbox remains static inspection only.

Hermes / WSL Truth:
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version: Hermes Agent v0.14.0 (2026.5.16).
- Hermes readiness: 58%.
- Parsed skills: 78.
- Codex provider in Hermes: pending/not proven.
- Telegram: manual later/no token.
- Browser/Playwright: degraded/not claimed.
- No VPS.

Apple Computer-Use Test Plan:
- Path: `docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md`
- Status: future plan only.
- It requires observation-first operation and human approval for every future click/type/live-account action.
- It forbids login, purchase, cart actions, account actions, cookie/CAPTCHA/bot/cloak bypass, fake user behavior, and autonomous browser control.

What Works Now:
- Gemma-backed local worker can route the safe `status-paragraph` task through the output guard.
- Routing demo generated local artifacts with guard pass results.
- Invented repo bundles/files are rejected before acceptance.
- Fallback to `local_demo` remains available if the guard rejects output or Gemma is unavailable.
- Dashboard and launcher surface guarded routing status without enabling unsafe autonomy.

What Remains:
- N+6.1A is not merged to main in this run.
- Broad production routing remains disabled.
- Hermes provider/Codex provider verification remains manual and unproven.
- Telegram remains manual/no token.
- Browser/Playwright and real computer-use remain future-gated.
- N+6.2A should verify Hermes manual bridge workflow safely.
- N+6.3A should prepare the safe computer-use observation harness.

Cleanup:
- Only repo-local validation artifacts were generated.
- No broad process kills were used.
- Dashboard checker rerun passed; no unrelated processes were killed.
- Primary worktree remained read-only except inspection.

Human Status:
Ghoti is about 90% complete toward the bigger local-first agent OS vision. The local MVP is stable and now has a real, guarded Gemma worker lane for narrow offline tasks. Current capabilities are dashboard/launcher, audited safety gates, compact memory/context packs, repo knowledge bundles, real Gemma local evaluation, guarded local task routing, Hermes manual bridge status, and observation-only computer-use planning. The main gaps are Hermes provider verification, Telegram/manual provider bridge, broader model routing, reliable browser/computer-use harnesses, and production/public release review. Confidence: high because the feature and safety contracts are covered by runtime tests, product probes, and public audit, while risky actions remain blocked.

Final Verdict:
CLEAN PASS / N+6.1A CONSTRAINED LOCAL MODEL ROUTING GUARD READY
