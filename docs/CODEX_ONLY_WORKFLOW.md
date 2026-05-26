# Codex-Only Workflow

Current baseline: N+6.1B clean/constrained local model routing guard on main.

Previous clean baseline: N+5.7B clean/repo-knowledge-context-retrieval on main
at `84e880e7c3f774580a5e4ac340acd497af3027ee`.

Lineage note: N+5.6B clean/local-model-easy-worker-lane landed at
`c9413108006d920e0110413d3d5e195b504489c1`.

```text
origin/main = 39daf4d81f8a5dc123c9949ce6d7c3ea49763978
launcher = python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
dashboard = http://127.0.0.1:3210
context_pack = python 03_scripts/ghoti_context_pack_builder.py --write --json
local_worker = python 03_scripts/local_model_worker_lane.py --status --json
local_worker_routing = python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json
gemma_status = python 03_scripts/ghoti_product_launcher.py --gemma-status --json
gemma_doctor = python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
gemma_quality = python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
local_model_eval = python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
repo_map = python 03_scripts/ghoti_repo_knowledge_map.py --write --json
repo_bundle = python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
hermes_bridge = python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json
hermes_manual = python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json
hermes_wsl_guide = python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json
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
- Do not run `ollama pull` from Codex unless the current prompt explicitly
  approves the exact model command. N+6.0A approved exactly one local
  `ollama pull gemma3:4b`; no extra model pulls are allowed.
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

## Current Roadmap Priority

The next safe order is:

1. N+6.1B - constrained Gemma worker routing plus repo-bundle hallucination
   guard is the current main baseline.
2. N+6.2A - Hermes Agent Workflow / Manual Bridge Verification. Safe probes and
   manual bridge packet only; no tokens, provider setup, Telegram setup, live
   APIs, browser automation, or computer-use click/type.
3. N+6.3A - Safe Computer-Use Preparation with Gemma, Hermes, UI-TARS
   observation, Browser Harness, and Vercel agent-browser roadmap. Observation
   first; every click/type/live-account action remains human-approved.

Do not start N+6.3A until N+6.2A passes a clean audit gate.

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

Check Gemma readiness and quality plan:

```text
Run python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json, python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json, and python 03_scripts/ghoti_product_launcher.py --gemma-write-readiness --json. Confirm Ollama status, Gemma installed yes/no, local_demo fallback when missing, manual approval required before model download, no ollama pull performed, production routing disabled, and generated files under 14_context/local_model_readiness/generated/. See docs/GEMMA_MODEL_INSTALL_DECISION.md and docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md.
```

Check first local model eval:

```text
Run python 03_scripts/ghoti_product_launcher.py --local-model-eval --json. Confirm the model, score, task pass count, safety/JSON flags, production routing disabled, and latest run path under 14_context/local_model_evaluation/runs/. Do not treat a real model score as permission for autonomous routing.
```

Plan constrained Gemma routing:

```text
Build or audit N+6.1A constrained Gemma worker routing from the clean N+6.0B result. Allowed tasks only: summarize latest report, status paragraph, Codex next prompt, safety classification, context bundle summary, next milestone outline, and report-to-bullets. Run python 03_scripts/local_model_output_guard.py --self-test --json. Use known repo-map bundle IDs only, reject invented bundle/file claims, require source metadata, fall back to local_demo on guard failure, and never execute commands or edit files from model output.
```

Generate focused repo context:

```text
Run python 03_scripts/ghoti_product_launcher.py --repo-map --json and python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json. Inspect 14_context/repo_knowledge/generated/repo_knowledge_map.md, latest_reports_index.md, and task_bundle_next_milestone.md. Confirm Graphify runtime is roadmap only/not wired, no external runtime, no network, and no live APIs.
```

Check Hermes manual bridge readiness:

```text
Run python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json and python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json. Inspect 14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md. Confirm Codex provider pending/not proven, Telegram manual later/no token, browser/Playwright degraded/not claimed, safe probes only, and no live provider setup.
```

Check Hermes WSL guide:

```text
Run python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json, python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json, and python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json. Confirm C:\\Users\\ai_sandbox\\Documents\\AI_Managed_Only maps to /mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only, generated files live under 14_context/hermes_manual_bridge/generated/, and no live API/provider/Telegram/browser/computer-use action was run.
```

Use a task bundle before coding:

```text
Before editing, run python 03_scripts/ghoti_repo_knowledge_map.py --bundle dashboard --json or the most relevant bundle. Inspect only the listed files first, then add focused tests and implement the smallest safe change.
```
