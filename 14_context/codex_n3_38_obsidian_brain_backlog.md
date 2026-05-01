# N+3.38 Obsidian Brain Backlog

Status: Codex docs/spec/backlog only.
Date: 2026-05-01

The Obsidian/local memory layer is vital infrastructure for Ghoti because it lowers token cost, preserves continuity, and gives Claude/Codex/ChatGPT compact high-signal context without losing durable records.

## Future vault structure

Proposed repo-local path:

```text
14_context/obsidian_vault/
  00_Index.md
  01_Current_State.md
  02_Next_Actions.md
  03_Decisions.md
  04_Tools_And_Repos.md
  05_Money_OS.md
  06_Safety_Gates.md
  07_Agent_Routing.md
  08_Dirty_State.md
  09_Migration_Handoff.md
```

## Folder/file naming rules

- Use stable numbered files for canonical overview memory.
- Use date-prefixed notes for time-based captures when needed: `YYYY-MM-DD_short_slug.md`.
- Use lowercase snake_case for generated artifacts and helper docs.
- Keep file names boring and searchable.
- Never encode secrets, API keys, account credentials, or private personal data in filenames or note bodies.

## Compact memory files

Proposed path:

```text
14_context/compact_memory/
  project_state.md
  repo_and_tool_index.md
  money_os_memory.md
  agent_routing_memory.md
  safety_rules.md
  dirty_state_warning.md
```

Compact memory is a compressed pointer layer. It must point back to durable source docs and must not be used as an excuse to delete original records.

## Source-of-truth vs compressed pointer memory

- Source-of-truth: milestone docs, current state, next actions, finish line logs, audit docs, schemas, trackers, and committed artifacts.
- Compressed pointer memory: small files optimized for prompt loading that cite exact source docs and summarize only stable facts.
- Draft memory: Gemma or Codex-generated compression output that has not been promoted by human/Claude/Codex review.

## No data loss rule

- Do not delete durable records when compacting memory.
- Do not overwrite canonical memory with model output unless explicitly requested and reviewed.
- Preserve commit hashes, file paths, commands, validation results, decisions, and open risks.
- Mark unknowns as unknown instead of filling gaps.

## Gemma compression drafts

Gemma can draft:

- milestone summaries
- dirty-state summaries
- money workflow summaries
- tool intake summaries
- prompt packs for Claude/Codex/ChatGPT
- risk labels and checklist summaries

Gemma must not:

- invent missing commit hashes, revenue, metrics, validation results, or tool status
- execute output
- promote drafts to canonical memory without review
- delete original source documents

## Human promotion to canonical memory

Promotion flow:

1. Generate local draft under a log or draft folder.
2. Include source file references and metadata header.
3. Human or trusted agent reviews factual accuracy.
4. Only then merge into canonical Obsidian vault or compact memory.
5. Record date, reviewer, source files, and open unknowns.

## Dirty-state tracking

`08_Dirty_State.md` and `dirty_state_warning.md` should always preserve:

- files intentionally dirty
- files that must not be staged
- whether dirty files are Claude partial implementation, user local notes, logs, third-party, CV docs, output, or scratch files
- latest safe staging whitelist
- latest branch/HEAD truth when known

## Token-efficient prompt packs

Future prompt packs should provide:

- compact project state
- current branch and known HEAD
- exact next milestone
- files to inspect
- files to avoid
- validation commands
- staging whitelist
- safety gates
- source pointers instead of copied walls of context

## Karpathy-style compression principles

- Preserve facts.
- Preserve decisions.
- Preserve commands.
- Preserve file paths.
- Preserve open risks.
- Preserve source references.
- Cut repetition.
- Use pointers to source docs.
- Prefer structured bullets and stable identifiers.
- Never invent missing data.
- Mark confidence and unknowns explicitly.

## Future script ideas only

- `memory_compress_draft.py`: stdlib-only helper that reads selected repo-local files and writes a draft compact memory file.
- `memory_promote_check.py`: verifies metadata, source references, and unknown markers before manual promotion.
- `dirty_state_snapshot.py`: captures git status into a markdown handoff.
- `prompt_pack_builder.py`: builds small Claude/Codex/ChatGPT prompt packs from compact memory.

No script is implemented in N+3.38.
