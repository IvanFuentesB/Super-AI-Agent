# N+6.2B Main Merge - Hermes Manual Bridge / WSL Guide

Date: 2026-05-26

## Verdict

N+6.2B merge gate in progress at this report commit.

This report lands the already-audited N+6.2A Hermes manual bridge milestone onto main through a clean merge gate. The report commit also replaces the automatic merge commit as `HEAD` so the existing N+5 latest-commit attribution scanner can evaluate a normal project-authored commit subject.

## Branches

- Starting main: `39daf4d81f8a5dc123c9949ce6d7c3ea49763978`
- Merged feature branch: `feat/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- Feature commit: `b77304b088538e5440f260e989f5845c1a3adeec`
- Merged audit branch: `audit/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- Audit commit: `30256d5d601bccd865261f60e30e4e4fbcd6fd1c`
- Merge gate worktree: `.claude/worktrees/n6_2b_main_merge_gate`
- Merge HEAD before this report: `e55485aa594a9fae3491695316f39f1cdc3610e3`

## Validation Notes

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- N+4 tests with runtime `PYTHONPATH`: 329 OK
- N+6 tests with runtime `PYTHONPATH`: 18 OK
- N+5 first run before this report commit: 96 OK / 1 attribution-scan failure caused by the automatic merge commit subject containing the source branch name. This is an expected merge-gate artifact; N+5 must be rerun after this report commit.

Remaining product, public audit, WSL, dashboard, and PowerShell checks are run after this report commit and before main is pushed.

## Product Truth

- Hermes manual bridge readiness: 64%.
- Hermes WSL path: `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`.
- Hermes skills: local parser saw 79 skills; safe WSL skills probe footer reports 84 enabled built-ins.
- Codex provider in Hermes: pending/not proven.
- Telegram: manual later/no token.
- Browser/Playwright: degraded/not claimed.
- No VPS.
- Gemma guarded lane: `gemma3:4b`, `ollama_gemma_guarded`, routing readiness 82%.
- UI-TARS: observation-only.
- Adapter runner: approval-gated/local-only.
- External sandbox: static inspection only.

## Commands

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Hermes manual bridge: `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json`
- Routing status: `python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json`

## What Landed

- `03_scripts/hermes_manual_bridge_verifier.py`
- Launcher commands for Hermes manual status, WSL guide, safe commands, and guide generation.
- Dashboard card: `Hermes Manual Bridge / WSL Guide`.
- WSL/Hermes docs, safe-command docs, blocked-command docs, and computer-use roadmap notes.
- Generated Hermes manual bridge files under `14_context/hermes_manual_bridge/generated/`.
- Context pack and repo knowledge references for the Hermes manual bridge lane.

## Safety

No Hermes setup, provider config, Telegram setup, token command, live API, browser automation, computer-use click/type, account action, extra model pull, or broad process kill was performed.

## Next

If the post-report validation remains clean, push main as N+6.2B, create a final main audit branch, and then start N+6.3A Safe Computer-Use Observation Harness / Apple Comparison Dry-Run.
