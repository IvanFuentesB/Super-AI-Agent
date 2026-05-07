# Codex N+3.7 Obsidian Token Vault Sync Plan

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: token_vault_sync_plan / markdown_only / not_runtime_wired / not_cap_bypass

## Current Vault Files

| File | Purpose |
|---|---|
| `14_context/obsidian_vault/00_Index.md` | Map of content / entry point |
| `14_context/obsidian_vault/01_Current_State.md` | Compact project state |
| `14_context/obsidian_vault/04_Tools.md` | Compact external tool status |
| `14_context/obsidian_vault/05_Safety_Gates.md` | Compact safety and approval rules |

## What Is Missing

Recommended next vault notes:

- `02_Next_Actions.md`
- `03_Runtime_Map.md`
- `06_Prompt_Handoff_Rules.md`
- `07_External_Repos.md`
- `08_Wait_Resume.md`

These should stay compact. The vault is for current truth and pointers, not full logs.

## Update Rules

- 200-400 words per note unless a topic truly needs more.
- One concept per note.
- Link to source files by path.
- Link to commit hashes.
- Do not paste long logs.
- Do not paste terminal transcripts.
- Do not paste runtime JSON dumps.
- Do not include secrets, private docs, credentials, or CV contents.
- Prefer "source: path" over copied paragraphs.

## Prompt Rule

Future Claude/Codex prompts should reference vault files by path and use compact summaries, not paste full logs.

Recommended prompt pattern:

```text
Read:
- 14_context/obsidian_vault/00_Index.md
- 14_context/obsidian_vault/01_Current_State.md
- 14_context/obsidian_vault/05_Safety_Gates.md

Then inspect only the specific source files needed for this milestone.
Do not paste or rewrite the full finish-line log.
```

## Suggested Sync Script Later

If a sync script is added later, it should:

- update timestamps
- check note word counts
- verify required source links exist
- optionally generate a short "vault freshness" report
- never overwrite notes without showing a diff
- never ingest private docs
- never run plugins

## No Plugins Needed Yet

Current recommendation:

- no Obsidian app dependency required
- no Obsidian plugin install
- no vector DB
- no RAG setup
- no cloud sync

Markdown is enough until context grows too large for file-based handoffs.

## Legal Token Savings

This is legal context compaction:

- compact state
- file paths
- checkpoint summaries
- small handoffs
- less duplicated prompt text

It is not:

- provider cap bypass
- quota evasion
- account abuse
- hidden usage manipulation
- safety-context removal

## Recommendation

Use the existing vault immediately as the top-level handoff surface. Add missing notes in a low-risk N+3.8 or N+3.9 doc-only/script milestone after the Screenpipe route decision.
