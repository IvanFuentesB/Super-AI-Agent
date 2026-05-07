# Codex N+3.28 Claude Implementation Checklist

Status: codex_planning_only / claude_handoff / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Goal

Implement the local manual decision queue intake and read-only weekly Money OS dashboard summary without enabling live actions.

## Step 1: Repo Truth

Run:

```powershell
git status --short
git branch --show-current
git log --oneline --graph --decorate --all -12
git fetch origin feat/ghoti-visible-operator-stack
git diff --cached --name-status
```

Record:

- starting HEAD
- origin HEAD
- dirty files
- staged files
- whether N+3.18 dirty work is still present

## Step 2: Resolve Milestone Boundary

Choose one:

- Finish N+3.18 first.
- Consciously pause N+3.18 and document that N+3.28 will avoid those dirty files.

Do not proceed ambiguously.

## Step 3: Add Decision Queue Schema And Sample

Create:

- `14_context/money_workflows/manual_decision_queue.schema.json`
- `14_context/money_workflows/manual_decision_queue.jsonl`

The sample queue may contain zero or one clearly marked local-only sample record.

Validation:

```powershell
python -m json.tool 14_context/money_workflows/manual_decision_queue.schema.json
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('manual decision queue jsonl ok')"
```

## Step 4: Add Optional Intake Helper

Only if scope allows, create:

```text
03_scripts/money_decision_queue_intake.py
```

Required behavior:

- dry-run mode
- append mode
- exactly one decision per run
- validate enum values
- generate stable decision IDs
- repo-local paths only
- append-only queue writes
- no decision execution
- no external API
- no posting/selling/outreach/payment/account actions

Suggested smoke:

```powershell
python 03_scripts/money_decision_queue_intake.py --dry-run --decision-type COLLECT_MORE_DATA --source-type experiment --source-id exp_20260428_120001_vid001 --reason "Needs real metrics before action" --next-manual-action "Record manual metrics after operator review" --risk-level low
```

## Step 5: Add Read-Only Backend Route

Modify:

```text
01_projects/dashboard_mvp/server.js
```

Add:

```text
GET /api/ghoti/money/weekly-review/summary
```

Route behavior:

- read local JSONL files only
- tolerate missing future files
- tolerate malformed lines
- return zero-state summaries
- never mutate files
- never call external APIs
- never use live accounts
- never call Gemma

Read sources:

- `14_context/money_workflows/experiment_tracker.jsonl`
- `14_context/money_workflows/manual_decision_queue.jsonl`
- `14_context/money_workflows/product_metrics.jsonl`
- `14_context/money_workflows/product_drafts.jsonl`
- `14_context/money_workflows/product_build_packs.jsonl`
- latest `05_logs/money_reviews/<run_id>/run_summary.json` if present

## Step 6: Add Dashboard Card

Modify:

```text
01_projects/dashboard_mvp/public/app.js
```

Add read-only card:

```text
Money OS - Weekly Review
```

Show:

- shots this week
- launches/manual metrics
- decisions pending
- top 5 next manual actions
- blocked items
- distribution gaps
- email-list opportunities
- latest review artifacts

Allowed interactions:

- refresh
- copy file path
- open local artifact path only if an existing safe project pattern supports it

Do not add:

- approve button
- delete button
- post button
- send button
- sell button
- publish button
- scrape button
- account button

## Step 7: Validate

Run:

```powershell
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
python -m json.tool 14_context/money_workflows/manual_decision_queue.schema.json
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('manual decision queue jsonl ok')"
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
git diff --check
```

Optional route smoke only if dashboard server is intentionally running:

```powershell
Invoke-RestMethod http://localhost:3210/api/ghoti/money/weekly-review/summary
```

## Step 8: Update State Docs

If implementation happens, update:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

Optional:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

Only update wait/resume if adding a concrete seed.

## Step 9: Stage Carefully

Stage only intentional N+3.28 files, such as:

- `14_context/money_workflows/manual_decision_queue.schema.json`
- `14_context/money_workflows/manual_decision_queue.jsonl`
- optional `03_scripts/money_decision_queue_intake.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- state/log docs
- optional wait/resume seed

Do not stage:

- unrelated dirty files
- `.claude/skills/`
- CV docs
- `output/`
- third-party files
- prompt scratch files
- local brain logs
- N+3.18 runtime files unless N+3.18 is intentionally finished in the same scoped prompt

Verify:

```powershell
git diff --cached --name-status
git diff --cached --check
```

## Step 10: Commit And Push

Commit message:

```text
feat/ghoti milestone N+3.28 — add weekly review read view and manual decision queue intake
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
- manual decision queue truth
- weekly review route truth
- dashboard card truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files intentionally left unstaged
- next milestone recommendation

## Recommended Next Future Milestone

After N+3.28 implementation, next recommended milestone:

```text
N+3.29 - Weekly Review Artifact Generator Implementation
```

That milestone should implement the local Gemma artifact generator only after the read-only dashboard and decision queue intake are stable.
