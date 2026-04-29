# Codex N+3.26 Launch Metrics Dashboard Spec

Status: codex_planning_only / launch_metrics_dashboard / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design a future read-only dashboard card for manually entered launch metrics. The dashboard should help the operator see what is working without scraping platforms, logging into accounts, fetching payment data, or mutating trackers.

## Future Card

Card name:

```text
Money OS — Launch Metrics
```

The card should be read-only and should show manually entered results only.

## Proposed Future Route

```text
GET /api/ghoti/money/launch-metrics/summary
```

Primary source:

```text
14_context/money_workflows/product_metrics.jsonl
```

Optional related sources:

- `14_context/money_workflows/product_build_packs.jsonl`
- `14_context/money_workflows/product_drafts.jsonl`
- `14_context/money_workflows/experiment_tracker.jsonl`

## Dashboard Fields

The card should show:

- total manual launches
- total manually recorded revenue
- total sales
- total opt-ins
- total replies
- total refunds
- conversion rate if data exists
- refund rate if data exists
- top products by manually entered revenue
- top channels by manually entered clicks
- top channels by manually entered opt-ins
- top channels by manually entered sales
- products needing follow-up
- products to pause, kill, iterate, or double down
- warnings for missing metrics
- parse errors

## Tolerant Parsing Behavior

The route should:

- tolerate missing `product_metrics.jsonl`
- tolerate empty file
- tolerate malformed lines
- continue after parse errors
- cap parse error samples
- tolerate missing fields
- treat missing numeric metrics as zero for totals
- return null for derived rates when denominator is zero
- never mutate records

## Example Response

```json
{
  "ok": true,
  "read_only": true,
  "tracker_exists": false,
  "total_manual_launches": 0,
  "total_revenue": 0,
  "total_sales": 0,
  "total_opt_ins": 0,
  "total_replies": 0,
  "total_refunds": 0,
  "conversion_rate": null,
  "refund_rate": null,
  "top_products_by_revenue": [],
  "top_channels_by_clicks": [],
  "top_channels_by_opt_ins": [],
  "top_channels_by_sales": [],
  "needs_follow_up": [],
  "decision_counts": {},
  "warnings": ["product_metrics.jsonl missing; returning zero-state summary"],
  "parse_errors": 0,
  "generated_at": "2026-04-29T00:00:00Z",
  "safety": {
    "manual_entry_only": true,
    "external_api_used": false,
    "scraping_enabled": false,
    "mutation_enabled": false,
    "payment_actions_enabled": false
  }
}
```

## Read-Only UI Behavior

Allowed:

- show totals
- show charts or tables later
- show latest manual metric records
- show products needing review
- show decision suggestions based on manually recorded data
- refresh

Not allowed:

- edit metrics
- delete metrics
- fetch platform metrics
- log into accounts
- scrape dashboards
- query payment providers
- send emails
- post content
- trigger launches
- change prices

## Missing Metrics Warnings

Warnings should include:

- product has manual launch but no metrics
- metrics record missing product ID
- metrics record missing platform
- sales exist but revenue missing
- refunds exceed sales without note
- decision missing
- traffic source missing

## Decision Summary

The dashboard can count decisions:

- `kill`
- `pause`
- `iterate`
- `double_down`
- `needs_more_data`

It should not make final business decisions. It should make the bottleneck visible for operator review.

## Launch Metrics Dashboard Verdict

The launch metrics card should make honest manual feedback visible. It should not become an analytics scraper or commerce control panel.
