Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`; keep the primary worktree read-only except inspection.
Refresh compact context first with `python 03_scripts/ghoti_product_launcher.py --context-pack --json` and repo knowledge with `python 03_scripts/ghoti_product_launcher.py --repo-map --json`.
For the next milestone, inspect `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`.

Current truth:
- Main hash: `39daf4d81f8a5dc123c9949ce6d7c3ea49763978`
- Latest clean milestone: N+6.1B - Constrained Local Model Routing + Repo-Bundle Hallucination Guard landed on main
- Current feature milestone: N+6.2A - Hermes Agent Manual Bridge Verification + WSL Usage Guide
- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.
- Hermes setup/provider config/Telegram/tokens remain manual later.
- Hermes Manual Bridge / WSL Guide files live under `14_context/hermes_manual_bridge/generated/`.
- Gemma local evaluation runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.
- N+6.1B landed repo-bundle hallucination guard before routing boring local tasks.
- After N+6.2A, prioritize N+6.3A safe computer-use preparation.
- UI-TARS remains observation-only.

Next recommended milestone:
N+6.3A - Safe Computer-Use Observation Harness / Apple Comparison Dry-Run
