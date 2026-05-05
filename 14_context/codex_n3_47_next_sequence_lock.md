# Codex N+3.47 - Next Sequence Lock

Milestone: N+3.47 - Re-Audit Claude N+3.45A-FIX And Prepare Final Merge Commands

Date: 2026-05-05

## Current Status

N+3.45A fix status: local commit `110a84a` present, validation passed, not pushed.

Remote Claude branch status: still old `13266ea`; not safe to merge as the final fixed branch.

Codex N+3.45B branch status: separate and clean.

N+3.46 branch status: pushed and available at `origin/audit/ghoti-agent-codex-n3-46-n3-45a-merge-audit`.

## Immediate Next Step

Claude or the user should push the two-file fix commit:

- `.claude/settings.json`
- `03_scripts/prompt_bus.py`

Expected local commit:

```text
110a84a fix(ghoti): preserve prompt bus dry-run purity
```

## After Fix Is Pushed

Recommended merge sequence:

1. Merge fixed Claude N+3.45A branch into `feat/ghoti-visible-operator-stack`.
2. Validate.
3. Push base.
4. Merge Codex N+3.45B docs.
5. Merge Codex N+3.46 docs.
6. Merge Codex N+3.47 docs.
7. Validate.
8. Push base.

## Next Milestone Recommendation

After N+3.45A/N+3.45B/N+3.46/N+3.47 are merged:

1. N+3.48 - Controlled Parallel Retrospective And Prompt Bus Dashboard Read Card.
2. N+3.49 - Ruflo isolated dependency/source audit only, no runtime wiring.
3. N+3.50 - Decide whether to expand controlled parallel pilots to one implementation lane plus one audit lane.

## Still Forbidden

- No Ruflo/OpenClaw/Paperclip/n8n/CUA/browser runtime.
- No live accounts or account connectors.
- No email sends, posting, payment, scraping, job applications, giveaway entries, or public/money actions.
- No cap-bypass, free-Claude, leaked, Mythos, or unrestricted runtime use.
- No destructive git cleanup or branch reset without explicit human approval.
