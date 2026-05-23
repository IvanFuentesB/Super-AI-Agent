# N+4.7A — One-Command Ghoti Product Launcher + Local Demo Smoke

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.7A — One-Command Ghoti Product Launcher + Local Demo Smoke |
| Branch | feat/ghoti-agent-claude-n4-7a-one-command-product-launcher-demo-smoke |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_7a_one_command_product_launcher_demo_smoke |
| Base main | 64759086b0ca7e63d0616753b998e32f07ce2e68 |

## Files changed

| File | Change |
|------|--------|
| `03_scripts/ghoti_product_launcher.py` | NEW — one-command launcher CLI (status, start, stop, smoke) |
| `01_projects/dashboard_mvp/public/index.html` | +`ghoti-local-launcher-truth` card in the Product Control Center section |
| `01_projects/runtime_mvp/tests/test_n4_7a_one_command_product_launcher_demo_smoke.py` | NEW — 25-test suite |
| `14_context/claude_n4_7a_one_command_product_launcher_demo_smoke.md` | NEW — this report |

`server.js` and `app.js` were not changed — the launcher is a standalone CLI and
the dashboard card is static. The launcher state file
`01_projects/dashboard_mvp/runtime_data/ghoti_product_launcher_state.json` is a
runtime artifact and is not committed.

## Product UX summary

N+4.7A makes Ghoti easy to open and test like a real local product. A single CLI
— `03_scripts/ghoti_product_launcher.py` — starts the dashboard, prints the exact
URL, optionally opens the browser, runs a product smoke test, can include a local
demo prompt-pair smoke, stops only the process it started, and (`--status`)
explains what Ghoti can do now.

### Exact user command to open the dashboard

```
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
```

- `--start-dashboard` alone starts the dashboard and prints `Dashboard URL: http://127.0.0.1:3210`.
- Add `--open-dashboard` to also open that localhost URL in the browser.
- `python 03_scripts/ghoti_product_launcher.py --status` explains what Ghoti can do.

## Launcher CLI

| Mode / flag | Behaviour |
|-------------|-----------|
| `--status` | Launcher + dashboard status; lists smoke endpoints and what Ghoti can do |
| `--json` | Emit JSON (bare `--json` == `--status --json`) |
| `--start-dashboard` | Start `node server.js` (fixed argv, `shell=False`), wait for readiness, record PID, print the URL |
| `--stop-dashboard` | Terminate only the launcher-recorded PID (and its tree); clear state |
| `--smoke` | Product smoke test of the 4 `/api/product-control/*` endpoints; smokes a running dashboard or starts/stops a temporary one |
| `--open-dashboard` | Optional — open the localhost dashboard in a browser (only when explicitly passed) |
| `--run-demo-smoke` | Optional — include a local demo prompt-pair smoke in the result |
| `--port` | Dashboard port (default 3210) |
| `--timeout-seconds` | Readiness / request timeout (default 25) |

PID tracking: `01_projects/dashboard_mvp/runtime_data/ghoti_product_launcher_state.json`
(repo-local, containment-enforced by `_is_repo_local` in `_write_state`).

## Dashboard card

New **Ghoti Local Launcher Truth** card added to the N+4.6A Product Control Center
section. All 11 required visible labels present: One-Command Launcher, Dashboard
URL, Start Dashboard, Stop Dashboard, Product Smoke Test, Open Dashboard Optional,
Localhost Only, No External API, No Live Account Actions, Safe PID Tracking, Run
Demo Smoke.

## Live launcher smoke result

```
--start-dashboard  ->  ok=True  pid=27512  port=3210  url=http://127.0.0.1:3210  ready=True
--smoke            ->  ok=True  used_existing_dashboard=True  all_passed=True  no_500=True  no_ref_error=True
--stop-dashboard   ->  ok=True  stopped=True  pid=27512  note="terminated recorded PID only"
post-stop --status ->  dashboard_running=False
```

Standalone `--smoke --json` (no dashboard running) also passed — it started a
temporary dashboard on a free port, smoked all 4 endpoints (HTTP 200, passed),
and stopped only that temporary process.

Smoke endpoint detail (all HTTP 200, passed):
- `GET /api/product-control/status`
- `POST /api/product-control/create-relay-pair`
- `POST /api/product-control/run-content-studio-demo`
- `GET /api/product-control/latest`

No 500s. No `method is not defined` / `pathname is not defined`.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `ghoti_product_launcher.py --status --json` | OK — valid JSON, dashboard_url http://127.0.0.1:3210 |
| `ghoti_product_launcher.py --json` (bare) | OK — valid JSON |
| `ghoti_product_launcher.py --smoke --json` | OK — all_passed=true, no_500=true |
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
| **Test total** | **257/257 pass** |
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
| No `shell=True` in the launcher | PASS — `shell=False` explicit on every subprocess call |
| Fixed argv for node | PASS — `["node", "server.js"]` |
| `--open-dashboard` off by default | PASS — browser opens only when the flag is passed; localhost only |
| stop-dashboard targets only the recorded PID | PASS — reads `state.get("pid")`, kills only that; no `/IM` broad kill |
| Launcher state path repo-local | PASS — `runtime_data/ghoti_product_launcher_state.json`, `_is_repo_local` enforced |
| No path escape | PASS — containment helper enforced; no `..` traversal |
| No external API | PASS — smoke uses only `http://127.0.0.1` product-control endpoints; no `https://` |
| No live account / posting / money / trading actions | PASS |
| No external repo clone/install/run | PASS |
| No autonomous Claude/Codex launch | PASS — relay remains copy-paste only |
| No secrets / API keys | PASS |
| Port-already-in-use detected truthfully | PASS |
| Dirty primary worktree untouched | PASS — read-only |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Can the user open Ghoti with one command?** YES —
   `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
   starts the dashboard, prints `http://127.0.0.1:3210`, and opens the browser.
2. **Can the user smoke-test the product with one command?** YES —
   `--smoke` checks all 4 product-control endpoints; it works standalone (starts
   and stops its own temporary dashboard) or against a running one.
3. **Does the launcher stop only what it started?** YES — `--stop-dashboard`
   terminates only the launcher-recorded PID; it never broad-kills node.
4. **Does this open a browser automatically?** NO — only when `--open-dashboard`
   is explicitly passed, and only to a `http://127.0.0.1` URL.
5. **Does this use external APIs / live accounts?** NO — local only; no external
   API, no live account/posting/money actions.
6. **Are approval gates intact?** YES — the launcher only starts/stops the local
   dashboard and runs read/dry-run smoke calls; all existing approval gates and
   the readiness `safety_gates` category remain intact.
7. **Is this full production 100%?** NO — supervised MVP / local usability layer.
   `supervised_mvp_slice_score` is 100, but `production_public_release_ready` is
   false and `production_autonomy_score` is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+4.7A adds `ghoti_product_launcher.py`, a
one-command launcher that starts the dashboard, prints the exact URL, runs a
product smoke test, and stops only what it started. 257/257 tests pass; both
PowerShell checks PASS; live launcher smoke clean (start -> smoke -> stop, no
500s, no ReferenceError); readiness 100. Local-only, no live actions. `main` was
not pushed.
