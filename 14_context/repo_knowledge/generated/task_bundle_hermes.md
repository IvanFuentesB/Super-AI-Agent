# Task Bundle: Hermes Status Work

## Purpose

Prepare the next human/manual Hermes workflow milestone without setup/token actions.

## Files To Inspect First

- `03_scripts/hermes_local_bootstrap.py`
- `docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md`
- `docs/CODEX_ONLY_WORKFLOW.md`
- `14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md`

## Current Truth

- Main hash: `c9413108006d920e0110413d3d5e195b504489c1`
- Latest clean milestone: N+5.6B - Local Model Easy Worker Lane landed on main
- Current milestone: N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0; browser/Playwright degraded/not claimed.
- Ollama available v0.24.0; Gemma missing unless a new local check proves otherwise; local_demo fallback active.
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
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle hermes --json`
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

Plan N+5.8A Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness. Safe probes only; no setup/provider config/Telegram/tokens.
