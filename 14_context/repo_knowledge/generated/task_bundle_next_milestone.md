# Task Bundle: Next Milestone

## Purpose

Prepare N+6.1A constrained Gemma worker routing with a repo-bundle hallucination guard before any Hermes or computer-use expansion.

## Files To Inspect First

- `03_scripts/local_model_worker_lane.py`
- `03_scripts/gemma_model_readiness.py`
- `docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md`
- `docs/EASY_WORKER_LANE_GUIDE.md`
- `docs/GEMMA_MODEL_INSTALL_DECISION.md`
- `docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md`
- `docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md`
- `14_context/local_worker/generated/local_worker_status.md`
- `14_context/local_model_readiness/generated/gemma_install_decision.md`
- `14_context/local_model_readiness/generated/local_task_quality_plan.md`
- `14_context/local_model_evaluation/runs/`
- `14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md`

## Current Truth

- Main hash: `20e1dce1e89f15a337054864560b95b82233877c`
- Latest clean milestone: N+5.9B - Gemma Readiness / Local Quality Plan landed on main
- Current milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation
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
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle next-milestone --json`
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

Plan N+6.1A constrained Gemma worker routing only after reading the N+6.0A eval. Use known repo-map bundle IDs only, reject invented bundle/file claims, require source metadata, fall back to local_demo when the guard fails, never execute or edit from model output, and keep production routing disabled unless the audit gate explicitly clears it. Then prioritize N+6.2A Hermes manual bridge verification and N+6.3A safe computer-use preparation; no live APIs/provider setup/Telegram/browser automation.
