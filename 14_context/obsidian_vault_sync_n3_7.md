# Obsidian Vault Sync — N+3.7

**Date:** 2026-04-27
**Milestone:** N+3.7 PATH B
**Branch:** `feat/ghoti-visible-operator-stack`

---

## Vault Notes Updated

| Note | Change |
|------|--------|
| `14_context/obsidian_vault/00_Index.md` | Milestone, date, source table updated to N+3.7 |
| `14_context/obsidian_vault/01_Current_State.md` | N+3.4–N+3.7 additions summarized |
| `14_context/obsidian_vault/04_Tools.md` | Screenpipe status updated; Docker/CUA truth updated |
| `14_context/obsidian_vault/05_Safety_Gates.md` | N+3.7 gates added; Docker/Screenpipe gate status updated |

---

## Vault Sync Rules Applied

- Notes kept compact (under 400 words each)
- References point to source file paths, not pasted content
- CUA blocked on Docker (Docker not installed, WSL not installed, PATH B chosen)
- Screenpipe is status-only/no capture
- Obsidian markdown vault is the active token-saving method for new-thread continuity

---

## CUA Truth (N+3.7)

- Docker: NOT installed
- WSL: NOT installed
- CUA container: NOT run
- CUA install: NOT performed
- PATH chosen: B (no Docker install)

---

## Screenpipe Truth (N+3.7)

- Capture started: NO
- Runtime wired: NO
- Policy file: exists at `23_configs/screenpipe_retention_policy.example.json`
- Cleanup script: exists at `03_scripts/screenpipe_retention_cleanup.ps1`
- Dashboard status route: `GET /api/ghoti/screenpipe/status` — added in N+3.7
- No screenshots read, no audio captured, no files deleted

---

## Token-Saving Guidance

Use vault notes in new-thread prompts:
- Reference `14_context/obsidian_vault/01_Current_State.md` instead of re-pasting `current_state.md`
- Reference `14_context/obsidian_vault/04_Tools.md` for tool status
- Reference `14_context/obsidian_vault/05_Safety_Gates.md` for gate status
- Keep future vault updates compact and append-only per milestone
