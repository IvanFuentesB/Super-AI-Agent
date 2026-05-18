# Codex N+4.9B Final Main Audit - First Approved Adapter Execution Demo

Generated: 2026-05-18

## Scope

| Item | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-9b-final-main-first-approved-adapter-execution-demo` |
| Remote main hash | `f863dc522d8a28b6265714daafa19a6ad5238fd7` |
| Main commit audited | `f863dc522d8a28b6265714daafa19a6ad5238fd7` |
| N+4.9A implementation commit | `fd4833ea91e30b9cb8c15471601cbacb8b7b6024` |
| Implementation on main | YES - `fd4833e` is an ancestor of audited main |
| Merge/report commits on main | YES - merge `ba4d27e`, report `f863dc5` |
| Prior N+4.9A audit | VERIFIED - remote audit branch points to `468496042a65bad80510076c08b760d18e406e46` and main merge report records CLEAN PASS |
| Note on audit commit ancestry | Prior audit commit is verified by remote branch/report, but is not an ancestor of main, matching prior merge-gate pattern |

## Main Content Verification

| Requirement | Result |
| --- | --- |
| `03_scripts/approved_adapter_runner.py` exists | PASS |
| `02_automation/external_tool_adapters/agent_skills_eval_adapter.py` exists | PASS |
| N+4.9A test file exists | PASS |
| Claude N+4.9A report exists | PASS |
| Claude N+4.9B main merge report exists | PASS |
| Approved Adapter Execution Truth dashboard card exists | PASS |
| Adapter execution endpoints exist | PASS |
| Seed run under `14_context/adapter_execution/runs/` exists | PASS |
| Seed evaluation JSON has score/recommendations | PASS - score 80 with 3 recommendations |
| Seed execution manifest unsafe flags | PASS - external code, installs, desktop control, and live API all false |

## Static Validation

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| `git show --check --stat HEAD` | PASS |
| `node --check 01_projects/dashboard_mvp/server.js` | PASS |
| `node --check 01_projects/dashboard_mvp/public/app.js` | PASS |
| Python AST for runner, adapter, and N+4.9A tests | PASS |

## Adapter Runner CLI Validation

| Command | Result |
| --- | --- |
| `python 03_scripts/approved_adapter_runner.py --status --json` | PASS - valid JSON, local approval-gated mode |
| `python 03_scripts/approved_adapter_runner.py --json` | PASS - valid JSON |
| `python 03_scripts/approved_adapter_runner.py --list-adapters --json` | PASS - valid JSON, approved catalog present |
| `python 03_scripts/approved_adapter_runner.py --create-approval --adapter agent_skills_eval --json` | PASS - one-time token returned, approval record written |
| `python 03_scripts/approved_adapter_runner.py --execute-approved --adapter agent_skills_eval --dry-run --json` | PASS - dry-run local execution created artifacts |
| Unknown adapter dry-run | PASS - rejected with non-zero JSON error |
| Non-dry-run without token | PASS - rejected with non-zero JSON error requiring approval token |

Latest audited run folder:

`14_context/adapter_execution/runs/20260518T095723Z_agent_skills_eval`

Artifacts verified:

| Artifact | Result |
| --- | --- |
| `00_demo_skill.md` | PASS |
| `01_skill_evaluation.md` | PASS |
| `02_skill_evaluation.json` | PASS - score 80, recommendations present |
| `03_safety_review.md` | PASS |
| `04_execution_manifest.json` | PASS |
| `05_human_next_steps.md` | PASS |

Execution manifest:

| Flag | Value |
| --- | --- |
| `external_code_executed` | false |
| `installs_performed` | false |
| `desktop_control_enabled` | false |
| `live_api_used` | false |
| `dry_run` | true |

Approval record behavior:

| Check | Result |
| --- | --- |
| Persisted approval records store `token_hash` | PASS |
| Persisted approval records include raw `approval_token` field | PASS - absent |
| Persisted approval records contain raw token pattern | PASS - absent |
| GET endpoints leak raw token | PASS - no raw token leaked |

## Dashboard / Endpoint Validation

Disposable dashboard server:

| Field | Result |
| --- | --- |
| Local port | `36076` |
| Server started | PASS |
| Server stopped | PASS - started PID stopped only |
| Lingering server process tied to audit worktree | PASS - none |

Live adapter endpoint smoke:

| Endpoint | Result |
| --- | --- |
| `GET /api/adapter-execution/status` | PASS - HTTP 200, valid JSON, `ok: true` |
| `GET /api/adapter-execution/adapters` | PASS - HTTP 200, valid JSON, `ok: true` |
| `POST /api/adapter-execution/create-approval` | PASS - HTTP 200, valid JSON, `ok: true`; one-time token returned only in POST response |
| `POST /api/adapter-execution/run-demo` | PASS - HTTP 200, valid JSON, `ok: true`; dry-run artifacts produced |
| `GET /api/adapter-execution/latest` | PASS - HTTP 200, valid JSON, `ok: true`; latest local artifact paths returned |
| 500 / ReferenceError / route bug | PASS - no 500s, no `method is not defined`, no `pathname is not defined` |

## Regression Totals

| Suite | Tests | Result |
| --- | ---: | --- |
| N+4.9A approved adapter execution | 37 | PASS |
| N+4.8A external tool sandbox | 35 | PASS |
| N+4.7A product launcher | 25 | PASS |
| N+4.6A product dashboard | 33 | PASS |
| N+4.5A parallel relay | 68 | PASS |
| N+4.4D preview containment | 18 | PASS |
| N+4.4C recipe runner preview polish | 16 | PASS |
| N+4.4B dashboard action center | 17 | PASS |
| N+4.4A desktop operator control plane | 20 | PASS |
| N+4.3A supervised content studio | 15 | PASS |
| N+4.2A local memory intake | 26 | PASS |
| N+4.1 runtime reliability | 19 | PASS |
| Total | 329 | PASS |

## Downstream Checks

| Check | Result |
| --- | --- |
| `python 03_scripts/external_tool_sandbox_manager.py --status --json` | PASS - no installs, no external code execution, no runtime wiring |
| `python 03_scripts/ghoti_product_launcher.py --status --json` | PASS |
| `python 03_scripts/parallel_agent_relay.py --status --json` | PASS |
| `python 03_scripts/local_memory_compression_bridge.py --json` | PASS - local-only, external API false, Gemma fallback truthful |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | PASS - 22 entries blocked from runtime wiring/live actions |
| `python 03_scripts/ghoti_readiness_check.py --status` | PASS - supervised MVP slice score 100 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | PASS - score 100 |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | PASS - exit 0 |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | PASS - exit 0 |

## Safety Summary

| Safety requirement | Result |
| --- | --- |
| No external repo code executed | PASS |
| No installs performed | PASS |
| No UI-TARS start | PASS |
| No desktop control enabled | PASS |
| No live APIs/accounts | PASS |
| No live posting/uploading | PASS |
| No money/trading actions | PASS |
| No unsafe adapter runtime wiring | PASS |
| No `shell:true` in inspected runtime path | PASS |
| Unknown adapters rejected | PASS |
| Dry-run works without token | PASS |
| Non-dry-run requires token | PASS |
| Approval records store hashes only | PASS |
| No secrets/API keys found in inspected runtime paths | PASS |
| Approval gates intact | PASS |
| Readiness remains 100 | PASS |

## Screenshot / Terminal Behavior

| Observation | Result |
| --- | --- |
| Blocking GUI popup | PASS - none observed |
| Weird duplicate clipboard command | PASS - none required; clipboard-related checks were intentional dashboard safety checks |
| Blocking node/window process | PASS - disposable dashboard process was stopped |
| Lingering validation process tied to audit worktree | PASS - none found |

## Direct Answers

| Question | Answer |
| --- | --- |
| Is N+4.9A on main? | YES |
| Is the first approved adapter execution demo present on main? | YES |
| Does the adapter runner create local run artifacts? | YES |
| Does evaluation JSON include score/recommendations? | YES - score 80 and recommendations present |
| Does the execution manifest keep unsafe flags false? | YES |
| Are unknown adapters rejected? | YES |
| Does dry-run work without a token? | YES |
| Does non-dry-run require an approval token? | YES |
| Are raw approval tokens persisted or leaked by GET endpoints? | NO |
| Was external repo code executed? | NO |
| Were dependencies installed? | NO |
| Was UI-TARS started or desktop control enabled? | NO |
| Were live APIs/accounts used? | NO |
| Are approval gates intact? | YES |
| Is this full Ghoti production 100%? | NO - this is still a supervised/local-only product slice, not autonomous public production |

## Final Verdict

CLEAN PASS

Exact next recommended action:

Merge/accept N+4.9A as clean on main and proceed to the next supervised milestone only if it preserves local-only execution, approval gates, and no external-code/live-action behavior.
