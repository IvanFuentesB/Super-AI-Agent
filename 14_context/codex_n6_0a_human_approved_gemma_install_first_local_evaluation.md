# Codex N+6.0A Human-Approved Gemma Install + First Local Evaluation Audit

Date: 2026-05-24

## Verdict

CLEAN PASS / N+6.0A HUMAN-APPROVED GEMMA INSTALL AND FIRST LOCAL EVAL READY

N+6.0A is pushed and audited clean. It is intentionally not merged to main in this run. N+6.1A was not started because the first real Gemma evaluation found one hallucinated repo-bundle answer and production routing remains not recommended.

## Branches

- Starting main after N+5.9B: `20e1dce1e89f15a337054864560b95b82233877c`
- N+6.0A feature branch: `feat/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- N+6.0A feature commit: `8b5a6302cbe23601343f01d6ab10efa6d777afb8`
- N+6.0A audit branch: `audit/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- Audit merge-gate HEAD before this report: `4619f70e4b8cc7eaff84996b86b3cc29e022b06b`
- N+6.0A merged to main: no, left ready per merge policy.

## Install Result

- Human approval source: this milestone prompt approved exactly one local model pull.
- Approved command run: `ollama pull gemma3:4b`
- Other pulls run: none.
- Pull result: exit 0.
- Ollama version: `ollama version is 0.24.0`
- Installed models after run: `gemma3:4b`
- Model id: `a2af6cc3eb7f`
- Model size: `3.3 GB`
- Active worker mode: `ollama_gemma`
- Gemma readiness: 74%
- Local worker readiness: 75%
- Production routing enabled: false.

## Evaluation Result

- Evaluation run: `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/`
- Preflight run: `14_context/local_model_evaluation/runs/20260524T140851Z_gemma_preflight/`
- Tasks total: 7
- Tasks passed: 6
- Real Gemma quality score: 86%
- Local demo comparison score: 55%
- JSON validity: passed.
- Production routing recommended: false.
- Quality gate note: one repo-bundle task hallucinated an external/nonexistent bundle, so N+6.1A routing was not attempted.

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 5 OK
- Total runtime tests: 431 OK
- Launcher smoke: PASS
- Context pack: PASS
- Local worker status/demo: PASS
- Gemma status/doctor/quality plan: PASS
- Local model eval launcher command: PASS, score 86%
- Hermes bridge status: PASS, readiness 58%
- Gemma readiness status: PASS, readiness 74%
- Local model worker status: PASS, readiness 75%
- Repo knowledge status: PASS, readiness 55%
- Model council scan: PASS
- Hermes local bootstrap: PASS
- Local memory status: PASS
- UI-TARS dry-run: PASS
- Adapter runner status: PASS
- External sandbox status: PASS
- Supervised content demo validation: PASS
- Node syntax checks: PASS
- Dashboard PowerShell check: PASS
- Runtime PowerShell check: PASS on isolated rerun; an earlier parallel run hit one desktop-session-sensitive checker failure, then the full rerun exited 0 and ended with `Summary: runtime MVP checks passed.`
- Dashboard HTTP/DOM/API check: PASS. Labels present, `active_worker_mode=ollama_gemma`, `gemma_installed=True`, `eval_score=86`, `production_routing=False`.
- Public audit: 150 checks / 0 blockers / 7 warnings requiring human review.

## Generated Files

- `14_context/local_model_evaluation/runs/20260524T140851Z_gemma_preflight/00_preflight.json`
- `14_context/local_model_evaluation/runs/20260524T140851Z_gemma_preflight/01_preflight.md`
- `14_context/local_model_evaluation/runs/20260524T140851Z_gemma_preflight/02_install_decision.md`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/00_manifest.json`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/01_model_status_before_after.json`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/02_eval_tasks.json`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/03_gemma_outputs.md`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/04_local_demo_baseline.md`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/05_quality_scores.json`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/06_quality_review.md`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/07_next_steps.md`
- `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/08_dashboard_summary.md`
- `docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md`

## Status Truth

- Hermes WSL: installed at `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version: Hermes Agent v0.14.0.
- Hermes bridge readiness: 58%.
- Hermes Codex provider: pending/not proven.
- Telegram: manual later/no token.
- Browser/Playwright: degraded/not claimed.
- No VPS.
- Ollama: installed, 0.24.0.
- Gemma: installed, `gemma3:4b`.
- Active worker mode: `ollama_gemma`.
- UI-TARS: observation-only.
- Adapter runner: approval-gated/local-only.
- External sandbox: static inspection only.
- Live APIs/provider setup: not used.

## What Works Now

- Ghoti can start the dashboard with `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`.
- Dashboard URL is `http://127.0.0.1:3210`.
- Gemma doctor/status/quality-plan commands report real local model truth.
- `gemma3:4b` is installed locally in Ollama and visible to Ghoti.
- First real local model evaluation is recorded and compared against local_demo fallback.
- Local demo fallback remains preserved.
- Context pack, repo map, dashboard, and docs surface the real local model state.

## What Remains

- N+6.1A local model routing should wait for a constrained task wrapper and a quality-gate repair because the first Gemma eval hallucinated one repo-bundle answer.
- Production routing remains disabled.
- Hermes provider setup, Codex provider verification, Telegram, and browser/Playwright remediation remain manual later.
- Public audit warnings still require human review before public release.

## Cleanup

- Only launcher-owned dashboard process was stopped after the local dashboard check.
- Generated validation residue was restored before writing this audit report.
- No broad process kills were used.
- No extra model pulls were run.

## Human Status

Human status: Ghoti is about 88% complete toward the bigger local-first agent OS vision. The local MVP is stable and usable. Current capabilities are a merged local-first dashboard, compact memory/context packs, repo knowledge map, Hermes manual bridge readiness, Ollama/Gemma model detection, one real Gemma model installed, and a first real local evaluation. The main gaps are quality-gated local model routing, Hermes provider verification, production-ready provider council routing, Graphify-grade retrieval, and audited computer-use actions. Confidence: high because the feature and audit branches passed 431 runtime tests plus product, safety, dashboard, and public audit checks, while the remaining routing blocker is clearly documented.
