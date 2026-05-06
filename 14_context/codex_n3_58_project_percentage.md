# Codex N+3.58 - Project Percentage

## Current Estimate

- Main before merge: 74-76%.
- N+3.56-FIX branch capability if merged with current issues: 88-91%.
- After Obsidian/dashboard/whitespace fix and merge: 90-94%.
- After first controlled local pilot: 94-97%.

## Why Not Clean 90-94 Yet?

The branch meaningfully improves the system, but clean-pass reliability is not met:

- Obsidian probe crashes on inaccessible executable candidate.
- Dashboard status/json/card crash through the same probe path.
- Target `ghoti_dashboard_card.md` has trailing whitespace that fails `git diff --cached --check`.
- Ruflo source is still absent in clean checkout, though the branch now reports that truthfully.
- Gemma worker is safe, but no Gemma model is installed in the audit environment.

## What Remains For 95-100%

1. Merge-safe N+3.56-FIX with Obsidian/dashboard checks passing.
2. Browser validation of dashboard local-orchestrator card.
3. First controlled CC/Codex/ChatGPT bridge handoff.
4. Gemma model installation and one draft compression to outbox.
5. Ruflo source bootstrap and isolated `npm ci --ignore-scripts` after approval.
6. Ruflo read-only help/version/catalog smoke.
7. Local memory promotion flow from draft to canonical memory.
8. Merge assistant and rollback/restore workflow.
9. Repeated supervised local pilot runs without hidden live-action paths.

## Definition Of 100%

100% means a practical MVP of the supervised Ghoti operator stack. It does not mean AGI, uncontrolled autonomy, live account execution, or approval-gate bypass.
