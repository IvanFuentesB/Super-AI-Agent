Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`; keep the primary worktree read-only except inspection.
Refresh compact context first with `python 03_scripts/ghoti_product_launcher.py --context-pack --json` and repo knowledge with `python 03_scripts/ghoti_product_launcher.py --repo-map --json`.
For the next milestone, inspect `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`.

Current truth:
- Main hash: `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`
- Latest clean milestone: N+6.0B - Human-Approved Gemma Install + First Local Evaluation landed on main
- Current feature milestone: N+6.1A - Constrained Local Model Routing + Repo-Bundle Hallucination Guard
- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.
- Hermes setup/provider config/Telegram/tokens remain manual later.
- Gemma local evaluation runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.
- N+6.1A must guard against repo-bundle hallucination before routing boring local tasks.
- After N+6.1A, prioritize N+6.2A Hermes manual bridge verification and N+6.3A safe computer-use preparation.
- UI-TARS remains observation-only.

Next recommended milestone:
N+6.2A - Hermes Agent Manual Bridge Verification + WSL Usage Guide
