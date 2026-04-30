# Codex N+3.32 Claude Implementation Checklist

Status: codex_planning_only / claude_implementation_checklist / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Recommended Claude Milestone

```text
N+3.32 Claude - Manual Decision Queue Read View And Operator Work Session Planner
```

## First Rule

FIRST resolve or consciously pause dirty N+3.18 before implementing N+3.32.

Do not stage or overwrite:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

unless the operator explicitly says Claude is finishing N+3.18 in the same recovery sequence.

## Minimal Implementation Scope

Implement only what is necessary:

- read-only manual decision queue summary route
- read-only dashboard card
- optional deterministic stdlib work session planner
- local artifacts under `05_logs/operator_work_sessions/<run_id>/`
- state/log docs if implementation happens

Do not broadly refactor dashboard, runtime, or money workflow files.

## Suggested Files For Future Implementation

Possible create:

- `03_scripts/operator_work_session_plan.py`
- `14_context/money_workflows/manual_decision_queue.schema.json`
- optional starter `14_context/money_workflows/manual_decision_queue.jsonl`

Possible modify:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/overlay.js` only if needed
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only for a seed/status update
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

## Implementation Steps

1. Run repo truth commands.
2. Confirm N+3.18 dirty files are intentionally preserved.
3. Read N+3.29 through N+3.32 Codex docs.
4. If queue files do not exist, implement zero-state behavior first.
5. Add tolerant JSONL parser for `manual_decision_queue.jsonl`.
6. Add read-only route `GET /api/ghoti/money/manual-decision-queue/summary`.
7. Ensure route never writes files or calls action helpers.
8. Add dashboard card `Money OS - Manual Decision Queue`.
9. Limit UI actions to refresh, expand, and copy text/path.
10. If implementing planner, create stdlib script with dry-run/artifact-only output.
11. Write work session artifacts under `05_logs/operator_work_sessions/<run_id>/`.
12. Validate with missing-file, empty-file, valid-line, and malformed-line cases.
13. Update state docs only after implementation truth is known.
14. Stage only intentional N+3.32 files.
15. Commit and push.

## Validation Commands

Always run:

```powershell
git diff --check
git diff --cached --check
```

If dashboard JS files are touched:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
```

If Python helper files are touched:

```powershell
python -m py_compile 03_scripts/operator_work_session_plan.py
```

If queue files are involved:

```powershell
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); print('queue missing ok' if not p.exists() else 'queue jsonl ok', sum(1 for line in p.read_text(encoding='utf-8').splitlines() if line.strip() and json.loads(line)))"
python -m json.tool 14_context/money_workflows/manual_decision_queue.schema.json
```

If existing experiment schema remains dirty from N+3.18, validate but do not stage it unless intentionally resolving N+3.18:

```powershell
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
```

## Staging Rules

For this Codex planning milestone:

- stage only the five N+3.32 Codex docs
- do not stage dirty N+3.18 files
- do not stage unrelated local dirt

For future Claude implementation:

- stage only intentional N+3.32 implementation files
- inspect `git diff --cached --name-status`
- confirm no third-party, CV, output, local logs, prompt scratch, or unrelated dirty files are staged

## Future Implementation Commit

Recommended implementation commit:

```text
feat/ghoti milestone N+3.32 - add manual decision queue read view and work session planner
```

## Final Report Fields

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- queue read-view truth
- work session planner truth
- safety gate truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files left unstaged
- next milestone recommendation

## Verdict

Claude should implement N+3.32 only after the N+3.18 dirty state is resolved or explicitly parked. The implementation should be small, local, read-only for dashboard routes, and artifact-only for planning.
