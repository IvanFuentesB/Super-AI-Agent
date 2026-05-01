# Codex N+3.37 Next Sequence Lock

Status: codex_sequence_lock / no_runtime_edits

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Current HEAD: e25a24c

## Current State

N+3.18 is now finished and pushed at:

```text
e25a24c feat(ghoti): finish N+3.18 video money runner
```

Ghoti MCP source appears safe and read-only, but Claude Code connection is not verified from this Codex shell because:

- `claude` is not available on PATH
- `14_context/n3_36_claude_mcp_connection_report.md` is missing
- no repo-root `.mcp.json` was found

## Sequence If MCP Is Verified Safe

If Claude Code can confirm `ghoti-local` is connected and read-only, proceed:

1. `N+3.29 Claude - Weekly Money Review Artifact Generator`
2. `N+3.30 Claude - Weekly Money Review Dashboard Read Card`
3. `N+3.31 Claude - Manual Queue Draft Intake Helper`
4. `N+3.32 Claude - Manual Queue Read View + Operator Work Session Planner`
5. `N+3.34 Claude - Obsidian Vault + Compact Memory Scaffolding`
6. Isolated Paperclip/OpenClaw/n8n/Paseo/Bulwark research only

Why this order:

- N+3.29 uses the now-finished N+3.18 money runner/scoring foundation.
- N+3.30 reads generated artifacts and stays read-only.
- N+3.31 converts reviewed candidates into local queue drafts only.
- N+3.32 lets the operator plan safe local work sessions.
- N+3.34 compresses stable repo truth after core artifacts exist.
- External orchestration/governance tools should not be connected until Ghoti's local gates are stable.

## Sequence If MCP Is Unsafe Or Unverified

Before connecting more tools:

1. Create or recover `14_context/n3_36_claude_mcp_connection_report.md`.
2. Confirm `claude mcp list`.
3. Confirm `claude mcp get ghoti-local`.
4. Confirm tool list contains only read/status tools.
5. Confirm there are no shell/write/delete/network/live-account tools.
6. Confirm project/user/global scope is intentional.

Then proceed to N+3.29.

Do not connect:

- OSINT tools
- posting tools
- email tools
- payment tools
- creative app connectors
- browser automation
- account APIs

until a separate explicit approval milestone.

## Tooling Research Sequence

After N+3.29 to N+3.34:

1. Paperclip isolated evaluation
2. Paseo isolated evaluation
3. Bulwark governance-pattern evaluation
4. n8n rails evaluation
5. OpenClaw worker/channel evaluation
6. Honcho memory comparison
7. Skene growth/onboarding comparison
8. Creative connector safety plan
9. OSINT defensive-only plan

All are planning/research until explicitly approved.

## Safety Lock

No future milestone should introduce:

- automatic posting
- automatic selling
- automatic outreach
- payments
- live account mutation
- scraping with legal/TOS risk
- fake proof/testimonials
- fake engagement
- autonomous trading or investment
- model-output execution

## Exact Next Claude Recommendation

If MCP can be verified quickly:

```text
N+3.29 Claude - Weekly Money Review Artifact Generator
```

If MCP cannot be verified:

```text
N+3.36 follow-up - Verify ghoti-local MCP connection and write connection report
```

## Exact Next Codex Recommendation

Codex should continue to:

- audit new Claude commits
- review MCP/tool safety
- create implementation briefs
- source-check candidate tools

Codex should not:

- implement runtime layers unless explicitly requested
- connect external tools
- stage local dirt
- run live-account workflows

## Verdict

N+3.18 unlocks the next Money OS implementation sequence. The only reason to delay N+3.29 is if the operator wants MCP verification finished first, because a read-only MCP bridge will make Claude's later work cheaper and safer.
