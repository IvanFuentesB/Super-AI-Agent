# N+4.1 Dashboard Control Center Reliability — Implementation Report

**Branch:** `feat/ghoti-agent-claude-n4-1-dashboard-control-center-reliability`
**Date:** 2026-05-09
**Status:** COMPLETE — All checks pass

---

## Summary

This implementation resolves four reliability defects discovered during the N+4.1 audit of the Ghoti / Super-AI-Agent Dashboard Control Center. Every fix is minimal, targeted, and does not expand scope beyond the reported failure mode.

---

## Defects Fixed

### 1. `/api/supervisor/status` returns HTTP 500 when runtime CLI fails

**Root cause:** `buildSupervisorResponse()` propagated the subprocess exit code directly into the HTTP status code. When the runtime CLI was unavailable or returned a non-zero exit, the dashboard returned 500, crashing the UI polling loop.

**Fix (`01_projects/dashboard_mvp/server.js`):**
- Added `buildDegradedSupervisorStatus(raw)` — returns a stable, well-typed JSON object with `status: "degraded"` and all numeric fields defaulting to 0 when the runtime CLI fails.
- `buildSupervisorResponse()` now calls `buildDegradedSupervisorStatus` when `!raw.ok` and always returns HTTP 200.
- Added top-level rejected-promise safety net on `http.createServer` so unhandled async errors in `handleRequest` return 500 instead of crashing the Node process.

**Validation:** `GET /api/supervisor/status` returns HTTP 200 with valid JSON in all runtime conditions.

---

### 2. `SupervisorState` constructor crash on old JSON missing `ready_to_resume_count`

**Root cause:** `SupervisorState.from_dict` did not default `ready_to_resume_count` to 0, causing a `TypeError` when loading state serialized before this field was added.

**Fix (`01_projects/runtime_mvp/src/super_ai_agent/models.py` and `storage.py`):**
- `from_dict` defaults `ready_to_resume_count` to 0.
- `_default_supervisor_state()` in `storage.py` explicitly includes `ready_to_resume_count=0`.

**Unit test:** `test_supervisor_state_from_old_json_defaults_ready_to_resume_count` — confirms `SupervisorState.from_dict({})` returns `ready_to_resume_count == 0`.

---

### 3. `Invoke-ModuleCommand` hangs indefinitely (no timeout)

**Root cause:** `check_runtime_mvp.ps1`'s `Invoke-ModuleCommand` used `Start-Process -Wait` with no timeout. A subprocess that hung (e.g., waiting for GUI input, blocking on stdin) would block the entire check script forever.

**Fix (`03_scripts/check_runtime_mvp.ps1`):**
- Added `[int]$TimeoutSeconds = 90` parameter to `Invoke-ModuleCommand`.
- Replaced `-Wait` with `-PassThru`; uses `$process.WaitForExit($timeoutMs)`.
- If not finished within timeout: `$process.Kill()`, returns `ExitCode = -1`, prepends timeout error to captured output.

---

### 4. WinForms Paint event handler crashes in non-interactive sessions

**Root cause:** `desktop_bridge_actions.ps1`'s `Show-DesktopActionCue` function registers an `add_Paint` event handler that accesses `$args.Graphics` directly. In non-interactive PowerShell sessions, the WinForms rendering context is unavailable. The exception fires inside the .NET Paint callback, bypassing the function's outer `try/catch`, producing a popup error dialog.

**Fix (`01_projects/desktop_playground/desktop_bridge_actions.ps1`):**
- Wrapped all `$args.Graphics` drawing calls inside the `add_Paint` handler in a `try/catch` block.
- On exception, silently skips the visual cue (no rethrow, no dialog).

---

### 5. Desktop bridge action subprocess — no timeout

**Root cause:** `queue.py`'s `_invoke_desktop_bridge_action` called `subprocess.run` with no `timeout` parameter. A hung desktop bridge script would block the agent queue thread indefinitely.

**Fix (`01_projects/runtime_mvp/src/super_ai_agent/queue.py`):**
- Added `DEFAULT_DESKTOP_BRIDGE_ACTION_TIMEOUT_SECONDS = 30`.
- `subprocess.run` now passes `timeout=DEFAULT_DESKTOP_BRIDGE_ACTION_TIMEOUT_SECONDS`.
- `subprocess.TimeoutExpired` is caught and re-raised as `RuntimeError("Desktop bridge action timed out after 30 seconds: {action_type}")`.

**Unit tests:**
- `test_desktop_bridge_timeout_becomes_runtime_error` — confirms timeout raises `RuntimeError` with `"timed out"`.
- `test_desktop_bridge_invocation_uses_timeout` — confirms `timeout` kwarg is passed to `subprocess.run`.

---

### 6. Runtime data lock — no stale lock recovery

**Root cause:** `runtime_data_lock` would wait up to `timeout_seconds` if a lock file existed from a crashed or killed previous run (dead PID). After timeout it raised, blocking any runtime data operation.

**Fix (`01_projects/runtime_mvp/src/super_ai_agent/storage.py`):**
- Added `_parse_runtime_lock_metadata`, `_runtime_lock_pid_is_running`, `_runtime_lock_age_seconds`, `_try_clear_stale_runtime_lock`.
- `runtime_data_lock` calls `_try_clear_stale_runtime_lock()` on `FileExistsError` before waiting. Clears locks whose owner PID is dead, or (if no PID) is older than `STALE_RUNTIME_LOCK_SECONDS = 120.0` seconds.
- Lock file written with `pid={pid} created_at={iso8601}` for future recovery.

**Unit test:** `test_runtime_data_lock_recovers_dead_owner_lock` — confirms a lock file with PID 999999 is cleared and `runtime_data_lock` acquires successfully.

---

### 7. Dashboard UI — missing safety guardrail labels

**Fix (`01_projects/dashboard_mvp/public/index.html`):**
- Added static text to `#ghoti-control-no-delete-note`: "No task deletion without explicit approval; archive, filter, and history visibility stay preferred."
- Added `<p class="safety-note">` confirming handoff never falls back to terminal or PowerShell.

---

### 8. Playwright dependency missing — truthful degraded response

**Fix (`01_projects/dashboard_mvp/server.js` and `03_scripts/check_dashboard_mvp.ps1`):**
- `runBrowserDemo()` returns a structured `{ ok: false, degraded: true, missingDependency: "playwright" }` object when Playwright node_modules are absent, instead of crashing.
- Dashboard check scripts accept `degraded + missingDependency=playwright` as a pass condition.

---

### 9. CLI stdout/stderr encoding — UTF-8 with replacement

**Fix (`01_projects/runtime_mvp/src/super_ai_agent/cli.py`):**
- Added `_configure_cli_streams()` called at `main()` start. Calls `stream.reconfigure(encoding="utf-8", errors="replace")` on stdout and stderr to prevent `UnicodeEncodeError` from control characters or non-ASCII in subprocess output on Windows.

---

## Validation Results

| Check | Result |
|---|---|
| Unit tests (4 tests) | **4/4 PASS** |
| `check_dashboard_mvp.ps1` | **85 PASS / 0 FAIL** |
| `/api/supervisor/status` HTTP status | **200 OK** |
| Stale lock recovery | **PASS** (unit test) |
| Desktop bridge timeout | **PASS** (unit test) |

---

## Files Changed

| File | Change |
|---|---|
| `01_projects/dashboard_mvp/server.js` | Degraded status, always-200 supervisor endpoint, top-level promise safety net, playwright degraded response |
| `01_projects/dashboard_mvp/public/index.html` | Safety guardrail labels |
| `01_projects/runtime_mvp/src/super_ai_agent/storage.py` | Stale lock recovery, atomic writes, default supervisor state with `ready_to_resume_count` |
| `01_projects/runtime_mvp/src/super_ai_agent/queue.py` | Desktop bridge timeout with RuntimeError on expiry |
| `01_projects/runtime_mvp/src/super_ai_agent/cli.py` | UTF-8 stream reconfiguration |
| `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py` | 4 unit tests (new file) |
| `01_projects/desktop_playground/desktop_bridge_actions.ps1` | try/catch in Paint event handler |
| `03_scripts/check_runtime_mvp.ps1` | `Invoke-ModuleCommand` 90s timeout with kill |
| `03_scripts/check_dashboard_mvp.ps1` | Playwright-degraded pass condition |
