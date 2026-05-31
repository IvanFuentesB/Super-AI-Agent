# Hermes Router Wrapper Policy (guidance-only)

Milestone: N+6.6 planning (command-center architecture)
Date: 2026-05-31
Status: guidance-only — this is a policy/playbook. No wrapper is implemented,
wired, or enabled by this note. Full contracts live in
`docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md`.

## Core rule

Hermes is the local coordinator, not the main brain. Hermes runs **approved
wrappers only** and will **never run arbitrary commands**. If a task cannot be
expressed as one of the named wrappers, it does not run through Hermes — it goes
to a human.

## Approved wrapper set (planned)

Phase 1 (read-only / note-writing): `read_current_task`, `write_handoff_note`,
`run_gemma_summary` (local loopback only), `prepare_claude_prompt`,
`prepare_codex_audit`, `collect_agent_outputs`.

Phase 2 (dry-run only): `launch_claude_task`, `launch_codex_audit` — print the
command they would run and exit; they do not launch anything.

## Hard limits for every wrapper

- Repo-root bounded; vault-bounded where possible; reject `..` traversal.
- **no secrets** read or written (no `.env`, tokens, cookies, auth files).
- **no Telegram**, **no browser/computer-use**, no live account/API/posting/money.
- **no MCP installed** and none invoked.
- No destructive commands, no broad process kills, no external/unknown scripts.
- One agent per task; no overlapping edits.
- Output goes to the Obsidian vault or the wrapper run log only.
- Every run logs `local_only: true` and `live_action: false`.
- Launch wrappers are dry-run first; real launch needs a separate milestone + human.

## Status legend (consistent with the skill registry)

- guidance-only — a playbook that shapes how work is done; no runtime execution.
- planned — specified, not built.
- NOT enabled — visible/named but not approved or turned on for Ghoti.

This policy is guidance-only and planned; nothing here is enabled today.
