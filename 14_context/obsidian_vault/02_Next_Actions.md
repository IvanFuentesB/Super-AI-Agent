# Ghoti Next Actions (Compact)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/next_actions.md`, `14_context/codex_n3_42_next_sequence_lock.md`

---

## Purpose

Compact list of next safe actions, blocked actions, and handoff pointers.
Do not use stale entries for live or money-facing decisions without checking `14_context/next_actions.md`.

## Source of Truth

- `14_context/next_actions.md`
- Latest Codex recommendation docs in `14_context/`

## Update Rules

- Update after each milestone commit.
- Mark blocked actions with `[BLOCKED]`.
- Mark approved actions with `[APPROVED]`.
- Mark pending operator decisions with `[NEEDS APPROVAL]`.

---

## Current Recommended Next Milestone

**N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding**

Source: `14_context/codex_n3_42_next_sequence_lock.md`

## Exact Next Claude Action

- Commit and push N+3.34 Obsidian compact memory scaffolding to `feat/ghoti-visible-operator-stack`.
- Await Codex audit of N+3.34 before implementing N+3.43.

## Exact Next Codex Action

- Audit N+3.34 Obsidian vault and compact memory scaffolding.
- Verify files created correctly, no overwrites, no live actions.
- Verify compact memory remains pointer layer, not replacement for durable records.
- Write next sequence lock doc for N+3.43.

## Operator Approval Gates

- [NEEDS APPROVAL] Any money-facing, public, or live-account action.
- [NEEDS APPROVAL] Any connector wiring or external API call.
- [BLOCKED] Docker CUA smoke — requires explicit approval phrase.
- [BLOCKED] JobSpy / email / social posting / giveaway workflows — forbidden.

## Blocked / Waiting

- External connector wiring: blocked until explicitly approved.
- JobSpy / email / LinkedIn / social posting: blocked (not in scope).
- Live account actions: require explicit operator approval per action.
- OpenClaw / Paperclip / n8n: planning_only only.

---

## Review Status

**status:** draft
**review_required:** yes — verify against `14_context/next_actions.md` before canonical use

## Related Files

- `14_context/next_actions.md` — full detail
- `14_context/codex_n3_42_next_sequence_lock.md` — N+3.42 sequence lock
- `14_context/obsidian_vault/09_Migration_Handoff.md` — session handoff
