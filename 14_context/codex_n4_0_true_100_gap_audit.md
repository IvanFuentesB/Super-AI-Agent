# Codex N+4.0 True-100 Gap Audit

Date: 2026-05-07

Audit branch: `audit/ghoti-agent-codex-n4-0-true-100-gap-audit`

Branch audited: `origin/main`

Main commit audited: `63ba393780823e2cf25c9e45b29d388262bd4593`

Final verdict: **TRUE_100_NOT_YET**

Implementation readiness: **READY_FOR_N4_IMPLEMENTATION**, but not ready to call true-100.

## Executive Summary

Current `origin/main` is a useful local operator foundation, not a serious true-100 supervised operator MVP yet.

Main contains a dashboard, runtime queue models, approval concepts, local-only scaffolds, GitHub/mail/Notion planning paths, browser and desktop bridge foundations, publishability checks, and many docs. But the daily operator loop is currently broken at the supervisor/status layer:

```text
SupervisorState.__init__() missing 1 required positional argument: 'ready_to_resume_count'
```

This breaks:

- `python -m super_ai_agent.cli status`
- `python -m super_ai_agent.cli supervisor-status`
- `python -m super_ai_agent.cli pending-approvals`
- `powershell -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`
- dashboard supervisor endpoint during `check_dashboard_mvp.ps1`

Also, current `origin/main` does not contain the N+3.65 supervised content MVP implementation or proof packet. That work is on `origin/feat/ghoti-visible-operator-stack` at `99c26b5` and should not be counted as present on main until merged.

## Validation Evidence

| Check | Result | Evidence |
|---|---:|---|
| `git fetch origin --prune` | PASS | Completed |
| `origin/main` resolved | PASS | `63ba393780823e2cf25c9e45b29d388262bd4593` |
| Main contains integration `99c26b5` | FAIL | `merge-base --is-ancestor 99c26b5 origin/main` exit `1` |
| Main contains N+3.65 `677d9f0` | FAIL | `merge-base --is-ancestor 677d9f0 origin/main` exit `1` |
| Python AST | PASS | 20 Python files parsed |
| JSON configs | PASS | 14 JSON config files parsed |
| `check_foundation.ps1` | PASS | 15 required foundation checks passed |
| Runtime CLI status | FAIL | `SupervisorState.__init__()` missing `ready_to_resume_count` |
| Runtime supervisor status | FAIL | Same constructor mismatch |
| Runtime pending approvals | FAIL | Same constructor mismatch |
| `check_runtime_mvp.ps1` | FAIL | 35 runtime checks failed, mostly cascading from supervisor state bug |
| `check_dashboard_mvp.ps1` | FAIL | Dashboard starts, but `/api/supervisor/status` returns HTTP 500 |
| Dashboard Node syntax | PASS | `node --check server.js` and `public/app.js` pass |
| Capability matrix | PASS | Reports available/blocking states |
| Publishability scan | PASS | `finding_count: 0` |
| `git diff --check` | PASS | Clean in audit worktree |

## Current Truth by Dimension

| Dimension | Status | Files involved | Missing behavior | Proving test | Safety condition | Owner |
|---|---|---|---|---|---|---|
| 1. Operator control center / dashboard | Implemented but weak | `01_projects/dashboard_mvp/server.js`, `01_projects/dashboard_mvp/public/app.js`, `03_scripts/check_dashboard_mvp.ps1` | Supervisor/status endpoint crashes; no N+3.65 readiness card on main | `powershell -File 03_scripts/check_dashboard_mvp.ps1` exits `0`; `/api/supervisor/status` returns 200 | Dashboard must remain local-only and no live-action buttons without approval | Claude Code |
| 2. Approval gate system | Implemented but broken | `01_projects/runtime_mvp/src/super_ai_agent/models.py`, `storage.py`, `queue.py`, `cli.py` | Default supervisor state does not include `ready_to_resume_count`; enqueue/status approval loop broken | `python -m super_ai_agent.cli init-data`, `status`, `enqueue`, `pending-approvals` all exit `0` | Approval gates cannot auto-send, auto-post, pay, apply, or publish | Claude Code |
| 3. Local memory / Obsidian memory | Scaffold only on main | `14_context/00_main_memory/*`, `14_context/current_state.md`, `14_context/next_actions.md` | No main-branch Obsidian vault, compact memory refresh, or promotion workflow | `Test-Path 14_context/obsidian_vault/00_Index.md`; memory refresh command creates draft only | Canonical memory updates require explicit review | Claude Code, then Codex audit |
| 4. Gemma/Ollama local brain routing | Scaffold only on main | `01_projects/runtime_mvp/src/super_ai_agent/providers.py`, `23_configs/provider_profiles.example.json` | Gemma is a provider label, not an automatic compression worker on main | `ollama list`; a local compression command writes draft summary | Local-only; no model pull without approval; no secret-path reads | Claude Code + Local Gemma |
| 5. LLM Council | Scaffold only on main | `council.py`, `truth_council.py`, CLI `council-plan`, `truth-plan` | No N+3.61 session runner or 3-stage artifact workflow on main | Council command creates first opinions, peer review, synthesis artifacts | External providers disabled unless separately approved | Claude Code; Codex audit |
| 6. Supervised content workflow | Missing on main | Missing `03_scripts/supervised_content_mvp_runner.py`, `ghoti_readiness_check.py`, proof packet | N+3.65 exists on integration branch, not main | `supervised_content_mvp_runner.py --validate-latest` exits `0` on main | No live posting, upload, account login, external API, or revenue claim | Operator merge, then Codex audit |
| 7. External repo intake / implementation map | Scaffold only on main | `08_research/repo_intake_matrix.md`, missing N+3.63/N+3.65 scripts | No main-branch OpenFang/MoneyPrinter Ghoti-native implementation map | `external_repo_implementation_map.py --status` exits `0` | No clone/install/run; concept mapping only until approval | Claude Code; Codex audit |
| 8. Browser/operator future path | Implemented but weak | `01_projects/browser_playground/*`, `01_projects/desktop_playground/*`, dashboard routes | Browser/app execution still explicitly blocked; desktop bridge is narrow | Browser/desktop checks pass and approval queue records actions | No autonomous browser actions; Ctrl+8/failsafe and visible operator cues | Claude Code |
| 9. MCP/server/tooling path | Scaffold only on main | `integrations.py`, docs, configs | No repo-local MCP server on main; later integration branch has more | MCP status command with read-only tools only | No external connectors or account actions without approval | Claude Code |
| 10. Queue/wait-state/async jobs | Implemented but broken | `queue.py`, `storage.py`, `models.py`, runtime data | Queue cannot run because supervisor state creation fails | `check_runtime_mvp.ps1` exits `0`; wait/resume tasks round-trip | Queue actions remain local and approval-gated | Claude Code |
| 11. Safety/secrets/public-action gates | Implemented and partially proven | `.gitignore`, publish configs, `publishability.py`, policies | GitHub remote write is possible if `gh` auth exists; needs visible operator confirmations | `publish-check` exits `0`; write commands refuse without approval | No secrets committed; no live action without explicit approval | Codex audit + Claude Code |
| 12. Test coverage and validation commands | Implemented but weak | `03_scripts/check_*.ps1` | Tests exist but runtime/dashboard checks fail; no single green all-up command | `check_foundation`, `check_runtime_mvp`, `check_dashboard_mvp` all exit `0` | Checks must avoid live external side effects | Claude Code |
| 13. Documentation/runbooks | Implemented but noisy | `04_docs/*`, `14_context/*`, `README.md` | Docs are extensive but scattered; run path not one obvious daily workflow | One `04_docs/daily_operator_runbook.md` matches real commands | Docs must not overclaim automation | ChatGPT + Codex |
| 14. User workflow friction | Implemented but high-friction | Dashboard, CLI, docs, prompts | User still must know which branch, which checker, which lane, and which artifacts matter | Dashboard shows one daily operator checklist and next action | No hidden background automation | ChatGPT + Claude Code |
| 15. Daily practical readiness | Not ready | Whole stack | Supervisor crash blocks core daily loop; N+3.65 not on main; memory/Gemma not wired | Fresh clone: run one command, dashboard works, approval queue works, proof packet visible | Human remains final approver | Claude Code first, then Codex |

## Already Implemented and Proven

- Foundation file layout and project docs exist.
- Dashboard package syntax and health route work.
- Runtime file layout exists.
- Approval policy concepts and local queue models exist.
- Capability matrix reports available vs blocked capabilities.
- Publishability scan reports no findings.
- GitHub, mail, Notion, personal-ops, and portfolio scaffolds are planning/draft oriented.
- GitHub remote actions refuse without explicit `--approve yes`.
- Browser/app execution is honestly reported as blocked.
- Current main is local-first and does not claim autonomous production.

## Implemented but Weak

- Dashboard exists but core supervisor endpoint can fail.
- Runtime queue, approval, wait/resume models exist but current state initialization is broken.
- Desktop bridge exists but remains narrow and not a general operator.
- GitHub remote capability exists and is authenticated in this environment, but it needs stronger dashboard-visible approval context before daily use.
- Docs are broad but not organized into a short daily operator path.

## Scaffold Only

- Gemma/Ollama local brain routing on main.
- LLM council on main.
- External repo implementation map on main.
- Obsidian/compact memory promotion workflow on main.
- MCP/server path on main.
- Supervised content workflow on main.

## Missing

- N+3.65 supervised content MVP on `origin/main`.
- One green daily health command.
- Working supervisor/status/approval queue on a clean checkout.
- Dashboard view that accurately joins control center, approvals, memory, local brain, LLM council, and supervised workflow state.
- Gemma draft compression integrated into memory refresh.
- Obsidian memory snapshot/promotion loop on main.
- Proof-packet browser/dashboard validation on main.
- Rollback/restore runbook for local runtime data.

## Dangerous or Not Allowed Yet

- Autonomous posting, upload, public release, job applications, payments, live outreach, fake engagement, and account automation.
- Broad browser/computer-use automation.
- External repo clone/install/run as runtime dependency.
- Ruflo runtime/swarm/MCP launch.
- Reading `.env`, credentials, tokens, browser sessions, or API keys.
- Auto-promotion of Gemma/LLM output into canonical memory.

## Next 3 Implementation Milestones

1. N+4.1 Dashboard Control Center Reliability and Daily Readiness
2. N+4.2 Local Memory and Gemma Draft Compression Bridge
3. N+4.3 Supervised Workflow Approval Packet on Main

## Recommended Immediate Fix

First fix the runtime supervisor crash:

- File: `01_projects/runtime_mvp/src/super_ai_agent/storage.py`
- File: `01_projects/runtime_mvp/src/super_ai_agent/models.py`
- Missing behavior: `_default_supervisor_state()` must include `ready_to_resume_count=0`, and existing supervisor state reads should tolerate older JSON.
- Proving tests:
  - `python -m super_ai_agent.cli init-data`
  - `python -m super_ai_agent.cli status`
  - `python -m super_ai_agent.cli supervisor-status`
  - `python -m super_ai_agent.cli pending-approvals`
  - `powershell -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1`
  - `powershell -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1`
- Safety condition: the fix must not loosen approval gates or enable any live/public action.

## Final Verdict

**TRUE_100_NOT_YET**

Ghoti is ready for focused N+4 implementation work, but current `origin/main` does not deserve a true-100 label. The first blocker is not glamorous: the daily supervisor/runtime status path must be made green before any higher-level control center claims are credible.
