# Ghoti MCP Read-Only - Setup Guide (Phase 3, scoped filesystem)

Status: **planned_only**. MCP is **not installed** and **not enabled** by this milestone.
No MCP server is started. This guide describes the *future* Phase-3 setup so a human can
enable a **read-only, scoped** filesystem MCP later, under approval.

## The first MCP phase is read-only and scoped

The first MCP phase is read-only and scoped to the vault, docs, tool_intake, and
hermes_integrations folders. The first MCP is a **filesystem read-only** server; it can
read those folders and nothing else.

### Allowed paths (read-only)

- `14_context/agent_handoff_vault`
- `docs`
- `14_context/tool_intake`
- `14_context/hermes_integrations`

### Forbidden MCP types

- write filesystem MCP
- browser MCP
- account action MCP
- social posting MCP
- unrestricted root filesystem MCP

## Setup steps (for the future, approval-gated)

1. A human approves the first MCP and its read-only scope.
2. The filesystem MCP is configured read-only and limited to the allowed paths above.
3. No write MCP, browser MCP, account/social MCP, or root-scope MCP is added.
4. Nothing is installed by this milestone; `enabled: false`, `requires_human_approval: true`.

## Not enabled now

MCP is not installed and not enabled. No MCP server runs. Secrets are never stored in the
repo, in Obsidian, or in prompts.
