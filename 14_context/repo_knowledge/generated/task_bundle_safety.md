# Task Bundle: Safety Audit

## Purpose

Keep unsafe automation blocked and public readiness truthful.

## Files To Inspect First

- `docs/BLOCKED_UNSAFE_AUTOMATION.md`
- `03_scripts/public_repo_security_audit.py`
- `03_scripts/model_council_tool_intake.py`
- `README.md`
- `SECURITY.md`

## Current Truth

- Main hash: `84e880e7c3f774580a5e4ac340acd497af3027ee`
- Latest clean milestone: N+5.7B - Repo Knowledge Context Retrieval landed on main
- Current milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0; Hermes Agent / Manual Bridge files available; browser/Playwright degraded/not claimed.
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
- `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- `python 03_scripts/ghoti_repo_knowledge_map.py --bundle safety --json`
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

Run a safety audit for false autonomy, secrets, unsafe automation, live actions, and shell command regressions. Fix blockers only.
