# N+4.1I — Runtime Task-Store Truth Polish

**Branch:** `feat/ghoti-agent-claude-n4-1i-runtime-task-store-truth-polish`
**Worktree:** `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_1i_runtime_task_store_truth_polish`
**Base main commit:** `cdedf6087ed9bb69b33981436840dbd1c2598b03`
**N+4.1H merged commit:** `35316c1841fb13ed9c199adda8726ea8b7e480ef`
**Date:** 2026-05-11
**Status:** COMPLETE — all checks reproducibly green

---

## N+4.1H CONDITIONAL PASS Summary

N+4.1H audit (`origin/audit/ghoti-agent-codex-n4-1h-runtime-task-store-null-hardening`) at `cc821f10`
returned **CONDITIONAL PASS** with two non-safety but real gaps:

1. **Truth gap**: Invalid task-store entries are silently skipped rather than surfaced as
   degraded/skipped/quarantined status. The null crash was fixed but bad entries disappeared
   without any observability.
2. **Label gap**: Exact dashboard label strings required by the audit prompt were absent verbatim:
   `Runtime Truth`, `Supervisor Truth`, `Approval Truth`, `Dashboard Truth`, `Content MVP Truth`.
   Also missing from intake list: `AirLLM`, `Vouch`, `Agent Exchange / AEX`.
   Missing exact phrases: `no clone/install/run`, `no runtime wiring`.

All other N+4.1H checks were green: crash fix confirmed, check scripts 334/0 and 167/0, N+3 proof
packet valid, safety checks clean.

---

## Exact Reproduced CONDITIONAL-PASS Issues

**Truth gap** — reproduced before fix:
```
tasks.json = [null]
ghoti-status output: (no task_store_* fields — silent skip)
ghoti-recent output: (no task_store_* fields — silent skip)
```

**Label gap** — reproduced before fix via grep/check:
```
Runtime Truth       → MISSING from index.html
Supervisor Truth    → MISSING
Approval Truth      → MISSING
Dashboard Truth     → MISSING
Content MVP Truth   → MISSING
AirLLM              → MISSING from intake list
Vouch               → MISSING from intake list
Agent Exchange      → MISSING from intake list
no clone/install/run → MISSING (had "no clone, install, or runtime wiring" instead)
no runtime wiring   → MISSING (split across phrase)
```

---

## Root Causes

**Truth gap root cause:**
`storage.py::read_tasks()` correctly skipped invalid entries (N+4.1H fix) but had no mechanism to
expose the skip count to callers. No module-level counter or diagnostic accessor existed. Neither
`ghoti-status` nor `ghoti-recent` called any post-read diagnostic function.

**Label gap root cause:**
The N+4.1D/N+4.1H `ghoti-control-center` section in `index.html` contained 7 Truth cards
(Brain / Provider, Specialist-Agent, Browser-Agent, Relay-Loop, Compact Memory, Operator Watchdog,
External Repo / Skill Intake Truth) but did not include 5 additional Truth cards requested by the
audit prompt. The intake list also omitted 3 newer tool entries added to the planning list after
N+4.1H, and used a slightly different phrasing for the safety disclaimer.

---

## Fix

### 1. `storage.py` — Module-level diagnostic tracking

Added `_last_task_store_skipped` module-level counter and `get_task_store_diagnostics()` accessor.
Modified `read_tasks()` to reset and increment the counter on each call.

```python
_last_task_store_skipped: int = 0

def get_task_store_diagnostics() -> dict:
    return {
        "skipped_entries": _last_task_store_skipped,
        "status": "degraded" if _last_task_store_skipped > 0 else "ok",
    }

def read_tasks() -> list[Task]:
    global _last_task_store_skipped
    _last_task_store_skipped = 0
    tasks: list[Task] = []
    for item in _read_json_list(TASKS_PATH):
        if not isinstance(item, dict):
            _last_task_store_skipped += 1
            continue
        try:
            tasks.append(Task.from_dict(item))
        except (KeyError, TypeError, ValueError):
            _last_task_store_skipped += 1
            continue
    return tasks
```

### 2. `cli.py` — Task-store truth in ghoti-status and ghoti-recent

Imported `get_task_store_diagnostics` and added two output lines to both commands:

```
task_store_status: ok | degraded
task_store_skipped_entries: 0 | N
```

For `tasks.json=[null]`: `task_store_status: degraded`, `task_store_skipped_entries: 1`
For `tasks.json=[]`: `task_store_status: ok`, `task_store_skipped_entries: 0`

### 3. `index.html` — 5 new Truth cards + updated intake section

Added 5 new `<div class="card"><h3 class="card-title">...</h3>` blocks within `#ghoti-control-center`:
- `Runtime Truth` — task-store health, skipped/invalid entry count, runtime pipeline state
- `Supervisor Truth` — supervisor state, active task, queued/blocked/waiting counts
- `Approval Truth` — pending approval requests and gate status
- `Dashboard Truth` — dashboard server health and endpoint availability
- `Content MVP Truth` — supervised content MVP slice readiness, proof packet, human-review gate

Updated `External Repo / Skill Intake Truth` card:
- Intro text now includes verbatim: `no clone/install/run`, `no runtime wiring`, `human approval required`
- List extended with: `AirLLM`, `Vouch`, `Agent Exchange / AEX` (all intake/planning only)
- `OpenFang/MoneyPrinter` — changed from `OpenFang / MoneyPrinter` to match exact audit phrase
- Safety note extended to include all three verbatim phrases

### 4. `check_dashboard_mvp.ps1` — Extended label verification

Extended `$taskFilterUiOk` block to also check:
```powershell
$dashboardHtml -match 'Runtime Truth'
$dashboardHtml -match 'Supervisor Truth'
$dashboardHtml -match 'Approval Truth'
$dashboardHtml -match 'Dashboard Truth'
$dashboardHtml -match 'Content MVP Truth'
$dashboardHtml -match 'External Repo / Skill Intake Truth'
$dashboardHtml -match 'no clone/install/run'
$dashboardHtml -match 'no runtime wiring'
$dashboardHtml -match 'human approval required'
```

---

## Files Changed

| File | Change |
|---|---|
| `01_projects/runtime_mvp/src/super_ai_agent/storage.py` | Added `_last_task_store_skipped` counter + `get_task_store_diagnostics()` + updated `read_tasks()` |
| `01_projects/runtime_mvp/src/super_ai_agent/cli.py` | Imported `get_task_store_diagnostics`; added `task_store_status` + `task_store_skipped_entries` to `ghoti-status` and `ghoti-recent` |
| `01_projects/dashboard_mvp/public/index.html` | Added 5 Truth cards; updated intake section with new entries + verbatim phrases |
| `03_scripts/check_dashboard_mvp.ps1` | Extended `$taskFilterUiOk` check for 9 new label strings |
| `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` | Added 3 new N+4.1I diagnostic tests (13 total) |
| `14_context/claude_n4_1i_runtime_task_store_truth_polish.md` | This report |

All other files (models.py, queue.py, server.js, desktop_bridge_actions.ps1, check_runtime_mvp.ps1)
were merged from N+4.1H and remain unchanged in N+4.1I.

---

## Regression Tests Added (N+4.1I)

**`test_task_store_diagnostics_degraded_for_null_entries`**
- Patches `TASKS_PATH` to `[null]`
- Calls `read_tasks()` then `get_task_store_diagnostics()`
- Asserts `skipped_entries == 1`, `status == "degraded"`

**`test_task_store_diagnostics_ok_for_valid_entries`**
- Patches `TASKS_PATH` to valid single task
- Asserts `skipped_entries == 0`, `status == "ok"`

**`test_task_store_diagnostics_counts_mixed_null_and_valid`**
- Patches `TASKS_PATH` to `[null, null, valid, null]`
- Asserts `len(result) == 1`, `skipped_entries == 3`, `status == "degraded"`

---

## Validation Results

| Check | Result |
|---|---|
| `git diff --check HEAD` | PASS (no whitespace errors) |
| Python AST compile (5 files) | PASS |
| `node --check server.js` | PASS |
| `node --check public/app.js` | PASS |
| `python -m unittest tests.test_n4_1_runtime_reliability -v` | **13/13 OK** |
| `ghoti_readiness_check.py --status` | PASS — `supervised_mvp_slice_score: 100`, `categories_passing: 9/9` |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — 13/13 files, all gates `pending_human_review` |
| `tasks.json=[null]` → `ghoti-status` | **EXIT 0** — `task_store_status: degraded`, `task_store_skipped_entries: 1` |
| `tasks.json=[null]` → `ghoti-recent` | **EXIT 0** — `task_store_status: degraded`, `task_store_skipped_entries: 1` |
| `tasks.json=[]` → `ghoti-status` | **EXIT 0** — `task_store_status: ok`, `task_store_skipped_entries: 0` |
| Dashboard labels (14 strings) | All PRESENT in index.html |
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

## .NET Popup / Screenshot Weird-Command Result

Not observed. The command `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` was not
reproduced from any repo script during `check_runtime_mvp.ps1` or `check_dashboard_mvp.ps1` runs.
No `.NET Graphics` popup was observed. This is consistent with all prior N+4.1x audits.

---

## External Repo / Skill Intake Note

All external tools remain **intake/planning only — no clone/install/run, no runtime wiring, human approval required**:

| Tool | Status |
|---|---|
| UI-TARS | Intake/planning only, N+4.2/N+4.4 milestone |
| The Agency | Intake/planning only, N+4.2/N+4.4 milestone |
| agent-skills-eval | Intake/planning only |
| arcads-claude-code | Intake/planning only |
| Weavy | Intake/planning only |
| Manychat | Intake/planning only |
| OpenFang/MoneyPrinter | Intake/planning only |
| AirLLM | Intake/planning only |
| Vouch | Intake/planning only |
| Agent Exchange / AEX | Intake/planning only |
| Claude + MetaTrader | Intake/planning only |
| Internship scraper/application assistant | Intake/planning only |
| Ethical hacking (Linux + Claude, CTF/lab/authorized only) | Intake/planning only |
| Dolphin or local less-restricted models | Intake/planning only, school research only |

---

## Automations / Plugins / Skills Reminder

After N+4.1 is merged to main (CLEAN PASS + merge gate), evaluate:
- Claude Code automations/plugins/skills
- Repo/skill intake for the tools listed above
- External tool integration roadmap (N+4.2+)

No runtime wiring, live action, or external repo integration in N+4.1I.

---

## Safety Validation

| Check | Result |
|---|---|
| No real secrets/API keys committed | PASS |
| No live posting/upload/account actions | PASS |
| No external repo clone/install/run | PASS |
| No UI-TARS/The Agency/Weavy/Manychat/Vouch runtime wiring | PASS |
| No OpenFang/MoneyPrinter/AirLLM/AEX runtime wiring | PASS |
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
| Does N+4.1I resolve N+4.1H CONDITIONAL PASS reasons? | **Yes** — both gaps closed |
| Are invalid task entries surfaced truthfully? | **Yes** — `task_store_status: degraded`, `task_store_skipped_entries: N` |
| Does `tasks.json=[null]` survive `ghoti-status`? | **Yes — EXIT 0**, `task_store_status: degraded` |
| Does `tasks.json=[null]` survive `ghoti-recent`? | **Yes — EXIT 0**, `task_store_status: degraded` |
| Do dashboard exact labels exist? | **Yes** — all 14 required labels confirmed present |
| Does `check_runtime_mvp.ps1` pass? | **Yes — 334 PASS, 0 FAIL** |
| Does `check_dashboard_mvp.ps1` pass? | **Yes — 167 PASS, 0 FAIL** |
| Were screenshot/terminal weird-command symptoms reproduced? | **No** — not observed |
| Are external repos/tools runtime-wired? | **No** — all intake/planning only |
| Did approval gates remain intact? | **Yes** |
| Is N+3 supervised MVP still valid? | **Yes — 13/13 files, score 100, all gates pending** |
| Is this full Ghoti production 100%? | **No — `production_public_release_ready: False` by design** |

---

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

Exact next action: **run Codex N+4.1I real audit** against
`feat/ghoti-agent-claude-n4-1i-runtime-task-store-truth-polish`
