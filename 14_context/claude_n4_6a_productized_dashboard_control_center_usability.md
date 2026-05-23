# N+4.6A — Productized Dashboard Control Center Usability Pass

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.6A — Productized Dashboard Control Center Usability Pass |
| Branch | feat/ghoti-agent-claude-n4-6a-productized-dashboard-control-center-usability |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_6a_productized_dashboard_control_center_usability |
| Base main | 3848c2664e6aed5e0a259d82f74135b3a072a8a7 |

## Files changed

| File | Change |
|------|--------|
| `01_projects/dashboard_mvp/server.js` | +4 `/api/product-control/*` endpoints (status, run-content-studio-demo, create-relay-pair, latest) |
| `01_projects/dashboard_mvp/public/index.html` | +`section-product-control` (Ghoti Product Control Center) + sidebar nav link |
| `01_projects/dashboard_mvp/public/app.js` | +`attachProductControlCenter` IIFE (client-side handlers) |
| `01_projects/runtime_mvp/tests/test_n4_6a_productized_dashboard_control_center_usability.py` | NEW — 33-test suite |
| `14_context/claude_n4_6a_productized_dashboard_control_center_usability.md` | NEW — this report |

No production code outside the dashboard was changed. No external tools were wired.

## Product UX summary

N+4.6A adds a **Ghoti Product Control Center** — a usability/product layer so a
user can open the dashboard and immediately understand what Ghoti can do and run
safe local demos. It is the 2nd section (right after Overview) and has a sidebar
nav entry, so it is the first functional surface a user reaches.

The section answers the six product questions directly:
1. **What Ghoti can do now** — a live capability list from `/api/product-control/status`.
2. **How to run a local content studio demo** — one button (safe dry-run).
3. **How to run desktop operator dry-run / recipe workflows** — labelled pointers
   to the existing Desktop Operator Action Center and Recipe Runner.
4. **How to generate paired Claude + Codex prompts** — one button (copy-paste only).
5. **Where the latest outputs/previews are** — a Latest Outputs card.
6. **What is planning-only / approval-gated** — a Safety & Scope card.

## Dashboard sections added

`section-product-control` contains four cards:
- **What Ghoti Can Do Now** — live capability list (6 capabilities) from the status endpoint.
- **Run & Generate** — buttons: Refresh Product Status, Run Local Content Studio,
  Generate Claude + Codex Prompt Pair, Open Latest Preview; plus labelled pointers
  to Desktop Operator Safe Dry Run, Recipe Runner, Local Memory Compression.
- **Latest Outputs** — Latest Content Studio Run, Latest Agent Relay Pair, Latest
  Desktop Operator Run, Latest generated preview (all repo-local paths).
- **Safety & Scope** — Approval Gates Required, Local Only, No Live Posting, No Live
  Account Actions, External Tools Planning Only.

All 16 required visible labels are present (verified by `test_all_required_labels_present`).

## Endpoints added

| Endpoint | Method | Behaviour |
|----------|--------|-----------|
| `/api/product-control/status` | GET | Capability + safety summary JSON. No subprocess. |
| `/api/product-control/run-content-studio-demo` | POST | Runs `supervised_content_mvp_runner.py --run --dry-run` via `runCommand` (fixed argv, `shell:false`, 60s timeout). Always HTTP 200 — works or truthfully reports unavailable, never 500. |
| `/api/product-control/create-relay-pair` | POST | Runs `parallel_agent_relay.py --create-pair` via `runCommand` (fixed argv, `shell:false`, 30s timeout). Body fields default to safe demo values; `codex_effort` whitelisted. |
| `/api/product-control/latest` | GET | Newest content studio run, relay pair, desktop operator run, preview path. Every path validated with the N+4.4D `isPathInsideRepo` containment helper; repo-relative POSIX output only. |

Reuse of existing safe helpers: `resolvePython()`, `runCommand()` (`shell:false`),
`readJsonBody()`, `isPathInsideRepo()` (N+4.4D), `loadDesktopOperatorLatest()`,
`sendJson()`. No new risky logic, no `child_process` use, no `shell:true`.

## Live smoke result

Real dashboard Node server spawned; all 4 product-control endpoints hit live:

```
[status]       HTTP 200  ok=True  local_only=True  external_tools=planning_only  capabilities=6
[create-pair]  HTTP 200  ok=True  pair_dir=14_context/agent_relay/pairs/20260517T132242Z_ghoti_product_control_center_demo
[content-demo] HTTP 200  ok=True  mode=dry_run  live_posting=False
[latest]       HTTP 200  ok=True  content_studio + relay_pair paths repo-local
[ref-errors]   0 occurrences of "method is not defined" / "pathname is not defined"
[no-500]       all endpoints returned 200
```

No 500s. No runtime ReferenceError. No path escape. No `shell:true`.

## Latest preview / relay output result

`/api/product-control/latest` returned (all repo-relative, containment-verified):
- content_studio_run: `14_context/content_workflows/runs/20260507T091135Z_ai_tools_for_students_and_crea`
- relay_pair: `14_context/agent_relay/pairs/20260517T132242Z_ghoti_product_control_center_demo`
- desktop_operator_run / preview_path: null when no desktop operator run has been
  recorded — surfaced truthfully, never a fabricated or out-of-repo path.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean — no whitespace errors |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `test_n4_6a_productized_dashboard_control_center_usability` | OK — 33/33 (incl. 6 live endpoint tests) |
| `test_n4_5a_parallel_agent_relay_command_center` | OK — 68/68 |
| `test_n4_4d_preview_path_containment_fix` | OK — 18/18 |
| `test_n4_4c_desktop_operator_recipe_runner_preview_polish` | OK — 16/16 |
| `test_n4_4b_desktop_operator_dashboard_action_center` | OK — 17/17 |
| `test_n4_4a_desktop_operator_control_plane` | OK — 20/20 |
| `test_n4_3a_supervised_content_studio_demo` | OK — 15/15 |
| `test_n4_2a_local_memory_intake` | OK — 26/26 |
| `test_n4_1_runtime_reliability` | OK — 19/19 (PYTHONPATH=src) |
| **Test total** | **232/232 pass** |
| `parallel_agent_relay.py --status --json` | OK — relay_mode=copy_paste_only |
| `local_memory_compression_bridge.py --json` | OK — local_only=true |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — all validation checks passed |
| `check_runtime_mvp.ps1` | PASS — exit 0, "runtime MVP checks passed" |
| `check_dashboard_mvp.ps1` | PASS — exit 0, "dashboard MVP checks passed" |

## Safety table

| Safety property | Status |
|-----------------|--------|
| `shell:true` in product section | NONE |
| Arbitrary command execution | NONE — `runCommand(py.command, fixedArgv)` only, no `child_process`, no `execSync` |
| Subprocess timeouts | present — 60s (content studio), 30s (relay) |
| Content studio runs dry-run only | YES — `--run --dry-run`, never `--apply` |
| Path containment | N+4.4D `isPathInsideRepo` reused for `/latest` paths |
| External API | NONE |
| Live account / posting / money actions | NONE |
| Autonomous Claude/Codex launch | NONE — relay create-pair is copy-paste only |
| External tools wired | NO — planning-only intake |
| Open Latest Preview auto-opens browser | NO — surfaces local path only |
| Approval gates | intact — readiness safety_gates PASS |
| N+4.5 relay routes intact | YES — regression test confirms request.method/requestUrl.pathname |
| N+4.4D containment intact | YES — `isPathInsideRepo` present, no `startsWith(repoRoot)` |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Can the user see what Ghoti can do now from the dashboard?** YES — the
   Product Control Center's "What Ghoti Can Do Now" card lists 6 live capabilities
   with how-to-run guidance, second section from the top, in the sidebar nav.
2. **Can the user run/generate a local demo from the dashboard?** YES — "Run Local
   Content Studio" button runs a safe dry-run; result is shown inline.
3. **Can the user generate Claude + Codex prompt pairs from the dashboard?** YES —
   "Generate Claude + Codex Prompt Pair" button calls
   `/api/product-control/create-relay-pair`; an 8-file pair is produced.
4. **Does this launch external tools automatically?** NO — external tool intake is
   planning-only; nothing is cloned, installed, or run.
5. **Does this use live APIs/accounts?** NO — local only; no external API, no live
   account/posting/money actions; content studio is dry-run.
6. **Are approval gates intact?** YES — every risky/outbound action stays
   approval-gated; readiness `safety_gates` category passes; no gate weakened.
7. **Is this full production 100%?** NO — supervised MVP slice / usability layer.
   `supervised_mvp_slice_score` is 100, but `production_public_release_ready` is
   false and `production_autonomy_score` is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+4.6A adds the Ghoti Product Control Center: a
dashboard section + 4 safe local endpoints + client handlers that make Ghoti's
local capabilities discoverable and runnable in one place. 232/232 tests pass;
both PowerShell checks PASS; live smoke clean (no 500s, no ReferenceError, no path
escape); readiness 100; all safety gates intact. `main` was not pushed.
