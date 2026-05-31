# Command-Center Architecture Summary (planning log)

Milestone: N+6.6 → N+6.9 command-center architecture (PLAN / SPEC ONLY)
Date: 2026-05-31
Lane: systems architect (planning lane)
Base main: origin/main contains N+6.4A and N+6.4B.

This log records what the planning milestone produced. Nothing is implemented,
wired, or enabled. Each phase below is a future milestone with its own branch,
audit, and human merge.

## End-state vision

> ChatGPT thinks → Hermes coordinates → Obsidian remembers → Claude implements →
> Codex audits → Gemma summarizes → Human approves.

ChatGPT is the main brain (architecture, prompts, safety). Hermes is the local
coordinator, not the main brain. Claude implements; Codex audits/merge-gates;
Gemma compresses; Llama is Hermes' local brain; Git is the rollback path; the
human owns the final gate.

## Documents produced

- `docs/GHOTI_COMMAND_CENTER_ROADMAP.md` — roles, phase order, MCP plan,
  computer-use clarification, standing safety guarantees.
- `docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md` — eight wrapper contracts.
- `docs/GHOTI_N6_7_TOOL_REPO_INTAKE_SPEC.md` — 10-step intake; candidate tables.
- `docs/GHOTI_N6_8_COMMAND_CENTER_ANALYTICS_SPEC.md` — fast dashboard + local-first analytics.
- `docs/GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md` — routing + Obsidian contract.
- `14_context/skills/hermes_router_wrapper_policy.md` — condensed wrapper policy (guidance-only).
- `14_context/agent_handoff_vault/05_Backlog/n6_6_7_8_9_command_center_backlog.md` — phased backlog.
- `02_Agent_Handoffs/NEXT_CLAUDE_TASK.md` / `NEXT_CODEX_AUDIT_PROMPT.md` — N+6.6A handoffs.

## Phase order

N+6.6A wrappers + tests → N+6.6B dry-run launch wrappers → N+6.7A first intake
(MarkItDown, Understand-Anything) → N+6.8A dashboard scaffold + local analytics →
N+6.9A router policy enforcement.

## Standing safety guarantees (whole roadmap)

- Hermes runs **approved wrappers only**; **never run arbitrary commands**.
- **no secrets**, **no Telegram**, **no browser/computer-use**, **no MCP installed**.
- Tool intake does **no blind installs**; analytics is **local-first**.
- No autonomous launch; launches are dry-run first; a human approves every merge.

## Recommended next step

N+6.6A — Hermes Router Wrapper System (dry-run only). See the NEXT_CLAUDE_TASK and
NEXT_CODEX_AUDIT_PROMPT notes in `02_Agent_Handoffs/`.
