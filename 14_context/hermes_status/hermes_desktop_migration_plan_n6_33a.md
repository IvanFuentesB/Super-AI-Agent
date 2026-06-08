# Hermes Desktop Migration Plan (N+6.33A)

**Milestone:** N+6.33A
**Status:** note + plan only — nothing migrated, installed, or enabled here

## Context

An **official NousResearch Hermes Desktop** application now exists. Ghoti
currently uses a local `.hermes` working area and the manual bridge scripts
(`hermes_agent_workflow_bridge.py`, `hermes_manual_bridge_verifier.py`). This
note records the safe migration path; it does not perform any migration.

## Migration principles

1. **Back up `.hermes` first.** Before touching anything, make a dated, read-only
   copy of the current `.hermes` directory (and any local Hermes config) inside
   the repo root's backup area. Verify the backup is complete and restorable
   before proceeding. Do not delete the original.
2. **Do not enable risky tools first.** When the official Desktop app is
   installed (in a separate, isolated step — not in the Ghoti environment), start
   with everything risky **off**: no computer-use, no browser automation, no
   account login, no MCP servers, no hooks, no auto-submit, no Docker. Bring
   capabilities online one at a time, each behind the existing approval gate.
3. **Manual bridge stays authoritative during transition.** The existing manual
   bridge (copy-paste handoff, verifier) remains the source of truth until the
   Desktop app is fully reviewed. No automatic wiring between Hermes Desktop and
   Ghoti is enabled by this milestone.
4. **Policy checker in front of any action.** Any Hermes-originated plan that
   carries an action must pass the Rust policy checker (and, for computer-use,
   the N+6.33A dual gate) before it could be accepted.

## Ordered steps (future, each needs its own audited milestone)

1. Back up `.hermes` (read-only, dated copy); verify restore.
2. Install the official NousResearch Hermes Desktop **outside** the Ghoti
   environment / working profile; review its settings and default tool surface.
3. Confirm all risky tools are disabled by default; document the exact toggles.
4. Trial a single, non-sensitive, dry-run handoff via the manual bridge; compare
   against the verifier output.
5. Only after a clean review, consider enabling one low-risk capability behind
   the approval gate. Re-audit before each additional capability.

## Hard guards

- No secrets, tokens, cookies, or `.env` content read or committed.
- No risky tool (computer-use, browser, account, MCP, hooks, auto-submit,
  Docker) enabled in this milestone or by default after migration.
- Back up before any change; never delete the existing `.hermes`.
- Migration work happens outside the operator's working profile where it touches
  installation; this repo holds the plan only.
- No NousResearch or third-party code is committed to this repo.

## References

- `hermes_agent_workflow_bridge.py`, `hermes_manual_bridge_verifier.py` (existing
  manual bridge).
- `HERMES_STATUS_PACKET.example.md`, `hermes_status_packet_schema.json` (existing
  status surface).
