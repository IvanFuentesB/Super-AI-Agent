# N+4.7B Main Merge Gate Report — One-Command Ghoti Product Launcher

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.7B — Main Merge Gate for the N+4.7A One-Command Product Launcher |
| Merge branch | merge/ghoti-agent-n4-7b-product-launcher-main |
| Merge worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_7b_main_merge_product_launcher |
| Starting main | 64759086b0ca7e63d0616753b998e32f07ce2e68 (N+4.6A merge gate) |
| Implementation branch | feat/ghoti-agent-claude-n4-7a-one-command-product-launcher-demo-smoke |
| Implementation commit | d5a218f67c5f2ffca8109be8d1b2b49b27d40338 |
| Codex audit branch | audit/ghoti-agent-codex-n4-7a-one-command-product-launcher-demo-smoke-real-audit |
| Codex audit commit | cc5a979772dd7446026316a01ddcb05c9c267dc8 |
| Codex verdict | CLEAN PASS |
| Merge commit | 0af13e0 |
| Report commit | (this report — see git log) |
| Remote main hash | (see Verify section) |

## Codex audit gate

All three refs were verified against the remote and matched the expected commits
exactly: `origin/main` = `64759086`, implementation = `d5a218f`, audit = `cc5a979`.
The Codex audit branch adds `codex_n4_7a_one_command_product_launcher_demo_smoke_real_audit.md`;
its **Final Verdict is CLEAN PASS** ("Claude can merge N+4.7A to main"). The gate
did not author its own audit — independent verification preserved.

## Merge

`git merge --no-ff origin/feat/ghoti-agent-claude-n4-7a-one-command-product-launcher-demo-smoke`
into a worktree branched from `origin/main` (64759086). Result: **clean automatic
merge**, no conflicts. Merge commit `0af13e0`. Lineage:

```
0af13e0 merge(ghoti): land N+4.7A one-command product launcher
d5a218f feat(ghoti): add one-command product launcher smoke
6475908 docs(ghoti): add N+4.6A main merge gate report   <- starting main
```

N+4.7A content merged (4 files, 975 insertions): `03_scripts/ghoti_product_launcher.py`,
the Ghoti Local Launcher Truth card in `index.html`, the `test_n4_7a` 25-test suite,
and the N+4.7A implementation report.

## Exact user command to open the dashboard

```
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
```

## Dashboard URL

`http://127.0.0.1:3210`

## Live launcher smoke result

```
--start-dashboard  ->  ok=True  pid=48472  url=http://127.0.0.1:3210  ready=True  opened_browser=False
--smoke            ->  ok=True  used_existing_dashboard=True  all_passed=True  no_500=True
--stop-dashboard   ->  ok=True  stopped=True  pid=48472  note="terminated recorded PID only"
```

`--start-dashboard` started the dashboard and printed the exact URL; no browser was
opened (the `--open-dashboard` flag was not passed). `--smoke` passed all 4 product
endpoints against the running dashboard. `--stop-dashboard` terminated only the
launcher-recorded PID.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `git show --check --stat HEAD` | clean — merge commit 0af13e0 |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `ghoti_product_launcher.py --status --json` | OK — dashboard_url http://127.0.0.1:3210 |
| `ghoti_product_launcher.py --json` (bare) | OK |
| `ghoti_product_launcher.py --smoke --json` | OK — all_passed=true |
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
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |
| `check_runtime_mvp.ps1` | PASS — exit 0 (serial rerun; see note) |

## check_runtime_mvp.ps1 result

**PASS** (exit 0, "runtime MVP checks passed"). The first run reported 2 failures in
the "Codex to ChatGPT handoff" desktop-recipe checks — caused by environmental
clipboard / foreground-window contention (the run's own `resource_guard_triggered`
log shows the safety guards correctly *blocked* input because the foreground window
and clipboard belonged to another process; `next_action` was "Reduce duplicate
windows or processes"). This is the known contention flakiness for shared-desktop
checks; the serial rerun is the terminal evidence and passed cleanly with zero
failures. N+4.7A does not touch handoff/clipboard/desktop code.

## check_dashboard_mvp.ps1 result

**PASS** (exit 0, "dashboard MVP checks passed"). No failures.

## Test totals

257/257 tests pass across 10 modules. N+4.7A contributes 25 tests (launcher status,
state-file repo-locality, fixed-argv / no-shell safety, smoke endpoint list,
open-dashboard-off-by-default, stop-dashboard-targets-recorded-PID, dashboard labels).

## Safety summary

| Safety property | Status |
|-----------------|--------|
| Codex independent audit obtained | PASS — CLEAN PASS, commit cc5a979 |
| Launcher starts dashboard + prints URL | PASS — http://127.0.0.1:3210 |
| Smoke passes product endpoints | PASS — all 4, no 500s |
| stop-dashboard terminates only the recorded PID | PASS — no broad kill |
| Browser opened only when --open-dashboard passed | PASS — opened_browser=false without the flag |
| No `shell=True` / `shell:true` | PASS — fixed argv, shell=False |
| No external API / live account / posting / money / trading | PASS |
| No autonomous Claude/Codex launch | PASS |
| No secrets | PASS |
| Dirty primary worktree untouched | PASS — read-only |
| Approval gates intact | PASS — readiness safety_gates PASS |
| N+3 readiness score | 100 (9/9 categories) |

## Verdict

**MERGED_AND_PUSHED** — Codex audit CLEAN PASS verified (`cc5a979`); N+4.7A
implementation commit `d5a218f` merged clean; the launcher starts the dashboard and
prints the URL; live launcher smoke passes (start → smoke → stop, recorded-PID only,
no browser auto-open); `check_dashboard_mvp.ps1` PASS; `check_runtime_mvp.ps1` PASS
(serial rerun, terminal evidence); 257/257 regression tests pass; readiness 100; all
safety gates intact. N+4.7A lands the one-command product launcher on `main`.
