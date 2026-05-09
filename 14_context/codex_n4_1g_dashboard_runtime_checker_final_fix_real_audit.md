# Codex N+4.1G Dashboard Runtime Checker Final Fix Real Audit

## Executive Verdict

Final verdict: **BLOCKED_VALIDATION**

The target remote ref is real, fetched correctly, and the no-commit merge rehearsal into `origin/main` is clean. The specific N+4.1E empty-queue / `focus_task=None` crash path is fixed: `_classify_executor_task()` now uses `getattr`, `ghoti-status` exits 0, `ghoti-recent` exits 0, and `check_runtime_mvp.ps1` exits 0 in a proper branch worktree.

However, the branch does **not** fully satisfy the N+4.1G prompt requirement that runtime task state containing `null`, malformed, partial, or legacy task entries must not crash status paths. A direct backup-and-restore fixture with `01_projects/runtime_mvp/runtime_data/tasks.json` set to `[null]` still crashes both `ghoti-status` and `ghoti-recent`:

```text
NULL_TASK_STATUS_EXIT=1
error: 'NoneType' object is not subscriptable
NULL_TASK_RECENT_EXIT=1
error: 'NoneType' object is not subscriptable
```

This is a real data-boundary gap in `read_tasks()` / `Task.from_dict()` handling. Merge to main is **not recommended** until this null/malformed task-store case is hardened.

## Remote Ref Resolution

| Check | Result | Evidence |
| --- | --- | --- |
| Target remote ref exists | PASS | `git ls-remote origin refs/heads/feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix` returned `5ec799fd56efcca4ce453906491b83ede161c931` |
| Local fetched target matches remote | PASS | `origin/feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix` resolved to `5ec799fd56efcca4ce453906491b83ede161c931` |
| Expected target commit verified | PASS | Target is exactly expected `5ec799fd56efcca4ce453906491b83ede161c931` |
| Base main verified | PASS | Audit branch started from `origin/main` at `cdedf6087ed9bb69b33981436840dbd1c2598b03` |
| Previous stale blocked audit ignored | PASS | Prior N+4.1F remote-missing audit was not reused as current evidence |

Audit branch: `audit/ghoti-agent-codex-n4-1g-dashboard-runtime-checker-final-fix-real-audit`

Target branch: `origin/feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix`

Target commit audited: `5ec799fd56efcca4ce453906491b83ede161c931`

Base main commit: `cdedf6087ed9bb69b33981436840dbd1c2598b03`

## Merge Rehearsal

| Check | Result | Evidence |
| --- | --- | --- |
| Isolated audit worktree used | PASS | `C:\w\n4_1g_audit` |
| No-commit merge into main | PASS | `git merge --no-commit --no-ff origin/feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix` succeeded |
| Conflicts | PASS | No conflicts |
| Merge aborted before audit doc commit | PASS | Target implementation files were removed from index before this audit doc was staged |

Changed files seen in merge rehearsal:

- `01_projects/dashboard_mvp/public/index.html`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/desktop_playground/desktop_bridge_actions.ps1`
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
- `01_projects/runtime_mvp/src/super_ai_agent/models.py`
- `01_projects/runtime_mvp/src/super_ai_agent/queue.py`
- `01_projects/runtime_mvp/src/super_ai_agent/storage.py`
- `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py`
- `03_scripts/check_dashboard_mvp.ps1`
- `03_scripts/check_runtime_mvp.ps1`
- `14_context/claude_n4_1_dashboard_control_center_reliability.md`
- `14_context/claude_n4_1d_dashboard_control_center_reliability_check_fix.md`
- `14_context/claude_n4_1f_dashboard_runtime_checker_final_fix.md`

No temp logs, `05_logs/tmp_n4_1_*.txt`, runtime data artifacts, `.env`, secrets, or generated output folders were staged by the target merge.

## Validation Table

| Validation | Result | Evidence |
| --- | --- | --- |
| `git diff --check` | PASS | No whitespace errors in merged state |
| `git diff --cached --check` | PASS | No staged whitespace errors in merged state |
| `git show --check --stat origin/...n4-1f...` | PASS | Target commit whitespace/stat check passed |
| Python AST/compile for changed Python files | PASS | `models.py`, `cli.py`, `queue.py`, `storage.py`, and `test_n4_1_runtime_reliability.py` parsed |
| `python -m pytest ...test_n4_1_runtime_reliability.py` | ENV GAP | `pytest` is not installed in this audit environment |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_1_runtime_reliability` | PASS | 7 tests ran, 7 passed |
| `python 03_scripts/ghoti_readiness_check.py --status` | PASS | 9/9 categories PASS, `supervised_mvp_slice_score: 100`, production public release false |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | PASS | 13/13 proof packet files present, gates pending human review, no live posting/API calls |
| `python 03_scripts/agent_lane_status.py --check` | PASS | Agent lane files/data valid |
| `node --check 01_projects/dashboard_mvp/server.js` | PASS | Syntax check passed |
| `node --check 01_projects/dashboard_mvp/public/app.js` | PASS | Syntax check passed |
| `03_scripts/check_runtime_mvp.ps1` | PASS in proper branch worktree | Final result: `Summary: runtime MVP checks passed.` |
| `03_scripts/check_dashboard_mvp.ps1` | PASS with longer bounded timeout | Final result: `Summary: dashboard MVP checks passed.` Runtime was about 201 seconds |
| Backup/restore fixture: `tasks.json = [null]` then `ghoti-status` | FAIL | `error: 'NoneType' object is not subscriptable` |
| Backup/restore fixture: `tasks.json = [null]` then `ghoti-recent` | FAIL | `error: 'NoneType' object is not subscriptable` |

## N+4.1E Blocker Resolution

| N+4.1E Blocker | Result | Evidence |
| --- | --- | --- |
| `check_runtime_mvp.ps1` failed with 2 runtime failures | FIXED FOR NORMAL CHECK PATH | Proper branch worktree run exits 0 |
| `ghoti-status` crashed on `focus_task=None` | FIXED | Direct `ghoti-status` exits 0 in normal restored state |
| `ghoti-recent` crashed on `focus_task=None` | FIXED | Direct `ghoti-recent` exits 0 in normal restored state |
| `_classify_executor_task(None)` unsafe | FIXED | `cli.py` now uses `getattr(task, "executor_action_type", "")` |
| Empty queue first-clean watchdog path | LIKELY FIXED | Added unit test around `_classify_executor_task(None)` and normal CLI status path passes |
| Null task entry in persisted task store | NOT FIXED | `[null]` task-store fixture still crashes status and recent |

## Runtime Checker Table

| Runtime Area | Result | Notes |
| --- | --- | --- |
| `check_runtime_mvp.ps1` | PASS | Reproduced as green in proper branch worktree after no-commit merge |
| `ghoti-status` normal runtime state | PASS | Exit 0; reports truthful degraded/approval-needed state, not fake green |
| `ghoti-recent` normal runtime state | PASS | Exit 0; reports actionable tasks, approvals, failures, and artifacts |
| `executor_action_type=None` in valid task dict | PASS | Unit test covers normalization to empty string |
| `_classify_executor_task(None)` | PASS | Unit test and source inspection confirm safe `getattr` path |
| `tasks.json` containing literal `null` item | FAIL | Both status commands crash before graceful degradation |
| Missing supervisor state | PASS | `/api/supervisor/status` returned HTTP 200 with generated/truthful status |
| Corrupt supervisor state | PASS | `/api/supervisor/status` returned HTTP 200 with `ok=false`, `status=degraded`, and parse-error headline |
| Browser dependency missing | PASS | Dashboard checker accepts Playwright missing as degraded/dependency-missing instead of 500 |

## Dashboard Checker Table

| Dashboard Area | Result | Evidence |
| --- | --- | --- |
| `check_dashboard_mvp.ps1` | PASS | Exit 0 with `Summary: dashboard MVP checks passed.` |
| Dashboard server start | PASS | `http://127.0.0.1:3211/api/health` passed in checker |
| `/api/supervisor/status` | PASS | Checker passed and custom corrupt-state probe returned HTTP 200 |
| Request-level async safety net | PASS BY SOURCE INSPECTION | `server.js` wraps `handleRequest()` with catch paths and returns structured 500 on unexpected request errors |
| Dashboard exact labels from prompt | PARTIAL | `ghoti-control-center`, Local Brain, Brain / Provider, Specialist-Agent, Browser-Agent, Relay-Loop, Compact Memory, Operator Watchdog, and External Repo / Skill Intake labels exist. Exact strings `Runtime Truth`, `Supervisor Truth`, `Approval Truth`, `Dashboard Truth`, and `Content MVP Truth` were not found |
| External intake wording | SEMANTIC PASS, EXACT STRING PARTIAL | Section says intake/planning only, no clone/install/runtime wiring, no live account actions, and human approval required, but exact compact strings like `OpenFang/MoneyPrinter`, `planning/intake only`, `no clone/install/run`, and `no runtime wiring` were not found verbatim |

## NoneType.executor_action_type Verification

Source inspection confirms the exact N+4.1E focus-task bug is addressed:

- `01_projects/runtime_mvp/src/super_ai_agent/cli.py` now implements `_classify_executor_task(task)` with `getattr(task, "executor_action_type", "")`.
- `_build_ghoti_watchdog()` can call `_classify_executor_task(focus_task)` without crashing when `focus_task` is `None`.
- The new unit suite includes `test_executor_action_type_none_does_not_crash_classify`.

But the storage boundary is still incomplete:

- `01_projects/runtime_mvp/src/super_ai_agent/storage.py` still returns `[Task.from_dict(item) for item in _read_json_list(TASKS_PATH)]`.
- `01_projects/runtime_mvp/src/super_ai_agent/models.py` still assumes `data["task_id"]`, `data["title"]`, and other required fields exist.
- Therefore a literal `null` item or malformed non-dict task entry in `tasks.json` can still crash status paths before downstream `list_executor_tasks()` gets a chance to skip anything.

This is the main blocker.

## Invoke-ModuleCommand Verification

`03_scripts/check_runtime_mvp.ps1` includes `Invoke-ModuleCommand` using a temporary Python wrapper around `super_ai_agent.cli.main(argv)` and returns the child process exit code. The runtime checker passed after this branch's changes, and command failures are not being masked as success in the observed check path.

The audit did not find evidence that timeout results are being reported as success. Timeout behavior remains explicit in the checker and desktop bridge paths.

## .NET Graphics Popup Result

No blocking .NET WinForms `Graphics` popup was observed during:

- `check_runtime_mvp.ps1`
- `check_dashboard_mvp.ps1`
- direct `ghoti-status`
- direct `ghoti-recent`

`desktop_bridge_actions.ps1` was changed in the target branch and the audit did not observe a GUI-blocking validation failure.

## External Repo / Skill Safety Table

| Area | Result | Evidence |
| --- | --- | --- |
| UI-TARS | PASS | Mentioned as intake/planning only; no clone/install/run detected |
| The Agency | PASS | Mentioned as intake/planning only; no clone/install/run detected |
| agent-skills-eval | PASS | Mentioned as intake/planning only; no clone/install/run detected |
| arcads-claude-code | PASS | Mentioned as intake/planning only; no live account/content action detected |
| Weavy | PASS | Mentioned as intake/planning only; no API/live account wiring detected |
| Manychat | PASS | Mentioned as intake/planning only; no API/live account wiring detected |
| OpenFang / MoneyPrinter | PASS | Mentioned as candidates/intake only; no runtime wiring detected |
| External repo runtime | PASS | No active clone/install/run behavior detected in target diff |
| Live account actions | PASS | No live posting/account/money/public actions enabled |

## N+3 Regression Table

| N+3 Check | Result | Evidence |
| --- | --- | --- |
| Proof packet exists | PASS | Latest run `20260507T091135Z_ai_tools_for_students_and_crea` validated |
| Full proof packet files | PASS | 13/13 required files present |
| `supervised_mvp_slice_score` | PASS | 100 |
| `production_public_release_ready` | PASS | False |
| `live_posting` / live posting enabled | PASS | False |
| External API calls in proof packet | PASS | False |
| Human approval required | PASS | True |
| Approval gates | PASS | All 5 gates `pending_human_review` |

## Safety Table

| Safety Check | Result | Notes |
| --- | --- | --- |
| No real secrets/API keys committed | PASS | No secret-bearing staged files or obvious executable secret reads found |
| No live posting/upload/account actions | PASS | No active live action path found |
| No autonomous money/public action | PASS | No autonomous money movement or public release action found |
| No external repo clone/install/run | PASS | No active clone/install/run behavior detected |
| No Ruflo/OpenFang/MoneyPrinter runtime wiring | PASS | Mentions remain planning/intake only |
| Approval gates intact | PASS | Dashboard and runtime still require approval for guarded actions |
| No temp logs committed | PASS | No `05_logs/tmp_n4_1_*.txt` or runtime data artifacts staged |

## Documentation Check

Expected Claude report found: `14_context/claude_n4_1f_dashboard_runtime_checker_final_fix.md`

The Claude report claims N+4.1F fixed the runtime checker blocker and records safe external repo/skill intake positioning. Codex agrees that the narrow reported `focus_task=None` blocker is fixed, but this audit adds the stricter persisted null-task blocker above.

## Direct Answers

| Question | Answer |
| --- | --- |
| Is target remote ref real/fetched? | Yes |
| Is N+4.1E blocker fixed? | Partially. The reported `_build_ghoti_watchdog` / `focus_task=None` path is fixed, but persisted `tasks.json` null entries still crash status paths |
| Does `check_runtime_mvp.ps1` pass? | Yes, in a proper branch worktree |
| Does `check_dashboard_mvp.ps1` pass? | Yes, with a longer bounded timeout; runtime about 201 seconds |
| Does `ghoti-status` survive `executor_action_type=None` / empty queue? | Yes for the fixed empty/focus-task path and valid task dict normalization; no for literal `null` task-store entries |
| Does `ghoti-recent` survive `executor_action_type=None` / empty queue? | Yes for the fixed empty/focus-task path and valid task dict normalization; no for literal `null` task-store entries |
| Does `/api/supervisor/status` avoid 500? | Yes. Corrupt supervisor state returned HTTP 200 with degraded status |
| Do automated checks avoid blocking GUI popups? | No blocking GUI popup observed |
| Are UI-TARS/The Agency/agent-skills-eval/arcads-claude-code/Weavy/Manychat planning-only? | Yes |
| Did approval gates remain intact? | Yes |
| Were live posting/account/money actions enabled? | No |
| Was external repo runtime wired? | No |
| Are secrets/API keys present? | No evidence found |
| Is N+3 supervised MVP still valid? | Yes |
| Is merge to main recommended? | No, not until the null/malformed persisted task-store blocker is fixed |

## Required Next Fix

Recommended next Claude branch:

`feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening`

Exact fix list:

1. Harden `01_projects/runtime_mvp/src/super_ai_agent/storage.py::read_tasks()` so non-dict/null task entries are skipped, quarantined, or reported as degraded without returning unsafe values to CLI/status paths.
2. Harden `01_projects/runtime_mvp/src/super_ai_agent/models.py::Task.from_dict()` against non-dict input and missing legacy fields, either by returning a safe degraded task only where appropriate or by raising a typed validation error that storage catches.
3. Add tests in `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` for `tasks.json` containing `[null]`, non-object entries, and malformed partial dict entries.
4. Ensure `ghoti-status`, `ghoti-recent`, `check_runtime_mvp.ps1`, and `check_dashboard_mvp.ps1` pass after those fixtures.
5. Optionally align dashboard static labels with the exact prompt strings: `Runtime Truth`, `Supervisor Truth`, `Approval Truth`, `Dashboard Truth`, `Content MVP Truth`, and exact compact external intake wording.

Final verdict remains: **BLOCKED_VALIDATION**.
