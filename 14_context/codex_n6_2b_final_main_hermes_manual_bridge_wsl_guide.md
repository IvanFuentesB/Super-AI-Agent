# N+6.2B Final Main Audit - Hermes Manual Bridge WSL Guide

Final verdict: CLEAN PASS / N+6.2B MAIN AUDITED.

## Branches And Commits

- Final origin/main hash audited: `8613508674deb9abb44dc1b9e5a54dfee3261ee6`
- Final main audit branch: `audit/ghoti-agent-codex-n6-2b-final-main-hermes-manual-bridge-wsl-guide`
- Starting N+6.2B main hash before merge: `39daf4d81f8a5dc123c9949ce6d7c3ea49763978`
- Merged N+6.2A feature branch: `feat/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- N+6.2A feature commit: `b77304b088538e5440f260e989f5845c1a3adeec`
- Merged N+6.2A audit branch: `audit/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- N+6.2A audit commit: `30256d5d601bccd865261f60e30e4e4fbcd6fd1c`
- N+6.2B main report commits: `e109943cad297032d49d0bf24491939e9f1a1e0c`, `8613508674deb9abb44dc1b9e5a54dfee3261ee6`

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 18 OK
- Total runtime tests: 444 OK
- `node --check 01_projects/dashboard_mvp/server.js`: PASS
- `node --check 01_projects/dashboard_mvp/public/app.js`: PASS
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`: PASS
- `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1 -RuntimeLockSafe`: PASS

## Product And Safety Checks

- Launcher smoke: PASS, all four product endpoints returned 200, no 500, no reference errors.
- Context pack generation: PASS.
- Repo map status: PASS.
- Hermes bridge status: PASS.
- Hermes manual status/doctor/WSL explain/safe commands/blocked commands/skills summary/write guide: PASS.
- Local model routing status: PASS, readiness 82%.
- Local model output guard self-test: PASS; invented bundle `StableLM-DanceDiffusion` rejected and unknown file source rejected.
- Public repo security audit: 150 checks, 0 blockers, 7 warnings requiring human review.
- Model council scan: PASS.
- UI-TARS dry-run: PASS, observation-only, no click/type/control.
- Approved adapter runner status: PASS, approval-gated/local-only.
- External sandbox status: PASS, static inspection only.
- Supervised content demo validation: PASS.

## Hermes And WSL Truth

- Hermes manual bridge readiness: 64%.
- Legacy Hermes workflow readiness: 58%.
- WSL Ubuntu: available.
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`
- Hermes manual bridge parser skills count: 79.
- WSL footer: `0 hub-installed, 84 builtin, 0 local - 84 enabled, 0 disabled`.
- Codex provider in Hermes: pending/not proven.
- Telegram: manual later/no token.
- Browser/Playwright: degraded/not claimed.
- VPS: none.
- Safe WSL probes run only:
  - `command -v hermes`
  - `hermes --version`
  - `hermes skills list | head -120`

## Safe And Blocked Hermes Commands

Safe commands documented:
- Show WSL working directory.
- Find Hermes.
- Print Hermes version.
- List visible Hermes skills.
- Show Hermes help.
- Run Ghoti manual bridge status.

Blocked commands documented:
- `hermes setup`
- `hermes login`
- `hermes auth`
- `hermes auth add`
- `hermes provider`
- `hermes telegram`
- `hermes whatsapp`
- `hermes browser`
- `hermes computer-use`
- `hermes gateway install`
- `hermes mcp install`

## Current Capability Truth

- Dashboard and launcher work.
- Launcher command: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard URL: `http://127.0.0.1:3210`
- Gemma installed: `gemma3:4b`.
- Active model lane: `ollama_gemma_guarded`.
- Guard enabled: yes.
- Source metadata required: yes.
- Safe routed tasks: summarize latest report, status paragraph, Codex next prompt, safety classification, context bundle summary, next milestone outline, report to bullets.
- UI-TARS remains observation-only.
- Adapter runner remains approval-gated/local-only.
- External sandbox remains static inspection only.
- No live APIs, provider setup, Telegram setup, browser automation, computer-use click/type, or account actions were performed.

## Cleanup

- Restored generated validation residue from context pack, repo map, external sandbox status, and Hermes manual status files.
- No broad process kills.
- No unrelated worktrees or primary worktree files were modified.

## Human Status

Human status: Ghoti is about 92% complete toward the bigger local-first agent OS vision. The local MVP is stable and increasingly usable. Current capabilities are a dashboard/launcher, compact context packs, repo knowledge bundles, Gemma guarded local routing for safe offline text tasks, public/security gates, UI-TARS observation-only dry-runs, adapter dry-runs, external static sandboxing, and a verified Hermes/WSL manual bridge. The main gaps are live Hermes provider verification, Telegram, browser/Playwright remediation, audited computer-use observation harness, and future human-approved click/type workflows. Confidence: high for local MVP and manual bridge truth because validation passed from fresh origin/main; medium for future agent/computer-use expansion because those lanes remain intentionally gated.
