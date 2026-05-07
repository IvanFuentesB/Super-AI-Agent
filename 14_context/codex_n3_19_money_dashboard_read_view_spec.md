# Codex N+3.19 Money Dashboard Read View Spec

Status: codex_planning_only / read_only_dashboard_spec / not_runtime_wired

## Goal

Add a read-only dashboard view that makes Ghoti's money workflow visible without giving the dashboard any live money/action capability.

The first dashboard slice should answer:

- How many shots/experiments exist?
- What workflow types are represented?
- Which statuses are present?
- Which score buckets exist, if scoring has been added?
- Which distribution channels are being targeted?
- Which shots need approval?
- What are the latest experiments and next actions?

## Proposed Backend Route

Route:

```text
GET /api/ghoti/money/summary
```

Input:

```text
14_context/money_workflows/experiment_tracker.jsonl
```

Required behavior:

- Read-only.
- No JSONL mutation.
- No model execution.
- No external API calls.
- No posting, selling, emailing, outreach, payment, app-store, account, browser, Docker, CUA, or scraping action.
- If tracker file is missing, return `ok: true`, `tracker_exists: false`, and zero counts.
- If a line is malformed, increment `parse_errors` and continue parsing the remaining lines.
- Limit latest experiments to 10.

## Proposed Summary Response Fields

```json
{
  "ok": true,
  "tracker_path": "14_context/money_workflows/experiment_tracker.jsonl",
  "tracker_exists": true,
  "total_experiments": 3,
  "parse_errors": 0,
  "by_workflow_type": {},
  "by_status": {},
  "by_priority_bucket": {},
  "total_revenue_usd": 0,
  "total_time_spent_hours": 0,
  "top_next_actions": [],
  "latest_experiments": [],
  "distribution_channels": {},
  "approval_required_count": 0,
  "read_only": true,
  "runtime_wiring_truth": "dashboard_read_model_only",
  "live_actions_enabled": false,
  "updated_at_utc": "..."
}
```

## Aggregation Rules

- `total_experiments`: count valid parsed JSONL records only.
- `by_workflow_type`: count `workflow_type || "unknown"`.
- `by_status`: count `status || "unknown"`.
- `by_priority_bucket`: count `record.scoring.priority_bucket` when present; skip when missing.
- `total_revenue_usd`: sum `record.metrics.revenue_usd` if numeric; otherwise treat as 0.
- `total_time_spent_hours`: sum `record.metrics.time_spent_hours` if numeric; otherwise treat as 0.
- `top_next_actions`: most recent non-empty `next_action` values, capped at 10.
- `latest_experiments`: most recent 10 records sorted by `created_at` if valid, otherwise file order fallback.
- `distribution_channels`: count each string from `distribution_channels`; also tolerate `channels` if future records use that name.
- `approval_required_count`: count records where `approval_required === true`.

## Dashboard UI Proposal

Add a read-only "Money OS" card/section.

Recommended layout:

- Hero stat: `Total shots`.
- Secondary stats:
  - `Approval required`.
  - `Revenue tracked`.
  - `Hours tracked`.
  - `Parse errors`.
- Compact chips:
  - workflow type counts.
  - status counts.
  - A/B/C/D score buckets when present.
- Latest experiments table:
  - experiment ID.
  - workflow type.
  - status.
  - priority bucket.
  - next action.
  - approval required.
- Distribution/exposure strip:
  - channel frequency.
  - reminder: every experiment should have 3+ distribution channels and an email-list angle.
- Safety label:
  - `Read-only. No live action from dashboard. Posting/selling/outreach/payment require explicit approval.`

Buttons:

- Allowed: `Refresh`.
- Not allowed: delete, publish, post, sell, send, email, outreach, scrape, payment, account login, app-store, browser automation.
- Future buttons may be shown only as disabled/planning-only labels.

## Suggested Implementation Files For Claude

Likely files:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css` if a small style addition is needed.
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a wait/resume seed.

Codex must not edit those files in this planning pass.

## Suggested Validation Commands

Claude should run:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
git diff --check
git status --short
```

If `styles.css` is changed, static syntax validation is visual/manual only unless an existing CSS checker exists.

## Done Definition

N+3.19 is done when a local read-only dashboard route and card can show money workflow shot counts and latest experiments without mutating the tracker or enabling any live action.
