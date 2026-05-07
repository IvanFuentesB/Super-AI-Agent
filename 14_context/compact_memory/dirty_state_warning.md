---
memory_type: compact_pointer
status: draft
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - git status --short (run at N+3.34 start)
  - 14_context/obsidian_vault/08_Dirty_State.md
generated_by: claude
reviewed_by: none
review_required_before_canonical_use: true
---

# Compact: Dirty State Warning

> **ALWAYS STALE AFTER A COMMIT, STASH, REBASE, OR RESET.**
> Re-run `git status --short` and update before trusting this file for staging decisions.
> **Max target size:** 200–400 words

---

## State at N+3.34 Start (2026-05-05)

**HEAD:** `df57706` (in sync with origin)

## Files That Must NOT Be Staged

| File/Path | Reason |
|-----------|--------|
| `14_context/ghoti_external_repo_tool_intake.md` | Unrelated external repo intake dirt |
| `21_repos/third_party/.gitkeep` | Third-party placeholder, intentionally local |
| `.claude/skills/` | Claude Code config, local-only |
| `01_projects/mcp_server/test.txt` | Local test artifact |
| `03_scripts/test_perm.tmp` | Local temp file |
| `05_logs/local_brain_runs/` | Generated run logs |
| `05_logs/money_reviews/` | Generated review artifacts |
| `05_logs/money_runs/` | Generated run artifacts |
| `14_context/ghoti_current_prompt_N1_6.md` | Prompt scratch file |
| `CV_Ivan_*.docx` / `output/` | Personal/out-of-scope files |

## Next Safe Staging Action

Stage only intentional N+3.34 files.
Do not `git add -A`.
Always run `git diff --check` before commit.

---

## Source Pointers

- Vault note: `14_context/obsidian_vault/08_Dirty_State.md`
- Current truth: `git status --short`

## Next Update Instructions

**STALE AFTER NEXT COMMIT.** Update immediately when `git status` changes.
Human/Codex review before staging guidance is trusted.
