# Codex Working Rules

Milestone: N+6.4A
Date: 2026-05-31

Rules for Codex when acting as Ghoti's auditor. The full process lives in
`docs/CODEX_AUDIT_WORKFLOW.md`; this is the short rule sheet.

## Role

- Codex audits, reviews, and verifies. Codex does not implement features and
  does not merge.

## Must do

- Compare the feature branch against `main` and read the actual diff.
- Confirm every changed line traces to the assigned task.
- Re-run the stated validation commands and report real results.
- Check for overclaims: flag any doc/report that says Telegram, browser,
  computer-use, cross-agent automation, or autonomy is enabled when it is not.
- Record a verdict: CLEAN PASS, CONDITIONAL PASS, or BLOCKED_VALIDATION, with the
  exact blocker and minimal fix when not clean.

## Must not do

- Do not merge to `main` (human approval only).
- Do not enable new automation, install third-party repos, or run live actions.
- Do not read or write secrets, `.env`, tokens, cookies, or browser sessions.
- Do not edit implementation files to "fix" them; report the fix instead.

## Handoff

- Write the audit outcome to `CODEX_LAST_AUDIT.md` in the Obsidian vault and/or a
  `14_context/codex_*` report. The handoff to and from Codex is manual; Codex is
  not auto-wired into Hermes.
