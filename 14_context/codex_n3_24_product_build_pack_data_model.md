# Codex N+3.24 Product Build Pack Data Model

Status: codex_planning_only / product_build_pack_data_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The product build pack data model should track which product drafts have been converted into local MVP build packs. It should remain append-only at first and should not imply that anything has been published, listed, sold, uploaded, or delivered to customers.

## Proposed Files

Future append-only tracker:

```text
14_context/money_workflows/product_build_packs.jsonl
```

Future schema, only if approved:

```text
14_context/money_workflows/product_build_packs.schema.json
```

## JSONL Fields

Recommended record fields:

- `build_pack_id`
- `created_at`
- `source_product_draft_id`
- `source_experiment_id`
- `source_run_id`
- `product_name`
- `product_type`
- `target_customer`
- `offer`
- `deliverables`
- `price_test`
- `approval_status`
- `build_status`
- `distribution_status`
- `email_list_status`
- `risk_level`
- `files`
- `artifact_dir`
- `metrics`
- `notes`

## Status Fields

Recommended `approval_status` values:

- `draft_created`
- `needs_review`
- `approved_for_build`
- `approved_for_manual_publish`
- `paused`
- `rejected`

Recommended `build_status` values:

- `not_started`
- `pack_generated`
- `mvp_building`
- `mvp_ready_for_review`
- `mvp_approved`
- `paused`
- `killed`

Recommended `distribution_status` values:

- `not_started`
- `content_draft_ready`
- `manual_publish_approved`
- `published_manually`
- `measuring`
- `paused`

Recommended `email_list_status` values:

- `not_started`
- `lead_magnet_drafted`
- `opt_in_copy_ready`
- `manual_setup_approved`
- `active_manual`
- `paused`

## Metrics Placeholder

Metrics should be optional and manually maintained:

```json
{
  "views": 0,
  "clicks": 0,
  "opt_ins": 0,
  "replies": 0,
  "sales": 0,
  "revenue_usd": 0,
  "refunds": 0,
  "time_spent_hours": 0,
  "support_requests": 0
}
```

No live platform metric fetch is part of this model.

## Example Record

```json
{"build_pack_id":"build_pack_20260429_001","created_at":"2026-04-29T00:00:00Z","source_product_draft_id":"draft_20260429_001","source_experiment_id":"exp_20260428_120001_vid001","source_run_id":"product_build_pack_20260429_001","product_name":"AI Operator Starter Kit","product_type":"markdown_template_bundle","target_customer":"solo AI builders and engineering students","offer":"local AI operator setup templates, safety gates, and workflow checklists","deliverables":["README","quick start","setup checklist","approval gate checklist","worker card template","example filled workflow"],"price_test":"$9-$27","approval_status":"needs_review","build_status":"pack_generated","distribution_status":"not_started","email_list_status":"lead_magnet_drafted","risk_level":"low","files":["05_logs/product_build_packs/product_build_pack_20260429_001/product_brief.md","05_logs/product_build_packs/product_build_pack_20260429_001/build_steps.md"],"artifact_dir":"05_logs/product_build_packs/product_build_pack_20260429_001","metrics":{"views":0,"clicks":0,"opt_ins":0,"replies":0,"sales":0,"revenue_usd":0,"refunds":0,"time_spent_hours":0,"support_requests":0},"notes":"Draft build pack only. No listing, upload, payment, or public action."}
```

## Schema Proposal

`product_build_packs.schema.json` should:

- require `build_pack_id`
- require `created_at`
- require `product_name`
- require `target_customer`
- require `offer`
- require `approval_status`
- require `build_status`
- require `artifact_dir`
- constrain status values
- allow missing metrics
- allow empty `files`
- disallow secret-like fields such as `api_key`, `password`, `token`, `stripe_key`, or `customer_email`

## Append-Only Policy

Initial behavior:

- The future generator may append one record after a successful artifact run.
- Dashboard reads must never edit, delete, or reorder records.
- Manual corrections should happen through a later explicit workflow.
- No record should mark live publication unless the operator records it manually after approval.

## Relationship To Other Trackers

This file should connect to:

- `experiment_tracker.jsonl` through `source_experiment_id`
- future `product_drafts.jsonl` through `source_product_draft_id`
- future `content_shots.jsonl` through product launch content

## Data Model Verdict

A simple append-only `product_build_packs.jsonl` tracker is enough. It keeps product MVP progress visible without building a database or connecting commerce platforms.
