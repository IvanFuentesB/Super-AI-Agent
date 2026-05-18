# Skill: Local Repository Markdown Link Auditor

## Purpose
A small supervised Ghoti skill that audits Markdown files in the repository for
broken relative links and reports them locally. It does not fix anything on its
own — it only produces a report for a human to act on.

## Allowed Tools
- Local filesystem read (repo-local Markdown files only)
- Local report writer (writes under 14_context/)

## Forbidden Actions
- No network access; no external API calls
- No file edits or deletes — read-only audit
- No desktop control, no browser automation
- No live account / posting / money actions

## Approval Gates
- The audit runs read-only and needs no approval.
- Any follow-up that edits files requires explicit human approval first.

## Testability
- Validated by a unit test that feeds known-good and known-broken Markdown
  fixtures and checks the reported counts.

## Expected Outputs
- A local Markdown report listing each file and any broken relative links.
- A machine-readable JSON summary with total/broken link counts.

## Rollback & Cleanup
- The skill only writes one report file; cleanup is deleting that report.
- No other state is changed, so rollback is trivial.
