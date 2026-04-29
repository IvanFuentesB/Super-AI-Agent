# Codex N+3.27 Manual Decision Queue Model

Status: codex_planning_only / manual_decision_queue / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The manual decision queue should collect candidate next actions from weekly reviews and operator notes. It is local-only, append-only, and operator-reviewed. It does not authorize Ghoti to publish, sell, send, scrape, pay, upload, or use live accounts.

## Future File

Append-only queue:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Optional schema:

```text
14_context/money_workflows/manual_decision_queue.schema.json
```

## Decision Types

Allowed decision types:

- `DOUBLE_DOWN`
- `ITERATE`
- `PAUSE`
- `KILL`
- `BUILD_NEXT`
- `CREATE_CONTENT_BATCH`
- `CREATE_LEAD_MAGNET`
- `REVIEW_LAUNCH_CHECKLIST`
- `COLLECT_MORE_DATA`

## Statuses

Recommended queue statuses:

- `candidate`
- `operator_review`
- `approved_for_local_work`
- `rejected`
- `paused`
- `completed_local`
- `needs_more_data`

No queue status should mean public action is approved.

## Required Fields

Each JSONL record should include:

- `decision_id`
- `created_at`
- `source_type`
- `source_id`
- `decision_type`
- `reason`
- `evidence`
- `next_manual_action`
- `approval_required`
- `risk_level`
- `status`
- `due_date_optional`
- `related_files`
- `metrics_snapshot`

Recommended extra fields:

- `operator_notes`
- `model_source`
- `created_by`
- `public_action_allowed`
- `live_account_action_allowed`
- `external_action_allowed`

For the first implementation, the three allowed flags should always be false:

- `public_action_allowed: false`
- `live_account_action_allowed: false`
- `external_action_allowed: false`

## Example Records

Double down candidate:

```json
{"decision_id":"dec_20260429_001","created_at":"2026-04-29T00:00:00Z","source_type":"experiment","source_id":"exp_digital_product_prompt_pack_test","decision_type":"DOUBLE_DOWN","reason":"High apparent leverage and clear content angles, but still no public launch approval.","evidence":["priority_bucket:A","email_list_angle_present:true","distribution_channels:youtube_shorts,tiktok,email"],"next_manual_action":"Draft a content batch and lead magnet locally for operator review.","approval_required":true,"risk_level":"medium","status":"candidate","due_date_optional":null,"related_files":["14_context/money_workflows/experiment_tracker.jsonl"],"metrics_snapshot":{"impressions":0,"clicks":0,"opt_ins":0,"sales":0,"revenue":0},"public_action_allowed":false,"live_account_action_allowed":false,"external_action_allowed":false}
```

Kill candidate:

```json
{"decision_id":"dec_20260429_002","created_at":"2026-04-29T00:00:00Z","source_type":"product_draft","source_id":"prod_unclear_offer_001","decision_type":"KILL","reason":"Weak buyer pain, unclear proof, and high claims risk.","evidence":["buyer_pain:low","proof_required:high","legal_tos_risk:high"],"next_manual_action":"Archive learnings locally and reuse any safe template pieces.","approval_required":false,"risk_level":"high","status":"candidate","due_date_optional":null,"related_files":[],"metrics_snapshot":{},"public_action_allowed":false,"live_account_action_allowed":false,"external_action_allowed":false}
```

## Source Types

Recommended `source_type` values:

- `experiment`
- `product_draft`
- `product_build_pack`
- `manual_launch_metric`
- `content_batch`
- `weekly_review`
- `operator_note`

## Metrics Snapshot

`metrics_snapshot` should store only manually recorded metrics or deterministic local counts:

- impressions
- clicks
- opt_ins
- replies
- sales
- revenue
- refunds
- content_assets
- distribution_channels
- email_list_growth

Do not scrape metrics or infer revenue.

## Safety Gates

The queue may recommend local actions:

- build local product draft
- create local content batch
- generate local lead magnet draft
- review launch checklist
- record manual metrics
- collect more data manually

The queue must not trigger:

- posting
- email sending
- outreach
- selling
- payment actions
- marketplace publishing
- product uploads
- app-store submissions
- browser automation
- account login
- scraping

## Role Boundaries

- Gemma can draft decision candidates.
- Codex can audit the decision model and review risks.
- Claude Code can implement local queue tooling later.
- ChatGPT/operator can decide strategy.
- Human operator must approve anything public, money-facing, account-based, or external.

## Append-Only Policy

The first version should be append-only. If a decision changes, add a new record referencing the earlier decision rather than editing history.

Reason:

- preserves audit trail
- prevents accidental deletion of rejected ideas
- makes weekly learning visible
- keeps the numbers-game record honest

## Verdict

The decision queue should turn weekly review output into local, reviewable next actions. It should not become an autopilot.
