# Notion Plan

Last updated: 2026-04-05

## Current verified state

Notion desktop is installed, but real Codex-side Notion integration is not verified.

I do not currently have verified ability to:

- search Notion
- read pages through a Notion API or MCP bridge
- write or update Notion pages from this session

## Exact blocker

There is no verified Notion MCP setup and auth flow for this session yet.

## Local-first plan for now

Use this workspace as the source of truth first, then sync selected docs into Notion later.

Local folders already prepared:

- `16_notion/exports`
- `16_notion/briefs`
- `16_notion/drafts`
- `16_notion/sync_queue`

## Proposed Notion structure later

### Top-level page: Sandbox HQ

Subsections:

- setup log
- decisions
- repo evaluations
- assistant stack roadmap
- automation ideas
- tool install tracker
- extension review tracker
- current priorities

### Suggested databases

1. Setup Log
   - date
   - change
   - risk
   - rollback
   - local doc link
2. Decisions
   - decision
   - status
   - rationale
   - alternatives
3. Repo Evaluations
   - repo
   - purpose
   - classification
   - verdict
   - source links
4. Tool Install Tracker
   - tool
   - status
   - reason
   - install timing
5. Extension Review
   - extension
   - editor
   - status
   - keep/remove/later
6. Experiments
   - experiment
   - stack
   - result
   - next step
7. Automation Ideas
   - automation
   - trigger
   - risk
   - benefit
8. Tasks
   - task
   - priority
   - blocker
   - owner

## Sync rule later

- Keep operational truth local in markdown first.
- Push summaries, decisions, and trackers into Notion later.
- Do not make Notion the only copy of setup-critical information.
