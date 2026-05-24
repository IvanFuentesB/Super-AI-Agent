Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`; keep the primary worktree read-only except inspection.
Refresh compact context first with `python 03_scripts/ghoti_product_launcher.py --context-pack --json` and repo knowledge with `python 03_scripts/ghoti_product_launcher.py --repo-map --json`.
For the next milestone, inspect `14_context/repo_knowledge/generated/task_bundle_next_milestone.md`.

Current truth:
- Main hash: `20e1dce1e89f15a337054864560b95b82233877c`
- Latest clean milestone: N+5.9B - Gemma Readiness / Local Quality Plan landed on main
- Current feature milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation
- Graphify runtime: roadmap only/not wired; no external repo runtime; no network.
- Hermes setup/provider config/Telegram/tokens remain manual later.
- Gemma local evaluation runs live under `14_context/local_model_evaluation/runs/`; production routing remains disabled.
- N+6.1A must guard against repo-bundle hallucination before routing boring local tasks.
- After N+6.1A, prioritize N+6.2A Hermes manual bridge verification and N+6.3A safe computer-use preparation.
- UI-TARS remains observation-only.

Next recommended milestone:
N+6.1A - Constrained Gemma Worker Routing + Repo-Bundle Hallucination Guard
