# Codex N+3.28 Weekly Review Summary Route Spec

Status: codex_planning_only / weekly_review_summary_route / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design the future read-only backend route for the weekly Money OS dashboard. The route should summarize local trackers and optional weekly review artifacts without mutating data, calling external APIs, scraping, or using live accounts.

## Future Route

```text
GET /api/ghoti/money/weekly-review/summary
```

## Local Sources

Read local files only:

- `14_context/money_workflows/experiment_tracker.jsonl`
- future `14_context/money_workflows/manual_decision_queue.jsonl`
- future `14_context/money_workflows/product_metrics.jsonl`
- future `14_context/money_workflows/product_drafts.jsonl`
- future `14_context/money_workflows/product_build_packs.jsonl`
- optional latest `05_logs/money_reviews/<run_id>/run_summary.json`

The route should tolerate missing future files because most of them do not exist yet.

## Tolerant Parser Design

Use one shared local helper inside the dashboard server implementation:

- `readJsonlSafe(absPath, label, maxRecords)`
- verify resolved path stays under repo root
- return zero-state if file is missing
- skip blank lines
- parse one JSON object per line
- continue after malformed lines
- collect `parse_errors_count`
- collect at most five parse error samples
- cap returned records for dashboard display
- never write to the file

Suggested parser return shape:

```json
{
  "label": "experiment_tracker",
  "exists": true,
  "path": "14_context/money_workflows/experiment_tracker.jsonl",
  "records": [],
  "valid_count": 0,
  "parse_errors_count": 0,
  "parse_error_samples": [],
  "warnings": []
}
```

## Latest Review Run Detection

Optional helper:

- scan `05_logs/money_reviews/`
- select newest directory by mtime or run ID timestamp
- read `run_summary.json` if present
- never read huge markdown files by default
- return warning if directory missing

Latest review run fields:

- `run_id`
- `path`
- `created_at_utc`
- `artifact_files`
- `decision_candidate_count`
- `tracker_mutated`
- `live_actions_taken`

## Response Fields

The route should return:

- `ok`
- `read_only`
- `generated_at`
- `source_files`
- `latest_review_run`
- `totals`
- `decisions_by_status`
- `decisions_by_type`
- `experiments_by_status`
- `experiments_by_workflow_type`
- `top_score_buckets`
- `approval_required_count`
- `blocked_count`
- `next_manual_actions`
- `warnings`
- `parse_errors`
- `safety`

## Response JSON Example

```json
{
  "ok": true,
  "read_only": true,
  "generated_at": "2026-04-29T00:00:00Z",
  "source_files": {
    "experiment_tracker": { "exists": true, "valid_count": 3, "parse_errors_count": 0 },
    "manual_decision_queue": { "exists": false, "valid_count": 0, "parse_errors_count": 0 },
    "product_metrics": { "exists": false, "valid_count": 0, "parse_errors_count": 0 },
    "product_drafts": { "exists": false, "valid_count": 0, "parse_errors_count": 0 },
    "product_build_packs": { "exists": false, "valid_count": 0, "parse_errors_count": 0 }
  },
  "latest_review_run": null,
  "totals": {
    "experiments": 3,
    "manual_decisions": 0,
    "manual_metric_records": 0,
    "product_drafts": 0,
    "product_build_packs": 0,
    "manual_sales": 0,
    "manual_revenue": 0,
    "opt_ins": 0
  },
  "decisions_by_status": {},
  "decisions_by_type": {},
  "experiments_by_status": { "idea": 3 },
  "experiments_by_workflow_type": {
    "video_to_business_system": 1,
    "digital_product": 1,
    "simple_phone_game": 1
  },
  "top_score_buckets": {},
  "approval_required_count": 3,
  "blocked_count": 0,
  "next_manual_actions": [
    {
      "source_type": "experiment",
      "source_id": "exp_20260428_120001_vid001",
      "action": "draft MVP outline and review with operator before any pricing or listing",
      "approval_required": true
    }
  ],
  "warnings": [
    "manual_decision_queue.jsonl missing; returning zero-state decision summary",
    "product_metrics.jsonl missing; manual launch metrics not available"
  ],
  "parse_errors": [],
  "safety": {
    "mutation_enabled": false,
    "external_api_used": false,
    "scraping_enabled": false,
    "live_account_actions_enabled": false,
    "posting_enabled": false,
    "selling_enabled": false,
    "outreach_enabled": false,
    "payment_actions_enabled": false
  }
}
```

## Computation Notes

Totals:

- experiments: valid experiment tracker records
- manual decisions: valid decision queue records
- manual metric records: valid product metrics records
- product drafts/build packs: valid future JSONL records
- sales/revenue/opt-ins: manually recorded metrics only

Counts:

- `decisions_by_status` from decision queue `status`
- `decisions_by_type` from decision queue `decision_type`
- `experiments_by_status` from experiment `status`
- `experiments_by_workflow_type` from experiment `workflow_type`
- `top_score_buckets` from experiment `scoring.priority_bucket`
- `approval_required_count` across experiments and decision records
- `blocked_count` from experiment `status == "blocked"` plus queue `status == "paused"`

Next manual actions:

- use accepted/in-progress queue records first
- fall back to experiment `next_action`
- include source IDs and file references
- never convert next actions into buttons that execute

## Zero-State Behavior

If every future file is missing, return:

- `ok: true`
- empty counts
- warnings
- no stack trace
- no crash

This lets the dashboard ship before every tracker exists.

## Safety Requirements

The route must not:

- mutate JSONL files
- append queue records
- execute model output
- call Gemma
- call external APIs
- scrape platforms
- use accounts
- post, sell, email, outreach, pay, upload, or publish

## Validation Plan

Future Claude checks:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
```

If a route smoke is added:

```powershell
Invoke-RestMethod http://localhost:3210/api/ghoti/money/weekly-review/summary
```

Only run the route smoke when the dashboard server is already intentionally running.

## Verdict

The summary route should be a safe read-only lens over local Money OS files. It is not a workflow engine.
