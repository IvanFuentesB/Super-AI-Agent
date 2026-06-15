# Assistant Productivity Stack Summary

## Scope

This branch adds disabled-by-default productivity packs for Codex, Hermes,
Claude Code, ChatGPT/Cowork, routines, MCP strategy, and Ruflo planning. It
also adds a deterministic Rust validator for the committed example configs.

The branch extends the acceleration-stack branch and does not replace or
overlap its tool-stack CLI, MCP implementation, or skills registry.

## Usable now

- Codex has reusable audit, continuation, merge-gate, repo-intake, and
  token-saving prompts.
- Hermes has source-linked status, memory, handoff, tool, and next-action
  summary prompts.
- Claude Code has a documented skills strategy and a pinned, inspect-first
  statusline setup candidate.
- ChatGPT/Cowork has morning-dashboard, strategy-to-builder, connector-review,
  memory-manager, and opportunity-review prompts.
- Ruflo has planning-only prompts grounded in statically inspected package
  metadata.
- The Rust `assistant_productivity_guard` validates the ten committed example
  configs for disabled defaults, secret-like values, private paths, command
  entries, credentialed connector enablement, and deterministic fingerprints.

## Still disabled

No pack installs tools, changes global settings, enables hooks, authenticates
connectors, schedules routines, launches Ruflo, performs live actions, or
touches accounts. Statusline installation and every credentialed connector
remain manual future steps.

## Validation evidence

- Ten example JSON configs parse and pass the Rust guard.
- Focused Python productivity tests cover configs, prompts, routines, statusline
  honesty, disabled connectors, and private-data checks.
- The Rust workspace passes with a temporary Cargo target directory.
- Public repository security audit passes with zero blockers.
- The acceleration-stack tool CLI's write-capable checks must be reproduced
  from a disposable writable worktree on this machine because Windows protects
  the Documents directory from generated-file writes.

## Integration order

1. Merge the acceleration-stack PR first.
2. Rebase or merge this productivity branch onto the resulting main.
3. Keep the independent Ruflo evidence branch separate unless its audit and
   merge gate pass.

The next implementation step is a narrow Agent OS integration that renders
these disabled configs and prompt packs as read-only status and operator
actions without enabling live connectors or routines.
