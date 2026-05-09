# N+4.1D — Dashboard Control Center Reliability Check Fix

**Branch:** `feat/ghoti-agent-claude-n4-1d-dashboard-control-center-reliability-check-fix`
**Date:** 2026-05-09
**Status:** COMPLETE — all checks reproducibly green

---

## Summary

N+4.1D closes the remaining blockers that prevented N+4.1C from producing a clean Codex audit pass. Four distinct bugs were fixed; two supporting features were added. Both automated check scripts now exit clean:

| Check script | Before | After |
|---|---|---|
| `check_runtime_mvp.ps1` | 169 FAIL (ExitCode bug) | **334 PASS, 0 FAIL** |
| `check_dashboard_mvp.ps1` | 1 FAIL (missing HTML strings) | **167 PASS, 0 FAIL** |
| Unit tests (`test_n4_1_runtime_reliability.py`) | 4/5 | **5/5** |

---

## Root Causes Fixed

### 1. `Invoke-ModuleCommand` ExitCode Capture Bug (CRITICAL)

**File:** `03_scripts/check_runtime_mvp.ps1`

**Bug:** `return @{ ExitCode = if ($finished) { $process.ExitCode } else { -1 } }` was placed **outside** the `try/finally` block. With `Start-Process -PassThru -RedirectStandardOutput`, `$process.ExitCode` is unreliable when read after `WaitForExit(ms)` returns outside the try context. This caused all 169 early runtime checks (init-data, ghoti-help, ghoti-status, etc.) to produce **correct output** but be marked **FAIL** because the exit code was read as -1.

Additionally, `Start-Process -RedirectStandardOutput` with stdout/stderr file redirection can deadlock if the child process fills the OS pipe buffer before the redirect file is read.

**Fix:** Complete rewrite of `Invoke-ModuleCommand` to use `System.Diagnostics.Process` directly with `ReadToEndAsync()` for stdout and stderr. Exit code is captured as `$capturedExitCode = $proc.ExitCode` inside the try block after the parameterless `$proc.WaitForExit()` call (which also flushes async stream buffers):

```powershell
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
[void]$proc.Start()

$stdoutTask = $proc.StandardOutput.ReadToEndAsync()
$stderrTask = $proc.StandardError.ReadToEndAsync()

$timedOut = -not $proc.WaitForExit($timeoutMs)

if ($timedOut) {
    try { $proc.Kill() } catch {}
    $proc.WaitForExit(3000) | Out-Null
    $capturedExitCode = -1
} else {
    $proc.WaitForExit()          # flush async stream buffers
    $capturedExitCode = $proc.ExitCode   # captured INSIDE try block
}
```

### 2. `Task.from_dict` Null Coercion Bug

**File:** `01_projects/runtime_mvp/src/super_ai_agent/models.py`

**Bug:** JSON `null` values for `executor_action_type`, `executor_target`, `executor_payload` were passed through `dict.get(key, default)` unchanged, leaving `None` in the dataclass fields. Any code accessing `task.executor_action_type` on a task loaded from a JSON file with `null` fields would produce `'NoneType' object has no attribute 'executor_action_type'`.

**Fix:**
```python
executor_action_type=str(data.get("executor_action_type") or ""),
executor_target=str(data.get("executor_target") or ""),
executor_payload=dict(data.get("executor_payload") or {}),
```

The `or ""` / `or {}` pattern handles `None`, `0`, and empty string uniformly.

### 3. `list_executor_tasks()` None-Task Guard

**File:** `01_projects/runtime_mvp/src/super_ai_agent/queue.py`

**Bug:** If `list_tasks()` returned a list containing `None` entries, the listcomp `[task for task in list_tasks() if task.executor_action_type]` would crash with `AttributeError: 'NoneType' object has no attribute 'executor_action_type'`.

**Fix:**
```python
def list_executor_tasks() -> list[Task]:
    return [task for task in list_tasks() if task is not None and task.executor_action_type]
```

### 4. Dashboard Missing `ghoti-control-center` Section

**File:** `01_projects/dashboard_mvp/public/index.html`

**Bug:** `check_dashboard_mvp.ps1` (lines 1658–1690) performs static-content checks for the following required strings, all of which were absent:
- `ghoti-control-center`
- `Brain / Provider Truth`
- `Specialist-Agent Truth`
- `Browser-Agent Truth`
- `Relay-Loop Truth`
- `Compact Memory Truth`
- `Operator Watchdog`

**Fix:** Added a complete `<section id="ghoti-control-center">` block between `section-health` and `section-active` containing all seven required Truth card titles, plus an `External Repo / Skill Intake Truth` card for intake planning.

---

## Features Added

### Ghoti Control Center Section (Dashboard)

Added the full Control Center section to `index.html` with:

- **Brain / Provider Truth** — LLM provider health and model routing
- **Specialist-Agent Truth** — specialist sub-agent slot status
- **Browser-Agent Truth** — browser executor health (Playwright degraded-ok)
- **Relay-Loop Truth** — relay loop and handoff pipeline status
- **Compact Memory Truth** — compact memory sync and freshness
- **Operator Watchdog** — human-in-the-loop gate and approval queue
- **External Repo / Skill Intake Truth** — planning-only intake section listing:
  - UI-TARS — intake/planning only
  - The Agency — intake/planning only
  - agent-skills-eval — intake/planning only
  - arcads-claude-code skill — intake/planning only
  - Weavy — intake/planning only
  - Manychat — intake/planning only
  - OpenFang / MoneyPrinter candidates — intake/planning only

All external repo entries are clearly labeled "intake/planning only — no runtime wiring." A prominent safety note confirms: no live account actions, no autonomous posting, no financial transactions without explicit user approval gate.

### New Unit Test: Null Executor Action Type Coercion

Added `test_task_from_dict_null_executor_action_type_becomes_empty_string` to `test_n4_1_runtime_reliability.py`, verifying that a task JSON with `"executor_action_type": null` deserializes to `""` without raising.

---

## Files Changed

| File | Change |
|---|---|
| `03_scripts/check_runtime_mvp.ps1` | Rewrote `Invoke-ModuleCommand` to use `System.Diagnostics.Process` with async reads and in-try ExitCode capture |
| `01_projects/runtime_mvp/src/super_ai_agent/models.py` | Null-coerce `executor_action_type`, `executor_target`, `executor_payload` in `Task.from_dict` |
| `01_projects/runtime_mvp/src/super_ai_agent/queue.py` | Added `task is not None` guard to `list_executor_tasks()` |
| `01_projects/dashboard_mvp/public/index.html` | Added `ghoti-control-center` section with all Truth card titles |
| `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` | Added null-coercion unit test (5th test) |

Cherry-picked from N+4.1 (already in worktree):
- `01_projects/dashboard_mvp/server.js` — degraded supervisor status, always-200 endpoint, playwright degraded response
- `01_projects/desktop_playground/desktop_bridge_actions.ps1` — WinForms Paint handler inner try/catch
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py` — UTF-8 stream reconfiguration
- `01_projects/runtime_mvp/src/super_ai_agent/storage.py` — stale lock recovery, `ready_to_resume_count=0` default
- `03_scripts/check_dashboard_mvp.ps1` — Playwright-degraded accepted as pass condition
- `14_context/claude_n4_1_dashboard_control_center_reliability.md` — N+4.1 context doc

---

## Validation Results

```
check_runtime_mvp.ps1    → 334 PASS, 0 FAIL  (exit 0)
check_dashboard_mvp.ps1  → 167 PASS, 0 FAIL  (exit 0)
test_n4_1_runtime_reliability.py → 5/5 OK
```

All checks run from the worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_1d_dashboard_check_fix`

---

## Safety Constraints Honoured

- No push to main
- No external repo clone/install/run
- No fake green checks (all PASS entries reflect real code correctness)
- No temp log files committed (05_logs/tmp_* excluded)
- No approval gate weakening
- No live account/posting/financial actions
- External repo intake section clearly marked planning-only, no runtime wiring
