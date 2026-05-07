# Ghoti Migration Handoff

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/current_state.md`, `14_context/next_actions.md`, N+3.34 session

---

## Purpose

Handoff note for moving between long Claude/Codex/ChatGPT sessions.
Cite this note + vault index to reduce token load instead of repasting full context.

## Source of Truth

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/obsidian_vault/00_Index.md`

## Update Rules

- Update at the end of major milestones.
- Before switching agents or losing context.
- Gemma can draft; human/Codex review before canonical use as a prompt base.

---

## Latest Pushed Commit

`df57706` — `docs(ghoti): audit N+3.32 and lock Obsidian readiness`

N+3.34 commit pending push after this file is written.

## Must-Read Files for Next Agent

| Priority | File | Why |
|----------|------|-----|
| 1 | `14_context/obsidian_vault/00_Index.md` | Vault navigation |
| 2 | `14_context/obsidian_vault/01_Current_State.md` | Compact project state |
| 3 | `14_context/current_state.md` | Full project state (authoritative) |
| 4 | `14_context/next_actions.md` | Next actions (authoritative) |
| 5 | `14_context/obsidian_vault/06_Safety_Gates.md` | Safety rules |
| 6 | `14_context/obsidian_vault/08_Dirty_State.md` | What not to stage |
| 7 | `14_context/compact_memory/safety_rules.md` | Compact safety rules |

## One-Screen Context Summary

- **Branch:** `feat/ghoti-visible-operator-stack`
- **Repo:** `IvanFuentesB/Super-AI-Agent`
- **Milestone completed:** N+3.34 — Obsidian Vault + Compact Memory Scaffolding
- **Core runtime:** Python operator console + Node.js dashboard at `01_projects/`
- **Money OS:** local artifact-only scripts at `03_scripts/`; data at `14_context/money_workflows/`
- **Agent routing:** Gemma=local drafts, Claude=impl, Codex=audit, ChatGPT=strategy
- **Safety:** no live actions without approval; no secrets in vault
- **Docker:** installed (N+3.11); CUA smoke ready but requires explicit approval phrase
- **Gemma3:4b:** installed and smoke-passed (N+3.13)
- **Memory:** Obsidian vault (10 files) + compact memory (6 new N+3.34 files)

## Exact Next Milestone Recommendation

**N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding**

Source: `14_context/codex_n3_42_next_sequence_lock.md`

## Known Blockers

- CUA live run: requires `APPROVE CUA IMAGE DIGEST sha256:2bb539bd... FOR SCREENSHOT-ONLY SMOKE`
- External connectors: blocked until explicitly approved
- Autonomous routing: blocked until lane locks are stable (N+3.43)

## Dirty Files (do not stage)

See `14_context/obsidian_vault/08_Dirty_State.md` for full list.

---

## Review Status

**status:** draft
**review_required:** yes — verify current state + commit hash before using as canonical prompt base

## Related Files

- `14_context/obsidian_vault/00_Index.md`
- `14_context/compact_memory/project_state.md`
- `14_context/codex_n3_42_next_sequence_lock.md`
