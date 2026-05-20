# Codex N+5.2A Real Audit: Hermes Local Bootstrap + Public Readiness + Model Provider Roadmap

## Audit Branch

- Audit branch: `audit/ghoti-agent-codex-n5-2a-hermes-local-bootstrap-public-readiness-model-provider-real-audit`
- Target branch: `origin/feat/ghoti-agent-codex-n5-2a-hermes-local-bootstrap-public-readiness-model-provider`
- Target commit: `5993afa790c07162dc443cfc8eee33c8fb9839e0`
- Remote truth: target `ls-remote` matched expected commit exactly
- Merge result: clean no-commit merge into isolated audit worktree from `origin/main`

## Hermes Bootstrap Result

- Script exists: yes, `03_scripts/hermes_local_bootstrap.py`
- Official installer URL: yes, `https://hermes-agent.nousresearch.com/install.sh`
- Status JSON: pass
- Prereq JSON: pass
- Windows commands: pass; output includes `curl.exe`, Git Bash/WSL guidance, no paid VPS note, and local secret handling warning
- Installer download: pass; installer downloaded to `14_context/hermes_agent/runs/20260520T171657Z_hermes_local_bootstrap/install.sh`
- Installer inspect: pass; SHA-256 recorded as `ade99101ec9bde981919a38b4c486123dcc341b5f33fc2e75e22e4e306835299`, first lines recorded, secrets redacted
- Report write: pass
- Latest report lookup: pass
- Install result: no install was executed during audit; branch reports no fake install success and keeps installer execution disabled without separate human approval
- Hermes command found on Windows: no
- WSL distro installed: yes, `Ubuntu`
- Hermes command found in Ubuntu WSL: no; `wsl -d Ubuntu -- bash -lc "command -v hermes && hermes --help | head -80"` returned command-not-found

## Hermes Artifact Result

Generated run folders under `14_context/hermes_agent/runs/` include the required artifact set:

- `00_manifest.json`
- `01_prereq_report.md`
- `02_installer_review.md`
- `03_install_attempt.json`
- `04_provider_support_review.md`
- `05_telegram_setup_plan.md`
- `06_local_ai_sandbox_plan.md`
- `07_model_council_integration.md`
- `08_human_next_steps.md`
- `09_preview.html`

Manifest verification:

- `local_only`: true
- `paid_vps_required`: false
- `vps_used`: false
- `admin_required`: false
- `telegram_token_required_from_user`: true
- `secrets_written`: false
- `live_api_used`: false
- `human_review_required`: true

## Documentation Result

- Required Hermes/model/provider docs exist: yes
- No paid VPS default documented: yes
- Telegram manual later documented: yes
- No tokens committed documented: yes
- Codex provider preferred if supported, pending if not verified: yes
- Gemma/Ollama local worker lane: yes
- ChatGPT/Claude/Codex model council lane: yes
- Approval gates: yes
- Bot/captcha/bypass automation blocked: yes
- Gap: explicit `Ubuntu` / `wsl -d Ubuntu` path and user-history WSL distro issue wording were not found in README/docs/script text

## Public Readiness Result

- `public_repo_security_audit.py --status --json`: pass
- `public_repo_security_audit.py --run --json`: pass
- `public_repo_security_audit.py --write-report --json`: pass
- Total checks: 150
- Passed checks: 143
- Failed checks: 0
- Warning checks: 7
- Blocking findings: 0
- `safe_to_make_public`: true
- Findings redacted: yes
- Secret values printed: no evidence found

Warning categories included claim/privacy review warnings in tests/dashboard/docs, all redacted by the audit output.

## Model Council Result

- `model_council_tool_intake.py --status --json`: pass
- `model_council_tool_intake.py --scan --json`: pass
- `model_council_tool_intake.py --write-report --json`: pass
- Manifest: local-only, no external repo install/execute, no live API, no runtime wiring, bot-detection bypass disabled
- Required registry entries present: `hermes-agent`, `codex`, `gemma/ollama`, `graphify`, `vercel-labs/agent-browser`, `browser-harness`, `claude skills`, `chatgpt/openai`, `claude-code`, `supabase`, `vercel`, `stripe`, `postgres`, `openwa`, `insforge`, `picoclaw`, `awesome-matlab-robotics / mthworks-robotics`
- Cloak/browser bot-detection entry: present and marked `BLOCKED`

## README Truthfulness Result

- Does not claim Hermes is installed without verification: pass
- Does not claim verified Hermes Codex provider support: pass
- Does not claim Telegram connected: pass
- Does not claim VPS running: pass
- Does not claim UI-TARS click/type/control enabled: pass
- Does not claim bot-detection bypass: pass
- Does not claim open-source license: pass

## Commit Attribution Result

Target branch commit audit:

- `5993afa790c07162dc443cfc8eee33c8fb9839e0`
- Author: `IvanFuentesB <IvanFuentesB@users.noreply.github.com>`
- Subject: `feat(ghoti): add Hermes local bootstrap and public readiness roadmap`
- AI co-author trailer found: no

## Validation Result

- `git diff --check`: pass
- `git show --check --stat HEAD`: pass for audited base HEAD

Regression tests:

- N+5.2A: 12 passed
- N+5.0A UI-TARS observation test: failed import, module missing from merged state
- N+4.9A: 37 passed
- N+4.8A: 35 passed
- N+4.7A: 25 passed
- N+4.6A: 33 passed
- N+4.5A: 68 passed
- N+4.4D: 18 passed
- N+4.4C: 16 passed
- N+4.4B: 17 passed
- N+4.4A: 20 passed
- N+4.3A: 15 passed
- N+4.2A: 26 passed
- N+4.1 reliability with `PYTHONPATH`: 19 passed

Test totals:

- Attempted tests: 342
- Passing tests: 341
- Failed modules: 1, `01_projects.runtime_mvp.tests.test_n5_0a_ui_tars_observation_only_adapter`

Runtime validators:

- `03_scripts/ui_tars_observation_adapter.py --status --json`: failed, file missing
- `approved_adapter_runner.py --status --json`: pass
- `external_tool_sandbox_manager.py --status --json`: pass
- `ghoti_product_launcher.py --status --json`: pass
- `parallel_agent_relay.py --status --json`: pass
- `local_memory_compression_bridge.py --json`: pass
- `repo_skill_plugin_intake.py --validate-config`: pass
- `ghoti_readiness_check.py --status`: pass, readiness remains 100
- `supervised_content_mvp_runner.py --validate-latest`: pass

Dashboard checks:

- Dashboard files were not changed by N+5.2A, so dashboard syntax and PowerShell dashboard check were not required by the conditional instruction.

## Cleanup Result

- No broad process kill was performed.
- No owned lingering validation process tied to the audit worktree was found.
- Generated Hermes/model/security run folders are ignored and not staged.

## Final Verdict

BLOCKED_VALIDATION

Reasons:

- Required N+5.0 UI-TARS observation test module is absent from the merged audit state.
- Required `03_scripts/ui_tars_observation_adapter.py` validator is absent from the merged audit state.
- Explicit `Ubuntu` / `wsl -d Ubuntu` path and user-history WSL distro issue wording were not documented in the implementation docs/scripts.

## Exact Next Action

Create a small fix branch from the N+5.2A feature branch or current `origin/main`, restore/merge the N+5.0 UI-TARS observation adapter and test coverage expected by the validator stack, and add explicit `wsl -d Ubuntu` / WSL distro troubleshooting language to the Hermes local bootstrap docs and command guidance. Then rerun this audit.
