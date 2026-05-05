# Codex N+3.46 - Parallel Branch Collision Review

Milestone: N+3.46 - Audit N+3.45A Claude Tooling/Prompt Bus Branch And Prepare Safe Merge

Date: 2026-05-05

## Collision Summary

Known issue from the controlled parallel pilot:

- Claude accidentally committed N+3.45A implementation on the local Codex audit branch as `370e19b`.
- Claude then cherry-picked the same implementation to the correct Claude branch as `13266ea`.
- Claude could not reset the local audit branch because reset permission was denied.

## Remote Branch Truth

Remote Codex audit branch:

- `origin/audit/ghoti-agent-codex-n3-45-tool-routing`
- HEAD: `c79940106f85ceffa30fba2e6de32225bec4c6fe`
- Contents: seven `14_context/codex_n3_45b_*.md` docs only

Remote Claude implementation branch:

- `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`
- HEAD: `13266eaf663bc0a6b7d205d57d869263b1af6e38`
- Contents: expected N+3.45A implementation/tooling/prompt-bus files

## Accidental Commit Reachability

Commands checked:

```powershell
git branch -r --contains 370e19b
git branch --contains 370e19b
```

Result:

- `370e19b` is not contained by any remote branch.
- `370e19b` is contained only by the local branch `audit/ghoti-agent-codex-n3-45-tool-routing`.

Verdict:

- The accidental commit is a local branch cleanup issue.
- It is not currently a remote merge risk.
- Do not merge from the local `audit/ghoti-agent-codex-n3-45-tool-routing` branch.
- If merging the Codex N+3.45B docs, merge from `origin/audit/ghoti-agent-codex-n3-45-tool-routing` or from commit `c799401`.

## File Separation Review

Claude branch diff against base:

- 25 files changed.
- Files are implementation/tooling/prompt-bus/local-worker/Claude-command/lane-status files.
- No `14_context/codex_n3_45b_*.md` files.

Codex branch diff against base:

- 7 files changed.
- Files are only `14_context/codex_n3_45b_*.md`.

Intersection check:

```powershell
$claude = git diff --name-only origin/feat/ghoti-visible-operator-stack..origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
$codex = git diff --name-only origin/feat/ghoti-visible-operator-stack..origin/audit/ghoti-agent-codex-n3-45-tool-routing
$claude | Where-Object { $codex -contains $_ }
```

Result:

- No file overlap.

## Collision Verdict

Branch collision verdict: SAFE AS REMOTE STATE, LOCAL CLEANUP NEEDED LATER.

Why:

- The polluted local audit branch is not pushed.
- The remote Codex audit branch remains file-separated.
- The remote Claude branch has the implementation commit in the correct place.
- There is no file overlap between the two remote branches.

## Required Cleanup Guidance

Do not reset automatically.

Safe future cleanup options:

1. Leave the polluted local audit branch alone and always reference `origin/audit/ghoti-agent-codex-n3-45-tool-routing`.
2. After all merges are complete and with explicit human approval, delete and recreate the local stale audit branch from origin:

```powershell
git switch feat/ghoti-visible-operator-stack
git branch -D audit/ghoti-agent-codex-n3-45-tool-routing
git fetch origin
git switch -c audit/ghoti-agent-codex-n3-45-tool-routing origin/audit/ghoti-agent-codex-n3-45-tool-routing
```

Do not run those cleanup commands during this audit unless explicitly asked.
