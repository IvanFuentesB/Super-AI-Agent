# Codex-Only Workflow

Current baseline: N+5.3B clean/product-ready.

```text
origin/main = 6628e6f6fc91921225182a66ebf927982bd5464d
launcher = python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
dashboard = http://127.0.0.1:3210
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
   model-council scan, Hermes status, adapter dry-runs, and content demo checks.
4. Merge to main only when the audit gate has no blockers.
5. Push main only after the clean local merge gate passes.

## Feature Gate

Feature branches must provide tests and a final report showing what works, what
is still pending, and how any local dashboard process was cleaned up.

## Safe Codex Prompts

Audit current main:

```text
Audit current origin/main from a clean .claude/worktrees audit worktree. Run N+4/N+5 tests, launcher smoke, public audit, model council scan, Hermes status, UI-TARS dry-run, adapter status, external sandbox status, and content demo validation. Report blockers first.
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
