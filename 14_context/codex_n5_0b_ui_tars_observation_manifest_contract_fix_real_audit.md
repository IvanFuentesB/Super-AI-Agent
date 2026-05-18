# Codex N+5.0B Real Audit - UI-TARS Observation Manifest Contract Fix

Generated: 2026-05-18

## Scope

| Item | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n5-0b-ui-tars-observation-manifest-contract-fix-real-audit` |
| Target branch | `origin/feat/ghoti-agent-claude-n5-0b-ui-tars-observation-manifest-contract-fix` |
| Target commit audited | `cdb8398a5bb71326cbfad01ae6810c62d1db03fd` |
| Remote polling | Branch appeared on attempt 27 |
| Fetch freshness | PASS - `ls-remote` and local tracking ref both matched `cdb8398a5bb71326cbfad01ae6810c62d1db03fd` |
| Base main | `origin/main` at `f863dc522d8a28b6265714daafa19a6ad5238fd7` |
| No-commit merge | PASS - automatic merge completed without conflicts |
| N+5.0A included | PASS - branch includes `62fd1e6deb30b1a1d440d14691cf51abfdb6013a` |
| N+5.0B fix commit | PASS - branch includes `cdb8398a5bb71326cbfad01ae6810c62d1db03fd` |
| Commit strategy | No-commit merge was audited, then aborted so only this audit report is committed |

## Manifest Contract Result

N+5.0A was blocked because `00_observation_manifest.json` omitted `local_only`, `click_enabled`, and `type_enabled`.

| Required manifest field | Committed seed run | CLI generated dry-run | Dashboard generated dry-run |
| --- | --- | --- | --- |
| `local_only: true` | PASS | PASS | PASS |
| `click_enabled: false` | PASS | PASS | PASS |
| `type_enabled: false` | PASS | PASS | PASS |
| `external_repo_code_executed: false` | PASS | PASS | PASS |
| `installs_performed: false` | PASS | PASS | PASS |
| `ui_tars_runtime_started: false` | PASS | PASS | PASS |
| `desktop_control_enabled: false` | PASS | PASS | PASS |
| `live_api_used: false` | PASS | PASS | PASS |

Explicit generated-manifest assertion:

`MANIFEST_CONTRACT_PASS`

Generated audit run:

`14_context/ui_tars_observation/runs/20260518T135603Z_ui_tars_observation`

Committed seed run:

`14_context/ui_tars_observation/runs/20260518T104524Z_ui_tars_observation`

## Observation Adapter Result

| Requirement | Result |
| --- | --- |
| UI-TARS observation adapter script exists | PASS |
| UI-TARS observation adapter stub exists | PASS |
| UI-TARS Observation Truth dashboard card exists | PASS |
| N+5.0B Claude report exists | PASS |
| `--status --json` | PASS - exit 0, valid JSON |
| bare `--json` | PASS - exit 0, valid JSON status |
| `--create-approval --json` | PASS - exit 0; one-time token returned only in create response |
| `--observe --dry-run --json` | PASS - exit 0, local artifacts written |
| `--latest --json` | PASS - exit 0, valid JSON |
| capture/non-dry-run without token | PASS - rejected non-zero with valid JSON |
| Approval records | PASS - persisted records contain `token_hash`, no raw `approval_token` field |

## Observation Artifacts

| Artifact | Result |
| --- | --- |
| `00_observation_manifest.json` | PASS - N+5.0B contract fields present |
| `01_ui_tars_static_context.md` | PASS |
| `02_observation_report.md` | PASS |
| `03_observation.json` | PASS |
| `04_safety_review.md` | PASS |
| `05_human_next_steps.md` | PASS |
| `10_preview.html` | PASS |

## Dashboard / Endpoint Result

Expected endpoints verified in source, tests, and live smoke:

| Endpoint | Result |
| --- | --- |
| `GET /api/ui-tars-observation/status` | PASS |
| `POST /api/ui-tars-observation/create-approval` | PASS |
| `POST /api/ui-tars-observation/dry-run` | PASS |
| `POST /api/ui-tars-observation/capture-approved` | PASS - missing token rejected |
| `GET /api/ui-tars-observation/latest` | PASS |

Live dashboard smoke:

| Check | Result |
| --- | --- |
| Disposable server local port | `34436` |
| Server started and stopped | PASS |
| `GET /api/ui-tars-observation/status` | PASS - HTTP 200, valid JSON, `ok: true` |
| `POST /api/ui-tars-observation/create-approval` | PASS - HTTP 200, valid JSON |
| `POST /api/ui-tars-observation/dry-run` | PASS - HTTP 200, valid JSON, manifest contract fields present |
| `POST /api/ui-tars-observation/capture-approved` without token | PASS - JSON rejection, `ok: false` |
| `GET /api/ui-tars-observation/latest` | PASS - HTTP 200, valid JSON, no raw token |
| 500 / ReferenceError | PASS - none observed |
| Lingering dashboard process | PASS - none |

## Static Validation

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| `git show --check --stat HEAD` | PASS |
| `node --check 01_projects/dashboard_mvp/server.js` | PASS |
| `node --check 01_projects/dashboard_mvp/public/app.js` | PASS |
| Python AST for N+5.0B script, adapter, and tests | PASS |

## Test Totals

| Suite | Tests | Result |
| --- | ---: | --- |
| N+5.0A/N+5.0B UI-TARS observation adapter | 41 | PASS |
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
| Total | 370 | PASS |

## Runtime / Dashboard Checks

| Check | Result |
| --- | --- |
| `python 03_scripts/approved_adapter_runner.py --status --json` | PASS |
| `python 03_scripts/external_tool_sandbox_manager.py --status --json` | PASS |
| `python 03_scripts/ghoti_product_launcher.py --status --json` | PASS |
| `python 03_scripts/parallel_agent_relay.py --status --json` | PASS |
| `python 03_scripts/local_memory_compression_bridge.py --json` | PASS |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | PASS |
| `python 03_scripts/ghoti_readiness_check.py --status` | PASS - readiness score 100 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | PASS - score 100 |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | PASS |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | PASS on rerun |

Dashboard note:

The first `check_dashboard_mvp.ps1` run hit a transient transport interruption during `open_allowed_app` execution after many prior PASS checks. A clean rerun from no related process state exited 0 and ended with `Summary: dashboard MVP checks passed.`

## Safety Summary

| Safety requirement | Result |
| --- | --- |
| No UI-TARS runtime start | PASS |
| No external repo code execution | PASS |
| No installs | PASS |
| No desktop control | PASS |
| No click/type/hotkey | PASS |
| No live APIs/accounts/posting/money/trading | PASS |
| No `shell:true` in inspected N+5.0B runtime path | PASS |
| Capture-approved without token rejected | PASS |
| Non-dry-run requires token | PASS |
| GET endpoints do not leak raw tokens | PASS |
| Approval records store hashes only | PASS |
| Readiness remains 100 | PASS |
| No blocking validation process tied to audit worktree | PASS |

## Screenshot / Terminal Behavior

| Observation | Result |
| --- | --- |
| Blocking GUI popup | PASS - none observed |
| Weird duplicate clipboard command | PASS - none required |
| Blocking node/window process | PASS - disposable dashboard process stopped |
| Lingering validation process tied to audit worktree | PASS - none found |

## Final Verdict

CLEAN PASS

Exact next action:

Merge/accept N+5.0B as the contract fix for N+5.0A. The next milestone can proceed only if UI-TARS remains observation-only unless a separate audited milestone explicitly approves a new capability.
