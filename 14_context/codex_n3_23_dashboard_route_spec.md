# Codex N+3.23 Dashboard Route Spec

Status: codex_planning_only / dashboard_route_spec / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define the future backend route for a read-only product draft summary. The route should make product-shot state visible without enabling commerce, posting, uploads, payments, account actions, or external calls.

## Proposed Route

```text
GET /api/ghoti/money/product-drafts/summary
```

Input:

```text
14_context/money_workflows/product_drafts.jsonl
```

## Required Behavior

- Parse product drafts if the file exists.
- Return safe zero-state summary if the file is missing.
- Tolerate malformed JSONL lines.
- Never mutate data.
- Never execute model output.
- Never call external APIs.
- Never inspect live platform accounts.
- Never expose secrets.
- Limit latest drafts to 10.
- Limit parse error samples to 3 to 5 items.

## Suggested Response Shape

```json
{
  "ok": true,
  "read_only": true,
  "route": "/api/ghoti/money/product-drafts/summary",
  "tracker_path": "14_context/money_workflows/product_drafts.jsonl",
  "tracker_exists": true,
  "total_product_drafts": 0,
  "parse_errors": 0,
  "parse_error_samples": [],
  "by_status": {},
  "by_workflow_type": {},
  "by_priority_bucket": {},
  "approval_queue_counts": {},
  "approval_required_count": 0,
  "distribution_readiness": {
    "with_distribution_channels": 0,
    "missing_distribution_channels": 0,
    "with_three_or_more_channels": 0
  },
  "email_list_readiness": {
    "with_email_list_angle": 0,
    "missing_email_list_angle": 0
  },
  "fulfillment_readiness": {
    "with_fulfillment_plan": 0,
    "missing_fulfillment_plan": 0,
    "with_deliverables": 0,
    "missing_deliverables": 0
  },
  "risk_flags": {},
  "missing_field_warnings": [],
  "top_drafts": [],
  "latest_drafts": [],
  "safety": {
    "live_actions_enabled": false,
    "publishing_enabled": false,
    "payment_actions_enabled": false,
    "account_actions_enabled": false,
    "external_api_used": false
  },
  "updated_at_utc": "..."
}
```

## Parser Behavior

Recommended parser:

1. Read the JSONL file as UTF-8.
2. Split on line breaks.
3. Ignore empty lines.
4. Try `JSON.parse` on each line.
5. On parse failure, increment `parse_errors`.
6. Store compact parse error samples with line number and message.
7. Continue parsing remaining lines.
8. Normalize missing fields with safe defaults.

## Aggregation Rules

- `total_product_drafts`: valid parsed records only.
- `by_status`: count `approval_status || status || "unknown"`.
- `by_workflow_type`: count `workflow_type || "unknown"`.
- `by_priority_bucket`: count `priority_bucket || score.priority_bucket || "unscored"`.
- `approval_queue_counts`: count each `approval_status`.
- `approval_required_count`: records where `approval_required === true`.
- `risk_flags`: frequency count of each string in `risk_flags`.
- `latest_drafts`: most recent 10 by `created_at`, falling back to file order.
- `top_drafts`: top 5 by `score.total_score`, falling back to `total_score`, excluding records without numeric score.

## Missing Field Warning Rules

Each warning should be compact:

```json
{
  "draft_id": "draft_...",
  "missing": ["offer", "email_list_angle"]
}
```

Limit warnings to a reasonable number, for example 20.

## Frontend Card Behavior

The frontend should:

- Fetch the summary route.
- Render a "Money OS — Product Drafts" card.
- Show zero-state copy if no file exists.
- Show parse error warnings without crashing.
- Render latest drafts and top drafts as compact tables.
- Show safety label.
- Offer refresh only.

The frontend should not:

- approve states
- reject states
- edit JSONL
- delete drafts
- publish/list/upload
- trigger payments
- open platform account actions
- send email or outreach
- call external APIs

## Safe Error Reporting

If reading fails:

- return `ok: false` or `ok: true` with `tracker_exists: false` depending on failure type
- include a short error message
- do not dump full file contents
- do not leak absolute paths beyond repo-relative paths where possible

## Suggested Validation Commands

Claude Code should later run:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/product_drafts.schema.json
git diff --check
git status --short
```

If sample JSONL is added, run a line-by-line JSON parse.

## Dashboard Route Verdict

The route should be a read-only local summary endpoint. It should make product drafts visible but intentionally powerless.
