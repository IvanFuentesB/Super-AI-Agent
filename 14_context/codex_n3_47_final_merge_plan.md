# Codex N+3.47 - Final Merge Plan

Milestone: N+3.47 - Re-Audit Claude N+3.45A-FIX And Prepare Final Merge Commands

Date: 2026-05-05

## Current Merge Verdict

Do not merge yet.

The intended fix is present as local Claude commit `110a84a fix(ghoti): preserve prompt bus dry-run purity`. The remote Claude branch still points to old commit `13266ea`, so `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus` is not yet the fixed branch.

## Step 1 - Push Claude Fix

From the Claude branch, first verify the local HEAD is the fix commit:

```powershell
git switch feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
git status --short
git rev-parse HEAD
git show --stat --oneline HEAD
git push origin feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
```

Expected local HEAD: `110a84a fix(ghoti): preserve prompt bus dry-run purity`.

If the local fix commit is missing, recreate and commit only these two files:

```powershell
git add -- .claude/settings.json 03_scripts/prompt_bus.py
git diff --cached --check
git commit -m "fix(ghoti): make prompt bus init dry-run pure"
git push origin feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
```

Stage only those two files. Do not stage unrelated local dirt.

## Step 2 - Verify Claude Fix Is Remote

```powershell
git fetch origin
git show --stat --oneline origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
git show --name-only --oneline origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
```

Expected latest commit should be `110a84a` or a newer equivalent fix commit, not `13266ea`.

## Step 3 - Merge Claude Branch First

Use the remote base branch, not the local unpushed base merge state.

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus -m "merge(ghoti): land N+3.45A tooling and prompt bus"
```

## Step 4 - Validate After Claude Merge

```powershell
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK')"
python 03_scripts/prompt_bus.py --init --dry-run
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/agent_lane_status.py --check
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Step 5 - Merge Codex Audit Docs Separately

After Claude merge is pushed:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/audit/ghoti-agent-codex-n3-45-tool-routing -m "merge(ghoti): land N+3.45B tool routing audit docs"
git merge --no-ff origin/audit/ghoti-agent-codex-n3-46-n3-45a-merge-audit -m "merge(ghoti): land N+3.46 merge audit docs"
git merge --no-ff origin/audit/ghoti-agent-codex-n3-47-prompt-bus-fix-reaudit -m "merge(ghoti): land N+3.47 prompt bus fix reaudit"
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Important Local-Branch Warning

Local `feat/ghoti-visible-operator-stack` currently shows unpushed merge commits:

- `2a9f423 merge(ghoti): land N+3.45A tooling and prompt bus`
- `69d81f1 merge(ghoti): land N+3.45B tool routing audit docs`

But `origin/feat/ghoti-visible-operator-stack` remains at `46941c8`.

Do not rely on local base branch history as canonical until it is reconciled. Prefer fresh `git fetch origin` and `git pull --ff-only` from origin. If Git reports divergence, stop and ask the user.

## What Not To Do

- Do not merge the old remote Claude branch before the fix commit is pushed.
- Do not merge from local polluted `audit/ghoti-agent-codex-n3-45-tool-routing`.
- Do not reset branches without explicit human approval.
- Do not stage recurring local dirt.
- Do not stage Ruflo eval files.
- Do not run Ruflo, OpenClaw, Paperclip, n8n, CUA, browser tools, Firecrawl, Glif, JobSpy, or account connectors.
- Do not send, post, sell, pay, scrape, apply to jobs, enter giveaways, or touch live accounts.

## Final Recommendation

Fix-first path required:

1. Commit and push the local Claude fix.
2. Merge fixed Claude branch first.
3. Validate and push base.
4. Merge Codex audit docs second.
5. Validate and push base.
