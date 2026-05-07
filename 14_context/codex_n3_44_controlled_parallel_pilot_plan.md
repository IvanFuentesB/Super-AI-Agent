# N+3.44 Controlled Parallel Pilot Plan

Status: Codex pilot plan only.
Date: 2026-05-05

## Pilot Verdict

Controlled parallel execution is not allowed yet because N+3.43 lane locks are missing.

This plan defines the first safe pilot after N+3.43 is implemented and pushed.

## Pilot Goal

Run two agents in parallel without touching the same files, while ChatGPT and Gemma remain non-writing support lanes.

The pilot should prove:

- separate branches work
- lock files prevent shared-file collisions
- status beacons keep humans oriented
- merge happens one branch at a time
- no external/live/account action occurs

## Recommended Lanes

### Claude Code Lane

Role:

- implementation-only
- dedicated branch
- owns a narrow implementation scope

Allowed pilot work:

- one small local read-only feature
- one helper script
- one docs update set

Forbidden:

- editing files locked by Codex
- external integrations
- account actions
- posting/email/payment/scraping

### Codex Lane

Role:

- audit/source-check/docs-only
- separate branch
- no runtime edits

Allowed pilot work:

- narrow source-check pack
- implementation audit
- sequence lock doc

Forbidden:

- runtime changes
- staging Claude implementation files
- shared state edits if Claude lock owns them

### ChatGPT Lane

Role:

- prompt/strategy only
- no repo writes

Allowed pilot work:

- prepare next prompts
- summarize strategy
- ask clarifying questions

Forbidden:

- claiming repo truth without Codex/Claude source
- live account actions

### Gemma Lane

Role:

- local summary/compression only
- artifact drafts only

Allowed pilot work:

- compress local docs into draft artifacts
- summarize N+3.18 through N+3.43
- never promote memory automatically

Forbidden:

- direct canonical memory overwrite
- model output execution
- external API/web calls

## Required Pilot Rules

1. Separate branches for writing agents.
2. Separate lock files.
3. No shared-file overlap.
4. No simultaneous edits to:
   - `14_context/current_state.md`
   - `14_context/next_actions.md`
   - `14_context/ghoti_finish_line_log.md`
   - `14_context/compact_memory/*`
   - `14_context/obsidian_vault/00_Index.md`
   - `14_context/obsidian_vault/01_Current_State.md`
5. No runtime external integrations.
6. No connector accounts.
7. No posting/email/payment/scraping.
8. No fake accounts or account creation.
9. Merge one branch at a time.
10. Run validation before merge.

## Suggested First Pilot

Claude branch:

```text
feat/ghoti-agent-claude-agent-lane-dashboard-read-card
```

Codex branch:

```text
feat/ghoti-agent-codex-tool-source-check-pack
```

Claude writes only dashboard/read-only agent lane files.

Codex writes only `14_context/codex_*` source-check docs.

Shared files:

- Neither branch edits `current_state.md` or `next_actions.md` until merge time.
- The integrator does state updates after one branch lands.

## Merge Protocol

1. Fetch origin in each lane before starting.
2. Create/update lane lock.
3. Record branch, local HEAD, origin HEAD.
4. Do assigned work only.
5. Validate.
6. Commit on lane branch.
7. Push lane branch.
8. Human/integrator merges one branch.
9. Rebase/refresh the other lane after first merge.
10. Merge second branch only after validation passes.

## Stop Conditions

Stop the pilot if:

- branches diverge unexpectedly
- both lanes need the same shared file
- any lane stages unrelated dirt
- validation fails
- a task requires accounts, connectors, posting, email, scraping, payments, or external tools
- an agent cannot determine whether it is overwriting user work

## Safety Boundary

Parallel does not mean autonomous. It only means multiple local planning/implementation lanes can proceed with branch isolation, locks, and human merge control.
