# Backlog — Command Center (N+6.6 → N+6.9)

Milestone where noted: N+6.6 planning
Date: 2026-05-31
Status: BACKLOG ONLY — documented, phased direction; not built in this milestone.

This note records the phased plan for the Ghoti command center so the order and
scope are not lost. Nothing here is implemented, wired, or enabled by this note.
Each phase is its own future milestone with its own branch, audit, and human
merge. Full contracts live in the `docs/GHOTI_N6_*` specs.

## Phases (in order)

### N+6.6A — Hermes router wrappers + tests
- Build the Phase-1 wrappers (read-only / note-writing) from
  `docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md`.
- Wrappers run **approved wrappers only**; **never run arbitrary commands**.
- Add tests: path-traversal rejection, secret rejection, dry-run writes nothing,
  run-log `local_only:true` / `live_action:false`.
- No agent launch. No live action.

### N+6.6B — dry-run launch wrappers
- Add `launch_claude_task` / `launch_codex_audit` as **print-only dry-run** (emit
  the command they would run; never execute it).
- No real launch; real launch is a later milestone with a human present.

### N+6.7A — first tool/repo intake
- Run the 10-step intake on two safe candidates: MarkItDown and
  Understand-Anything (static review; **no blind installs**).
- Record INTAKE notes and decision records. No runtime wiring.

### N+6.8A — command-center dashboard scaffold
- Add a fast "command center" view that reads vault notes + the wrapper run log.
- Add a **local-first** analytics writer (local JSONL; no external telemetry; no
  secrets; no PII). Deletion/export are human-approved.

### N+6.9A — router policy enforcement
- Wire the orchestration policy (classification, risk gate, status lifecycle) into
  the wrappers from `docs/GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md`.
- Still supervised; launches still dry-run; `human_decision` before any merge.

## Hard constraints across all phases

- **no secrets**, **no Telegram**, **no browser/computer-use**, **no MCP installed**.
- No live account/API/posting/money actions; no autonomous launch.
- Tool intake does **no blind installs**; static inspection before any code runs.
- Analytics is **local-first** and local-only by default; nothing leaves the
  machine without explicit human approval.
- One agent per task; Git is the rollback path; a human approves every merge.

## Why this is backlog-only now

This milestone only registers the plan. Building any phase exceeds the planning
scope and requires its own milestone with a safety review and explicit human
approval. The recommended next step is N+6.6A (see the NEXT_CLAUDE_TASK and
NEXT_CODEX_AUDIT_PROMPT handoff notes).
