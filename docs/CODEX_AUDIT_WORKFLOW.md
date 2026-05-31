# Codex Audit Workflow

Milestone: N+6.4A
Date: 2026-05-31

Codex is Ghoti's audit, review, and verification specialist. Codex does not
implement features; it independently checks Claude Code's work before a human
approves a merge.

## When Codex runs

After Claude Code finishes a task on a feature branch and records
`CLAUDE_LAST_RUN.md`, Codex audits that branch against `main`.

## What Codex checks

1. Scope: does every changed line trace to the assigned task? Flag drive-by
   refactors or unrelated edits.
2. Safety: no secrets, `.env`, tokens, cookies, or browser sessions; no live
   account/API/posting/money actions; approval gates intact.
3. Truthfulness: do the docs and report match what the code actually does?
   Flag any overclaim (for example, claiming Telegram, browser/computer-use, or
   full autonomy is enabled when it is not).
4. Validation: do the stated validation commands actually pass? Re-run them.
5. Reversibility: changes are minimal and safe to roll back via Git.

## Verdict format

Codex records the outcome in `CODEX_LAST_AUDIT.md` (vault) and/or a
`14_context/codex_*` report using one of:

- CLEAN PASS — safe to recommend for human merge.
- CONDITIONAL PASS — minor issues; list exact fixes.
- BLOCKED_VALIDATION — a required check fails or a claim is unsupported; list the
  exact blocker and the minimal fix.

## Boundaries

- Codex audits; it does not merge. Humans approve merges.
- Codex does not enable new automation, install repos, or take live actions.
- Codex and Claude Code are not automatically wired into Hermes; the audit
  handoff is manual through the vault.
