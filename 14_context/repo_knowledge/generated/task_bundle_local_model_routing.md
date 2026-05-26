# Task Bundle: Local Model Routing / Guarded Worker

## Purpose

Route safe offline tasks through Gemma only when output passes repo-bundle and source metadata guard checks.

## Files To Inspect First

- `03_scripts/local_model_worker_lane.py`
- `03_scripts/local_model_output_guard.py`
- `03_scripts/ghoti_repo_knowledge_map.py`
- `docs/LOCAL_MODEL_ROUTING_GUIDE.md`
- `docs/LOCAL_MODEL_OUTPUT_GUARD.md`
- `docs/LOCAL_WORKER_SAFE_TASKS.md`
- `14_context/local_worker/routing_runs/`
- `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`
- `01_projects/runtime_mvp/tests/test_n6_1a_constrained_local_model_routing_repo_bundle_guard.py`

## Current Truth

- Main hash: `39daf4d81f8a5dc123c9949ce6d7c3ea49763978`
- Latest clean milestone: N+6.1B - Constrained Local Model Routing + Repo-Bundle Hallucination Guard landed on main
- Current milestone: N+6.2A - Hermes Agent Manual Bridge Verification + WSL Usage Guide
- Previous Hermes bridge milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness.
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0; Hermes Agent / Manual Bridge and Hermes Manual Bridge / WSL Guide files available; browser/Playwright degraded/not claimed.
- Windows `C:\Users\ai_sandbox\Documents\AI_Managed_Only` maps to WSL `/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only`.
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
- `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json`
- `python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json`
- `python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json`
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle local-model-routing --json`
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

Work on constrained local model routing. Use only known repo-map bundle IDs, require source metadata, reject invented files/URLs, fallback to local_demo on guard failure, and never execute or edit from model output.
