# Codex N+3.46 - Next Sequence Lock

Milestone: N+3.46 - Audit N+3.45A Claude Tooling/Prompt Bus Branch And Prepare Safe Merge

Date: 2026-05-05

## Current Verdict

Claude N+3.45A branch: CONDITIONAL PASS.

Codex N+3.45B branch separation: PASS.

Branch collision verdict: local-only cleanup issue. The accidental `370e19b` was not pushed to the remote Codex branch.

Merge recommendation:

- Preferred: have Claude patch `prompt_bus.py --init --dry-run` so dry-run makes no filesystem changes, then merge Claude first and Codex second.
- Acceptable: merge Claude first and Codex second now if the user explicitly accepts the local-only dry-run issue as a known follow-up fix.

## Exact Next Claude Recommendation

If using the safest path, Claude should do one tiny follow-up:

```text
Patch N+3.45A prompt_bus.py dry-run purity. Only edit 03_scripts/prompt_bus.py. Make --init --dry-run avoid creating directories. Keep --apply behavior unchanged. Run AST, prompt_bus smoke commands, agent_lane_status check, git diff --check. Commit on feat/ghoti-agent-claude-n3-45-tooling-prompt-bus and push.
```

If the user accepts the issue as non-blocking, Claude should not do more before merge.

## Exact Next ChatGPT Recommendation

ChatGPT should prepare a merge operator prompt that:

- Uses remote branches, not the polluted local Codex audit branch.
- Merges Claude first.
- Runs validations after Claude merge.
- Merges Codex docs second.
- Runs validations after Codex merge.
- Pushes `feat/ghoti-visible-operator-stack`.
- Leaves recurring local dirt unstaged.

## Exact Next Future Milestone Recommendation

After N+3.45A and N+3.45B are merged to base:

1. N+3.47 - Post N+3.45 Merge Audit And Prompt Bus Dry-Run Follow-Up, if the dry-run issue was not fixed before merge.
2. N+3.48 - Agent Lane Dashboard Read Card, if the merge is clean and the prompt bus is stable.
3. N+3.49 - Ruflo isolated source/dependency audit only, no runtime wiring.

## Still Forbidden

- No live account actions.
- No sending email.
- No posting, selling, payment, scraping, job applications, giveaway entries, or account creation.
- No Ruflo/OpenClaw/Paperclip/n8n/CUA/browser runtime wiring.
- No free-Claude cap bypass or leaked/private code runtime use.
- No branch reset or destructive cleanup without explicit human approval.
