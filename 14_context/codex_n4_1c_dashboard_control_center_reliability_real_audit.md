# Codex N+4.1C Dashboard Control Center Reliability Real Audit

Audit branch: `audit/ghoti-agent-codex-n4-1c-dashboard-control-center-reliability-real-audit`

Audit worktree: `C:\w\n4_1c_audit`

Target branch: `origin/feat/ghoti-agent-claude-n4-1-dashboard-control-center-reliability`

Target commit audited: `26cbd42cc5f4daeca5d968060feeacd3f85cafed`

Base main commit: `cdedf6087ed9bb69b33981436840dbd1c2598b03`

Final verdict: `BLOCKED`

## Executive Result

Codex verified that the real N+4.1 implementation branch exists remotely at the expected commit and merges cleanly into current `origin/main`.

The implementation fixes several important runtime/dashboard reliability issues:

- `SupervisorState.ready_to_resume_count` is defaulted for old/missing state.
- `/api/supervisor/status` returns HTTP 200 with truthful degraded JSON for corrupt supervisor state instead of 500.
- Browser dependency absence is represented as `dependency_missing` / degraded rather than a hard server crash.
- Desktop bridge subprocess actions now have a 30 second timeout.
- WinForms Paint handler errors are caught in `desktop_bridge_actions.ps1`.
- N+3 supervised content MVP validation still passes.

However, the branch is not clean-pass merge-ready because required validation scripts did not reproduce Claude's reported green state:

- `03_scripts/check_runtime_mvp.ps1` exited non-zero with `169 runtime MVP check(s) failed`.
- `03_scripts/check_dashboard_mvp.ps1` exited non-zero with `1 dashboard check(s) failed`.
- Claude's report says `check_dashboard_mvp.ps1` was `85 PASS / 0 FAIL`, but Codex observed a failing UI static check.

This is a reliability/check-contract blocker, not a safety violation.

## Ref Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Remote target exists | PASS | `git ls-remote` and `git rev-parse` resolved target branch. |
| Target commit expected | PASS | Target resolved to `26cbd42cc5f4daeca5d968060feeacd3f85cafed`. |
| Base main current | PASS | `origin/main` resolved to `cdedf6087ed9bb69b33981436840dbd1c2598b03`. |
| Target based on main | PASS | `git merge-base --is-ancestor origin/main target` exited `0`. |
| No-commit merge into main | PASS | `git merge --no-commit --no-ff target` completed with no conflicts. |
| Merge aborted before audit commit | PASS | Audit worktree returned clean to `origin/main` before this report was written. |

## Changed Files Audited

Target branch changed 10 files:

- `01_projects/dashboard_mvp/public/index.html`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/desktop_playground/desktop_bridge_actions.ps1`
- `01_projects/runtime_mvp/src/super_ai_agent/cli.py`
- `01_projects/runtime_mvp/src/super_ai_agent/queue.py`
- `01_projects/runtime_mvp/src/super_ai_agent/storage.py`
- `01_projects/runtime_mvp/tests/test_n4_1_runtime_reliability.py`
- `03_scripts/check_dashboard_mvp.ps1`
- `03_scripts/check_runtime_mvp.ps1`
- `14_context/claude_n4_1_dashboard_control_center_reliability.md`

Note: the changed desktop bridge path is `01_projects/desktop_playground/desktop_bridge_actions.ps1`, not `03_scripts/desktop_bridge_actions.ps1`.

## Validation Table

| Validation | Result | Notes |
| --- | --- | --- |
| `git diff --check` / staged diff check during merge | PASS | No whitespace errors found. |
| `git show --check --stat target` | PASS | Target commit whitespace check clean. |
| Python AST parse for changed Python files | PASS | `cli.py`, `queue.py`, `storage.py`, and new test file parsed. |
| Node syntax check | PASS | `server.js` and `public/app.js` passed `node --check`. |
| JSON config parse | PASS | Relevant N+3/N+4 configs parsed successfully. |
| Pytest | CONDITIONAL | `pytest` unavailable in audit environment: `No module named pytest`. |
| Unit test fallback | PASS | `PYTHONPATH=01_projects/runtime_mvp/src; python -m unittest ...test_n4_1_runtime_reliability` ran 4 tests, all passed. |
| `ghoti_readiness_check.py --status` | PASS | `supervised_mvp_slice_score: 100`, `categories_passing: 9/9`, public release false. |
| `supervised_content_mvp_runner.py --validate-latest` | PASS | 13/13 proof packet files present; safety gates pending human review. |
| `agent_lane_status.py --check` | PASS | Lane files valid. |
| Safety scan over target diff | PASS | Hits were approval/dependency docs and guardrail strings; no active secrets, live posting, clone/install, or runtime wiring found. |
| Claude report accuracy | FAIL | Report claims all checks pass; Codex did not reproduce green PowerShell checks. |

## PowerShell And Check Script Table

| Command | Result | Evidence |
| --- | --- | --- |
| `powershell -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | FAIL | Exited `1`; summary reported `169 runtime MVP check(s) failed`. |
| `powershell -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | FAIL | Exited `1`; summary reported `1 dashboard check(s) failed`. |
| Runtime check hang behavior | PASS | Script returned after about 138 seconds; no indefinite hang observed. |
| Dashboard check hang behavior | PASS | Script returned after about 195 seconds; no indefinite hang observed. |
| Blocking `.NET Graphics` popup | PASS_WITH_OBSERVATION | No blocking GUI exception dialog required interaction during Codex runs. |

### Runtime Check Failure Detail

`check_runtime_mvp.ps1` is still not green. The audit observed a non-zero exit and `169 runtime MVP check(s) failed`.

Representative failure text included:

- `CLI ghoti-status: error: 'NoneType' object has no attribute 'executor_action_type'`
- `CLI ghoti-recent: error: 'NoneType' object has no attribute 'executor_action_type'`

Focused direct CLI reruns later succeeded for `ghoti-status`, `ghoti-recent`, `supervisor-status`, and `status`, so the failure may be state/setup/order sensitive. That does not make the branch merge-ready: the required runtime check script remains red and must be made reproducibly green.

### Dashboard Check Failure Detail

`check_dashboard_mvp.ps1` is also not green. It failed this assertion:

- `Dashboard task filter controls are present for noise reduction`
- Detail: `task filter controls missing from dashboard HTML`

The audit compared the checker's expected strings with `public/index.html`. Missing strings include:

- `ghoti-control-center`
- `Brain / Provider Truth`
- `Specialist-Agent Truth`
- `Browser-Agent Truth`
- `Relay-Loop Truth`
- `Compact Memory Truth`

The branch therefore does not reproduce Claude's reported `85 PASS / 0 FAIL`.

## Dashboard And Runtime Reliability Table

| Area | Result | Evidence |
| --- | --- | --- |
| `SupervisorState.ready_to_resume_count` crash | PASS | `storage.py` now defaults old/missing state to `ready_to_resume_count=0`; unit test covers old JSON. |
| Default supervisor state | PASS | `_default_supervisor_state()` includes `ready_to_resume_count=0`. |
| `/api/supervisor/status` known crash path | PASS | Corrupt `supervisor_state.json` test returned HTTP `200` with `status=degraded`, `ok=false`, `degraded=true`. |
| Missing/corrupt state truthfulness | PASS | Corrupt state headline included parse error instead of fake green. |
| Request-level async server errors | PASS_BY_SOURCE | `http.createServer` wraps `handleRequest(...).catch(...)`; request errors should not kill server. |
| Browser dependency missing | PASS | `runBrowserDemo()` reports `missingDependency: playwright` and degraded status instead of hard failure. |
| Stale lock recovery | PASS_BY_SOURCE_AND_TEST | `_try_clear_stale_runtime_lock()` only clears dead-owner/no-owner stale locks; unit tests pass. |
| Desktop bridge timeout | PASS_BY_SOURCE_AND_TEST | `subprocess.run(... timeout=30)` and unit test confirm timeout kwarg. |
| CLI UTF-8/control-character robustness | PASS_BY_SOURCE | `cli.py` reconfigures streams to UTF-8 with replacement behavior. |
| Dashboard static UI check contract | FAIL | Checker expects UI labels/IDs missing from `index.html`. |

## N+3 Regression Table

| N+3 Requirement | Result | Evidence |
| --- | --- | --- |
| Proof packet still exists | PASS | Latest proof packet validated. |
| `supervised_mvp_slice_score` remains 100 | PASS | Readiness status and proof packet validation both report 100 for supervised MVP slice only. |
| `production_public_release_ready` remains false | PASS | Readiness command reports `False`; proof packet validation confirms no public release claim. |
| `live_posting_enabled` remains false | PASS | Proof packet manifest still reports no live posting. |
| Human approval gates remain pending | PASS | Proof packet validation reports all five gates `pending_human_review`. |

## Safety Table

| Safety Area | Result | Notes |
| --- | --- | --- |
| Live posting/account/money action | PASS | No active behavior found. |
| External repo clone/install/run | PASS | No active clone/install/run behavior found in target diff. |
| Ruflo/OpenFang/MoneyPrinter runtime wiring | PASS | No runtime wiring introduced by this branch. |
| Secrets/API keys | PASS | No real secrets/API keys found in changed files. |
| Approval gates | PASS | UI/report preserve approval and no-delete language; no weakening found. |
| Hidden fake green behavior | CONDITIONAL | Endpoint degraded handling is truthful, but check reports are not green. |

## Documentation Check

Claude report file exists:

- `14_context/claude_n4_1_dashboard_control_center_reliability.md`

Documentation gap:

- It states `Status: COMPLETE — All checks pass`.
- It states `check_dashboard_mvp.ps1` was `85 PASS / 0 FAIL`.
- Codex observed `check_dashboard_mvp.ps1` fail with `1 dashboard check(s) failed`.
- Codex observed `check_runtime_mvp.ps1` fail with `169 runtime MVP check(s) failed`.

The report needs correction after the fix branch reruns the same checks Codex ran.

## Direct Answers

Is `SupervisorState.ready_to_resume_count` crash fixed?

- Mostly yes. Code and unit tests show old/missing supervisor state defaults `ready_to_resume_count` to `0`.

Does `/api/supervisor/status` avoid 500?

- Yes for the tested corrupt supervisor state path. The endpoint returned HTTP `200` with truthful degraded JSON.

Do runtime/dashboard checks pass?

- No. `check_runtime_mvp.ps1` and `check_dashboard_mvp.ps1` both exited non-zero in the Codex audit.

Do automated checks avoid blocking GUI popups?

- No blocking `.NET Graphics` popup was observed. The scripts returned normally, though with failing exit codes.

Is missing/corrupt runtime state handled gracefully?

- Yes for the tested corrupt `supervisor_state.json`: stable HTTP `200`, `ok=false`, `status=degraded`.

Is stale lock recovery safe?

- Appears yes by source inspection and unit tests. It targets stale/dead-owner locks and avoids clearing active owner locks.

Did approval gates remain intact?

- Yes. No approval weakening found.

Were live posting/account/money actions enabled?

- No.

Was external repo runtime wired?

- No.

Are secrets/API keys present?

- No evidence of real secrets/API keys in changed files.

Is N+3 supervised MVP still valid?

- Yes. N+3 readiness/proof packet validation still passes.

Is merge to main recommended?

- No. Merge is blocked until required runtime/dashboard check scripts are reproducibly green and the Claude report matches observed results.

## Required Fix Before Merge

Recommended next branch:

`feat/ghoti-agent-claude-n4-1d-dashboard-control-center-reliability-check-fix`

Fix list:

1. Reproduce `powershell -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` from a clean checkout and fix the `169` failures, including the state/order-sensitive `NoneType.executor_action_type` failures.
2. Reproduce `powershell -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` and fix the missing dashboard static contract strings or update the checker if those labels were intentionally renamed.
3. Keep `/api/supervisor/status` degraded behavior truthful; do not fake green.
4. Keep Playwright absence as `dependency_missing` / degraded, not a hard failure.
5. Rerun N+3 regression commands:
   - `python 03_scripts/ghoti_readiness_check.py --status`
   - `python 03_scripts/supervised_content_mvp_runner.py --validate-latest`
6. Update `14_context/claude_n4_1_dashboard_control_center_reliability.md` with the actual final validation results.

## Final Verdict

`BLOCKED`

The branch is directionally good and fixes the core supervisor endpoint crash path, but it is not merge-ready because the required PowerShell checks are red and the implementation report overstates validation success.
