# AGENTS.md - Ghoti / Super-AI-Agent

Short, practical rules for any agent (Codex, Claude, Hermes) working in this repo.
This file is loaded automatically, so it stays concise.

## Project

- Repo root: `C:\Users\ai_sandbox\Documents\AI_Managed_Only`. Stay inside it.
- Supervised operator system. Make minimal, reversible changes - only what the task
  asks. No drive-by refactors.

## One agent per task

- One agent owns one task on one branch in one worktree. Do not edit another lane's
  worktree, and do not edit the dirty primary worktree except read-only.

## Branch & worktree

- Work on a feature branch in a repo-contained worktree under `.claude/worktrees/`.
- Branch name: `feat/ghoti-agent-<who>-n<major>-<minor><letter>-<slug>`.
- Stage explicit paths; never `git add -A`.

## Main is protected

- Never commit on `main`. Push the feature branch only.
- No push or merge to `main` without an explicit, separate merge-gate step after a
  CLEAN independent audit. Implementation lanes never push main.

## Secrets & safety

- No secrets in the repo: no tokens, no chat ids, no API keys. Secrets live outside
  the repo.
- No live browser/computer-use, no OS click/type, no account login, no email/WhatsApp,
  no auto-send, no auto-submit, no Enter/submit keystrokes, no Docker - unless the
  milestone explicitly allows it AND a feature flag enables it.
- Every example config keeps risky flags `false`; only
  `telegram_status_commands_enabled` may be true globally.

## Commits

- No AI attribution: no AI co-author trailer, and no mention of AI assistants or AI
  tools in the commit message. Keep the configured human operator identity. Never
  change git config.

## Subprocess / shell

- Argument-list subprocess only - never a shell string, never an interpolated
  PowerShell expression invocation (`Invoke-Expression` / `iex`), never a downloaded
  script piped into a shell.

## Validation (run before reporting done)

```
git diff --check
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py"
python 03_scripts/public_repo_security_audit.py --run --json
```

Restore any generated validation residue before committing.

## Workflow docs (ECC-inspired, adapt only)

- See `docs/GHOTI_ECC_AGENT_WORKFLOW_UPGRADE_PLAN.md`,
  `docs/GHOTI_GBRAIN_MEMORY_UPGRADE_PLAN.md`,
  `docs/GHOTI_ECC_INTENDED_USE_VS_GHOTI_ADAPTATION.md`, and
  `docs/GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md`.
- Adapt inspected ideas only (agent roles, skill layout, command templates, hooks as
  validators, security-scanner and token-saving ideas). Do NOT install the ECC plugin,
  enable its hooks, or run its Node scripts.
