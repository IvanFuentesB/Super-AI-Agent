# Task Bundle: Next Milestone

## Purpose

Prepare N+5.8A Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness.

## Files To Inspect First

- `03_scripts/hermes_local_bootstrap.py`
- `docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md`
- `docs/REPO_KNOWLEDGE_MAP_GUIDE.md`
- `docs/GRAPHIFY_REPO_KNOWLEDGE_ROADMAP.md`
- `14_context/repo_knowledge/generated/task_bundle_hermes.md`

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

Build N+5.8A Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness. Keep Hermes setup/provider config/Telegram/tokens manual later; safe WSL probes only.
