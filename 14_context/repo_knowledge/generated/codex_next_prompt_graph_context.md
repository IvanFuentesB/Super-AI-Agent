Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`; keep the primary worktree read-only except inspection.
Refresh compact context first with `python 03_scripts/ghoti_product_launcher.py --context-pack --json` and repo knowledge with `python 03_scripts/ghoti_product_launcher.py --repo-map --json`.
For the next milestone, inspect `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`.

Current truth:
- Main hash: `84e880e7c3f774580a5e4ac340acd497af3027ee`
- Latest clean milestone: N+5.7B - Repo Knowledge Context Retrieval landed on main
- Current feature milestone: N+5.8A - Hermes Agent Workflow / Provider Setup Plan + Manual Bridge Readiness
- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.
- Hermes setup/provider config/Telegram/tokens remain manual later.
- UI-TARS remains observation-only.

Next recommended milestone:
N+5.9A - Real Gemma Install/Model Availability Decision + Local Task Quality Evaluation
