# Untracked Audit Docs Triage

Status label: `triage_note / n3_4 / commit_decision`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.4

---

## Docs Reviewed

| File | Coherent | Useful | Secrets | Decision |
|------|----------|--------|---------|----------|
| `14_context/ruflo_isolated_clone_audit.md` | YES | YES | NO | **COMMIT** |
| `14_context/autobrowser_isolated_clone_audit.md` | YES | YES | NO | **COMMIT** |
| `14_context/obscura_isolated_clone_audit.md` | YES | YES (historical) | NO | **COMMIT** |
| `14_context/ghoti_next_implementation_plan.md` | YES | YES | NO | **COMMIT** |
| `14_context/gemma_repo_tool_triage_output.md` | YES | YES | NO | **COMMIT** |

---

## Decision Details

### ruflo_isolated_clone_audit.md
Intentional audit of the RUFLO clone from N+2.9. Accurate read-only analysis. No secrets. Provides the source of truth for RUFLO install-risk and MCP injection history. Commit.

### autobrowser_isolated_clone_audit.md
Intentional audit of the AutoBrowser clone from N+2.9. Accurate read-only analysis. Verifies human-takeover and approval-gate claims are stated but unrun. No secrets. Commit.

### obscura_isolated_clone_audit.md
Intentional audit from N+2.9 before the build milestone. The build-not-run state is superseded by `obscura_runtime_verification.md` (committed at 87357f1 in N+3.2), but this doc remains valuable as the pre-build audit record. No secrets, no stale errors. Commit as historical record.

### ghoti_next_implementation_plan.md
Implementation roadmap written in N+2.9. Still accurate as a baseline plan. No secrets. Some items have been completed (Obscura build, N+3.3 plans). Commit; note it is a historical plan, not the live next-actions list.

### gemma_repo_tool_triage_output.md
Diagnostic skipped record. Accurately documents that Ollama is present but no model is installed. Updated with history table across milestones. No secrets. Commit.

---

## Files NOT Staged in This Milestone

Per the milestone prompt rules, the following remain unstaged:
- `14_context/ghoti_current_prompt_N1_6.md` — archived prompt, not current
- `.claude/skills/` — operator-side skill configs, not project files
- `CV*.docx` — personal documents, not repo content
- `output/` — runtime output directory
- `01_projects/mcp_server/test.txt` — temporary test file
- `21_repos/third_party/` contents — read-only third-party repos, intentionally excluded from commits

---

## Note on ghoti_current_prompt*.md

Both `ghoti_current_prompt.md` and `ghoti_current_prompt_N1_6.md` are session-control files. They should NOT be staged. The canonical current prompt is always the live session file; archived versions have no durable value.
