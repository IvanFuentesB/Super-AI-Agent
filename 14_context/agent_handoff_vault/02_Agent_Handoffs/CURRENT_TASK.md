# Current Task

Status: ready-for-codex-or-claude

## Milestone
N+6.4A — Ghoti Skills System + Karpathy Guidelines + Current Hermes Truth Registration

## Goal
Register the real local Hermes setup inside Ghoti repo truth, create a safe skills/playbook workflow, and prepare Ghoti for future multi-agent routing without enabling unsafe autonomy.

## Assigned Agent
Codex first when quota resets.
Claude Code only if implementation help is needed.
Hermes/local Llama can help draft/summarize only.

## Current Hermes Truth
- Hermes works in ai_sandbox WSL Ubuntu.
- Hermes version seen: v0.14.0.
- Hermes uses llama3.1:8b.
- Provider is custom local endpoint.
- Ollama models available: llama3.1:8b and gemma3:4b.
- Gemma is kept for cheap summaries/compression.
- qwen was removed.
- Telegram is not configured for Ghoti Hermes yet.
- Browser/computer-use tools are visible but not approved/enabled for Ghoti use yet.

## Files Allowed
- 14_context/ghoti_current_truth.md
- 14_context/skills/
- docs/GHOTI_SKILLS_AND_AGENT_WORKFLOW.md
- docs/CLAUDE_CODE_SKILLS_POLICY.md
- docs/CODEX_AUDIT_WORKFLOW.md
- docs/HERMES_LOCAL_SETUP_CURRENT_TRUTH.md
- 01_projects/runtime_mvp/tests/test_n6_4a_*.py
- 03_scripts/ghoti_product_launcher.py only if needed and low-risk

## Files Forbidden
- Secrets, .env files, auth files, browser sessions, cookies, tokens.
- Main branch direct edits.
- Unrelated dashboard/app refactors.
- Any live Telegram/browser/computer-use integration.

## Success Criteria
- Repo truth documents current Hermes/Llama/Gemma setup accurately.
- Skill policy says external skills are inspected before use.
- Karpathy-style rules are adapted safely: think first, simple changes, surgical edits, tests.
- Claude/Codex/Hermes roles are clearly separated.
- No claim that browser click/type, Telegram, or full autonomy is enabled.
- Tests or validation checks prove the docs exist and avoid unsafe claims.
- Final report says what changed, what is still not enabled, and next step.

## Safety Rules
- No secrets.
- No live actions.
- No broad process kills.
- No browser click/type.
- No Telegram setup yet.
- No random executable repo installs.
- Inspect third-party repos before installing anything.
- One agent per task.
- Never let multiple agents edit the same files.
