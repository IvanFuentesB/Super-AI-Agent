# ghoti-finish-line-log-update

**Status:** skill_package_created / not_runtime_wired
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Keep `14_context/ghoti_finish_line_log.md` accurate, append-only, and useful as the durable milestone history for Ghoti / Super-AI-Agent.

This skill standardizes how Codex records milestone truth: what changed, what was validated, what was pushed, what stayed dirty, and what remains manual, scaffolded, or unproven.

---

## When to Use

Use this skill near the end of every Ghoti milestone, before staging and committing.

Also use it when:

- Reconciling a local finish-line-log edit made after a commit.
- Recording a pushed commit hash after a milestone commit.
- Documenting a failed validation, blocked push, or manual-only status.
- Preparing a clean final handoff report for ChatGPT, Claude Code, or a future Codex run.

---

## Forbidden Uses

- Rewriting old milestone history to make results look cleaner.
- Deleting task history, failure notes, dirty-file notes, or safety caveats.
- Claiming runtime wiring, autonomy, model capability, deployment, bridge status, or external service integration without validation proof.
- Marking push as successful before `git push` actually succeeds.
- Hiding dirty/local-only files by omitting them from the "Files Intentionally Not Staged" section.
- Using this skill to justify committing runtime data, screenshots, CV files, third-party repos, scratch files, secrets, or local prompt artifacts.

---

## Required Append-Only Workflow

1. Run git truth commands:

```powershell
git status --short
git branch --show-current
git log --oneline -5
git diff --cached --name-status
```

2. Inspect the current finish-line-log diff:

```powershell
git diff --ignore-space-at-eol -- 14_context/ghoti_finish_line_log.md
```

3. If the log already has a local edit, classify it:

- Keep it if it correctly records a real commit hash, push truth, validation result, or explicit correction.
- Narrow it if it includes accidental broad rewrites, noisy formatting changes, or unsupported claims.
- Reject it if it erases history, overclaims capability, or hides dirty files.

4. Append a new milestone section at the bottom of `14_context/ghoti_finish_line_log.md`.
5. Do not rewrite earlier entries except to correct a clearly documented typo/status error.
6. Run validation commands and record exact command + result.
7. After commit, update the new milestone entry with the real commit hash.
8. If the milestone requires an amend to record the commit hash, do only the documented log update, then run:

```powershell
git add 14_context/ghoti_finish_line_log.md
git commit --amend --no-edit
```

Only amend when the user explicitly requested this flow or the milestone instructions require it.

---

## Standard Milestone Log Template

```markdown
## Milestone Run: N+X.Y <title>

Date: <YYYY-MM-DD>
Branch: `feat/ghoti-visible-operator-stack`
Starting HEAD: `<hash>`
Commit hash after commit: <hash or TBD before commit>
Pushed: <YES/NO/BLOCKED>

### Files Changed

- Created: `<path>`
- Updated: `<path>`

### Validation Commands / Results

- `<command>`: PASS/FAIL/BLOCKED — <short evidence>

### Skill / Feature Truth

- `<feature or skill>`: `<honest_status_label>`
- Runtime wired: YES/NO, proof: <route/test/code evidence or "not proven">

### Dirty Files Intentionally Not Staged

- `<path>` — <reason>

### What Remains Manual / Unproven

- <manual-only or scaffolded truth>

### Recovery Notes

- None, or <exact correction/unstage/narrowing action>

### Next Recommendation

<one focused next milestone>
```

---

## Required Evidence Fields

Every milestone entry must include:

- Date.
- Branch.
- Starting HEAD.
- Commit hash after commit, or `TBD before commit`.
- Push truth: `YES`, `NO`, or `BLOCKED`.
- Exact files changed.
- Exact validation commands and results.
- Dirty/local-only files intentionally left unstaged.
- Honest status labels for new skills/features.
- Runtime wiring truth.
- Next recommendation.

---

## Honest Status Label Rules

Use explicit labels. Prefer these:

- `skill_package_created / not_runtime_wired`
- `strategy_only / not_runtime_wired`
- `manual_handoff_only`
- `scaffold_only`
- `diagnostic_only`
- `read_only`
- `local_only`
- `approval_gated`
- `not_implemented`
- `validated`
- `blocked`
- `unproven`

Never imply:

- Ghoti is autonomous unless runtime proof exists.
- Codex plugins/skills are wired into Ghoti runtime unless repo code proves it.
- Claude Code and Codex are automatically bridged unless proven.
- Gemma/Ollama drives operator actions unless a validated task path proves it.
- Browser overlay is a native always-on-top window.
- Capture gallery is AI screen sharing.

---

## Commit Hash Handling Rules

- Before commit, use `Commit hash after commit: TBD before commit`.
- After commit, replace only that new milestone line with the real short hash.
- Verify with:

```powershell
git rev-parse --short HEAD
```

- If the user requested an amend flow, amend only after updating the hash line.
- Do not amend unrelated content into the commit.

---

## Push Truth Handling Rules

Record push truth only after `git push` returns.

- `Pushed: YES` only if push succeeded.
- `Pushed: NO` if no push was attempted by instruction.
- `Pushed: BLOCKED` if push failed or auth/permission/network blocked it.

If blocked, record:

- exact command attempted
- exact blocker summary
- exact next command the user should run if appropriate

---

## Dirty-File Section Rules

Always list known dirty/local-only files that remain unstaged, especially:

- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `14_context/ghoti_current_prompt_N1_6.md`
- CV `.docx` files
- `output/`
- runtime data
- `.tmp-screenshots`
- local temp/probe files

Do not summarize them away if they appear in `git status --short`.

---

## Validation Section Rules

Validation must include command + result.

Examples:

```markdown
- `git diff --check`: PASS
- `node --check 01_projects/dashboard_mvp/server.js`: PASS
- `GET /overlay`: 200
- `git diff --cached --name-status`: PASS — only intended files staged
```

If a validation was not run, say `NOT RUN` and why.

If validation fails, record the failure honestly before fixing. Do not replace the history with a fake green result.

---

## Recovery Behavior If Log Was Edited Incorrectly

If the log contains accidental broad edits:

1. Stop before staging.
2. Inspect:

```powershell
git diff --ignore-space-at-eol -- 14_context/ghoti_finish_line_log.md
```

3. Restore or narrow only the accidental portion.
4. Keep legitimate truth updates, such as a real commit hash or push status correction.
5. Add a `Recovery Notes` section to the current milestone entry explaining what was corrected.

If old history was deleted:

- Do not commit.
- Restore the deleted history unless the user explicitly instructed deletion.
- Record the attempted correction in the current milestone log.

---

## Final Report Format

Final milestone reports should include:

```markdown
- branch
- previous HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail list
- skill package truth
- runtime wiring truth
- finish-line-log reconciliation truth
- dirty files intentionally left unstaged
- next recommended milestone
```

---

*Status: skill_package_created / not_runtime_wired*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, MCP server, or executor.*
