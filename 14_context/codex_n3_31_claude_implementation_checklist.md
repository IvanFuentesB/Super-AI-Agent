# Codex N+3.31 Claude Implementation Checklist

Status: codex_planning_only / claude_implementation_checklist / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Recommended Claude Milestone

```text
N+3.31 Claude - Manual Decision Candidate Review To Queue Draft Intake
```

Claude should implement this only after finishing or consciously pausing the dirty N+3.18 work. Do not mix unresolved video-to-money runtime changes with dashboard or queue intake changes unless the operator explicitly chooses that sequence.

## Required First Step

Run repo truth:

```powershell
git status --short
git branch --show-current
git log --oneline -12
git diff --cached --name-status
```

Confirm dirty N+3.18 files are preserved and not accidentally staged unless the operator explicitly resumes N+3.18.

## Scope

Future implementation may include:

- `14_context/money_workflows/manual_decision_queue.schema.json`
- optional starter `14_context/money_workflows/manual_decision_queue.jsonl`
- `03_scripts/manual_decision_queue_new_item.py`
- optional read-only decision candidates summary route
- optional read-only dashboard card
- state/log updates if implementation happens

Do not implement posting, selling, outreach, payments, scraping, browser automation, live account actions, or approval execution.

## Suggested Implementation Sequence

1. Finish or consciously pause N+3.18 dirty partial work.
2. Read the N+3.29, N+3.30, and N+3.31 Codex specs.
3. Add `manual_decision_queue.schema.json` if operator approves local queue file creation.
4. Implement `03_scripts/manual_decision_queue_new_item.py` with Python standard library only.
5. Make dry-run the safest/default path.
6. Add explicit `--append` mode that appends exactly one JSONL record.
7. Reject unsupported decision types, statuses, risk levels, and live-action flags.
8. Reject or warn on next actions implying posting, selling, outreach, payment, scraping, upload, launch, or live account login.
9. If adding dashboard support, make it read-only and copy-only.
10. If adding a route, make it local-read-only and tolerant of missing files and malformed JSONL.
11. Update `wait_resume_supervisor.py`, `14_context/current_state.md`, `14_context/next_actions.md`, and `14_context/ghoti_finish_line_log.md` only if the implementation milestone proceeds.
12. Stage only intentional files.
13. Commit and push.

## Files Claude May Edit Later

Only if implementing the milestone:

- `03_scripts/manual_decision_queue_new_item.py`
- `14_context/money_workflows/manual_decision_queue.schema.json`
- `14_context/money_workflows/manual_decision_queue.jsonl`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/overlay.js` only if truly needed
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

## Files Claude Must Not Stage Accidentally

- unrelated `.claude/skills/`
- CV docs
- `output/`
- third-party repo contents
- prompt scratch files
- old local brain logs
- unrelated dirty files
- N+3.18 dirty implementation files unless Claude is intentionally finishing N+3.18 in the same operator-approved recovery sequence

## Validation Commands

Minimum validation if helper is implemented:

```powershell
python -m py_compile 03_scripts/manual_decision_queue_new_item.py
python -m json.tool 14_context/money_workflows/manual_decision_queue.schema.json
python 03_scripts/manual_decision_queue_new_item.py --dry-run --source-type weekly_review_candidate --source-run-id mrev_sample --candidate-id cand_sample --decision-type COLLECT_MORE_DATA --recommendation "Collect manual metrics" --reason "No real metrics yet" --risk-level low --next-manual-action "Record manual observations locally"
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); print('queue missing ok' if not p.exists() else 'queue jsonl ok', sum(1 for line in p.read_text(encoding='utf-8').splitlines() if line.strip() and json.loads(line)))"
git diff --check
```

If dashboard files are touched:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
```

## Stage, Commit, Push

Before commit:

```powershell
git diff --cached --name-status
git diff --cached --check
```

Recommended implementation commit:

```text
feat/ghoti milestone N+3.31 - add manual decision candidate review queue
```

Then:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Fields For Claude

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- candidate review truth
- manual queue helper truth
- dashboard route/card truth if implemented
- safety gate truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files left unstaged
- next milestone recommendation

## Next Future Milestone

Recommended next future milestone:

```text
N+3.32 - Manual Decision Queue Read View And Operator Work Session Planner
```

That milestone should remain local/read-only first unless the operator explicitly approves narrow queue mutation tooling.

## Verdict

Claude should implement N+3.31 as an explicit local draft intake path. The milestone succeeds when candidates can become reviewed local queue records without becoming public actions.
