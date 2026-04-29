# Codex N+3.26 Product Metrics Intake Model

Status: codex_planning_only / manual_product_metrics_intake / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The metrics intake model should let the operator manually record launch or distribution results after a product test. Ghoti should not scrape, log in, fetch platform metrics, inspect payments, or infer revenue. Every number is manually entered or explicitly imported through a future approved workflow.

## Proposed File

Future append-only tracker:

```text
14_context/money_workflows/product_metrics.jsonl
```

Optional schema:

```text
14_context/money_workflows/product_metrics.schema.json
```

## Manual Metrics Fields

Recommended record fields:

- `metrics_id`
- `created_at`
- `product_id`
- `date`
- `platform`
- `experiment_id`
- `build_pack_id`
- `manual_launch_review_id`
- `impressions`
- `clicks`
- `opt_ins`
- `replies`
- `sales`
- `revenue`
- `refunds`
- `conversion_notes`
- `traffic_sources`
- `content_used`
- `email_list_growth`
- `customer_feedback`
- `next_action`
- `decision`
- `approval_required`
- `manual_entry_only`
- `notes`

Decision values:

- `kill`
- `pause`
- `iterate`
- `double_down`
- `needs_more_data`

## JSONL Shape

Each line should be one JSON object:

```json
{"metrics_id":"metrics_20260429_001","created_at":"2026-04-29T00:00:00Z","product_id":"prod_ai_operator_starter_kit","date":"2026-04-29","platform":"manual_whop_or_store_record","experiment_id":"exp_20260428_120001_vid001","build_pack_id":"build_pack_20260429_001","manual_launch_review_id":"launch_review_20260429_001","impressions":0,"clicks":0,"opt_ins":0,"replies":0,"sales":0,"revenue":0,"refunds":0,"conversion_notes":"Manual placeholder. No platform API used.","traffic_sources":["manual_entry"],"content_used":[],"email_list_growth":0,"customer_feedback":[],"next_action":"Review after first real manual launch metrics exist.","decision":"needs_more_data","approval_required":true,"manual_entry_only":true,"notes":"No scraping, no platform login, no automated revenue fetch."}
```

## Validation Rules

Required:

- `metrics_id`: string
- `created_at`: ISO timestamp string
- `product_id`: string
- `date`: date string
- `platform`: string
- `decision`: enum
- `manual_entry_only`: true

Numeric fields should be numbers greater than or equal to zero:

- `impressions`
- `clicks`
- `opt_ins`
- `replies`
- `sales`
- `revenue`
- `refunds`
- `email_list_growth`

Array fields:

- `traffic_sources`
- `content_used`
- `customer_feedback`

Recommended constraints:

- `refunds` should not exceed `sales` unless explained in notes.
- `sales` should not be inferred from revenue.
- `conversion_notes` should distinguish facts from hypotheses.
- `manual_entry_only` should always be true in the first version.

## Derived Metrics

Dashboard may compute only when denominator exists:

- click-through rate: `clicks / impressions`
- opt-in rate: `opt_ins / clicks`
- reply rate: `replies / clicks`
- sales conversion: `sales / clicks`
- refund rate: `refunds / sales`
- revenue per click: `revenue / clicks`

If denominator is zero or missing, return null rather than fake precision.

## No Automatic Scraping

Not allowed:

- platform API calls
- browser login
- dashboard scraping
- payment provider scraping
- revenue inference
- email provider scraping
- app-store scraping
- social metric scraping

## Metrics Intake Verdict

Use append-only manual metrics first. Honest small numbers beat automated fake certainty.
