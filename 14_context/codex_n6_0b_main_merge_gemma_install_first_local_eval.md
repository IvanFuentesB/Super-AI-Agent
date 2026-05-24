# Codex N+6.0B Main Merge - Gemma Install And First Local Eval

Date: 2026-05-24

## Final Verdict

CLEAN PASS / N+6.0B MAIN MERGE READY.

N+6.0A was merged into the main merge gate through the latest clean audit branch. The prompt listed older N+6.0A branch hashes, but remote truth had already advanced after the roadmap-priority refresh, so this merge used the latest audited branch state.

## Branches

- Starting `origin/main`: `20e1dce1e89f15a337054864560b95b82233877c`
- Feature branch: `feat/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- Remote feature commit used: `fdb4279684af54372d0a05d8e5b4bd7098cced1e`
- Audit branch: `audit/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- Remote audit commit used: `43bccf63905f5261b81be1ce486aa628fc149f68`
- Merge-gate branch: `merge/ghoti-agent-codex-n6-0b-main-gemma-install-first-local-eval`
- Merge-gate commit before this report: `7fe917d999b92b6943bdf87d81a43d2112e7662e`

## Validation

Run from:

`C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_0b_main_merge_gate`

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
- Dashboard PowerShell check: PASS

The seven public-audit warnings remain human-review items, not blockers.

## Status Truth

- `gemma3:4b` is installed locally through the earlier human-approved N+6.0A pull.
- No additional model pulls were run in this merge gate.
- Ollama version: `ollama version is 0.24.0`
- Installed model count: 1
- Active local worker mode: `ollama_gemma`
- Local worker readiness: 75%
- Gemma readiness: 74%
- First real local model evaluation: complete
- Real Gemma score: 86%
- Passed tasks: 6 of 7
- Local demo comparison: 55%
- Production routing: disabled
- Routing blocker: one repo-bundle hallucination was caught in N+6.0A, so N+6.1A must add the repo-bundle hallucination guard before routing.

Hermes remains manual bridge only:

- WSL path: `/home/ai_sandbox/.local/bin/hermes`
- Version: Hermes Agent v0.14.0
- Readiness: 58%
- Codex provider: pending/not proven
- Telegram: manual later/no token
- Browser/Playwright: degraded/not claimed
- No VPS

## Operator Commands

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Gemma status: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Local model eval: `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`
- Hermes bridge: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`

## Cleanup

- No broad process kills were run.
- Launcher smoke used an owned temporary dashboard process.
- Generated timestamp/status residue from validation was restored before this report.
- Primary worktree was not mutated.

## Next

Build N+6.1A: constrained local model routing with a repo-bundle hallucination guard. After that, prioritize N+6.2A Hermes manual bridge verification and N+6.3A safe computer-use observation preparation.
