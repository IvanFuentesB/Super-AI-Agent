# N+4.8B Main Merge Gate Report — External Tool Sandbox + Adapter Discovery

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.8B — Main Merge Gate for N+4.8A External Tool Sandbox + Adapter Discovery |
| Merge branch | merge/ghoti-agent-n4-8b-external-tool-sandbox-main |
| Merge worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_8b_main_merge_external_tool_sandbox |
| Starting main | 238c80cbd8056a1171b8ae57a94c93de0860abbe (N+4.7B merge gate) |
| Implementation branch | feat/ghoti-agent-claude-n4-8a-external-tool-sandbox-adapter-discovery |
| Implementation commit | 79c4bad18e42ec74946c8c63c6228fbf6018e36b |
| Codex audit branch | audit/ghoti-agent-codex-n4-8a-external-tool-sandbox-adapter-discovery-real-audit-2 |
| Codex audit commit | 5456e9e07fe6cf1ec0459221fc25990b95cf708f |
| Codex verdict | CLEAN PASS |
| Merge commit | 6bba611 |
| Report commit | (this report — see git log) |
| Remote main hash | (see Verify section) |

## Codex audit gate

All three refs were verified against the remote and matched the expected commits
exactly: `origin/main` = `238c80c`, implementation = `79c4bad`, audit = `5456e9e`.

The audit branch was inspected **by its explicit commit hash** (not a transient
`FETCH_HEAD`, which during this gate briefly resolved to a stale ref and showed a
misleading diff — treated with scrutiny and discarded per the remote-truth rule).
Verified from `5456e9e` directly: the audit branch sits on top of `origin/main`
(`238c80c`), is purely additive (15 files, 2406 insertions, 0 deletions), and
contains `14_context/codex_n4_8a_external_tool_sandbox_adapter_discovery_real_audit.md`.
Its **Final Verdict is CLEAN PASS** — `--sync-approved` 5 cloned / 0 failed,
installs performed false, desktop control enabled false, adapter stubs present.

## Merge

`git merge --no-ff origin/feat/ghoti-agent-claude-n4-8a-external-tool-sandbox-adapter-discovery`
into a worktree branched from `origin/main` (238c80c). Result: **clean automatic
merge**, no conflicts. Merge commit `6bba611`. The N+4.7B merge-gate report
(`claude_n4_7b_main_merge_product_launcher.md`), which post-dates the N+4.8A feat
branch, was correctly preserved by the 3-way merge.

N+4.8A content merged: `03_scripts/external_tool_sandbox_manager.py`, 5 adapter
stubs + `__init__.py` under `02_automation/external_tool_adapters/`, the External
Tool Sandbox Truth card + 4 endpoints across `server.js`/`index.html`/`app.js`, the
`test_n4_8a` 35-test suite, the sandbox status file, the approval packet, and the
N+4.8A implementation report.

## Cloned / degraded repo result

The N+4.8A milestone (and the Codex audit) shallow-cloned all 5 approved public
repos for static inspection only — **5/5 cloned, 0 failed, degraded=false**:

| Repo | Commit |
|------|--------|
| bytedance/UI-TARS-desktop | 7986f5aea500 |
| bytedance/UI-TARS | 582f3a7ea5d2 |
| the-agency-ai/the-agency | dd2430bfe62c |
| darkrishabh/agent-skills-eval | b60eebe3c6ed |
| vouch-protocol/vouch | 1b37c3ef661b |

Cloned repos live under `21_repos/third_party/sandboxed/` and are gitignored
(`21_repos/third_party/*`) — never committed. The `test_n4_8a` suite in this merge
worktree re-ran `--sync-approved` and confirmed 5/5 clone again. No installs were
performed; no external repo code was executed.

## Adapter stubs result

5 safe Ghoti-local adapter stubs present under `02_automation/external_tool_adapters/`:
`ui_tars_desktop_adapter.py`, `ui_tars_model_adapter.py`, `the_agency_adapter.py`,
`agent_skills_eval_adapter.py`, `vouch_adapter.py`. `--generate-adapters` returned
ok with count 5. Each stub is local-only, imports no external repo package, runs no
external code, and reports `requires_human_approval = true` / `wired = false`.

## Approval packet result

`--write-approval-packet` returned ok. The committed milestone packet is
`14_context/external_tools/approval_packets/external_tool_approval_packet_20260517T192949Z.md`
— a per-tool human review + sign-off gate. No tool is wired until a human approves.

## Endpoint smoke result

Real dashboard Node server spawned; the 3 external-tool-sandbox endpoints hit live:

```
[status]  HTTP 200  ok=True  mode=sandbox_static_inspection_only  installs_performed=False  desktop_control_enabled=False
[scan]    HTTP 200  ok=True  installs_performed=False  external_code_executed=False
[latest]  HTTP 200  ok=True
```

No 500s. No `method`/`pathname` ReferenceError. No installs, no external runtime
wiring, no live API/account actions.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `git show --check --stat HEAD` | clean — merge commit 6bba611 |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `external_tool_sandbox_manager.py --status --json` | OK — catalog 5, mode sandbox_static_inspection_only |
| `external_tool_sandbox_manager.py --json` | OK |
| `external_tool_sandbox_manager.py --scan --json` | OK — installs_performed=false |
| `external_tool_sandbox_manager.py --generate-adapters --json` | OK — 5 adapters |
| `external_tool_sandbox_manager.py --write-approval-packet --json` | OK |
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
| **Test total** | **292/292 pass** |
| `ghoti_product_launcher.py --status --json` | OK |
| `parallel_agent_relay.py --status --json` | OK — relay_mode=copy_paste_only |
| `local_memory_compression_bridge.py --json` | OK — local_only=true |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Test totals

292/292 tests pass across 11 modules. N+4.8A contributes 35 tests (approved catalog,
unknown-repo rejection, manager status, truthful sync degradation, repo-local clone
targets, no-install guarantees, adapter stub generation/import-safety/interface,
approval packet, dashboard labels, server endpoints, safety).

## check_runtime_mvp.ps1 result

**PASS** — exit 0, "runtime MVP checks passed", no failures.

## check_dashboard_mvp.ps1 result

**PASS** — exit 0, "dashboard MVP checks passed", no failures.

## Safety summary

| Safety property | Status |
|-----------------|--------|
| Codex independent audit obtained | PASS — CLEAN PASS, commit 5456e9e (verified from remote truth) |
| 5 approved repos sandboxed (shallow) or degraded truthfully | PASS — 5/5 cloned, degraded=false |
| Install commands executed | NO — none |
| External repo code executed | NO — none |
| Adapter stubs exist and require human approval | YES — 5 stubs, requires_human_approval=true |
| Dashboard External Tool Sandbox Truth card | PRESENT |
| `shell:true` | NONE — fixed argv, shell=False |
| Desktop control enabled | NO |
| Live APIs / accounts / posting / money / trading | NONE |
| Cloned repos committed to Ghoti | NO — `21_repos/third_party/*` is gitignored |
| Secrets | NONE |
| Dirty primary worktree | untouched (read-only) |
| Approval gates intact | YES — readiness safety_gates PASS |
| N+3 readiness score | 100 (9/9 categories) |

## Verdict

**MERGED_AND_PUSHED** — Codex audit CLEAN PASS verified from remote truth
(`5456e9e`); N+4.8A implementation commit `79c4bad` merged clean; 5/5 approved repos
sandboxed (no installs, no external code execution); adapter stubs present and
human-approval-gated; the External Tool Sandbox Truth dashboard card + endpoints
work live (no 500s); `check_runtime_mvp.ps1` + `check_dashboard_mvp.ps1` PASS;
292/292 regression tests pass; readiness 100; all safety gates intact. N+4.8A lands
the External Tool Sandbox + Adapter Discovery on `main`.
