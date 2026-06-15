# Ghoti Codex, Hermes, and Cowork MCP Strategy

This branch adds strategy examples only. It deliberately does not overlap
Claude's unpublished MCP registry/CLI work.

## Codex

Prefer repo-local handoffs and built-in/read-only connectors where available.
Do not assume native MCP support in every Codex surface. Audit PR metadata,
tests, and repo state read-only first; account actions remain blocked.

## Hermes

MCP is status/memory read-only first. Hermes may summarize status, memory, and
handoffs. It may not execute, authenticate, configure providers, or control a
browser.

## ChatGPT / Cowork

Operator-reported Gmail, Calendar, and Figma connectors remain outside Ghoti's
runtime and are treated as disabled examples. Future GitHub, Notion, Ghoti
status, tool-stack status, and PR-status views should be read-only first.

## Claude Code

Claude Desktop/Claude Code may use MCP configs where supported, but real configs
and credentials stay local and manual. Reuse the disabled templates from
`14_context/mcp_connectors/config_templates/`.

Ghoti remains the repo-local source of truth and later internalizes only
reviewed, narrow connector capabilities.
