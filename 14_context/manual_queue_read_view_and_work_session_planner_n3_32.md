# N+3.32 — Manual Queue Read View + Operator Work Session Planner

Status: delivered / local_only / draft_intake_only / not_approved / no_live_actions

Date: 2026-05-05
Branch: feat/ghoti-visible-operator-stack
Lane: Claude
Starting HEAD: 6758784

## Purpose

Adds a read-only dashboard view for the manual decision queue (Part A) and a local
stdlib-only planner script that converts queue items into a structured work session
plan (Part B). No live actions, no approval execution, no external APIs.

## Part A — Dashboard Read View

### Route Added

```
GET /api/ghoti/money/manual-decision-queue
```

Source: `01_projects/dashboard_mvp/server.js`

### Response Fields

| Field | Description |
|-------|-------------|
| ok | always true |
| status | "zero_state" / "empty" / "found" / "read_error" |
| queue_path | relative path to queue JSONL |
| item_count | number of valid items parsed |
| items | array of queue item summaries |
| status_counts | count by item status |
| risk_counts | count by risk_level |
| warnings | parse warnings / missing file warnings |
| safety_flags | all false except manual_review_required=true |
| generated_at | ISO timestamp |

### Each item includes

queue_item_id, created_at, source_review_run_id, source_decision_id,
title, category, recommendation, risk_level, approval_required,
status, public_or_money_facing, next_local_step, blocked_reason,
human_review_note

### Zero-state behavior

- Returns ok/zero_state if queue file missing
- Shows suggested local command for adding items
- No crash, no error status

### Malformed JSONL handling

- Skips malformed lines, adds to warnings
- Returns partial valid items

### Dashboard Card Added

Section: `#section-manual-queue`
Sidebar: "Manual Queue"
Source: `01_projects/dashboard_mvp/public/index.html`

### App.js Functions Added

- `renderManualQueueCard(payload)` — renders card from API response
- `refreshManualQueue()` — fetches route and calls render; called on page load

Source: `01_projects/dashboard_mvp/public/app.js`

### Card Sections

- Item count, status counts, risk counts
- Queue path (copy only — no edit)
- Top 5 queue items with next_local_step, risk, status, blocked_reason
- Safety Flags (expand/collapse)

### Forbidden UI Actions

No approve, execute, post, sell, pay, email, outreach, scrape, or live-account buttons.

## Part B — Operator Work Session Planner

### Script

`03_scripts/operator_work_session_planner.py`

- stdlib only, no external dependencies
- no model calls
- reads manual decision queue JSONL
- classifies items: safe_local_work / needs_human_approval / blocked / reject_or_unsafe
- selects top N tasks (default 3)
- writes local artifacts under `05_logs/operator_work_sessions/<run_id>/`

### Classification Logic

| Class | Condition |
|-------|-----------|
| blocked | status in {paused, killed, superseded} |
| reject_or_unsafe | category=KILL or next_step contains forbidden phrase |
| needs_human_approval | risk=high, category in RISKY_CATEGORIES, or approval_required=true |
| safe_local_work | safe category + risk low/medium + approval not explicitly false |

### Output Artifacts

Under `05_logs/operator_work_sessions/<run_id>/`:

| File | Contents |
|------|----------|
| work_session_plan.md | Markdown plan with tasks, validation, approval questions, risk notes |
| work_session_plan.json | Full plan as JSON |
| source_index.json | Queue summary: run_id, queue_path, counts |
| request.json | Planner request metadata |

### CLI

```powershell
python 03_scripts/operator_work_session_planner.py --help
python 03_scripts/operator_work_session_planner.py --dry-run
python 03_scripts/operator_work_session_planner.py --queue-path 14_context/money_workflows/manual_decision_queue.jsonl --dry-run
python 03_scripts/operator_work_session_planner.py --queue-path 14_context/money_workflows/manual_decision_queue.jsonl --max-tasks 3
```

### Safety Truth

- no external API calls
- no scraping
- no posting, selling, outreach, payment, login
- no model output executed
- no queue item approved or marked as such
- no live accounts touched
- all outputs labeled: local draft, not approval, not execution

## Files Changed

- `01_projects/dashboard_mvp/server.js` — added route GET /api/ghoti/money/manual-decision-queue
- `01_projects/dashboard_mvp/public/index.html` — added sidebar link + section-manual-queue
- `01_projects/dashboard_mvp/public/app.js` — added renderManualQueueCard + refreshManualQueue
- `03_scripts/operator_work_session_planner.py` — new planner script
- `14_context/manual_queue_read_view_and_work_session_planner_n3_32.md` — this doc

## Validation Results

- node --check server.js: PASS
- node --check app.js: PASS
- git diff --check: PASS
- AST parse operator_work_session_planner.py: PASS
- --help smoke: PASS
- --dry-run zero-state smoke: PASS (queue missing → graceful zero_state)

## Non-Goals (N+3.32)

- NO Obsidian scaffolding (N+3.34)
- NO approval execution or approve button
- NO external connector or live account tools
- NO model inference calls
- NO posting, selling, emailing, scraping

## Next Milestone

N+3.33 or N+3.34 — Obsidian local memory layer scaffolding
