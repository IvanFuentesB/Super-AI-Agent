# ChatGPT / Cowork Artifacts

Artifact specifications for the dashboard / artifact agent. These are
specifications, not live integrations: they describe views to render, not wired
connectors. Any underlying connector stays disabled until set up per
`docs/GHOTI_MCP_SETUP_GUIDE.md`. Status of record:
`14_context/tool_stack/skills_registry.json`.

| Artifact | Purpose | manual_required |
|----------|---------|-----------------|
| morning-dashboard-artifact | Morning Dashboard: status + top next actions at a glance | true |
| ghoti-command-dashboard-artifact | Ghoti Command Dashboard: tool-stack status, queues, gates | true |
| gmail-calendar-figma-connectors | Read-only views over Gmail/Calendar/Figma (drafts/read only) | true |
| github-notion-connector-view | Future view over GitHub issues/PRs and Notion notes | true |
| prompt-memory-manager | Manage saved prompts and memory snapshots | true |

## Artifact specs (not live integrations)

- Morning Dashboard: a daily read-only summary surface (status, queues, top 5
  next actions). It reads generated status, it does not act.
- Ghoti Command Dashboard: surfaces tool-stack status (installed safe tools, MCP
  templates ready, skills registered, priority counts, queues, safety flags),
  ideally from the CLI `--status` JSON to avoid shared-file conflicts.
- Gmail / Calendar / Figma connector views: read-only / draft-only displays.
  Sending, posting, and edits stay blocked until the relevant connector is set
  up and reviewed.
- GitHub / Notion connector view: future, read-first.
- Prompt / memory manager: organizes prompts and memory snapshots; it does not
  duplicate the existing memory path.

All entries are manual-required: confirm the canonical source/approach before
building, and never wire a live action through an artifact view.
