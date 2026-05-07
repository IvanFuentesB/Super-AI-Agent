# Codex N+3.27 Weekly Money Dashboard Spec

Status: codex_planning_only / weekly_money_dashboard / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 8132c81
Origin HEAD: 8132c81
Local/origin sync: synced at audit start

## Purpose

Design a future read-only dashboard card that shows the weekly Money OS review: what was created, what moved, what is blocked, what needs approval, and what should be considered next. This card is a scoreboard and decision aid, not an execution surface.

The dashboard should support the numbers-game principle: many shots, many products, many content/distribution attempts, honest metrics, fast feedback, and human-controlled decisions.

## Future Card

Card name:

```text
Money OS - Weekly Review
```

The card should be read-only and should not include mutation buttons.

## Route Idea

Future backend route:

```text
GET /api/ghoti/money/weekly-review/summary
```

Primary local sources:

- `14_context/money_workflows/experiment_tracker.jsonl`
- future `14_context/money_workflows/product_drafts.jsonl`
- future `14_context/money_workflows/product_build_packs.jsonl`
- future `14_context/money_workflows/product_metrics.jsonl`
- future `14_context/money_workflows/content_shots.jsonl`
- future `14_context/money_workflows/manual_decision_queue.jsonl`

Optional artifact sources:

- `05_logs/money_reviews/<run_id>/run_summary.json`
- `05_logs/money_reviews/<run_id>/weekly_summary.md`
- `05_logs/product_drafts/<run_id>/run_summary.json`
- `05_logs/product_build_packs/<run_id>/run_summary.json`
- `05_logs/content_batches/<run_id>/run_summary.json`

## Summary Fields

The route should return:

- `total_shots_this_week`
- `experiments_created`
- `product_drafts_created`
- `build_packs_created`
- `launches_manually_recorded`
- `manual_sales_recorded`
- `manual_revenue_recorded`
- `opt_ins_recorded`
- `email_list_growth_recorded`
- `content_assets_created`
- `distribution_channels_used`
- `top_experiments_by_score`
- `top_launches_by_metrics`
- `stuck_or_blocked_experiments`
- `missing_distribution`
- `missing_email_list_angle`
- `missing_cta`
- `approval_required_items`
- `next_10_recommended_shots`
- `decision_queue_counts`
- `warnings`
- `parse_errors`
- `generated_at`

## Response Shape Example

```json
{
  "ok": true,
  "read_only": true,
  "week_start": "2026-04-27",
  "week_end": "2026-05-03",
  "total_shots_this_week": 0,
  "experiments_created": 0,
  "product_drafts_created": 0,
  "build_packs_created": 0,
  "launches_manually_recorded": 0,
  "manual_sales_recorded": 0,
  "manual_revenue_recorded": 0,
  "opt_ins_recorded": 0,
  "email_list_growth_recorded": 0,
  "content_assets_created": 0,
  "distribution_channels_used": {},
  "top_experiments_by_score": [],
  "top_launches_by_metrics": [],
  "stuck_or_blocked_experiments": [],
  "missing_distribution": [],
  "missing_email_list_angle": [],
  "missing_cta": [],
  "approval_required_items": [],
  "next_10_recommended_shots": [],
  "decision_queue_counts": {},
  "warnings": [],
  "parse_errors": [],
  "safety": {
    "mutation_enabled": false,
    "external_api_used": false,
    "live_account_actions_enabled": false,
    "posting_enabled": false,
    "selling_enabled": false,
    "outreach_enabled": false,
    "payment_actions_enabled": false
  },
  "generated_at": "2026-04-29T00:00:00Z"
}
```

## Dashboard Layout

Recommended read-only sections:

- Shot counter: total weekly shots, experiments, drafts, build packs, content assets, manual launches.
- Revenue and opt-in snapshot: manually recorded revenue, sales, opt-ins, and email-list growth only.
- Top candidates: highest-scoring experiments, strongest launches, and best next product/content shots.
- Bottlenecks: missing distribution, missing CTA, missing email-list angle, approval required, or blocked status.
- Decision queue preview: items grouped by double down, iterate, pause, kill, build next, and collect more data.
- Safety label: "Read-only. No posting, selling, outreach, payments, scraping, or account actions."

## Zero-State Behavior

If source files are missing, empty, or not yet implemented, the route should return a safe zero-state summary:

- counts set to zero
- arrays set to empty
- warnings explaining which source file is missing
- `ok: true` unless file parsing itself crashes unexpectedly
- no stack traces sent to the browser

Zero-state is not failure. It tells the operator which tracker needs to be created next.

## Tolerant Parsing

The future route should:

- parse JSONL line by line
- skip blank lines
- continue after malformed lines
- count parse errors
- include at most five parse error samples
- tolerate missing fields
- tolerate field drift between milestones
- treat missing numeric metrics as zero for totals
- return `null` for derived rates when denominators are zero
- never mutate files

## Read-Only Safety Rules

Allowed:

- read local tracker files
- compute counts
- show warnings
- show file paths
- show draft decision candidates
- refresh summary

Not allowed:

- delete files
- append records
- change statuses
- approve decisions
- post content
- send email
- publish listings
- create accounts
- upload products
- set prices
- process payments
- scrape metrics
- use live accounts
- execute model output

## Suggested Implementation Files For Claude Later

Codex should not edit these in this milestone. Claude Code may later modify:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- optionally `01_projects/dashboard_mvp/public/styles.css` if present
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- optionally `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` if adding a seed

## Suggested Validation Commands

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
```

If Claude adds sample JSONL files, also run a line-by-line JSONL parse check.

## Verdict

N+3.27 should make the weekly Money OS visible as a read-only command center. It should show progress and bottlenecks without becoming a launch, commerce, email, scraping, or account automation tool.
