# Codex N+6.0B Final Main Audit - Gemma Install And First Local Eval

Date: 2026-05-24

## Final Verdict

CLEAN PASS / N+6.0B MAIN AUDITED AFTER REPORT-HISTORY REPAIR.

N+6.0A was merged to main as N+6.0B. A fresh final-main audit initially caught a report-history regression caused by newer N+6 reports pushing required older reports out of compact generated outputs. N+6.0C repaired that by pinning key milestone reports in the context-pack and repo-map report discovery helpers. The repaired main was pushed and audited clean.

## Branches And Commits

- Final `origin/main`: `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`
- N+6.0B merge-gate branch: `merge/ghoti-agent-codex-n6-0b-main-gemma-install-first-local-eval`
- N+6.0B merge report commit: `56f97929725f5a293e80e9ea2d15ad38c0c45887`
- N+6.0C repair branch: `feat/ghoti-agent-codex-n6-0c-report-history-stability-repair`
- N+6.0C repair commit: `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`
- Final main audit branch: `audit/ghoti-agent-codex-n6-0b-final-main-gemma-install-first-local-eval`

## Validation

Run from:

`C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_0b_final_main_audit`

Validation passed:

- `git diff --check`
- `git show --check --stat HEAD`
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 5 OK
- Total runtime tests: 431 OK
- Launcher smoke: PASS
- Context pack generation: PASS
- Local worker status/demo: PASS
- Gemma status and local model eval: PASS
- Hermes bridge status: PASS
- Gemma readiness status: PASS
- Local model worker status: PASS
- Repo knowledge status: PASS
- Public security audit: 150 checks / 0 blockers / 7 warnings requiring human review
- Model council scan: PASS
- UI-TARS dry-run: PASS
- Approved adapter status: PASS
- External sandbox status: PASS
- Supervised content demo validation: PASS
- Node syntax checks: PASS
- Runtime PowerShell check: PASS
- Dashboard PowerShell check: PASS with repo-supported resource-guard fixture

The first raw dashboard PowerShell run in the repair branch hit a desktop-session timeout in `open_allowed_app`. The fixture rerun passed and exercised the intended resource-guard path without opening new unrelated processes.

## Status Truth

- Gemma installed: yes, `gemma3:4b`
- Ollama version: `ollama version is 0.24.0`
- Installed model count: 1
- Active local worker mode: `ollama_gemma`
- Local worker readiness: 75%
- Gemma readiness: 74%
- First real local evaluation: complete
- Real Gemma score: 86%
- Tasks passed: 6 of 7
- Local demo comparison: 55%
- Production routing: disabled
- Routing gate: N+6.1A must implement the repo-bundle hallucination guard before routing.

Hermes remains manual bridge only:

- WSL path: `/home/ai_sandbox/.local/bin/hermes`
- Version: Hermes Agent v0.14.0
- Readiness: 58%
- Codex provider: pending/not proven
- Telegram: manual later/no token
- Browser/Playwright: degraded/not claimed
- No VPS

## Cleanup

- No broad process kills were run.
- No additional `ollama pull` commands were run.
- No Hermes setup, provider config, Telegram setup, tokens, browser automation, or live APIs were run.
- Generated validation residue was restored before this audit report.
- Primary worktree was not mutated.

## Next

Build N+6.1A: Constrained Local Model Routing / Repo-Bundle Hallucination Guard + Real Worker Task Integration.
