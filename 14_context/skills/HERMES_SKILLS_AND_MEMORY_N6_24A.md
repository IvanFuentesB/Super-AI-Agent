# Hermes: Skills, Session Memory, and Tooling (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: guidance-only / planned. No Hermes wrapper is implemented, wired, or enabled by
this note. Builds on `hermes_router_wrapper_policy.md`.

Hermes is Ghoti's **local coordinator** (a local llama-class model), not the main brain.
Its job is to read handoffs, prepare prompts, summarize, and route work to approved
wrappers - status-only, manual bridge today.

## Hermes "skills" = approved wrappers (never arbitrary commands)

Hermes runs **approved, named wrappers only**. If a task cannot be expressed as one of
the named wrappers, it does not run through Hermes - it goes to a human.

- **Phase 1 (read-only / note-writing):** `read_current_task`, `write_handoff_note`,
  `run_gemma_summary` (local loopback only), `prepare_claude_prompt`,
  `prepare_codex_audit`, `collect_agent_outputs`.
- **Phase 2 (dry-run only):** `launch_claude_task`, `launch_codex_audit` - print the
  command they *would* run and exit. They launch nothing.

The wrapper set is the safest possible shape of "Hermes skills": a closed allowlist, not
a general shell.

## Session memory

- **Durable shared memory:** the Obsidian vault (handoffs, last-audit notes, status).
- **Compiled status:** the Ghoti status brain + compact-memory snapshots under
  `14_context/compact_memory/`.
- **Repo memory vault:** `14_context/memory_vault/` (from N+6.22B) holds lists,
  preferences, tool-backlog notes, and project notes - with the no-sensitive-data rule.
- **Rule:** memory holds notes and decisions, never secrets, tokens, cookies, or auth
  files. Every wrapper run logs `local_only: true` and `live_action: false`.

## Tooling (visible names are not enablement)

`hermes skills list` may show names like `codex`, `claude-code`, `memory`, `obsidian`,
`github`, `plan`, `test-driven-development`, `mcp`, `browser`, `computer-use`. Their
presence in a list is **not** enablement. For Ghoti:

| Tool | Status for Ghoti |
|------|------------------|
| codex / claude-code | manual roles; not auto-wired |
| memory / obsidian | manual, vault-backed |
| github | human-approved git/push only |
| plan / test-driven-development | guidance-only |
| mcp | NOT enabled |
| browser / computer-use | NOT enabled (no click/type/screen/desktop control) |

## Hermes in the swarm picture

When the controlled-launcher stage is eventually approved, Hermes is the natural
**conductor**: it already reads handoffs and prepares Claude/Codex prompts. The Phase-2
`launch_*` wrappers are the seam where a real (dry-run-first) launcher would attach.

Until that audited milestone:

- Hermes coordinates **status only**; it launches and controls nothing.
- No MCP, no Telegram outbound, no browser/computer-use, no live account/API/posting/money.
- Repo-root bounded; rejects `..` traversal; one agent per task; no overlapping edits.

This note is guidance-only and planned; nothing here is enabled today.
