# MCP Read-Only Plan (Phase 3, planned_only)

Status: **planned_only**. MCP is **not installed** and **not enabled**. No MCP server is
started. This note mirrors `mcp_read_only_plan.ps1`.

## The first MCP phase is read-only and scoped

The first MCP is a **filesystem read-only** server scoped to the vault, docs, tool_intake,
and hermes_integrations folders.

- **Allowed paths (read-only):** `14_context/agent_handoff_vault`, `docs`,
  `14_context/tool_intake`, `14_context/hermes_integrations`.
- **Forbidden:** write filesystem MCP, browser MCP, account action MCP, social posting
  MCP, unrestricted root filesystem MCP.

## Flags

`enabled: false`. `requires_human_approval: true`. `install_performed: false`.
`network_used: false`. Nothing is installed by this milestone.
