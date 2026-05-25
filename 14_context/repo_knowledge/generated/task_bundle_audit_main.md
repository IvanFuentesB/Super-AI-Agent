# Task Bundle: Audit Current Main

## Purpose

Validate origin/main from a clean worktree and report blockers only.

## Files To Inspect First

- `README.md`
- `03_scripts/public_repo_security_audit.py`
- `03_scripts/ghoti_product_launcher.py`
- `01_projects/runtime_mvp/tests`
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md`

## Current Truth

- Main hash: `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`
- Latest clean milestone: N+6.0B - Human-Approved Gemma Install + First Local Evaluation landed on main
- Current milestone: N+6.1A - Constrained Local Model Routing + Repo-Bundle Hallucination Guard
- Previous Hermes bridge milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness.
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0; Hermes Agent / Manual Bridge files available; browser/Playwright degraded/not claimed.
- Ollama available v0.24.0; Gemma is installed only if local `ollama list` proves it; local_demo fallback remains available.
- Gemma / Local Model Quality files live under `14_context/local_model_readiness/generated/`; local eval runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.
- UI-TARS observation-only; adapter runner approval-gated/local-only; external sandbox static inspection only.
- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.

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

## Useful Commands

- `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`
- `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`
- `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle audit-main --json`
- `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`

## Validation Commands

- `git diff --check`
- `git show --check --stat HEAD`
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n4_*.py" -v`
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n5_*.py" -v`
- `python 03_scripts/ghoti_product_launcher.py --smoke --json`
- `python 03_scripts/ghoti_repo_knowledge_map.py --write --json`
- `python 03_scripts/public_repo_security_audit.py --run --json`

## Known Limitations

- Graphify is a roadmap concept here; the external Graphify runtime is not wired.
- This bundle is generated from a selected local file map, not a full graph database.
- Browser/Playwright and Hermes provider support are not claimed.
- Generated reports may need refresh after a new milestone.

## Next Recommended Prompt

Audit current origin/main from a clean repo-contained worktree. Run N+4/N+5 tests, product probes, public audit, and report blockers only.
