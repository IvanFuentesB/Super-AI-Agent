# Codex N+5.0A Real Audit - UI-TARS Observation-Only Adapter

Generated: 2026-05-18

## Scope

| Item | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n5-0a-ui-tars-observation-only-adapter-real-audit` |
| Target branch | `origin/feat/ghoti-agent-claude-n5-0a-ui-tars-observation-only-adapter` |
| Target commit audited | `62fd1e6deb30b1a1d440d14691cf51abfdb6013a` |
| Remote polling | Branch appeared on attempt 33 |
| Fetch freshness | PASS - `ls-remote` and local tracking ref both matched `62fd1e6deb30b1a1d440d14691cf51abfdb6013a` |
| Base main | `origin/main` at `f863dc522d8a28b6265714daafa19a6ad5238fd7` |
| No-commit merge | PASS - automatic merge completed without conflicts |
| Commit strategy | No-commit merge was audited, then aborted so only this audit report is committed |

## Deliverables

| Requirement | Result |
| --- | --- |
| `03_scripts/ui_tars_observation_adapter.py` exists | PASS |
| `02_automation/external_tool_adapters/ui_tars_observation_adapter.py` exists | PASS |
| `01_projects/runtime_mvp/tests/test_n5_0a_ui_tars_observation_only_adapter.py` exists | PASS |
| Claude report exists | PASS - `14_context/claude_n5_0a_ui_tars_observation_only_adapter.md` |
| UI-TARS Observation Truth dashboard card exists | PASS |
| Dashboard endpoints exist | PASS |
| Seed run exists | PASS - `14_context/ui_tars_observation/runs/20260518T102053Z_ui_tars_observation/` |

Expected endpoints verified in source and live smoke:

| Endpoint | Result |
| --- | --- |
| `GET /api/ui-tars-observation/status` | PASS |
| `POST /api/ui-tars-observation/create-approval` | PASS |
| `POST /api/ui-tars-observation/dry-run` | PASS |
| `POST /api/ui-tars-observation/capture-approved` | PASS - present and rejects missing token |
| `GET /api/ui-tars-observation/latest` | PASS |

## Observation Adapter Result

| Check | Result |
| --- | --- |
| `--status --json` | PASS - exit 0, valid JSON |
| bare `--json` | PASS - exit 0, valid JSON status |
| `--create-approval --json` | PASS - exit 0, one-time token returned |
| `--observe --dry-run --json` | PASS - exit 0, local run artifacts written |
| `--latest --json` | PASS - exit 0, valid JSON |
| `--observe --capture-screen --json` without token | PASS - rejected non-zero with valid JSON |
| GET endpoints raw token leak | PASS - no raw `approval_token` in GET responses |
| Approval records | PASS - persisted records contain `token_hash`, no `approval_token` field |

Generated audit smoke run:

`14_context/ui_tars_observation/runs/20260518T103244Z_ui_tars_observation`

## Observation Artifacts

| Artifact | Result |
| --- | --- |
| `00_observation_manifest.json` | BLOCKED - missing required `local_only`, `click_enabled`, and `type_enabled` fields |
| `01_ui_tars_static_context.md` | PASS |
| `02_observation_report.md` | PASS |
| `03_observation.json` | PASS - includes `local_only: true`, `click_enabled: false`, `type_enabled: false` |
| `04_safety_review.md` | PASS |
| `05_human_next_steps.md` | PASS |
| `10_preview.html` | PASS |

Manifest contract validation:

| Required manifest field | Seed manifest | CLI dry-run manifest | Dashboard dry-run manifest |
| --- | --- | --- | --- |
| `local_only: true` | MISSING | MISSING | MISSING |
| `external_repo_code_executed: false` | PASS | PASS | PASS |
| `installs_performed: false` | PASS | PASS | PASS |
| `ui_tars_runtime_started: false` | PASS | PASS | PASS |
| `desktop_control_enabled: false` | PASS | PASS | PASS |
| `click_enabled: false` | MISSING | MISSING | MISSING |
| `type_enabled: false` | MISSING | MISSING | MISSING |
| `live_api_used: false` | PASS | PASS | PASS |

This is the blocking validation issue. The requested contract specifically says the observation manifest must include these fields. They are present in `03_observation.json`, but not in `00_observation_manifest.json`.

## Static Validation

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| `git show --check --stat HEAD` | PASS |
| `node --check 01_projects/dashboard_mvp/server.js` | PASS |
| `node --check 01_projects/dashboard_mvp/public/app.js` | PASS |
| Python AST for N+5.0A script, adapter, and tests | PASS |

## Live Dashboard Smoke

Disposable dashboard server:

| Field | Result |
| --- | --- |
| Local port | `37618` |
| Server started | PASS |
| Server stopped | PASS |
| Lingering process tied to audit worktree | PASS - none |

Endpoint results:

| Endpoint | Result |
| --- | --- |
| `GET /api/ui-tars-observation/status` | PASS - HTTP 200, valid JSON, `ok: true` |
| `POST /api/ui-tars-observation/create-approval` | PASS - HTTP 200, valid JSON, one-time token returned only in POST response |
| `POST /api/ui-tars-observation/dry-run` | PASS - HTTP 200, valid JSON, run artifacts written |
| `POST /api/ui-tars-observation/capture-approved` without token | PASS - JSON rejection with `ok: false` |
| `GET /api/ui-tars-observation/latest` | PASS - HTTP 200, valid JSON, no raw token |
| 500 / ReferenceError | PASS - none observed |

Live endpoint smoke also reproduced the blocking manifest gap for dashboard-created dry-run artifacts.

## Test Totals

| Suite | Tests | Result |
| --- | ---: | --- |
| N+5.0A UI-TARS observation-only adapter | 37 | PASS |
| N+4.9A first approved adapter execution | 37 | PASS |
| N+4.8A external tool sandbox | 35 | PASS |
| N+4.7A product launcher | 25 | PASS |
| N+4.6A product dashboard | 33 | PASS |
| N+4.5A parallel agent relay | 68 | PASS |
| N+4.4D preview containment | 18 | PASS |
| N+4.4C recipe runner preview polish | 16 | PASS |
| N+4.4B dashboard action center | 17 | PASS |
| N+4.4A desktop operator control plane | 20 | PASS |
| N+4.3A content studio | 15 | PASS |
| N+4.2A local memory intake | 26 | PASS |
| N+4.1 runtime reliability | 19 | PASS |
| Total | 366 | PASS |

The 37 N+5.0A tests pass, but they do not catch the missing `00_observation_manifest.json` contract fields.

## Downstream Checks

| Check | Result |
| --- | --- |
| `python 03_scripts/approved_adapter_runner.py --status --json` | PASS |
| `python 03_scripts/external_tool_sandbox_manager.py --status --json` | PASS |
| `python 03_scripts/ghoti_product_launcher.py --status --json` | PASS |
| `python 03_scripts/parallel_agent_relay.py --status --json` | PASS |
| `python 03_scripts/local_memory_compression_bridge.py --json` | PASS |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | PASS |
| `python 03_scripts/ghoti_readiness_check.py --status` | PASS - score 100 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | PASS - score 100 |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | PASS |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | PASS |

## Safety Summary

| Safety requirement | Result |
| --- | --- |
| No UI-TARS runtime start | PASS |
| No external repo code execution | PASS |
| No installs | PASS |
| No desktop control | PASS |
| No click/type/hotkey | PASS |
| No live APIs/accounts/posting/money/trading | PASS |
| No `shell:true` in inspected N+5.0A runtime path | PASS |
| Capture-approved without token rejected | PASS |
| Non-dry-run requires token | PASS |
| GET endpoints do not leak raw tokens | PASS |
| Approval records store hashes only | PASS |
| Readiness remains 100 | PASS |

## Screenshot / Terminal Behavior

| Observation | Result |
| --- | --- |
| Blocking GUI popup | PASS - none observed |
| Weird duplicate clipboard command | PASS - none required |
| Blocking node/window process | PASS - disposable dashboard process was stopped |
| Lingering validation process tied to audit worktree | PASS - none found |

## Final Verdict

BLOCKED_VALIDATION

Exact blocker:

`00_observation_manifest.json` for the seed run, CLI dry-run, and dashboard dry-run does not include required fields:

- `local_only: true`
- `click_enabled: false`
- `type_enabled: false`

Exact next recommended action:

Patch `02_automation/external_tool_adapters/ui_tars_observation_adapter.py` so `00_observation_manifest.json` includes `local_only: true`, `click_enabled: false`, and `type_enabled: false`; update `test_n5_0a_ui_tars_observation_only_adapter.py` to assert those manifest fields; regenerate/refresh the seed run; then repush N+5.0A for audit rerun.
