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

## Goal-to-proof loop

- Begin with the user-visible outcome, minimal scope and concrete proof. Use
  just-in-time planning for nontrivial changes; small fixes need no extra ritual.
- Read relevant current source, accepted PRs, installed state and retained failures
  before rebuilding or repeating tests. A report is not a runtime result.
- Keep one implementation owner per file set. Delegate independent exploration,
  tests and design critique only with disjoint ownership and clear outputs.
- Iterate: reproduce -> change -> affected build/tests -> actual app or UI check
  where supported. Keep original failing assertions; separate environment failures,
  synthetic proof and authenticated installed behavior.
- Require independent review of a frozen candidate. Let automated checks handle
  mechanical issues; retain human judgment on security, intent and visual quality.
- Publish safe source and verify the remote PR; separately verify deployment and
  the actual user journey. A passing test or a merged PR is not installation.
- Convert repeated real failures into focused regression tests or reviewed skills;
  retire obsolete procedures when they add friction without protecting outcomes.
- Track accepted user journeys, cycle time, regressions and source-to-installed
  latency rather than using lines of code, agent count or test totals alone.

## Branch & worktree

- Work on a feature branch in a repo-contained worktree under `.claude/worktrees/`.
- Branch name: `feat/ghoti-agent-<who>-n<major>-<minor><letter>-<slug>`.
- Stage explicit paths; never `git add -A`.

## Main is protected

- Never commit on `main`. Push the feature branch only.
- No push or merge to `main` without an explicit, separate merge-gate step after a
  CLEAN independent audit. Implementation lanes never push main.

## GitHub publication checkpoints

- Canonical remote: `IvanFuentesB/Super-AI-Agent`. At task start, verify the actual
  remote, branch, current instructions and publication owner; do not overwrite a
  dirty worktree to synchronize it.
- For source-changing tasks, commit scoped source/tests at meaningful milestones.
  Before session closeout, publish the safe feature branch and create or update
  its draft PR within the authorized scope. Record failing or unrun tests in the
  draft; do not wait for every product gate before publishing reviewable work.
- In parallel work, use one remote publisher. Builders hand over immutable commits
  or snapshots and obtain a remote-publication acknowledgment, not merely a local
  handoff receipt.
- Scan all newly reachable history before publishing. Exclude credentials, private
  memory, transcripts, databases and dependency installations. Port only the safe
  source delta with provenance when its original history is unsuitable.
- Read the remote back and verify the expected published commit and PR. Every
  source-changing closeout reports the remote link and separately states local,
  published, merged and installed status. If publication is blocked, name the exact
  blocker and owner; say LOCAL ONLY, not delivered.
- A merge, deployment or live-execution hold is not a feature-branch publication
  hold. Respect explicit task-scoped publication restrictions and native controls;
  do not silently carry an old task's no-push instruction into unrelated work.

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
