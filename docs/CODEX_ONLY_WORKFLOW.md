# Codex-Only Workflow

Current baseline: N+5.6B clean/local-model-easy-worker-lane on main.

```text
origin/main = c9413108006d920e0110413d3d5e195b504489c1
launcher = python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
dashboard = http://127.0.0.1:3210
context_pack = python 03_scripts/ghoti_context_pack_builder.py --write --json
local_worker = python 03_scripts/local_model_worker_lane.py --status --json
repo_map = python 03_scripts/ghoti_repo_knowledge_map.py --write --json
repo_bundle = python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
```

This milestone is handled by Codex only. Work must stay inside repo-contained
worktrees under `.claude/worktrees/`; the primary worktree is read-only except
for inspection.

## Operating Rules

- Create local worktrees for audit, merge-gate, and feature work.
- Do not force-push, rewrite history, or erase user changes.
- Do not commit secrets, `.env` files, browser sessions, cookies, tokens, or
  generated runtime bundles.
- Do not perform live account actions, posting, money movement, trading, legal
  actions, provider setup, or token setup.
- Do not claim hidden or independent operation. Ghoti is supervised,
  local-first, and approval-gated.
- Keep unsafe browser/computer-use behavior blocked.
- no primary worktree mutation except read-only inspection.
- no live providers/tokens setup in Codex runs.
- `/goal` may only work once or may be restricted; normal prompts are
  acceptable when they include the same constraints.

## Merge Gate

1. Fetch remote truth.
2. Audit the target branch in an isolated worktree.
3. Run N+4/N+5 tests, launcher smoke, dashboard checks, public security audit,
   model-council scan, Hermes status, local memory/context pack checks, local
   worker lane checks, repo knowledge map checks, adapter dry-runs, and content
   demo checks.
4. Merge to main only when the audit gate has no blockers.
5. Push main only after the clean local merge gate passes.

## Feature Gate

Feature branches must provide tests and a final report showing what works, what
is still pending, and how any local dashboard process was cleaned up.

## Safe Codex Prompts

Audit current main:

```text
Audit current origin/main from a clean .claude/worktrees audit worktree. Run N+4/N+5 tests, launcher smoke, context pack, local worker status/demo, public audit, model council scan, Hermes status, UI-TARS dry-run, adapter status, external sandbox status, and content demo validation. Report blockers first.
```

Create a feature branch:

```text
Create a repo-contained worktree under .claude/worktrees from origin/main for <milestone-branch>. Keep the primary worktree read-only, add tests first, implement the smallest safe change, validate, commit, and push the feature branch.
```

Create an audit branch:

```text
Create a clean audit worktree under .claude/worktrees from origin/main, merge the pushed feature branch, run the full validation gate, write a 14_context report, commit, and push the audit branch. Do not merge main unless the user explicitly asks or the mission says to merge after a clean gate.
```

Check the daily dashboard:

```text
Start Ghoti with python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard, verify Daily Operator and Status Truth labels on http://127.0.0.1:3210, then stop only the recorded launcher PID.
```

Refresh the compact context pack:

```text
Run python 03_scripts/ghoti_context_pack_builder.py --write --json, inspect 14_context/compact_memory/generated/ghoti_status_short.md and ghoti_codex_next_prompt.md, and confirm no secrets or live-provider claims were generated.
```

Check the Easy Worker Lane:

```text
Run python 03_scripts/local_model_worker_lane.py --doctor --json and python 03_scripts/local_model_worker_lane.py --write-demo-output --json. Confirm Ollama/Gemma truth, local_demo fallback when Gemma is missing, no live APIs, no auto-downloads, and generated files under 14_context/local_worker/generated/. See docs/LOCAL_MODEL_GEMMA_SETUP_GUIDE.md and docs/EASY_WORKER_LANE_GUIDE.md.
```

Generate focused repo context:

```text
Run python 03_scripts/ghoti_product_launcher.py --repo-map --json and python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json. Inspect 14_context/repo_knowledge/generated/repo_knowledge_map.md, latest_reports_index.md, and task_bundle_next_milestone.md. Confirm Graphify runtime is roadmap only/not wired, no external runtime, no network, and no live APIs.
```

Use a task bundle before coding:

```text
Before editing, run python 03_scripts/ghoti_repo_knowledge_map.py --bundle dashboard --json or the most relevant bundle. Inspect only the listed files first, then add focused tests and implement the smallest safe change.
```
