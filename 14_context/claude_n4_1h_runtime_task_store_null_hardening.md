# N+4.1H — Runtime Task Store Null Hardening

**Branch:** `feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening`
**Worktree:** `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_1h_runtime_task_store_null_hardening`
**Base main commit:** `cdedf6087ed9bb69b33981436840dbd1c2598b03`
**N+4.1F merged commit:** `5ec799fd56efcca4ce453906491b83ede161c931`
**Date:** 2026-05-11
**Status:** COMPLETE — all checks reproducibly green

---

## N+4.1G Blocker Summary

N+4.1G audit (`origin/audit/ghoti-agent-codex-n4-1g-dashboard-runtime-checker-final-fix-real-audit`) at `19f30728` returned **BLOCKED_VALIDATION** with 2 specific failures:

```
NULL_TASK_STATUS_EXIT=1
error: 'NoneType' object is not subscriptable
NULL_TASK_RECENT_EXIT=1
error: 'NoneType' object is not subscriptable
```

The audit used a backup/restore fixture setting `tasks.json = [null]`. Both `ghoti-status` and `ghoti-recent` crashed with `TypeError: 'NoneType' object is not subscriptable`.

All other checks in N+4.1G were green: N+4.1F's empty-queue crash fix was confirmed working, 7/7 unit tests passed, check_runtime_mvp.ps1 and check_dashboard_mvp.ps1 both passed. The only remaining blocker was the null task store entry crash.

---

## Exact Reproduced Failure

```
tasks.json = [null]
ghoti-status → EXIT 1: error: 'NoneType' object is not subscriptable
ghoti-recent → EXIT 1: error: 'NoneType' object is not subscriptable
```

Code path:
1. `ghoti-status` / `ghoti-recent` → `_build_ghoti_watchdog()` → `list_tasks()` → `read_tasks()`
2. `read_tasks()` calls `[Task.from_dict(item) for item in _read_json_list(TASKS_PATH)]`
3. `_read_json_list(TASKS_PATH)` returns `[None]` (JSON `null` → Python `None`)
4. `Task.from_dict(None)` → `data["task_id"]` → `TypeError: 'NoneType' object is not subscriptable`

---

## Root Cause

**File:** `01_projects/runtime_mvp/src/super_ai_agent/storage.py`
**Function:** `read_tasks()` (line 381)

```python
# Before (crashes when tasks.json contains null entries):
def read_tasks() -> list[Task]:
    return [Task.from_dict(item) for item in _read_json_list(TASKS_PATH)]
```

`_read_json_list()` validates that the JSON top-level value is a `list` but does not
validate that each list element is a `dict`. When the file contains `[null]`, the list
`[None]` passes the top-level list check. `Task.from_dict(None)` then accesses
`data["task_id"]` on `None`, crashing with `TypeError: 'NoneType' object is not
subscriptable`.

This is a distinct bug from the N+4.1F crash (`focus_task=None` in
`_classify_executor_task`). N+4.1F protected the classification boundary; N+4.1H
protects the data-loading boundary.

How `tasks.json` ends up containing `[null]`:
- Partial write failure that produces a `null` entry
- JSON produced by a tool that serialises Python `None` as JSON `null`
- Manual editing error
- Legacy data migration that didn't handle missing task objects

---

## Fix

**Two targeted changes** in `storage.py`:

### 1. `read_tasks()` — primary fix

```python
# After (safe for null/non-dict entries):
def read_tasks() -> list[Task]:
    # N+4.1H: skip null/non-dict entries so tasks.json=[null] (or any partially
    # corrupted list) does not crash ghoti-status / ghoti-recent with
    # "TypeError: 'NoneType' object is not subscriptable".
    tasks: list[Task] = []
    for item in _read_json_list(TASKS_PATH):
        if not isinstance(item, dict):
            continue
        try:
            tasks.append(Task.from_dict(item))
        except (KeyError, TypeError, ValueError):
            continue
    return tasks
```

### 2. `read_approvals()` and `read_approval_requests()` — consistency hardening

Same `isinstance(item, dict)` + `try/except` guard applied to both functions.
`ApprovalRecord.from_dict` and `ApprovalRequest.from_dict` use direct key access
(`data["task_id"]`, `data["approval_id"]`, etc.) that would crash identically if
their JSON files contained null entries.

---

## Data-Boundary Hardening Progression

| Layer | Before N+4.1 | After N+4.1D | After N+4.1F | After N+4.1H |
|---|---|---|---|---|
| `Task.from_dict` | `None` fields pass through | Coerces `null→""`, `null→{}` for executor fields | Same | Same |
| `list_executor_tasks` | Could iterate None tasks | Guards `task is not None` | Same | Same |
| `_classify_executor_task` | Direct `.executor_action_type` | Same (bug) | Uses `getattr` — safe for None task | Same |
| `read_tasks()` | Direct `Task.from_dict(item)` — crashes on null | Same | Same | `isinstance(item, dict)` guard + `try/except` |
| `read_approvals()` | Direct `ApprovalRecord.from_dict(item)` | Same | Same | Same guard |
| `read_approval_requests()` | Direct `ApprovalRequest.from_dict(item)` | Same | Same | Same guard |

---

## Files Changed

| File | Change |
|---|---|
| `01_projects/runtime_mvp/src/super_ai_agent/storage.py` | `read_tasks()`, `read_approvals()`, `read_approval_requests()`: added `isinstance(item, dict)` guard + `try/except` |
| `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` | Added 3 new regression tests (10 total); added `json` and `unittest.mock` imports |
| `14_context/claude_n4_1h_runtime_task_store_null_hardening.md` | This report |

All other files (models.py, queue.py, cli.py, server.js, index.html, check scripts,
desktop_bridge_actions.ps1) were merged from N+4.1F and remain unchanged in N+4.1H.

---

## Regression Tests Added

**`test_read_tasks_skips_null_entries`**
- Writes `tasks.json = [null]` to a temp dir
- Patches `storage.TASKS_PATH`
- Calls `storage.read_tasks()` — must return `[]`, not raise

**`test_read_tasks_skips_null_mixed_with_valid`**
- Writes `[null, <valid_task>, null]` to a temp dir
- Calls `storage.read_tasks()` — must return only the 1 valid task

**`test_read_tasks_skips_malformed_dict_entries`**
- Writes `[{"not_a_task": True}, <valid_task>]` to a temp dir
- Calls `storage.read_tasks()` — malformed dict silently dropped, valid task kept

---

## Validation Results

| Check | Result |
|---|---|
| `git diff --check HEAD` | PASS (no whitespace errors) |
| Python AST compile (5 files) | PASS |
| `node --check server.js` | PASS |
| `node --check public/app.js` | PASS |
| `python -m unittest tests.test_n4_1_runtime_reliability -v` | **10/10 OK** |
| `ghoti_readiness_check.py --status` | PASS — `supervised_mvp_slice_score: 100`, `categories_passing: 9/9` |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — 13/13 files, all gates `pending_human_review` |
| `ghoti-status` with `tasks.json=[null]` | **EXIT 0** — no crash |
| `ghoti-recent` with `tasks.json=[null]` | **EXIT 0** — no crash |
| `check_runtime_mvp.ps1` | **334 PASS, 0 FAIL** (exit 0) |
| `check_dashboard_mvp.ps1` | **167 PASS, 0 FAIL** (exit 0) |

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

## External Repo / Skill Intake Note

The following are queued for controlled intake only — **not runtime-wired**:
- **UI-TARS** — intake/planning only, no clone/install/run, no runtime wiring
- **The Agency** — intake/planning only
- **agent-skills-eval** — intake/planning only
- **arcads-claude-code** — intake/planning only
- **Weavy** — intake/planning only
- **Manychat** — intake/planning only
- **OpenFang / MoneyPrinter** — intake/planning only
- **AirLLM** — intake/planning only
- **Mermaid** — intake/planning only
- **Claude Cowork** — intake/planning only
- **Speckit** — intake/planning only
- **Sigmap** — intake/planning only
- **Anvac** — intake/planning only
- **Agent Exchange / AEX** — intake/planning only
- **Claude+MetaTrader** — intake/planning only

Dashboard `External Repo / Skill Intake Truth` section reflects this with explicit
"intake/planning only" labels and a safety note.

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
| No temp logs committed | PASS |
| N+3 proof packet validates | PASS |
| `supervised_mvp_slice_score` remains 100 | PASS |
| `production_public_release_ready` remains false | PASS |
| `live_posting_enabled` remains false | PASS |

---

## Direct Answers

| Question | Answer |
|---|---|
| Does N+4.1H fix the N+4.1G task-store null blocker? | **Yes** — `read_tasks()` now uses `isinstance(item, dict)` guard |
| Does `ghoti-status` survive `tasks.json=[null]`? | **Yes — EXIT 0** |
| Does `ghoti-recent` survive `tasks.json=[null]`? | **Yes — EXIT 0** |
| Does `check_runtime_mvp.ps1` pass? | **Yes — 334 PASS, 0 FAIL** |
| Does `check_dashboard_mvp.ps1` pass? | **Yes — 167 PASS, 0 FAIL** |
| Unit tests? | **10/10 OK** |
| Are UI-TARS/The Agency/etc. wired into runtime? | **No** — intake/planning only |
| Did approval gates remain intact? | **Yes** |
| Is N+3 supervised MVP still valid? | **Yes — 13/13 files, score 100, all gates pending** |
| Is this full Ghoti production 100%? | **No — `production_public_release_ready: False` by design** |

---

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

Exact next action: **run Codex N+4.1I real audit** against
`feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening`
