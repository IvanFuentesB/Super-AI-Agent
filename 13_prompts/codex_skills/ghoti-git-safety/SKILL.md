# ghoti-git-safety

**Status:** skill_package_created / not_runtime_wired
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Protect every Ghoti milestone from accidentally staging or committing runtime data, private files, local artifacts, screenshots, CV documents, third-party repo contents, scratch files, or any file not intentionally part of the current milestone deliverable.

---

## When to Use

Before every `git add`, `git commit`, or `git push` in the Ghoti repo. Applies to every milestone regardless of scope.

---

## Forbidden Uses

- Running `git add .` or `git add -A` without an explicit approved exception.
- Force-pushing (`git push --force`) to any branch.
- Rewriting history (`git rebase -i`, `git commit --amend`) on pushed commits without explicit user approval.
- Staging files listed under the Blocklist below.
- Deleting files from the repo as a side-effect of cleanup.
- Skipping pre-commit checks (`--no-verify`).
- Bypassing the approval gate for risky actions.

---

## Required Workflow

Run these commands in order before staging anything:

```
git status --short
git diff --name-status
git diff --cached --name-status
```

1. **Classify every modified/untracked file** against the Allowlist and Blocklist below.
2. **Stage only files on the Allowlist** that the current milestone intentionally creates or modifies.
3. **Confirm no Blocklist file appears in staged output** (`git diff --cached --name-status`).
4. **Run whitespace check:** `git diff --check`
5. **Commit** with the standard milestone message format.
6. **Verify staged set one more time** before push: `git status --short`
7. **Push** to the correct feature branch only.

---

## Dirty-File Classification

### Blocklist — Never Stage Unless Milestone Explicitly Requires It

| Pattern | Reason |
|---|---|
| `21_repos/third_party/` | Read-only reference intake; repo rule |
| `.claude/skills/` | Local Claude Code session data, not repo artifacts |
| `output/` | Runtime output / screenshot gallery |
| `.tmp-screenshots/` | Capture artifacts |
| `*.png`, `*.jpg`, `*.gif` in output or runtime dirs | Screenshot/capture artifacts |
| `01_projects/mcp_server/test.txt` | Local scratch / test file |
| `14_context/ghoti_current_prompt_N1_6.md` | Old prompt leftover, not milestone deliverable |
| `14_context/ghoti_current_prompt.md` | Live session prompt; do not commit mid-session |
| `CV_*.docx`, `*.docx` | Personal CV/document files unless a doc milestone explicitly requires them |
| `.env`, `*.env`, `secrets.*`, `credentials.*` | Secret/private files — never stage |
| `*.log`, `*.tmp`, `*.bak` | Ephemeral runtime/build artifacts |
| Anything under `node_modules/` | Dependencies, not repo artifacts |
| Local experiment files not named in milestone tasks | Scratch work |

### Allowlist — Stage Only When the Current Milestone Intentionally Modifies These

| Pattern | When allowed |
|---|---|
| `14_context/*.md` | Milestone status/log/strategy docs explicitly updated this milestone |
| `13_prompts/codex_skills/<skill>/SKILL.md` | Skill package created or updated this milestone |
| `13_prompts/codex_skills/README.md` | Skills index updated this milestone |
| `01_projects/dashboard_mvp/**` | Dashboard/server files only when milestone explicitly edits dashboard |
| `02_automation/**` | Automation scripts only when milestone explicitly requires them |
| `23_configs/**` | Config files only when milestone explicitly requires them |
| `CLAUDE.md` | Only when explicitly updating repo instructions |

**When in doubt, do not stage. Ask the user.**

---

## Safe Staging Rules

1. Use explicit file paths: `git add 14_context/ghoti_finish_line_log.md`, not `git add 14_context/`.
2. Never use `git add .`, `git add -A`, or `git add *`.
3. After staging, run `git diff --cached --name-status` and verify the list matches exactly what was intended.
4. If a Blocklist file appears in staged output, run `git restore --staged <file>` immediately before committing.

---

## Required Pre-Commit Checks

Run all of these before committing:

```
git status --short
git diff --cached --name-status
git diff --check
```

For milestones that touch JS or server files, also run:

```
node --check <file>
```

Confirm:
- [ ] No Blocklist file is staged.
- [ ] Every staged file was explicitly required by this milestone.
- [ ] `git diff --check` exits 0 (no trailing whitespace or bad line endings).
- [ ] Commit message follows milestone format: `docs/feature milestone N+X.Y — <short description>`

---

## Required Final Report Format

After commit and push, record in `14_context/ghoti_finish_line_log.md`:

```
## Milestone Run: N+X.Y <title>

Date: <YYYY-MM-DD>
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: <hash>
Commit hash after commit: <hash>

### Files Changed
- Created/Updated: <path>

### Validation Commands / Results
- git status --short: clean (only expected dirty files remain)
- git diff --check: PASS

### Files Intentionally Not Staged
- 21_repos/third_party/.gitkeep
- .claude/skills/

### Honest Status Labels
- <feature>: <label>

### Next Recommendation
<one paragraph>
```

---

## Recovery Behavior If a Risky File Was Staged

1. **Stop immediately.** Do not commit.
2. Unstage the file: `git restore --staged <file>`
3. Re-run `git diff --cached --name-status` to confirm it is removed.
4. Identify how it was staged (e.g., glob, typo, wrong path).
5. Record the near-miss in the milestone log under a "Recovery" note.
6. Proceed with the corrected staged set only.

If a risky file was already committed but not pushed:
- Ask the user before any corrective action. Do not `git reset --hard` without explicit approval.

If a risky file was already pushed:
- Stop all automation. Surface the issue to the user immediately.
- Do not force-push or rewrite history without explicit user instruction.

---

## Standard Allowlist / Blocklist Guidance Summary

**Always block:**
- Runtime data, capture artifacts, screenshots, `output/`
- Personal documents (CV, `.docx`) unless explicitly a doc milestone
- Third-party repo contents (`21_repos/third_party/`)
- Local Claude session artifacts (`.claude/skills/`)
- Scratch/test files not named in milestone tasks
- Secret/env/private files

**Allow only:**
- Files explicitly named in the milestone task list
- Files the milestone TASKS section requires creating or updating
- Confirmed with `git diff --cached --name-status` before commit

---

*Status: skill_package_created / not_runtime_wired*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, or executor. It becomes runtime behavior only if a future milestone explicitly proves and documents that integration.*
