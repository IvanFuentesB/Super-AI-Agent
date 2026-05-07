# Ghoti Dirty State Warning

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `git status --short` (run at N+3.34 start)

---

## Purpose

Visible dirty-worktree warning. Hard to miss, always stale after a commit.
Do not paste reset or delete commands here without operator approval.

## Source of Truth

- `git status --short` — always authoritative
- `14_context/codex_n3_34_memory_safety_gate_review.md`

## Update Rules

- Update whenever `git status --short` materially changes.
- Before every staging or commit milestone.
- Mark stale after every commit, stash, rebase, or reset.
- Human/Codex review before staging guidance is trusted.

---

## Current Dirty State (N+3.34 start — 2026-05-05)

**HEAD:** `df57706` (in sync with origin)

### Files That Must NOT Be Staged

| File/Path | Class |
|-----------|-------|
| `14_context/ghoti_external_repo_tool_intake.md` | Modified — external repo intake, unrelated |
| `21_repos/third_party/.gitkeep` | Modified — third-party placeholder, intentionally local |
| `.claude/skills/` | Untracked — Claude Code config, local-only |
| `01_projects/mcp_server/test.txt` | Untracked — local test artifact |
| `03_scripts/test_perm.tmp` | Untracked — local temp file |
| `05_logs/local_brain_runs/` | Untracked — generated run logs |
| `05_logs/money_reviews/` | Untracked — generated review artifacts |
| `05_logs/money_runs/` | Untracked — generated run artifacts |
| `14_context/ghoti_current_prompt_N1_6.md` | Untracked — prompt scratch file |
| `CV_Ivan_*.docx` | Untracked — personal CV files, out-of-scope |
| `output/` | Untracked — local output, not tracked |

### N+3.34 Intentional Files (stage these)

- `14_context/obsidian_vault/02_Next_Actions.md` through `09_Migration_Handoff.md` (new)
- `14_context/compact_memory/project_state.md` through `dirty_state_warning.md` (new)
- `03_scripts/obsidian_memory_scaffold.py` (new)
- `14_context/obsidian_compact_memory_scaffolding_n3_34.md` (new)
- Appended: `14_context/obsidian_vault/00_Index.md`, `01_Current_State.md`
- Appended: `14_context/current_state.md`, `14_context/next_actions.md`
- Appended: `14_context/ghoti_finish_line_log.md`

## Next Safe Action

1. Run `python 03_scripts/obsidian_memory_scaffold.py --check` to verify files.
2. Stage only intentional N+3.34 files.
3. Run `git diff --check` before commit.
4. Commit: `feat(ghoti): add N+3.34 Obsidian compact memory scaffolding`
5. Push to `feat/ghoti-visible-operator-stack`.

## Do Not

- Do not `git add -A` — stages unrelated dirty files.
- Do not reset or delete unrelated dirty files without operator approval.
- Do not stage `14_context/ghoti_external_repo_tool_intake.md` or `21_repos/third_party/.gitkeep`.

---

## Review Status

**status:** draft
**STALE AFTER NEXT COMMIT** — re-run `git status --short` after commit

## Related Files

- `14_context/compact_memory/dirty_state_warning.md`
