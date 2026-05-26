# CLEAN PASS / N+6.2A HERMES MANUAL BRIDGE WSL GUIDE READY

## Branches

- Starting main: `39daf4d81f8a5dc123c9949ce6d7c3ea49763978`
- N+6.1B final main audit: `audit/ghoti-agent-codex-n6-1b-final-main-constrained-local-model-routing-guard` at `cc5bb498f27f2902497f929bca6c8930ba8e538a`
- Feature branch: `feat/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- Audit branch: `audit/ghoti-agent-codex-n6-2a-hermes-agent-manual-bridge-verification-wsl-guide`
- Merge policy: N+6.2A remains feature/audit only; it is not merged to main in this run.

## What Changed

- Added `03_scripts/hermes_manual_bridge_verifier.py`.
- Added launcher commands:
  - `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json`
  - `python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json`
  - `python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json`
- Added dashboard card: `Hermes Manual Bridge / WSL Guide`.
- Added generated Hermes manual bridge files under `14_context/hermes_manual_bridge/generated/`.
- Added WSL/Hermes docs, safe/blocked command docs, and the future Apple comparison test plan.
- Updated context packs and repo knowledge map outputs to reference the Hermes manual bridge, WSL guide, safe command list, blocked command list, and N+6.3A Apple comparison observation plan.

## Hermes Truth

- Hermes manual bridge readiness: `64%`.
- WSL Ubuntu: installed and inspectable.
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`.
- N+6.2A verifier parsed skills: `79`.
- Safe WSL footer evidence: `0 hub-installed, 84 builtin, 0 local - 84 enabled, 0 disabled`.
- Older Hermes workflow bridge still reports readiness `58%` and `78` parsed skills.
- Codex provider in Hermes: pending/not proven.
- Telegram: manual later/no token.
- Browser/Playwright: degraded/not claimed.
- VPS: none.

## Safe Commands

- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; pwd"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --help | head -120 || true"`
- `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json`

## Blocked Commands

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

These remain blocked/manual because provider setup, token flows, Telegram, browser automation, computer-use click/type, and external runtime installs require separate human-approved audited milestones.

## Generated Files

- `14_context/hermes_manual_bridge/generated/00_hermes_manual_bridge_status.json`
- `14_context/hermes_manual_bridge/generated/01_wsl_usage_guide.md`
- `14_context/hermes_manual_bridge/generated/02_hermes_safe_commands.md`
- `14_context/hermes_manual_bridge/generated/03_hermes_blocked_commands.md`
- `14_context/hermes_manual_bridge/generated/04_hermes_skills_summary.md`
- `14_context/hermes_manual_bridge/generated/05_hermes_agent_bridge_next_steps.md`
- `14_context/hermes_manual_bridge/generated/06_computer_use_roadmap_note.md`
- `14_context/hermes_manual_bridge/generated/07_apple_comparison_manual_bridge_plan.md`

Apple comparison future plan:

- `docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md`

The Apple plan is observation/manual-approval only. It does not execute browser control in this milestone.

## Validation

- `git diff --check`: PASS.
- N+4 tests: 329 OK.
- N+5 tests: 97 OK.
- N+6 tests: 18 OK.
- Total runtime tests: 444 OK.
- Launcher smoke: PASS.
- Context pack: PASS.
- Local worker routing status: PASS.
- Repo map: PASS.
- Hermes bridge status: PASS.
- Hermes manual status/doctor/WSL explain/safe commands/blocked commands/skills summary/write guide: PASS.
- Hermes agent workflow bridge: PASS.
- Local model routing status: PASS.
- Local model output guard self-test: PASS.
- Public audit: 150 checks / 0 blockers / 7 warnings requiring human review.
- Model council scan: PASS.
- UI-TARS dry-run: PASS, observation-only.
- Adapter runner status: PASS, approval-gated/local-only.
- External sandbox status: PASS, static inspection only.
- Supervised content demo validation: PASS.
- Node syntax checks: PASS.
- Runtime PowerShell check: PASS.
- Dashboard PowerShell check: initial parallel run timed out after ~124 seconds; rerun with repo-supported `-RuntimeLockSafe` mode passed.
- Safe WSL probes: PASS for Hermes path, version, and skills list.

## Status Truth

- Gemma guarded lane: `gemma3:4b`, active guarded routing, readiness `82%`.
- Routing guard: enabled, source metadata required, invented bundles rejected.
- UI-TARS: observation-only.
- Adapter runner: approval-gated/local-only.
- External sandbox: static inspection only.
- No live APIs.
- No provider setup.
- No Telegram setup.
- No browser automation.
- No computer-use click/type.
- No extra model pulls.

## Human Status

Human status: Ghoti is about 92% complete toward the bigger local-first agent OS vision. The local MVP is stable and usable. Current capabilities are a dashboard/launcher, compact context packs, repo knowledge bundles, real Gemma guarded local worker routing, public/security audit gates, UI-TARS observation-only dry-runs, and a safe Hermes manual bridge/WSL guide. The main gaps are live Hermes provider verification, Telegram, browser/Playwright remediation, audited computer-use observation harness, and any future click/type/account actions behind explicit human approval. Confidence: high because the feature and existing safety lanes passed local validation, with only public-audit warnings left for human review.

## Final Verdict

CLEAN PASS / N+6.2A HERMES MANUAL BRIDGE WSL GUIDE READY
