# Codex N+4.1H Runtime Task-Store Null Hardening Audit

## Executive Verdict

Final verdict: **CONDITIONAL PASS**

The target branch was missing through the required initial check plus 12 polling attempts, so Codex first committed a `BLOCKED_REMOTE_REF_MISSING` diagnostic. Immediately after that diagnostic push, the target branch appeared remotely. Codex did not stop on stale missing-branch evidence; it fetched the new ref, verified remote/local hash agreement, ran a no-commit merge rehearsal, and audited the real target commit.

The core N+4.1G blocker is fixed: `tasks.json=[null]`, non-dict task-store entries, and malformed partial task dicts no longer crash `ghoti-status` or `ghoti-recent`. `check_runtime_mvp.ps1` and `check_dashboard_mvp.ps1` both pass.

The audit is not a clean pass because two non-safety but real audit gaps remain:

1. Invalid task-store entries are silently skipped rather than surfaced as degraded/skipped/quarantined status. This avoids crashes and does not fake bad entries as valid tasks, but it does not fully meet the prompt's "report degraded/skipped/quarantined or truthful handling" language.
2. Several exact dashboard label strings requested by the audit prompt remain absent verbatim, even though the safety/intake content is semantically present.

## Branches And Commits

| Field | Value |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-1h-runtime-task-store-null-hardening` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening` |
| Target remote ref | `refs/heads/feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening` |
| `ls-remote` target hash | `35316c1841fb13ed9c199adda8726ea8b7e480ef` |
| Local fetched target hash | `35316c1841fb13ed9c199adda8726ea8b7e480ef` |
| Target commit audited | `35316c1841fb13ed9c199adda8726ea8b7e480ef` |
| Base main commit | `cdedf6087ed9bb69b33981436840dbd1c2598b03` |
| Expected Claude report | `14_context/claude_n4_1h_runtime_task_store_null_hardening.md` present |

Target log excerpt:

```text
35316c1 fix(ghoti): harden runtime task store against null entries (N+4.1H)
f7c667f merge(ghoti): bring N+4.1F into N+4.1H null-hardening branch
5ec799f fix(ghoti): harden runtime task state for N+4.1 checks
73ecf45 docs(ghoti): add remote push verification section to N+4.1D report
fbc9812 fix(ghoti): stabilize N+4.1 dashboard reliability checks
cdedf60 docs(ghoti): add N+3.72B final main merge gate report
```

## Polling Attempts

| Attempt | Target Ref Result | Nearby Branch Result |
| --- | --- | --- |
| Initial | empty | Prior N+4.1 audit/feature/report branches only |
| 1 | empty | No N+4.1H/null-hardening branch |
| 2 | empty | No N+4.1H/null-hardening branch |
| 3 | empty | No N+4.1H/null-hardening branch |
| 4 | empty | No N+4.1H/null-hardening branch |
| 5 | empty | No N+4.1H/null-hardening branch |
| 6 | empty | No N+4.1H/null-hardening branch |
| 7 | empty | No N+4.1H/null-hardening branch |
| 8 | empty | No N+4.1H/null-hardening branch |
| 9 | empty | No N+4.1H/null-hardening branch |
| 10 | empty | No N+4.1H/null-hardening branch |
| 11 | empty | No N+4.1H/null-hardening branch |
| 12 | empty | No N+4.1H/null-hardening branch |
| Post-diagnostic recheck | `35316c1841fb13ed9c199adda8726ea8b7e480ef` | Target branch appeared |

Polling commands used:

```text
git ls-remote origin refs/heads/feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening
git fetch origin --prune
git ls-remote --heads origin | findstr /i "n4-1h n4-1 runtime-task-store null-hardening"
```

## Merge Rehearsal

| Check | Result | Evidence |
| --- | --- | --- |
| Isolated worktree | PASS | `C:\w\n4_1h_audit` |
| Primary worktree untouched | PASS | Primary was read-only inspected only |
| No-commit merge | PASS | `git merge --no-commit --no-ff origin/feat/ghoti-agent-claude-n4-1h-runtime-task-store-null-hardening` |
| Conflicts | PASS | No conflicts |
| Merge aborted before audit commit | PASS | Implementation changes were not committed on audit branch |

Changed files observed in merge rehearsal:

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
- `14_context/claude_n4_1h_runtime_task_store_null_hardening.md`

No `05_logs/tmp_n4_1_*.txt`, runtime data/log artifacts, `.env`, secrets, node_modules, output folders, or generated logs were staged by the target merge.

## N+4.1G Blocker Resolution

| N+4.1G Finding | N+4.1H Result | Evidence |
| --- | --- | --- |
| `tasks.json=[null]` crashed `ghoti-status` | FIXED | Fixture exits 0 |
| `tasks.json=[null]` crashed `ghoti-recent` | FIXED | Fixture exits 0 |
| Non-dict task-store entries | FIXED | `null`, number, string, and array entries exit 0 |
| Malformed partial task dict | FIXED | `{"task_id":"legacy-partial"}` exits 0 |
| Invalid entries not faked as valid tasks | PASS | CLI reports idle/normal task summary rather than rendering invalid task rows |
| Invalid entries surfaced as skipped/degraded | CONDITIONAL GAP | Entries are silently dropped; no skipped count/degraded warning is surfaced |

## Specific Fixture Verification

Backup-and-restore fixtures were run inside the isolated audit worktree against `01_projects/runtime_mvp/runtime_data/tasks.json`.

| Fixture | `ghoti-status` | `ghoti-recent` | Evidence |
| --- | --- | --- | --- |
| `[null]` | PASS, exit 0 | PASS, exit 0 | `CASE=null_only STATUS_EXIT=0 RECENT_EXIT=0` |
| `[null, 123, "legacy-string", ["bad-array"]]` | PASS, exit 0 | PASS, exit 0 | `CASE=non_dict_mixed STATUS_EXIT=0 RECENT_EXIT=0` |
| `[{"task_id":"legacy-partial"}]` | PASS, exit 0 | PASS, exit 0 | `CASE=malformed_partial_dict STATUS_EXIT=0 RECENT_EXIT=0` |
| Restored original task store | PASS, exit 0 | PASS, exit 0 | `RESTORED_STATUS_EXIT=0`, `RESTORED_RECENT_EXIT=0` |

Direct `Task.from_dict(None)` still raises:

```text
TypeError: 'NoneType' object is not subscriptable
```

This is acceptable only if `Task.from_dict()` remains an internal raw parser and all file-loading boundaries keep the new storage guard. For a clean contract, prefer a typed `ValueError` or explicit parser documentation/test.

## Implementation Quality

Source inspection confirms:

- `storage.py::read_tasks()` now skips non-dict entries and catches `KeyError`, `TypeError`, and `ValueError` from `Task.from_dict()`.
- `storage.py::read_approvals()` and `read_approval_requests()` received the same guard for consistency.
- `queue.py::list_executor_tasks()` still skips `None` tasks.
- `cli.py::_classify_executor_task()` still handles `task=None` via `getattr`, preserving the N+4.1F fix.
- The new test suite includes null-entry, mixed valid/null, and malformed-dict regression tests.

The main weakness is observability: bad entries disappear silently rather than incrementing an invalid/skipped task count or adding a degraded note.

## Validation Table

| Validation | Result | Evidence |
| --- | --- | --- |
| `git diff --check` | PASS | No whitespace errors |
| `git diff --cached --check` | PASS | No staged whitespace errors |
| `git show --check --stat origin/...n4-1h...` | PASS | Target commit check/stat succeeded |
| Python AST/compile for changed Python files | PASS | `models.py`, `storage.py`, `queue.py`, `cli.py`, test file parsed |
| `python -m pytest ...test_n4_1_runtime_reliability.py` | ENV GAP | `pytest` unavailable: `No module named pytest` |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_1_runtime_reliability` | PASS | 10 tests ran, 10 passed |
| `python 03_scripts/ghoti_readiness_check.py --status` | PASS | 9/9 categories PASS; supervised MVP score 100 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | PASS | 13/13 files; all gates pending human review |
| `03_scripts/check_runtime_mvp.ps1` | PASS | Exit 0, about 144.7s, runtime MVP checks passed |
| `03_scripts/check_dashboard_mvp.ps1` | PASS | Exit 0, about 177.1s, dashboard MVP checks passed |
| `node --check 01_projects/dashboard_mvp/server.js` | PASS | Syntax OK |
| `node --check 01_projects/dashboard_mvp/public/app.js` | PASS | Syntax OK |

## Runtime Checker Table

| Runtime Check | Result | Evidence |
| --- | --- | --- |
| `ghoti-status` normal restored state | PASS | Exit 0 |
| `ghoti-recent` normal restored state | PASS | Exit 0 |
| `ghoti-status` with null-only task store | PASS | Exit 0 |
| `ghoti-recent` with null-only task store | PASS | Exit 0 |
| Empty/focus-task watchdog path | PASS | N+4.1F `getattr` fix preserved |
| Runtime checker | PASS | `Summary: runtime MVP checks passed.` |
| Weird terminal command symptom | NOT OBSERVED | No `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` process/output observed |
| Blocking .NET GUI popup | NOT OBSERVED | No popup observed during runtime/dashboard checks |

## Dashboard Checker Table

| Dashboard Check | Result | Evidence |
| --- | --- | --- |
| Dashboard checker | PASS | `Summary: dashboard MVP checks passed.` |
| Dashboard server start | PASS | `http://127.0.0.1:3211/api/health` |
| Supervisor endpoint | PASS | `Supervisor status endpoint: 3 approval request(s) need review.` |
| Browser dependency missing | PASS | Browser smoke reports Playwright missing as unavailable/degraded, not 500 |
| Exact `ghoti-control-center` string | PASS | Present |
| Exact truth labels | PARTIAL | Present: Local Brain, Brain / Provider, Specialist-Agent, Browser-Agent, Relay-Loop, Compact Memory, Operator Watchdog, External Repo / Skill Intake. Missing exact: Runtime, Supervisor, Approval, Dashboard, Content MVP |
| External intake exact compact phrases | PARTIAL | Semantics present, but exact strings `OpenFang/MoneyPrinter`, `no clone/install/run`, `no runtime wiring`, `human approval required` were not all present verbatim |

## External Repo / Skill Safety

| Tool / Direction | Result | Notes |
| --- | --- | --- |
| UI-TARS | PASS | Planning/intake mention only; no clone/install/run |
| The Agency | PASS | Planning/intake mention only; no clone/install/run |
| agent-skills-eval | PASS | Planning/intake mention only; no clone/install/run |
| arcads-claude-code | PASS | Planning/intake mention only; no account/content action |
| Weavy | PASS | Planning/intake mention only; no live API wiring |
| Manychat | PASS | Planning/intake mention only; no live API wiring |
| OpenFang / MoneyPrinter | PASS | Planning/intake mention only; no runtime wiring |
| AirLLM | PASS | Claude report mentions intake/planning only |
| Mermaid | PASS | Claude report mentions intake/planning only |
| Claude Cowork | PASS | Claude report mentions intake/planning only |
| Speckit | PASS | Claude report mentions intake/planning only |
| Sigmap | PASS | Claude report mentions intake/planning only |
| Anvac | PASS | Claude report mentions intake/planning only |
| Agent Exchange / AEX | PASS | Claude report mentions intake/planning only |
| Claude + MetaTrader | PASS | Claude report mentions intake/planning only |
| Internship scraper/application assistant | PASS | No live scraping/application behavior added |
| Automations/plugins/skills future reminder | PASS | No runtime wiring or live action; future intake only |

## Safety Table

| Safety Check | Result | Evidence |
| --- | --- | --- |
| No real secrets/API keys committed | PASS | No secret-bearing staged files or active secret reads found |
| No live posting/upload/account action | PASS | No active live action path found |
| No autonomous money/public action | PASS | No autonomous money movement, trading, or public release action found |
| No external repo clone/install/run | PASS | No active clone/install/run behavior detected |
| No Ruflo/OpenFang/MoneyPrinter runtime wiring | PASS | Mentions remain planning/intake only |
| Approval gates intact | PASS | Dashboard/runtime checks still approval-gated |
| No generated logs/temp artifacts committed | PASS | No `05_logs/tmp_n4_1_*.txt`, runtime data, or logs staged |

## N+3 Regression Table

| N+3 Check | Result | Evidence |
| --- | --- | --- |
| Proof packet exists | PASS | Latest run validated |
| Full proof packet files | PASS | 13/13 files present |
| `supervised_mvp_slice_score` | PASS | 100 |
| `production_public_release_ready` | PASS | False |
| `live_posting_enabled` / live posting | PASS | False |
| External API calls in proof packet | PASS | False |
| Human approval required | PASS | True |
| Approval gates | PASS | All 5 gates `pending_human_review` |

## Direct Answers

| Question | Answer |
| --- | --- |
| Is target remote ref real/fetched? | Yes. It appeared after polling and resolves to `35316c1841fb13ed9c199adda8726ea8b7e480ef` |
| Is N+4.1G blocker fixed? | Yes for the crashing `tasks.json=[null]` status/recent bug |
| Does `tasks.json=[null]` survive `ghoti-status`? | Yes, exit 0 |
| Does `tasks.json=[null]` survive `ghoti-recent`? | Yes, exit 0 |
| Does `check_runtime_mvp.ps1` pass? | Yes, exit 0 |
| Does `check_dashboard_mvp.ps1` pass? | Yes, exit 0 |
| Do automated checks avoid blocking GUI popups? | Yes in this audit; none observed |
| Were terminal weird-command symptoms observed? | No |
| Are external tools planning-only? | Yes; no runtime wiring detected |
| Are automations/plugins/skills only future-reminder? | Yes; no live automation/plugin action was added |
| Did approval gates remain intact? | Yes |
| Is N+3 supervised MVP still valid? | Yes |
| Is merge to main recommended? | Conditional. Runtime hardening is safe, but clean-pass polish should surface invalid task counts/degraded status and align exact dashboard labels if those remain hard requirements |

## Conditions For Clean Pass

Recommended small follow-up branch:

`feat/ghoti-agent-claude-n4-1i-runtime-task-store-truth-polish`

Required fixes for clean pass:

1. Add truthful observability for skipped invalid task-store entries, such as `invalid_task_entry_count`, `skipped_task_entry_count`, or a degraded status note visible to `ghoti-status` / dashboard status paths.
2. Either make `Task.from_dict(None)` raise a typed `ValueError` with a clear message, or document/test that it is an internal raw parser and storage is the only accepted boundary for untrusted task-store data.
3. If exact UI labels are still a hard requirement, add verbatim dashboard strings: `Runtime Truth`, `Supervisor Truth`, `Approval Truth`, `Dashboard Truth`, `Content MVP Truth`, plus exact compact intake wording like `OpenFang/MoneyPrinter`, `no clone/install/run`, `no runtime wiring`, `no live account actions`, and `human approval required`.

Final verdict: **CONDITIONAL PASS**.
