# Codex N+3.19 Shot Counter Data Model Audit

Status: codex_planning_only / data_model_audit / not_runtime_wired

## Current Tracker Observations

Current file inspected:

```text
14_context/money_workflows/experiment_tracker.jsonl
```

Observed valid records:

- `exp_20260428_120001_vid001`
- `exp_20260428_120002_dig002`
- `exp_20260428_120003_gam003`

Current count: 3 sample experiments.

Observed workflow types:

- `video_to_business_system`
- `digital_product`
- `simple_phone_game`

Observed status:

- all current sample records use `idea`.

Observed approval state:

- all current sample records set `approval_required: true`.

Observed metrics:

- each sample has `metrics.revenue_usd: 0`.
- each sample has `metrics.time_spent_hours: 0`.

Observed distribution fields:

- current records use `distribution_channels`.
- current values include `manual_review_first`, `future_gumroad`, `future_whop`, `future_tiktok_bio`, `future_google_play`, and `future_app_store`.

Observed scoring:

- current committed tracker records do not include scoring.
- dirty N+3.18 schema work adds optional scoring support, but N+3.18 is not committed yet.

## Schema Compatibility Notes

Current/dirty schema expects:

- `experiment_id`
- `created_at`
- `workflow_type`
- `source`
- `product_idea`
- `target_customer`
- `pain_point`
- `offer`
- `status`
- `next_action`
- `approval_required`

Optional useful fields:

- `price_test`
- `distribution_channels`
- `content_assets`
- `metrics`
- `risk_level`
- `notes`
- `files`
- `scoring`

N+3.19 should not require scoring to exist. It should display bucket counts only when `record.scoring.priority_bucket` is present.

## Malformed-Line Handling

The route should read JSONL defensively:

1. Split on newlines.
2. Ignore empty lines.
3. Try `JSON.parse` each non-empty line.
4. On parse failure, increment `parse_errors`.
5. Continue processing later lines.
6. Return a parse error summary but do not crash.

Recommended parse error field:

```json
{
  "parse_errors": 1,
  "parse_error_samples": [
    { "line": 7, "error": "Unexpected token ..." }
  ]
}
```

Cap samples to 3-5 items so the dashboard never dumps huge malformed content.

## Metrics Aggregation Notes

Metrics may be missing, null, partial, or string-typed in future hand-edited records. The route should use safe numeric conversion:

- `Number(record.metrics?.revenue_usd) || 0`
- `Number(record.metrics?.time_spent_hours) || 0`

Other future metrics can be passed through later, but N+3.19 should keep the first summary small.

## Scoring Bucket Expectations

N+3.18 scoring target:

- `A`: total score >= 40
- `B`: total score >= 32
- `C`: total score >= 24
- `D`: total score < 24

N+3.19 route should not recompute scores. It should read `record.scoring.priority_bucket` if present. Recomputing belongs in the experiment helper, not the dashboard read model.

Recommended response shape:

```json
"by_priority_bucket": {
  "A": 0,
  "B": 0,
  "C": 0,
  "D": 0,
  "unscored": 3
}
```

## Channel And Exposure Aggregation Notes

Handle both:

- `distribution_channels`
- `channels`

Normalization:

- trim whitespace.
- lowercase for counts.
- preserve display label as source value if useful.
- skip empty strings.

Initial route should count frequency only. It should not infer platform account state or attempt account checks.

## Latest Experiment Selection

Preferred:

- sort by `created_at` descending when valid.

Fallback:

- preserve file order and take last 10 valid records.

Each latest experiment should be compact:

```json
{
  "experiment_id": "...",
  "created_at": "...",
  "workflow_type": "...",
  "status": "...",
  "priority_bucket": null,
  "product_idea": "...",
  "next_action": "...",
  "approval_required": true
}
```

## Data Model Verdict

The existing tracker is already enough for a read-only shot counter. The dashboard route must be tolerant of missing scoring, missing metrics, malformed JSONL lines, and future field name drift.
