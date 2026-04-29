# Codex N+3.25 Product Pack Summary Route Spec

Status: codex_planning_only / product_pack_summary_route / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define a future read-only backend route that summarizes product build packs for the dashboard. The route should tolerate missing data, malformed JSONL, field drift, missing scoring, and missing metrics while never mutating files or touching live services.

## Proposed Route

```text
GET /api/ghoti/money/product-build-packs/summary
```

Primary source:

```text
14_context/money_workflows/product_build_packs.jsonl
```

Optional related sources later:

- `14_context/money_workflows/product_drafts.jsonl`
- `14_context/money_workflows/experiment_tracker.jsonl`

## Response Fields

The response should include:

- `ok`
- `read_only`
- `route`
- `source_files`
- `tracker_exists`
- `total_build_packs`
- `status_counts`
- `approval_status_counts`
- `build_status_counts`
- `distribution_status_counts`
- `email_list_status_counts`
- `risk_level_counts`
- `latest_build_packs`
- `top_ready_to_build`
- `blocked_items`
- `warnings`
- `parse_errors`
- `parse_error_samples`
- `generated_at`
- `safety`

## Example Response

```json
{
  "ok": true,
  "read_only": true,
  "route": "/api/ghoti/money/product-build-packs/summary",
  "source_files": {
    "product_build_packs": "14_context/money_workflows/product_build_packs.jsonl",
    "product_drafts": "14_context/money_workflows/product_drafts.jsonl",
    "experiments": "14_context/money_workflows/experiment_tracker.jsonl"
  },
  "tracker_exists": false,
  "total_build_packs": 0,
  "status_counts": {},
  "approval_status_counts": {},
  "build_status_counts": {},
  "distribution_status_counts": {},
  "email_list_status_counts": {},
  "risk_level_counts": {},
  "latest_build_packs": [],
  "top_ready_to_build": [],
  "blocked_items": [],
  "warnings": ["product_build_packs.jsonl missing; returning zero-state summary"],
  "parse_errors": 0,
  "parse_error_samples": [],
  "generated_at": "2026-04-29T00:00:00Z",
  "safety": {
    "live_actions_enabled": false,
    "mutation_enabled": false,
    "external_api_used": false,
    "payment_actions_enabled": false,
    "publishing_enabled": false
  }
}
```

## Tolerant JSONL Parser

Algorithm:

1. Resolve the repo-relative JSONL path.
2. If missing, return zero-state.
3. Read UTF-8 text.
4. Split by line.
5. Ignore blank lines.
6. Try `JSON.parse` for each non-empty line.
7. On parse failure, increment `parse_errors`.
8. Store compact parse error samples with line number and message.
9. Continue parsing later lines.
10. Normalize missing fields with safe defaults.

Limit parse error samples to 3 to 5 items.

## Count Rules

- `total_build_packs`: valid parsed records only.
- `status_counts`: count `build_status || status || "unknown"`.
- `approval_status_counts`: count `approval_status || "unknown"`.
- `build_status_counts`: count `build_status || "unknown"`.
- `distribution_status_counts`: count `distribution_status || "unknown"`.
- `email_list_status_counts`: count `email_list_status || "unknown"`.
- `risk_level_counts`: count `risk_level || "unknown"`.

## Latest Items

`latest_build_packs` should include at most 10 records, sorted by `created_at` descending when valid, otherwise file order fallback.

Recommended compact row fields:

- `build_pack_id`
- `created_at`
- `product_name`
- `product_type`
- `approval_status`
- `build_status`
- `distribution_status`
- `email_list_status`
- `risk_level`
- `artifact_dir`
- `next_manual_action`

## Top Ready-To-Build

Route should compute a safe priority list:

- include records with `approval_status === "approved_to_build_local"`
- prefer `build_status` in `draft_ready`, `build_pack_generated`, or `operator_review`
- exclude `risk_level === "high"` unless explicitly marked reviewed
- prefer records with non-empty `deliverables`
- prefer records with `artifact_dir`

Cap list at 5.

## Blocked Items

Return compact blocked items:

```json
{
  "build_pack_id": "build_pack_...",
  "product_name": "AI Operator Starter Kit",
  "blocked_reasons": ["needs_operator_review", "missing_distribution_status"]
}
```

Potential blocked reasons:

- `needs_operator_review`
- `approval_missing`
- `high_risk`
- `missing_deliverables`
- `missing_artifact_dir`
- `missing_distribution_status`
- `missing_email_list_status`
- `paused`
- `killed`

## Safety Requirements

The route must not:

- write JSONL
- delete records
- approve records
- publish, upload, sell, email, post, or message
- call Whop/Gumroad/Stripe/social/email APIs
- run Gemma/Ollama
- scrape or fetch platform data
- expose secrets

## Summary Route Verdict

The route should be intentionally boring: read local files, count states, report warnings, and stay powerless.
