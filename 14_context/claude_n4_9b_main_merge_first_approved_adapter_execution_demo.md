# N+4.9B Main Merge Gate Report — First Approved Adapter Execution Demo

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.9B — Main Merge Gate for N+4.9A First Approved Adapter Execution Demo |
| Merge branch | merge/ghoti-agent-n4-9b-first-approved-adapter-execution-main |
| Merge worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_9b_main_merge_first_approved_adapter_execution |
| Starting main | 9f29a275d386b926ec4e9f66878cbfaa251377e7 (N+4.8B merge gate) |
| Implementation branch | feat/ghoti-agent-claude-n4-9a-first-approved-adapter-execution-demo |
| Implementation commit | fd4833ea91e30b9cb8c15471601cbacb8b7b6024 |
| Codex audit branch | audit/ghoti-agent-codex-n4-9a-first-approved-adapter-execution-demo-real-audit |
| Codex audit commit | 468496042a65bad80510076c08b760d18e406e46 |
| Codex verdict | CLEAN PASS |
| Merge commit | ba4d27e |
| Report commit | (this report — see git log) |
| Remote main hash | (see Verify section) |

## Codex audit gate

All three refs were verified against the remote and matched the expected commits
exactly. The audit branch was inspected **by its explicit commit hash**
(`4684960`): it sits directly on top of `origin/main` (`9f29a27`), and contains
`14_context/codex_n4_9a_first_approved_adapter_execution_demo_real_audit.md`. Its
**Final Verdict is CLEAN PASS** — external_code_executed false, installs_performed
false, desktop_control_enabled false, no installs, no desktop control, approval
gates intact. The gate did not author its own audit.

## Merge

`git merge --no-ff origin/feat/ghoti-agent-claude-n4-9a-first-approved-adapter-execution-demo`
into a worktree branched from `origin/main` (9f29a27). Result: **clean automatic
merge**, no conflicts. Merge commit `ba4d27e`.

N+4.9A content merged: `03_scripts/approved_adapter_runner.py` (approval-gated
runner), the promoted `agent_skills_eval_adapter.py`, the
`external_tool_sandbox_manager.py` tweak that preserves a promoted adapter, the
loosened `test_n4_8a` import test, the Approved Adapter Execution Truth card + 5
endpoints, the `test_n4_9a` suite, and the canonical demo run folder.

## Adapter execution result

`approved_adapter_runner.py` works: `--status`, `--json`, `--list-adapters`,
`--create-approval`, and `--execute-approved --dry-run` all returned ok. The
`agent_skills_eval` dry-run demo produced an evaluation **score of 80/100
("adequate")** with real recommendations. Non-dry-run execution remains gated:
without an approval token it is refused; `--create-approval` issues a one-time
token (only its SHA-256 hash is persisted).

## Run folder / artifacts result

Canonical committed run: `14_context/adapter_execution/runs/20260518T085322Z_agent_skills_eval/`
— 6 artifacts: `00_demo_skill.md`, `01_skill_evaluation.md`,
`02_skill_evaluation.json`, `03_safety_review.md`, `04_execution_manifest.json`,
`05_human_next_steps.md`. The execution manifest records `external_code_executed`
false, `installs_performed` false, `desktop_control_enabled` false,
`live_api_used` false.

## Dashboard / endpoints result

Real dashboard Node server spawned; all 5 adapter-execution endpoints hit live:

```
[status]          HTTP 200  ok=True
[adapters]        HTTP 200  ok=True  (5 adapters)
[create-approval] HTTP 200  ok=True
[run-demo]        HTTP 200  ok=True  mode=dry_run  score=80
[latest]          HTTP 200  ok=True  approval_token NOT present in GET body
```

No 500s. No `method`/`pathname` ReferenceError. The raw approval token is never
exposed by a GET endpoint.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `git show --check --stat HEAD` | clean — merge commit ba4d27e |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `approved_adapter_runner.py --status / --json / --list-adapters` | OK |
| `approved_adapter_runner.py --create-approval --json` | OK |
| `approved_adapter_runner.py --execute-approved --dry-run --json` | OK — score 80, 6 artifacts |
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
| **Test total** | **329/329 pass** |
| `external_tool_sandbox_manager.py --status --json` | OK |
| `ghoti_product_launcher.py --status --json` | OK |
| `parallel_agent_relay.py --status --json` | OK — relay_mode=copy_paste_only |
| `local_memory_compression_bridge.py --json` | OK — local_only=true |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Test totals

329/329 tests pass across 12 modules. N+4.9A contributes 37 tests (runner status,
catalog, unknown-adapter rejection, approval flow + token gating, dry-run
artifacts, manifest safety flags, evaluation JSON shape, adapter interface +
import safety, dashboard labels, server endpoints, live endpoints).

## check_runtime_mvp.ps1 result

**PASS** — exit 0, "runtime MVP checks passed", no failures (first-run clean).

## check_dashboard_mvp.ps1 result

**PASS** — exit 0, "dashboard MVP checks passed", no failures.

## Safety summary

| Safety property | Status |
|-----------------|--------|
| Codex independent audit obtained | PASS — CLEAN PASS, commit 4684960 (verified by hash) |
| Approved adapter runner works | PASS |
| agent_skills_eval dry-run demo creates local artifacts | PASS — 6 artifacts, score 80 |
| Non-dry-run approval gate intact | PASS — refused without a verified token |
| External repo code executed | NO |
| External repo packages imported | NO — adapter is stdlib-only |
| Dependencies installed | NO |
| UI-TARS / desktop control | NO |
| Live APIs / accounts / posting / money / trading | NO |
| Raw approval token exposed by a GET endpoint | NO |
| `shell:true` | NONE — fixed argv, shell=False |
| Secrets | NONE |
| Dirty primary worktree | untouched (read-only) |
| Approval gates intact | YES — readiness safety_gates PASS |
| N+3 readiness score | 100 (9/9 categories) |

## Verdict

**MERGED_AND_PUSHED** — Codex audit CLEAN PASS verified by explicit hash
(`4684960`); N+4.9A implementation commit `fd4833e` merged clean; the approved
adapter runner works; the `agent_skills_eval` dry-run demo creates 6 local
artifacts (score 80/100); the non-dry-run approval gate holds; the 5
adapter-execution endpoints work live (no 500s, token not leaked via GET);
`check_runtime_mvp.ps1` + `check_dashboard_mvp.ps1` PASS; 329/329 regression tests
pass; readiness 100; all safety gates intact. N+4.9A lands the First Approved
Adapter Execution Demo on `main`.
