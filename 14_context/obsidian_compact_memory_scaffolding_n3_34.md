# N+3.34 — Obsidian Vault + Compact Memory Scaffolding

**Milestone:** N+3.34
**Status:** implemented
**Date:** 2026-05-05
**Branch:** `feat/ghoti-visible-operator-stack`
**Starting HEAD:** `df57706` (in sync with origin)

---

## Purpose

Create a durable local memory layer and compact token-saving pointer layer for Ghoti
without losing data.

## Scope

- Docs/scaffolding/local files only.
- No runtime behavior changes.
- No installs, connectors, MCP changes, live accounts, posting, emailing, selling, payments,
  scraping, or external tool integration.

---

## Part A — Obsidian Vault Scaffolding

**Vault root:** `14_context/obsidian_vault/`

### Files Created (new)

- `02_Next_Actions.md` — compact next-step list with exact Claude/Codex recommendations
- `03_Decisions.md` — durable decision log with rationale and source links
- `04_Tools_And_Repos.md` — tool/repo truth N+3.34+ canonical (predecessor `04_Tools.md` intact)
- `05_Money_OS.md` — Money OS workflow memory through N+3.32
- `06_Safety_Gates.md` — safety gates N+3.34 canonical (predecessor `05_Safety_Gates.md` intact)
- `07_Agent_Routing.md` — agent routing policy compact
- `08_Dirty_State.md` — dirty worktree warning with file classification
- `09_Migration_Handoff.md` — session handoff note

### Files Appended (existing, not overwritten)

- `00_Index.md` — N+3.34 section added listing new notes
- `01_Current_State.md` — N+3.34 section added with current milestone state

### Files Preserved (intact, not touched)

- `04_Tools.md` — N+3.7 predecessor, left intact
- `05_Safety_Gates.md` — N+3.7 predecessor, left intact

---

## Part B — Compact Memory Scaffolding

**Compact root:** `14_context/compact_memory/`

### Files Created (new — N+3.34 contract)

- `project_state.md` — compressed project state pointer (400–700 word target)
- `repo_and_tool_index.md` — compressed tool/repo status pointer (300–600 word target)
- `money_os_memory.md` — compressed Money OS pointer (500–900 word target)
- `agent_routing_memory.md` — compressed agent routing pointer (300–600 word target)
- `safety_rules.md` — compressed safety rules pointer (400–800 word target)
- `dirty_state_warning.md` — dirty state warning pointer (200–400 word target)

### Older Files Preserved

All older compact memory files (`decision_extracts.md`, `plan_extracts.md`, etc.) left intact.

---

## Part C — Helper Script

**Script:** `03_scripts/obsidian_memory_scaffold.py`

- Stdlib only, no external APIs, no model calls, no installs, no live actions
- `--check`: verify all expected files exist
- `--dry-run` (default): show what would be created
- `--apply`: create missing files using stub templates
- `--force` (with `--apply`): overwrite existing files
- Never overwrites without explicit `--force`

---

## Part D — State Updates

- `14_context/current_state.md` — N+3.34 line appended
- `14_context/next_actions.md` — N+3.34 line appended
- `14_context/ghoti_finish_line_log.md` — N+3.34 section appended

---

## Validation

- `python -m py_compile 03_scripts/obsidian_memory_scaffold.py` — PASS
- `python 03_scripts/obsidian_memory_scaffold.py --help` — PASS
- `python 03_scripts/obsidian_memory_scaffold.py --check` — expected: all 16 files present
- `python 03_scripts/obsidian_memory_scaffold.py --dry-run` — expected: nothing to create
- `python 03_scripts/obsidian_memory_scaffold.py --apply` — expected: nothing to create
- `git diff --check` — PASS

---

## Safety Confirmations

- No existing files overwritten.
- No source records deleted.
- No runtime behavior changed.
- No external APIs called.
- No live accounts used.
- No installs performed.
- No model output executed.
- No money-facing or public actions taken.
- All N+3.18 dirty files remain unstaged.

---

## Commit

`feat(ghoti): add N+3.34 Obsidian compact memory scaffolding`

## Next Recommended Actions

**Next Claude:** Commit and push N+3.34, then await Codex audit.

**Next Codex:** Audit N+3.34 after push. Verify no memory loss, source references correct,
compact memory remains a pointer layer, dirty-state warnings accurate.

**Next Future Milestone:** N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding.
