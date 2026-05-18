# N+4.9A — First Approved Adapter Execution Demo

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.9A — First Approved Adapter Execution Demo |
| Branch | feat/ghoti-agent-claude-n4-9a-first-approved-adapter-execution-demo |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_9a_first_approved_adapter_execution_demo |
| Base main | 9f29a275d386b926ec4e9f66878cbfaa251377e7 |

## Files changed

| File | Change |
|------|--------|
| `03_scripts/approved_adapter_runner.py` | NEW — approval-gated adapter execution runner |
| `02_automation/external_tool_adapters/agent_skills_eval_adapter.py` | PROMOTED — added `evaluate_skill_file` / `execute_demo` (execution-capable, still safe) |
| `03_scripts/external_tool_sandbox_manager.py` | `--generate-adapters` now preserves a promoted adapter instead of regenerating it to a stub |
| `01_projects/runtime_mvp/tests/test_n4_8a_external_tool_sandbox_adapter_discovery.py` | import test loosened to a stdlib allowlist (still forbids external repo packages) |
| `01_projects/dashboard_mvp/server.js` | +5 `/api/adapter-execution/*` endpoints |
| `01_projects/dashboard_mvp/public/index.html` | +`approved-adapter-execution-truth` dashboard card |
| `01_projects/dashboard_mvp/public/app.js` | +`attachApprovedAdapterExecution` handlers |
| `01_projects/runtime_mvp/tests/test_n4_9a_*.py` | NEW — 37-test suite |
| `14_context/adapter_execution/runs/20260518T085322Z_agent_skills_eval/` | NEW — canonical demo run (6 artifacts) |
| `14_context/claude_n4_9a_*.md` | NEW — this report |

Runtime-generated content under `14_context/adapter_execution/` (extra run
folders, `approvals/`, `latest_adapter_run.json`) is not committed; one canonical
demo run is committed as milestone evidence.

## What this milestone delivers

N+4.8A left Ghoti with static external-tool adapter *stubs*. N+4.9A moves to
**one safe adapter that actually executes a real local demo workflow and
produces a useful artifact** — without controlling the desktop, installing
anything, running external repo code, or calling any live API.

- `approved_adapter_runner.py` — an approval-gated runner. `--dry-run` executes
  with no token; non-dry-run execution requires a one-time approval token
  (`--create-approval` issues it; only its SHA-256 hash is persisted).
- `agent_skills_eval_adapter.py` — promoted from stub to execution-capable. It
  evaluates an agent-skill spec against Ghoti's own 9-dimension skill-quality
  checklist (clarity, safety boundaries, allowed tools, forbidden actions,
  approval gates, testability, expected outputs, rollback/cleanup, prompt
  quality) and emits a score + recommendations. It runs only Ghoti-owned local
  code over local files.

## Adapter selected

`agent_skills_eval` — chosen because it is safer than UI-TARS desktop control:
it produces a local evaluation report with no desktop control, no live accounts,
no dependency installs, and no external repo code execution. The other 4
adapters remain catalog entries with `execution_approved = false`.

## Run folder + artifacts

Canonical demo run: `14_context/adapter_execution/runs/20260518T085322Z_agent_skills_eval/`

| Artifact | Purpose |
|----------|---------|
| `00_demo_skill.md` | The demo agent-skill spec that was evaluated |
| `01_skill_evaluation.md` | Human-readable evaluation report |
| `02_skill_evaluation.json` | Machine-readable score + per-dimension results + recommendations |
| `03_safety_review.md` | Per-run safety review |
| `04_execution_manifest.json` | Execution manifest (safety flags + artifact list) |
| `05_human_next_steps.md` | Human next-step / approval packet |

## Evaluation score

**80 / 100 — "adequate"**. The demo skill ("Local Repository Markdown Link
Auditor") scored well on most checklist dimensions; the evaluator emitted
genuine recommendations for the dimensions that scored below full marks. The
evaluation is a real rule-based local assessment — the score is not hardcoded.

## Dashboard result

New **Approved Adapter Execution Truth** card in the Product Control Center
section. All 13 required labels present: Approved Adapter Execution Truth,
Approved Adapter Execution, agent-skills-eval Adapter, Run Safe Adapter Demo,
Dry Run Available, Approval Token Required, Local Artifacts Only, No External
Repo Code Execution, No Installs, No Desktop Control, No Live APIs, Human
Approval Required, Latest Adapter Run. Four buttons (refresh, list, create
approval, run demo); the "Run Safe Adapter Demo" button runs a **dry run only**.

## Endpoint smoke result

Real dashboard Node server spawned; all 5 adapter-execution endpoints hit live:

```
[status]          HTTP 200  ok=True
[adapters]        HTTP 200  ok=True  (5 adapters)
[create-approval] HTTP 200  ok=True  (token returned by POST only)
[run-demo]        HTTP 200  ok=True  mode=dry_run  score=80
[latest]          HTTP 200  ok=True  approval_token NOT present in GET body
```

No 500s. No `method`/`pathname` ReferenceError. The raw approval token is
returned only by the create-approval POST; the GET endpoints never expose it.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `approved_adapter_runner.py --status --json` | OK |
| `approved_adapter_runner.py --json` | OK |
| `approved_adapter_runner.py --list-adapters --json` | OK — includes agent_skills_eval |
| `approved_adapter_runner.py --create-approval --json` | OK — approval record written |
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
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Test totals

329/329 tests pass across 12 modules. N+4.9A contributes 37 tests (runner status,
catalog, unknown-adapter rejection, approval flow incl. token gating, dry-run
artifacts, manifest safety flags, evaluation JSON shape, adapter interface +
import safety, dashboard labels, server endpoints, live endpoints).

## Runtime / dashboard check result

`check_runtime_mvp.ps1`: **PASS** (exit 0). `check_dashboard_mvp.ps1`: **PASS**
(exit 0). Both first-run clean.

## Safety summary

| Safety property | Status |
|-----------------|--------|
| Approved adapter demo creates local artifacts | YES — 6 artifacts per run |
| External repo code executed | NO — only Ghoti-owned adapter code ran |
| External repo packages imported | NO — adapter imports stdlib only |
| Dependencies installed | NO |
| Desktop control used | NO |
| Live API / account / posting / money actions | NO |
| Approval token required for non-dry-run | YES — verified by token SHA-256 hash |
| Dry-run allowed without token | YES |
| Dashboard run-demo path | dry-run only — never non-dry-run, never with a token |
| Raw approval token exposed by a GET endpoint | NO — POST-only, never persisted in raw form |
| `shell=True` / `shell:true` | NONE |
| Unknown adapter name accepted | NO — approved catalog only |
| Path containment | run/output dirs validated repo-local |
| Secrets / API keys | NONE |
| Dirty primary worktree | untouched (read-only) |
| Approval gates intact | YES — readiness safety_gates PASS |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Did Ghoti execute an approved adapter demo?** YES — the `agent_skills_eval`
   adapter ran a real local skill-evaluation demo and produced 6 artifacts.
2. **Did it run external repo code?** NO — only Ghoti-owned adapter code ran;
   no external repo package was imported or executed.
3. **Did it install anything?** NO — no npm / pnpm / pip install.
4. **Did it control the desktop?** NO — no click / type / screenshot control.
5. **Did it use live APIs / accounts?** NO — fully local, no network calls.
6. **Can the user approve real runtime wiring later?** YES — `--create-approval`
   issues a one-time token; non-dry-run execution and any future wiring stay
   gated behind explicit human approval.
7. **Are approval gates intact?** YES — non-dry-run requires a verified token;
   the dashboard only triggers dry runs; readiness `safety_gates` passes.
8. **Is this full production 100%?** NO — this is the first safe adapter
   execution demo. `supervised_mvp_slice_score` is 100, but
   `production_public_release_ready` is false and `production_autonomy_score`
   is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+4.9A promotes the `agent_skills_eval` adapter to
execution-capable and adds `approved_adapter_runner.py`: an approval-gated runner
that executes a real local skill-evaluation demo and produces 6 useful artifacts
(score 80/100). 329/329 tests pass; both PowerShell checks PASS; live endpoint
smoke clean; readiness 100. No external repo code executed, no installs, no
desktop control, no live APIs — all approval gates intact. `main` was not pushed.
