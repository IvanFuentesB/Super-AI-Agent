# Codex N+3.30 Claude Implementation Checklist

Status: codex_planning_only / claude_handoff / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Goal

Add a read-only dashboard/backend view that summarizes generated weekly Money OS review artifacts from `05_logs/money_reviews/<run_id>/`.

## Step 1: Resolve Dirty N+3.18 Boundary

Before implementation, Claude must choose:

- finish N+3.18 dirty partial work, or
- consciously pause N+3.18 and avoid staging those dirty files.

Do not stage N+3.18 runtime/scoring files as part of N+3.30 unless the operator explicitly expands the scope.

## Step 2: Implement Or Simulate N+3.29 Dependency

Choose one:

- implement N+3.29 weekly review artifact generator first, or
- create a tiny safe sample artifact directory for route/dashboard development.

Sample artifact directory, if approved:

```text
05_logs/money_reviews/mrev_sample_read_only/
```

It should contain only harmless local sample files. Do not run Gemma unless the implementation milestone explicitly allows it.

## Step 3: Add Backend Route

Modify:

```text
01_projects/dashboard_mvp/server.js
```

Add:

```text
GET /api/ghoti/money/weekly-review/artifacts/summary
```

Route requirements:

- scan `05_logs/money_reviews/`
- find latest run dirs
- read `run_summary.json`
- read `weekly_summary.md`
- read `decisions_recommended.jsonl`
- read `next_10_shots.md`
- read `risk_review.md`
- tolerate missing directory
- tolerate malformed JSON/JSONL
- return zero-state safely
- never mutate files
- never execute model output
- never trigger live actions

## Step 4: Add Dashboard Card

Modify:

```text
01_projects/dashboard_mvp/public/app.js
```

Add read-only card:

```text
Money OS - Weekly Review
```

Show:

- latest weekly review run
- total review runs
- summary excerpt
- decision candidate counts
- top 3 recommended decisions
- next 10 shots preview
- risk flags
- warnings
- artifact paths as copy-only text

Allowed:

- refresh
- copy path
- expand/collapse sections

Forbidden:

- approve
- execute
- append queue
- post
- sell
- outreach
- pay
- scrape
- use accounts
- run Gemma

## Step 5: Add CSS Only If Necessary

Modify CSS only if the existing card styles are insufficient.

If CSS changes are needed:

- keep minimal
- reuse existing design tokens
- do not redesign dashboard

## Step 6: Validate Zero-State

With no `05_logs/money_reviews/` directory or with it empty, the route should return:

- `ok: true`
- `status: "zero_state"`
- `runs_total: 0`
- warning explaining no review artifacts exist

Dashboard should render:

```text
No weekly review artifacts found yet.
```

## Step 7: Validate With Sample Artifact Dir

If a sample is added, validate:

- latest run is detected
- summary excerpt appears
- decisions are counted
- top three candidates appear
- malformed candidate line becomes warning
- risk flags appear
- no mutation occurs

## Step 8: Run Checks

Required:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
git diff --check
```

If JSON fixtures are added:

```powershell
python -m json.tool 05_logs/money_reviews/mrev_sample_read_only/run_summary.json
```

If Python files are touched by adjacent work:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
```

## Step 9: Update State Docs

If implementation happens, update:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- optionally `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

Only update wait/resume if adding a concrete seed.

## Step 10: Stage Intentional Files Only

Likely stage:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- optional CSS file if changed
- optional safe sample artifact directory if approved
- state/log docs
- optional wait/resume seed

Do not stage:

- dirty N+3.18 partial files unless explicitly finishing them
- `.claude/skills/`
- CV docs
- `output/`
- third-party repo files
- prompt scratch files
- unrelated local brain logs

Before commit:

```powershell
git diff --cached --name-status
git diff --cached --check
```

## Step 11: Commit And Push

Commit:

```text
feat/ghoti milestone N+3.30 — add weekly review artifact dashboard read view
```

Push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Fields

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- weekly artifact route truth
- dashboard card truth
- sample artifact truth
- safety gate truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files intentionally left unstaged
- next milestone recommendation

## Recommended Next Future Milestone

After N+3.30:

```text
N+3.31 - Manual Decision Candidate Review To Queue Draft Intake
```

That milestone may design or implement an explicit operator-reviewed path from generated candidates to the local manual decision queue. It must still avoid public/live actions.
