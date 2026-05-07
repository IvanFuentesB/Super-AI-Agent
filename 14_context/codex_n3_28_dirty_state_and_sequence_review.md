# Codex N+3.28 Dirty State And Sequence Review

Status: codex_planning_only / dirty_state_sequence_review / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ac53eed
Origin HEAD: ac53eed
Local/origin sync: synced at audit start

## Current Dirty State Observed

At audit start, local and origin were synced at `ac53eed`, with no staged files.

Dirty files observed:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/ghoti_external_repo_tool_intake.md`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `05_logs/local_brain_runs/`
- `14_context/ghoti_current_prompt_N1_6.md`
- `14_context/money_workflows/sample_video_notes_n3_18.md`
- CV `.docx` files
- `output/`

Known N+3.18 partial implementation files:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

These should be preserved and not reset.

## Sequencing Rule

N+3.18 dirty implementation must be finished or consciously paused before N+3.28 implementation begins.

Reason:

- N+3.18 modifies runtime money workflow routing and experiment scoring.
- N+3.28 would add dashboard summaries and a decision queue based on those trackers.
- Mixing them without an explicit boundary risks staging the wrong runtime files or validating against a half-finished tracker shape.

## Safe Sequence Option A: Finish N+3.18 First

Preferred sequence:

1. Claude resumes dirty N+3.18 work.
2. Claude validates `video_to_money` and experiment scoring.
3. Claude creates missing N+3.18 docs and state updates.
4. Claude stages only intentional N+3.18 implementation files.
5. Claude commits and pushes N+3.18.
6. Claude then starts N+3.28 from a clean or consciously understood worktree.

Benefit:

- dashboard work reads stable tracker formats
- fewer accidental commits
- clearer milestone history

## Safe Sequence Option B: Consciously Pause N+3.18

If the operator wants dashboard planning/implementation first:

1. Document that N+3.18 is intentionally paused.
2. Do not stage N+3.18 runtime files.
3. Implement only read-only N+3.28 route/card and queue schema/sample.
4. Keep N+3.28 independent from dirty runtime changes.
5. Validate dashboard with current committed files plus tolerant missing-field behavior.

Risk:

- dashboard may need adjustment after N+3.18 tracker/scoring finalizes.

## Do Not Mix Without Decision

Do not:

- stage `local_brain_router.py` as part of dashboard work unless N+3.18 is being finished
- stage `money_workflow_new_experiment.py` as part of N+3.28 unless explicitly required
- stage the dirty experiment schema unless Claude is completing the N+3.18 scoring model
- stage sample video notes in the dashboard milestone
- edit or stage unrelated local files

## N+3.28 Clean Implementation Boundary

If implemented later, N+3.28 should be limited to:

- `14_context/money_workflows/manual_decision_queue.schema.json`
- `14_context/money_workflows/manual_decision_queue.jsonl`
- optional `03_scripts/money_decision_queue_intake.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- optional dashboard CSS if established pattern requires it
- state/log docs
- optional wait/resume seed

No live action capabilities should be added.

## Safety Gate Truth

N+3.28 must stay read-only or local append-only:

- dashboard route is read-only
- dashboard card has no mutation buttons
- decision queue helper is dry-run first
- append only happens after operator command
- appending a decision does not execute it
- all public/money-facing actions require human approval and manual execution

## Recommended Claude Sequencing

Exact recommendation:

```text
Continue N+3.18 dirty partial work and finish Gemma Video-to-Money Runner + Experiment Scoring. If that cannot happen now, explicitly mark N+3.18 paused before implementing N+3.28. Do not stage N+3.18 runtime files in the N+3.28 dashboard/decision queue commit unless the prompt explicitly expands the scope.
```

## Verdict

N+3.28 is safe to plan now. It should be implemented only after the dirty N+3.18 boundary is resolved or intentionally paused.
