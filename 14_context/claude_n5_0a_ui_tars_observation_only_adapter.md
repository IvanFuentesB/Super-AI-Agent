# N+5.0A — UI-TARS Observation-Only Adapter

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+5.0A — UI-TARS Observation-Only Adapter |
| Branch | feat/ghoti-agent-claude-n5-0a-ui-tars-observation-only-adapter |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n5_0a_ui_tars_observation_only_adapter |
| Base main | f863dc522d8a28b6265714daafa19a6ad5238fd7 |

## Files changed

| File | Change |
|------|--------|
| `02_automation/external_tool_adapters/ui_tars_observation_adapter.py` | NEW — observation-only adapter module |
| `03_scripts/ui_tars_observation_adapter.py` | NEW — observation adapter CLI |
| `01_projects/dashboard_mvp/server.js` | +5 `/api/ui-tars-observation/*` endpoints |
| `01_projects/dashboard_mvp/public/index.html` | +`ui-tars-observation-truth` dashboard card |
| `01_projects/dashboard_mvp/public/app.js` | +`attachUiTarsObservation` handlers |
| `01_projects/runtime_mvp/tests/test_n5_0a_*.py` | NEW — 37-test suite |
| `14_context/ui_tars_observation/runs/20260518T102053Z_ui_tars_observation/` | NEW — canonical dry-run observation packet (7 artifacts) |
| `14_context/claude_n5_0a_*.md` | NEW — this report |

Runtime-generated content under `14_context/ui_tars_observation/` (extra run
folders, `approvals/`, `latest.json`) is not committed; one canonical dry-run
observation packet is committed as milestone evidence.

## What this milestone delivers

N+5.0A adds the **first UI-TARS-related adapter** — strictly **observation-only**.
It produces a local "observation packet" describing the UI-TARS context. It is
explicitly **NOT** desktop control, **NOT** UI-TARS runtime execution, and **NOT**
click/type.

- `ui_tars_observation_adapter.py` (adapter module) — `status()`,
  `capabilities()`, `safety_gates()`, `create_observation_packet(...)`. Reads
  static metadata from the sandboxed UI-TARS repos (never runs them). The only
  optional desktop interaction is a single read-only screen capture, gated
  behind an approval token, implemented with built-in Windows PowerShell/.NET
  (no external screenshot library), and it degrades truthfully if unavailable.
- `ui_tars_observation_adapter.py` (CLI) — `--status`, `--json`,
  `--create-approval`, `--observe`, `--dry-run`, `--capture-screen`,
  `--approval-token`, `--output-dir`, `--latest`. Dry-run needs no token and
  never captures; a screen capture or non-dry-run observation requires a
  verified token (`--create-approval` issues one; only its SHA-256 hash is
  stored).

## Observation run folder

Canonical committed run:
`14_context/ui_tars_observation/runs/20260518T102053Z_ui_tars_observation/`

## Artifacts created (7)

`00_observation_manifest.json`, `01_ui_tars_static_context.md`,
`02_observation_report.md`, `03_observation.json`, `04_safety_review.md`,
`05_human_next_steps.md`, `10_preview.html`. (Optional `screen_capture.png` is
written only on an approved, successful capture — not part of the committed
dry-run packet.)

## Screenshot result — captured / degraded

The canonical committed run is a **dry-run** — `screenshot_captured: false` (a
dry run never captures the screen). The approval-gated capture path is
implemented (built-in PowerShell/.NET, read-only) and exercised by the test
suite with a valid token; the adapter reports `screenshot_captured` truthfully
and, when it does not capture, records a `screenshot_skipped_reason`. The
milestone never depends on a successful capture.

## Dashboard result

New **UI-TARS Observation Truth** card in the Product Control Center section.
All 14 required labels present: UI-TARS Observation Only, Observation Packet,
Dry Run Observation, Screenshot Capture Requires Approval, No Click, No Type,
No Hotkeys, No Desktop Control Yet, No UI-TARS Runtime Yet, No External Repo
Code Execution, No Installs, Local Artifacts Only, Human Approval Required,
Latest Observation Run. Three buttons: refresh, create-approval, dry-run — the
dashboard never exposes a capture button (capture stays CLI + token only).

## Endpoint smoke result

Real dashboard Node server spawned; all 5 ui-tars-observation endpoints hit live:

```
[status]           HTTP 200  ok=True  desktop_control_enabled=False
[create-approval]  HTTP 200  ok=True
[dry-run]          HTTP 200  ok=True  mode=dry_run  screenshot_captured=False  7 artifacts
[capture-approved] HTTP 200  ok=False  (rejected — no token in body)
[latest]           HTTP 200  ok=True  approval_token NOT present in GET body
```

No 500s. The raw approval token is never returned by a GET endpoint.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `ui_tars_observation_adapter.py --status / --json / --latest` | OK |
| `ui_tars_observation_adapter.py --create-approval --json` | OK — hash-only record |
| `ui_tars_observation_adapter.py --observe --dry-run --json` | OK — 7 artifacts, no capture |
| `test_n5_0a_ui_tars_observation_only_adapter` | OK — 37/37 |
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
| **Test total** | **366/366 pass** |
| `approved_adapter_runner.py --status --json` | OK |
| `external_tool_sandbox_manager.py --status --json` | OK |
| `ghoti_product_launcher.py --status --json` | OK |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Test totals

366/366 tests pass across 13 modules. N+5.0A contributes 37 tests (CLI status,
approval + gating, dry-run artifacts, manifest safety flags, capture
truthful-degrade, adapter interface + stdlib-only + no-UI-TARS-imports +
no-desktop-control-libs, dashboard labels, server endpoints, live endpoints,
token non-leak).

## Runtime / dashboard check result

`check_runtime_mvp.ps1`: **PASS** (exit 0). `check_dashboard_mvp.ps1`: **PASS**
(exit 0). Both first-run clean.

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
| Path containment for output dirs | enforced repo-local |
| Secrets / API keys | NONE |
| Dirty primary worktree | untouched (read-only) |
| Approval gates intact | YES — readiness safety_gates PASS |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Did Ghoti run UI-TARS?** NO — UI-TARS was never started or imported.
2. **Did Ghoti install anything?** NO — no npm / pnpm / pip install.
3. **Did Ghoti execute external repo code?** NO — only Ghoti-owned adapter code
   ran; the sandboxed UI-TARS repos were read statically, never run.
4. **Did Ghoti control / click / type the desktop?** NO — observation-only;
   no click, type, hotkeys, or mouse actions; no desktop-control libraries.
5. **Did Ghoti create an observation packet?** YES — a 7-artifact local
   observation packet under `14_context/ui_tars_observation/runs/`.
6. **Can the user approve screenshot capture later?** YES — `--create-approval`
   issues a one-time token; `--observe --capture-screen --approval-token <token>`
   then performs a read-only, local-only capture.
7. **Are approval gates intact?** YES — capture and any non-dry-run observation
   require a verified token; the dashboard triggers dry-run only; readiness
   `safety_gates` passes.
8. **Is this full production 100%?** NO — this is observation-only, the first
   safe UI-TARS step. `supervised_mvp_slice_score` is 100, but
   `production_public_release_ready` is false and `production_autonomy_score`
   is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+5.0A adds the UI-TARS observation-only adapter: a
CLI + adapter module that produce a local 7-artifact observation packet, with an
approval-token-gated read-only screen-capture path that degrades truthfully.
366/366 tests pass; both PowerShell checks PASS; live endpoint smoke clean;
readiness 100. No UI-TARS runtime, no external repo code, no installs, no desktop
control, no click/type — all approval gates intact. `main` was not pushed.
