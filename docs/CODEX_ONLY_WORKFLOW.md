# Codex-Only Workflow

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
