# Shared File Lock Policy

Status: N+3.43 local safety policy.

No two active lanes may edit the same locked shared file. If overlap is needed, stop and ask the operator before continuing.

## Files Requiring Locks

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/*.md`
- `14_context/obsidian_vault/00_Index.md`
- `14_context/obsidian_vault/01_Current_State.md`
- `14_context/obsidian_vault/02_Next_Actions.md`
- `14_context/obsidian_vault/08_Dirty_State.md`
- `14_context/obsidian_vault/09_Migration_Handoff.md`
- Dashboard runtime files if a UI lane owns them.
- Scripts if an implementation lane owns them.

## Ownership Rules

- One lane owns state docs per milestone.
- A lane must declare locked shared files before writing.
- Active lock status must be visible before work begins.
- If a lock conflict is found, the later lane stops and asks.
- State docs and compact memory files are coordination surfaces, not scratchpads.
- Generated logs are not shared state unless a milestone explicitly promotes them.

## Parallel Mode Rule

Parallel mode is allowed only when branches, locks, status beacons, and merge order are explicit. Without locks, agents must work sequentially.
