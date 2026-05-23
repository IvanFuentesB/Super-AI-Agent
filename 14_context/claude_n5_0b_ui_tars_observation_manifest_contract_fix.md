# N+5.0B — UI-TARS Observation Manifest Contract Fix

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+5.0B — UI-TARS Observation Manifest Contract Fix |
| Branch | feat/ghoti-agent-claude-n5-0b-ui-tars-observation-manifest-contract-fix |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n5_0b_ui_tars_observation_manifest_contract_fix |
| Base main | f863dc522d8a28b6265714daafa19a6ad5238fd7 |
| Merge of N+5.0A | 1fc9c05 (merge of feat N+5.0A 62fd1e6 into the N+5.0B branch) |
| Blocked base branch | origin/feat/ghoti-agent-claude-n5-0a-ui-tars-observation-only-adapter |
| Blocked base commit | 62fd1e6deb30b1a1d440d14691cf51abfdb6013a |
| Codex audit branch | origin/audit/ghoti-agent-codex-n5-0a-ui-tars-observation-only-adapter-real-audit |
| Codex audit commit | 68937cc7bdb6f2d273a2c6e77348a7b1cbde7cf4 |

## Blocked audit summary

The Codex real audit of N+5.0A returned **BLOCKED_VALIDATION**. N+5.0A delivered a
working UI-TARS observation-only adapter — the dry-run produced all 7 artifacts,
the 5 dashboard endpoints worked, the 37-test suite passed, and the safety scan
passed — but the observation **manifest contract** was incomplete.

Codex finding (verbatim from the audit report):

- `00_observation_manifest.json` — BLOCKED: missing required `local_only`,
  `click_enabled`, and `type_enabled` fields.
- `03_observation.json` — PASS: includes `local_only: true`, `click_enabled:
  false`, `type_enabled: false`.
- "They are present in `03_observation.json`, but not in
  `00_observation_manifest.json`."
- The gap reproduced across all three manifest sources: committed seed manifest,
  CLI dry-run manifest, and dashboard endpoint dry-run manifest.
- "The 37 N+5.0A tests pass, but they do not catch the missing
  `00_observation_manifest.json` contract fields."

## Exact blocker reproduced

The blocked N+5.0A commit's committed manifest was inspected directly:

`git show 62fd1e6:14_context/ui_tars_observation/runs/20260518T102053Z_ui_tars_observation/00_observation_manifest.json`

```
{
  "adapter": "ui_tars_observation_only",
  "mode": "dry_run",
  "dry_run": true,
  "capture_requested": false,
  "screenshot_captured": false,
  "external_repo_code_executed": false,
  "installs_performed": false,
  "ui_tars_runtime_started": false,
  "desktop_control_enabled": false,
  "live_api_used": false,
  "generated_at": "20260518T102053Z"
}
```

Confirmed: `local_only`, `click_enabled`, `type_enabled` are **absent**. The same
N+5.0A run's `03_observation.json` did contain all three. Blocker reproduced
exactly as Codex described.

## Root cause

`create_observation_packet(...)` in
`02_automation/external_tool_adapters/ui_tars_observation_adapter.py` built two
separate JSON payloads — one for `03_observation.json` (which included the three
contract fields) and one for `00_observation_manifest.json` (which omitted them).
The manifest dict literal simply did not list `local_only` / `click_enabled` /
`type_enabled`.

## The fix

Single-file, surgical. The `00_observation_manifest.json` dict in
`create_observation_packet(...)` now includes the three required contract fields,
alongside the safety flags that were already present:

```python
# 00 manifest — full observation manifest contract (N+5.0B):
# local_only / click_enabled / type_enabled are required contract fields.
_write(output_dir / "00_observation_manifest.json", json.dumps({
    "adapter": ADAPTER_KEY,
    "mode": mode,
    "dry_run": bool(dry_run),
    "local_only": True,
    "capture_requested": bool(capture_screen),
    "screenshot_captured": capture["screenshot_captured"],
    "external_repo_code_executed": False,
    "installs_performed": False,
    "ui_tars_runtime_started": False,
    "desktop_control_enabled": False,
    "click_enabled": False,
    "type_enabled": False,
    "live_api_used": False,
    "generated_at": ts,
}, indent=2))
```

Manifest generation is **not duplicated** — `create_observation_packet(...)` is
the single producer of `00_observation_manifest.json`; the CLI
(`03_scripts/ui_tars_observation_adapter.py`) and the dashboard endpoints both
call it. Fixing this one dict fixes the CLI, the endpoints, and the seed run.

## Files changed

| File | Change |
|------|--------|
| `02_automation/external_tool_adapters/ui_tars_observation_adapter.py` | MODIFIED — `00_observation_manifest.json` now includes `local_only`/`click_enabled`/`type_enabled` |
| `01_projects/runtime_mvp/tests/test_n5_0a_ui_tars_observation_only_adapter.py` | MODIFIED — +4 tests covering the manifest contract (CLI, endpoint, every-run) |
| `14_context/ui_tars_observation/runs/20260518T102053Z_ui_tars_observation/` | REMOVED — stale broken N+5.0A seed run (7 files) |
| `14_context/ui_tars_observation/runs/20260518T104524Z_ui_tars_observation/` | NEW — regenerated canonical seed run with the fixed manifest (7 files) |
| `14_context/claude_n5_0b_ui_tars_observation_manifest_contract_fix.md` | NEW — this report |

Runtime-generated content under `14_context/ui_tars_observation/` (extra run
folders from validation, `approvals/`, `latest.json`) is not committed; one
canonical seed observation packet is committed as milestone evidence.

## Manifest fields fixed

Added to every generated `00_observation_manifest.json`:

```
local_only:    true
click_enabled: false
type_enabled:  false
```

Preserved and verified (already present in N+5.0A, kept intact):

```
external_repo_code_executed: false
installs_performed:          false
ui_tars_runtime_started:     false
desktop_control_enabled:     false
live_api_used:               false
```

## New seed run path

`14_context/ui_tars_observation/runs/20260518T104524Z_ui_tars_observation/`

7 artifacts: `00_observation_manifest.json`, `01_ui_tars_static_context.md`,
`02_observation_report.md`, `03_observation.json`, `04_safety_review.md`,
`05_human_next_steps.md`, `10_preview.html`. The stale broken N+5.0A seed run
`20260518T102053Z_ui_tars_observation` was removed (`git rm -r`) so no broken
manifest remains in the tree.

## Manifest field verification table

All three manifest sources inspected directly after the fix. Seed =
committed `20260518T104524Z`; CLI dry-run = `20260518T133407Z`; endpoint
dry-run = `20260518T134117Z`.

| Required field | Expected | Seed run | CLI dry-run | Endpoint dry-run |
|----------------|----------|----------|-------------|------------------|
| `local_only` | `true` | true | true | true |
| `click_enabled` | `false` | false | false | false |
| `type_enabled` | `false` | false | false | false |
| `external_repo_code_executed` | `false` | false | false | false |
| `installs_performed` | `false` | false | false | false |
| `ui_tars_runtime_started` | `false` | false | false | false |
| `desktop_control_enabled` | `false` | false | false | false |
| `live_api_used` | `false` | false | false | false |

All 8 fields present and correct in all 3 manifest sources.

## Test fix

`test_n5_0a_ui_tars_observation_only_adapter.py` strengthened with 4 new tests
so the contract gap cannot regress (N+5.0A had 37 tests, now 41):

- `TestDryRunArtifacts.test_manifest_includes_contract_fields` — CLI dry-run
  manifest must contain `local_only=true`, `click_enabled=false`,
  `type_enabled=false`.
- `TestLiveEndpoints.test_dry_run_endpoint_manifest_has_contract_fields` —
  the dashboard endpoint dry-run manifest must satisfy the same contract.
- `TestAllRunManifestsContract.test_at_least_one_manifest_present` — at least
  one observation run manifest exists on disk.
- `TestAllRunManifestsContract.test_every_manifest_satisfies_contract` — **every**
  `runs/*/00_observation_manifest.json` on disk (including the committed seed
  run) must have `local_only` true and `click_enabled`, `type_enabled`,
  `external_repo_code_executed`, `installs_performed`, `ui_tars_runtime_started`,
  `desktop_control_enabled`, `live_api_used` all present and false.

These cover all three required surfaces: CLI dry-run manifest, endpoint dry-run
manifest, and committed seed run manifest. Reverting the adapter fix makes all
four fail.

## Test totals

370/370 tests pass across 13 modules (real `python -m unittest` output):

| Module | Result |
|--------|--------|
| `test_n5_0a_ui_tars_observation_only_adapter` | OK — 41/41 |
| `test_n4_9a_first_approved_adapter_execution_demo` | OK — 37/37 |
| `test_n4_8a_external_tool_sandbox_adapter_discovery` | OK — 35/35 |
| `test_n4_7a_one_command_product_launcher_demo_smoke` | OK — 25/25 |
| `test_n4_6a_productized_dashboard_control_center_usability` | OK — 33/33 |
| `test_n4_5a_parallel_agent_relay_command_center` | OK — 68/68 |
| `test_n4_4d_preview_path_containment_fix` | OK — 18/18 |
| `test_n4_4c_desktop_operator_recipe_runner_preview_polish` | OK — 16/16 |
| `test_n4_4b_desktop_operator_dashboard_action_center` | OK — 17/17 |
| `test_n4_4a_desktop_operator_control_plane` | OK — 20/20 |
| `test_n4_3a_supervised_content_studio_demo` | OK — 15/15 |
| `test_n4_2a_local_memory_intake` | OK — 26/26 |
| `test_n4_1_runtime_reliability` | OK — 19/19 (PYTHONPATH=src) |
| **Total** | **370/370 pass** |

N+5.0B adds 4 net-new tests to the N+5.0A suite (366 → 370 overall).

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `git show --check --stat HEAD` | clean — no whitespace errors |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `ui_tars_observation_adapter.py --status --json` | OK — ok=true |
| `ui_tars_observation_adapter.py --json` | OK — ok=true |
| `ui_tars_observation_adapter.py --create-approval --json` | OK — hash-only record |
| `ui_tars_observation_adapter.py --observe --dry-run --json` | OK — 7 artifacts, no capture |
| `ui_tars_observation_adapter.py --latest --json` | OK |
| latest manifest field assertions (8 fields) | OK — all 8 PASS |
| `approved_adapter_runner.py --status --json` | OK — ok=true |
| `external_tool_sandbox_manager.py --status --json` | OK — ok=true |
| `ghoti_product_launcher.py --status --json` | OK — ok=true |
| `parallel_agent_relay.py --status --json` | OK — relay_version 1.0.0 |
| `local_memory_compression_bridge.py --json` | OK — local_only true, external_api_used false |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — all validation checks passed |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Runtime / dashboard check result

`check_runtime_mvp.ps1`: **PASS** (exit 0). `check_dashboard_mvp.ps1`: **PASS**
(exit 0). Both first-run clean.

## Live endpoint result

Real dashboard Node server spawned (port 3399, `/api/health` readiness poll);
all 5 ui-tars-observation endpoints hit live:

```
[GET  status]            HTTP 200  ok=True
[POST create-approval]   HTTP 200  ok=True
[POST dry-run]           HTTP 200  ok=True  mode=dry_run  screenshot_captured=False
[endpoint manifest]      20260518T134117Z  contract=PASS (all 8 fields)
[POST capture-approved]  HTTP 200  ok=False  rejected_without_token=True
[GET  latest]            HTTP 200  ok=True  raw_token_in_body=False
SAW_500=False
```

No 500s. The endpoint-generated dry-run manifest includes `local_only`,
`click_enabled`, `type_enabled` (contract PASS). `capture-approved` without a
token is rejected. The raw approval token is never returned by a GET endpoint.

## Safety summary

| Safety property | Status |
|-----------------|--------|
| UI-TARS runtime started | NO |
| UI-TARS / external repo packages imported | NO |
| External repo code executed | NO |
| Dependencies installed | NO |
| Desktop control enabled | NO |
| Click / type / hotkeys | NO — no desktop-control libraries used |
| Live API / account / posting / money | NO |
| Screen capture | approval-token-gated; dry-run never captures; built-in PowerShell/.NET only |
| Raw approval token exposed by a GET endpoint | NO — POST-only, only the hash persisted |
| `shell=True` / `shell:true` | NONE |
| Approval gates intact | YES — unchanged; capture + non-dry-run still require a verified token |
| Path containment for output dirs | enforced repo-local |
| Secrets / API keys | NONE |
| Dirty primary worktree | untouched (read-only inspection only) |
| Scope | manifest contract fix + tests + seed regen only — no broad refactor |
| `main` pushed | NO |
| N+3 readiness score | 100 (9/9 categories, safety_gates PASS) |

## Direct answers

1. **Does manifest now include `local_only`?** YES — `local_only: true` in every
   generated `00_observation_manifest.json` (seed, CLI, endpoint all verified).
2. **Does manifest now include `click_enabled=false`?** YES — verified in seed,
   CLI dry-run, and endpoint dry-run manifests.
3. **Does manifest now include `type_enabled=false`?** YES — verified in seed,
   CLI dry-run, and endpoint dry-run manifests.
4. **Did Ghoti run UI-TARS?** NO — UI-TARS was never started or imported.
5. **Did Ghoti install anything?** NO — no npm / pnpm / pip install.
6. **Did Ghoti execute external repo code?** NO — only Ghoti-owned adapter code
   ran; the sandboxed UI-TARS repos were not run.
7. **Did Ghoti control / click / type the desktop?** NO — observation-only; no
   click, type, hotkeys, or mouse actions; no desktop-control libraries.
8. **Are approval gates intact?** YES — the approval-token model is unchanged;
   capture and any non-dry-run observation still require a verified token; the
   dashboard triggers dry-run only; readiness `safety_gates` passes.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+5.0B completes the UI-TARS observation manifest
contract: `00_observation_manifest.json` now carries `local_only`,
`click_enabled`, and `type_enabled` alongside the five preserved safety flags.
The stale broken N+5.0A seed run was removed and a fixed canonical seed run
regenerated. 4 new tests lock the contract across the CLI, endpoint, and every
on-disk run manifest so the gap cannot regress. 370/370 tests pass; both
PowerShell checks PASS; the live endpoint smoke is clean (no 500s, no token
leak, capture-without-token rejected); readiness 100. No UI-TARS runtime, no
external repo code, no installs, no desktop control, no click/type — all
approval gates intact. `main` was not pushed.
