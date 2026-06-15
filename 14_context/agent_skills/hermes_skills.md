# Hermes Skills

Skills for the local coordinator agent. Hermes reads Ghoti and Obsidian files
and summarizes; it does NOT execute. Status of record:
`14_context/tool_stack/skills_registry.json`.

| Skill | Purpose | manual_required |
|-------|---------|-----------------|
| local-coordinator | Coordinate local agent work from read-only state | true |
| status-summarizer | Summarize current repo/lane status | true |
| memory-compressor | Compress context into compact memory files | true |
| handoff-summarizer | Produce handoff summaries between agents | true |
| top-5-next-actions-reporter | Report the top 5 next actions | true |

## No execution

Hermes is read-only by design:

- It reads Ghoti repo files and the Obsidian vault / compact memory; it does not
  run commands, install anything, or take outbound actions.
- It must not write a second memory store; it extends the one existing memory
  path (`14_context/obsidian_vault` + `14_context/compact_memory`).
- All Hermes skills are manual-install candidates pending canonical source
  confirmation; install into a project-scoped location only.
