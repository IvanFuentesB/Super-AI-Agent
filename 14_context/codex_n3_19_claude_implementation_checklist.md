# Codex N+3.19 Claude Implementation Checklist

Status: claude_implementation_checklist / read_only_dashboard / no_codex_runtime_changes

## Sequencing Note

Preferred sequence:

1. Finish and commit N+3.18 Gemma video-to-money runner + experiment scoring.
2. Then implement N+3.19 Money Dashboard Read View + Shot Counter.

If the operator chooses to do N+3.19 before N+3.18 is finished, Claude must keep N+3.19 read-only and must not stage the dirty N+3.18 implementation files unless explicitly finishing N+3.18 at the same time.

## Step 1 - Repo Truth

Run:

```powershell
git status --short
git branch --show-current
git log --oneline -10
git diff --cached --name-status
```

Confirm:

- branch is `feat/ghoti-visible-operator-stack`.
- no unexpected staged files.
- dirty N+3.18 files are either already committed by Claude or intentionally left unstaged.

## Step 2 - Read Inputs

Read:

- `14_context/money_workflows/experiment_tracker.jsonl`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/distribution_and_exposure_checklist.md`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css`

## Step 3 - Add Backend Route

Add:

```text
GET /api/ghoti/money/summary
```

Route requirements:

- Read `14_context/money_workflows/experiment_tracker.jsonl`.
- Handle missing tracker file.
- Handle malformed JSONL lines with `parse_errors`.
- Compute:
  - `total_experiments`
  - `by_workflow_type`
  - `by_status`
  - `by_priority_bucket`
  - `total_revenue_usd`
  - `total_time_spent_hours`
  - `top_next_actions`
  - `latest_experiments`
  - `distribution_channels`
  - `approval_required_count`
- Return `read_only: true`.
- Return `runtime_wiring_truth: "dashboard_read_model_only"`.
- Do not mutate files.
- Do not call external APIs.
- Do not execute model output.

## Step 4 - Add Dashboard Card

Add a "Money OS" card/section to the dashboard UI.

Show:

- total shots.
- approval-required count.
- workflow type counts.
- status counts.
- score buckets when present.
- latest experiments.
- distribution channel frequencies.
- reminder that every experiment should have distribution and email-list thinking.
- safety label: no live action from dashboard.

Do not add:

- delete buttons.
- post buttons.
- sell buttons.
- send/email/outreach buttons.
- payment/app-store/account buttons.
- scrape/fetch buttons.
- model-run buttons.

## Step 5 - Optional Wait/Resume Seed

Only if useful, add a wait/resume seed noting:

```text
N+3.19 money_dashboard_read_view_ready
```

Do not add any seed that implies live posting/selling/outreach automation is available.

## Step 6 - Update State Docs

Update:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

Record:

- read-only money dashboard route added.
- no live actions.
- no external APIs.
- no runtime money automation.
- dirty local-only files left unstaged.

## Step 7 - Validation Commands

Run:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
git diff --check
git status --short
```

If the dashboard is running and safe to query locally, optionally verify:

```powershell
Invoke-RestMethod http://127.0.0.1:3210/api/ghoti/money/summary
```

Do not start live account workflows or external services to test this route.

## Step 8 - Staging

Stage only intentional N+3.19 files, likely:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css` if changed
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if intentionally updated

Do not stage:

- dirty N+3.18 implementation files unless explicitly finishing N+3.18 too.
- `14_context/ghoti_external_repo_tool_intake.md`.
- `21_repos/third_party/.gitkeep`.
- `.claude/skills/`.
- `01_projects/mcp_server/test.txt`.
- local brain logs.
- CV docs.
- `output/`.
- prompt scratch files.
- third-party repo contents.

## Commit And Push

Commit:

```powershell
git commit -m "feat/ghoti milestone N+3.19 - add money workflow dashboard read view"
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Fields

Claude should report:

- branch.
- previous HEAD.
- new commit hash.
- pushed yes/no.
- files changed.
- validation pass/fail.
- dashboard route truth.
- UI card truth.
- shot counter truth.
- safety gate truth.
- runtime wiring truth.
- live action truth.
- dirty files intentionally left unstaged.
- next milestone recommendation.
