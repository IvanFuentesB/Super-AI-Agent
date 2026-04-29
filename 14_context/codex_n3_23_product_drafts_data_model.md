# Codex N+3.23 Product Drafts Data Model

Status: codex_planning_only / product_drafts_jsonl_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The product drafts data model should let Ghoti track many product shots without requiring a database or live commerce platform. The first version should be append-only JSONL plus a schema. Dashboard reads should tolerate missing or malformed data.

## Proposed Files

```text
14_context/money_workflows/product_drafts.jsonl
14_context/money_workflows/product_drafts.schema.json
```

These should not be created by Codex in this planning pass. Claude Code can add them later if approved.

## JSONL Fields

Recommended record fields:

- `draft_id`
- `created_at`
- `source_experiment_id`
- `source_run_id`
- `workflow_type`
- `product_name`
- `target_customer`
- `pain_point`
- `offer`
- `deliverables`
- `price_test`
- `score`
- `priority_bucket`
- `recommended_action`
- `approval_required`
- `approval_status`
- `distribution_channels`
- `email_list_angle`
- `fulfillment_plan`
- `risk_flags`
- `files`
- `artifact_dir`
- `metrics`
- `notes`

## Field Validation Rules

Required for a useful record:

- `draft_id`: string
- `created_at`: ISO timestamp string
- `product_name`: string
- `target_customer`: string
- `pain_point`: string
- `offer`: string
- `approval_required`: boolean
- `approval_status`: one of the approved queue states

Recommended but optional:

- `source_experiment_id`
- `source_run_id`
- `workflow_type`
- `deliverables`
- `price_test`
- `score`
- `priority_bucket`
- `recommended_action`
- `distribution_channels`
- `email_list_angle`
- `fulfillment_plan`
- `risk_flags`
- `files`
- `artifact_dir`
- `metrics`

## Score Object

Recommended score object:

```json
{
  "raw_scores": {
    "speed_to_ship": 5,
    "buyer_pain": 4,
    "buyer_access": 3,
    "distribution_fit": 4,
    "email_list_fit": 5,
    "content_volume_fit": 5,
    "monetization_clarity": 4,
    "proof_required": 2,
    "build_complexity": 2,
    "legal_tos_risk": 1,
    "fulfillment_burden": 2
  },
  "adjusted_scores": {
    "speed_to_ship": 5,
    "buyer_pain": 4,
    "buyer_access": 3,
    "distribution_fit": 4,
    "email_list_fit": 5,
    "content_volume_fit": 5,
    "monetization_clarity": 4,
    "proof_required": 4,
    "build_complexity": 4,
    "legal_tos_risk": 5,
    "fulfillment_burden": 4
  },
  "total_score": 47,
  "priority_bucket": "A"
}
```

## Metrics Placeholder

The first version should allow metrics but expect zeros or nulls:

```json
{
  "views": 0,
  "clicks": 0,
  "opt_ins": 0,
  "replies": 0,
  "sales": 0,
  "revenue_usd": 0,
  "time_spent_hours": 0
}
```

Metrics should be manually entered later. No live platform metric fetch is part of N+3.23.

## Example Record

```json
{"draft_id":"draft_20260429_001","created_at":"2026-04-29T00:00:00Z","source_experiment_id":"exp_20260428_120001_vid001","source_run_id":"product_draft_20260429_001","workflow_type":"digital_product","product_name":"AI Operator Starter Kit","target_customer":"solo AI builders and engineering students","pain_point":"local AI workflows feel chaotic and unsafe","offer":"markdown templates, safety gates, and workflow checklists for a first local AI operator setup","deliverables":["README","setup checklist","worker card template","approval gate checklist","Gemma task routing worksheet"],"price_test":"$9-$27","score":{"total_score":47,"priority_bucket":"A"},"priority_bucket":"A","recommended_action":"BUILD_NOW","approval_required":true,"approval_status":"needs_review","distribution_channels":["email_list","youtube_shorts","x_build_log"],"email_list_angle":"free AI operator setup checklist","fulfillment_plan":"self-serve markdown bundle with examples","risk_flags":["avoid autonomy overclaiming","avoid income claims"],"files":["05_logs/product_drafts/product_draft_20260429_001/whop_listing_draft.md"],"artifact_dir":"05_logs/product_drafts/product_draft_20260429_001","metrics":{"views":0,"clicks":0,"opt_ins":0,"replies":0,"sales":0,"revenue_usd":0,"time_spent_hours":0},"notes":"Draft only. No live listing or payment action."}
```

## Schema Proposal

`product_drafts.schema.json` should be Draft 7 compatible and should:

- require key identity and approval fields
- constrain `approval_status` to approved states
- constrain `priority_bucket` to `A`, `B`, `C`, `D`, or null
- constrain score values to 1 through 5 when raw scores are present
- allow missing score for unscored drafts
- allow `metrics` to be partial
- disallow unexpected secrets fields such as API keys, passwords, tokens, or payment credentials

## Append-Only Policy

Initial behavior:

- Product draft generator may append a new line only when explicitly run.
- Dashboard must never append, edit, delete, or reorder records.
- Manual correction should happen through a later explicit workflow, not the N+3.23 read view.

## Data Model Verdict

`product_drafts.jsonl` is enough for the first product queue. Keep it simple, append-only, and read-only from the dashboard until the approval workflow is mature.
