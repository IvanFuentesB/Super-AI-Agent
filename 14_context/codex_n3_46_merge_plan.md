# Codex N+3.46 - Safe Merge Plan

Milestone: N+3.46 - Audit N+3.45A Claude Tooling/Prompt Bus Branch And Prepare Safe Merge

Date: 2026-05-05

## Recommended Merge Order

Recommended order:

1. Fix the Claude dry-run purity issue if the user wants strict safety before merge.
2. Merge Claude N+3.45A implementation branch.
3. Run validation on base after Claude merge.
4. Merge Codex N+3.45B audit docs from the remote Codex branch.
5. Run validation again.
6. Push base.

Why Claude first:

- Claude branch adds implementation/tooling and lane JSONL records.
- Codex branch adds docs only.
- There is no file overlap, but implementation should land before audit/source-check docs that reference it.

## Preferred Pre-Merge Fix

Before merging Claude, fix this small issue on `feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`:

- In `03_scripts/prompt_bus.py`, `cmd_init()` should not call `_ensure_dirs()` before checking dry-run.
- `--init --dry-run` should print planned directories only and make no filesystem changes.

Suggested future Claude prompt:

```text
Patch N+3.45A dry-run purity only. In 03_scripts/prompt_bus.py, make --init --dry-run avoid directory creation. Do not change behavior for --apply. Validate prompt_bus smoke commands, git diff --check, and commit on feat/ghoti-agent-claude-n3-45-tooling-prompt-bus.
```

## Merge Commands If Fixing First

After Claude pushes the dry-run fix:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus -m "merge(ghoti): land N+3.45A tooling and prompt bus"
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK prompt_bus.py local_worker_router.py')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --init --dry-run
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/agent_lane_status.py --check
git diff --check
git merge --no-ff origin/audit/ghoti-agent-codex-n3-45-tool-routing -m "merge(ghoti): land N+3.45B tool routing audit docs"
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Merge Commands If Accepting The Known Dry-Run Issue

If the user accepts the local-only dry-run issue as non-blocking:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus -m "merge(ghoti): land N+3.45A tooling and prompt bus"
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK prompt_bus.py local_worker_router.py')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/agent_lane_status.py --check
git diff --check
git merge --no-ff origin/audit/ghoti-agent-codex-n3-45-tool-routing -m "merge(ghoti): land N+3.45B tool routing audit docs"
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## What Not To Do

- Do not merge from the local polluted `audit/ghoti-agent-codex-n3-45-tool-routing` branch.
- Do not reset branches without explicit human approval.
- Do not stage `21_repos/third_party/evals/ruflo`.
- Do not stage recurring local dirt such as CV docs, logs, `.claude/skills/`, or `output/`.
- Do not connect Ruflo, OpenClaw, Paperclip, n8n, CUA, browser tools, email accounts, social accounts, payment tools, or job tools during merge.
- Do not run any live-account or external orchestrator workflows.

## Merge Safety Summary

Merge safety verdict: SAFE AFTER EITHER FIXING OR EXPLICITLY ACCEPTING THE DRY-RUN ISSUE.

Best recommendation:

- Fix the dry-run issue first because it is small and directly affects a safety contract.
- Then merge Claude first, Codex second.
