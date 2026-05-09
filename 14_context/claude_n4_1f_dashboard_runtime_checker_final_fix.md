# N+4.1F — Dashboard Runtime Checker Final Fix

**Branch:** `feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix`
**Worktree:** `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_1f_runtime_checker_final_fix`
**Base main commit:** `cdedf6087ed9bb69b33981436840dbd1c2598b03`
**N+4.1D merged commit:** `73ecf4525a752ffe5206644cdf6517cce5ea128a`
**Date:** 2026-05-10
**Status:** COMPLETE — all checks reproducibly green

---

## N+4.1E Blocker Summary

N+4.1E audit (`origin/audit/ghoti-agent-codex-n4-1e-dashboard-control-center-reliability-remote-ref-verified`) returned **BLOCKED_VALIDATION** with 2 specific failures:

```
[FAIL] CLI ghoti-status: error: 'NoneType' object has no attribute 'executor_action_type'
[FAIL] CLI ghoti-recent: error: 'NoneType' object has no attribute 'executor_action_type'
```

The audit noted these failures were **initial-state / order-sensitive**: they occurred on the first clean run of `check_runtime_mvp.ps1` (empty task queue) but not after the check script had created tasks during later checks. All other checks (dashboard, N+3 proof, merge rehearsal) were green.

---

## Exact Reproduced Failure

Running `check_runtime_mvp.ps1` from a clean worktree:
1. `init-data` → creates runtime files with empty `tasks.json`
2. `ghoti-status` → **CRASH**: `'NoneType' object has no attribute 'executor_action_type'`
3. `ghoti-recent` → **CRASH**: same error

Both `ghoti-status` and `ghoti-recent` use `list_executor_tasks()` (which was already guarded `task is not None`). The crash happened inside `_build_ghoti_watchdog()` which is called by both commands.

---

## Root Cause

**File:** `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
**Function:** `_classify_executor_task(task)` (line ~403)

```python
def _classify_executor_task(task) -> str:
    action_type = str(task.executor_action_type or "").strip().lower()  # BUG
```

`_build_ghoti_watchdog()` constructs a `focus_task` variable:

```python
focus_task = (
    active_task
    or (wrong_window_blocks[0] if wrong_window_blocks else None)
    or (stalled_tasks[0] if stalled_tasks else None)
    or next(
        (task for task in sorted_tasks if ... in GHOTI_ACTIONABLE_STATUSES),
        None,  # ← None when task queue is EMPTY
    )
)
```

When the task queue is empty (first clean run), all four branches evaluate to `None`, so `focus_task = None`. The watchdog then calls:

```python
handoff_hint = (
    "..."
    if wrong_window_blocks or _classify_executor_task(focus_task) == "handoff"
    ...
)
```

`_classify_executor_task(None)` → `None.executor_action_type` → `AttributeError: 'NoneType' object has no attribute 'executor_action_type'`.

This is **why the failure is order-sensitive**: after the check script creates tasks (via queue-task checks), `sorted_tasks` is non-empty and `focus_task` is a real Task object, so the crash doesn't occur.

The N+4.1D fix (`str(data.get("executor_action_type") or "")` in `Task.from_dict`) addressed JSON null→None coercion but did not address the case where the *task object itself* is `None`.

---

## Fix

**One targeted change** in `_classify_executor_task`:

```python
# Before (crashes when task is None):
def _classify_executor_task(task) -> str:
    action_type = str(task.executor_action_type or "").strip().lower()
    if action_type == "run_operator_recipe":
        recipe_name = str(task.executor_payload.get("recipe_name", "")).strip().lower()

# After (safe for None task — uses getattr, consistent with _describe_overlay_target):
def _classify_executor_task(task) -> str:
    action_type = str(getattr(task, "executor_action_type", "") or "").strip().lower()
    if action_type == "run_operator_recipe":
        recipe_name = str(
            (getattr(task, "executor_payload", {}) or {}).get("recipe_name", "")
        ).strip().lower()
```

`getattr(None, "executor_action_type", "")` returns `""` instead of raising `AttributeError`. The rest of the function (DESKTOP_EXECUTOR_ACTIONS check, fallthrough to `"repo"`) continues to work correctly for all valid Task objects and now also for `None`.

This matches the pattern already used by `_describe_overlay_target` and other defensive helpers in cli.py.

---

## Data-Boundary Hardening Explanation

The fix adds a defensive layer at the classification boundary rather than at the data-loading boundary:

| Layer | Before N+4.1 | After N+4.1D | After N+4.1F |
|---|---|---|---|
| `Task.from_dict` | `None` fields pass through | Coerces `null→""`, `null→{}` | Same |
| `list_executor_tasks` | Could iterate None tasks | Guards `task is not None` | Same |
| `list_tasks` | May return None entries if storage errors | Unchanged | Unchanged |
| `_classify_executor_task` | Direct `.executor_action_type` | Same (bug) | Uses `getattr` — safe for None task |
| `_describe_overlay_target` | Already used `getattr` | Same | Same |

**Why `_classify_executor_task` and not the call site:** Fixing the function itself protects all callers, including `_print_ghoti_task_lines` which also calls it (though that path is guarded by `if not tasks`). It also makes the function's contract explicit: it handles None input gracefully and returns the default `"repo"` classification.

---

## Files Changed

| File | Change |
|---|---|
| `01_projects/runtime_mvp/src/super_ai_agent/cli.py` | `_classify_executor_task`: direct attribute access → `getattr` (safe for None) |
| `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` | Added 2 new regression tests (7 total) |
| `14_context/claude_n4_1f_dashboard_runtime_checker_final_fix.md` | This report |

All other files (models.py, queue.py, storage.py, server.js, index.html, check scripts, desktop_bridge_actions.ps1, cli.py UTF-8 fix) were merged from N+4.1D and remain unchanged in N+4.1F.

---

## Regression Tests Added

**`test_executor_action_type_none_does_not_crash_classify`**
- Calls `_classify_executor_task(None)` — must return `"repo"`, not crash
- Calls `_classify_executor_task(Task.from_dict({..., "executor_action_type": None}))` — must return `"repo"`
- Calls `_classify_executor_task(Task.from_dict({..., "executor_action_type": "wait_seconds"}))` — must return `"desktop"`

**`test_list_executor_tasks_skips_none_entries`**
- Patches `queue.list_tasks` to return `[None, valid_task, None]`
- Verifies `list_executor_tasks()` returns only the valid task
- Regression for N+4.1D `task is not None` guard

---

## Validation Results

| Check | Result |
|---|---|
| `git diff --check HEAD` | PASS (no whitespace errors) |
| Python AST compile (5 files) | PASS |
| `node --check server.js` | PASS |
| `node --check public/app.js` | PASS |
| `python -m unittest tests.test_n4_1_runtime_reliability -v` | **7/7 OK** |
| `ghoti_readiness_check.py --status` | PASS — `supervised_mvp_slice_score: 100`, `categories_passing: 9/9` |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — 13/13 files, all gates `pending_human_review` |
| `check_runtime_mvp.ps1` | **334 PASS, 0 FAIL** (exit 0) |
| `check_dashboard_mvp.ps1` | **167 PASS, 0 FAIL** (exit 0) |

---

## Node/Python Validation Summary

- Python AST: all changed files compile clean
- Node: server.js and app.js pass `--check` with no syntax errors
- Runtime checker: 334/334 PASS, 0 FAIL — first clean run, empty task queue

---

## N+3 Regression Validation

```
supervised_mvp_slice_score: 100
production_public_release_ready: False
categories_passing: 9/9
all_required_pass: True
Files: 13/13 present
All 5 approval gates: pending_human_review
```

N+3 proof packet fully intact.

---

## .NET Popup Result

No `.NET Graphics` popup observed during check_runtime_mvp.ps1 or check_dashboard_mvp.ps1 runs. WinForms Paint handler inner try/catch (from N+4.1D cherry-pick) remains in place.

---

## External Repo / Skill Intake Note

The following are queued for controlled intake only — **not runtime-wired**:
- **UI-TARS** — intake/planning only, no clone/install/run, no runtime wiring
- **The Agency** — intake/planning only
- **agent-skills-eval** — intake/planning only
- **arcads-claude-code** — intake/planning only
- **Weavy** — intake/planning only
- **Manychat** — intake/planning only
- **OpenFang / MoneyPrinter** — intake/planning only

Dashboard `External Repo / Skill Intake Truth` section reflects this with explicit "intake/planning only" labels and a safety note: no live account actions, no autonomous posting, no financial transactions without explicit user approval gate.

---

## Safety Validation

| Check | Result |
|---|---|
| No real secrets/API keys committed | PASS |
| No live posting/upload/account actions | PASS |
| No external repo clone/install/run | PASS |
| No UI-TARS/The Agency/Weavy/Manychat runtime wiring | PASS |
| No OpenFang/MoneyPrinter runtime wiring | PASS |
| No approval gate weakening | PASS |
| No temp logs committed (05_logs/tmp_n4_1f_*.txt excluded) | PASS |
| N+3 proof packet validates | PASS |
| `supervised_mvp_slice_score` remains 100 | PASS |
| `production_public_release_ready` remains false | PASS |
| `live_posting_enabled` remains false | PASS |

---

## Direct Answers

| Question | Answer |
|---|---|
| Does N+4.1F fix the N+4.1E runtime blocker? | **Yes** — `_classify_executor_task` now uses `getattr`, safe for `None` task |
| Does `check_runtime_mvp.ps1` pass? | **Yes — 334 PASS, 0 FAIL** |
| Does `check_dashboard_mvp.ps1` pass? | **Yes — 167 PASS, 0 FAIL** |
| Does `ghoti-status` survive `executor_action_type=None`? | **Yes** — `_classify_executor_task(None)` returns `"repo"` |
| Does `ghoti-recent` survive `executor_action_type=None`? | **Yes** — same fix covers both paths via `_build_ghoti_watchdog` |
| Is `/api/supervisor/status` stable and non-500 for bad state? | **Yes** — N+4.1D `buildDegradedSupervisorStatus()` remains in server.js |
| Are UI-TARS/The Agency/agent-skills-eval/arcads-claude-code/Weavy/Manychat wired into runtime? | **No** — intake/planning only |
| Did approval gates remain intact? | **Yes** |
| Is N+3 supervised MVP still valid? | **Yes — 13/13 files, score 100, all gates pending** |
| Is this full Ghoti production 100%? | **No — `production_public_release_ready: False` by design** |

---

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

Exact next action: **run Codex N+4.1F real audit** against
`feat/ghoti-agent-claude-n4-1f-dashboard-runtime-checker-final-fix`
