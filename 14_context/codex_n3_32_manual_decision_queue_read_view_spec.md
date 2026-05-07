# Codex N+3.32 Manual Decision Queue Read View Spec

Status: codex_planning_only / manual_decision_queue_read_view / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 557b624
Origin HEAD: 557b624
Local/origin sync: synced at audit start

## Purpose

Design the future read-only view for the Money OS manual decision queue. This is the layer after N+3.31's candidate review and dry-run queue intake design.

The read view should show queued local work and review notes. It must not approve, execute, mutate, publish, sell, email, pay, scrape, upload, or log into accounts.

## Source Files

Primary future queue source:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Optional future schema:

```text
14_context/money_workflows/manual_decision_queue.schema.json
```

Upstream candidate source for reference only:

```text
05_logs/money_reviews/<run_id>/decisions_recommended.jsonl
```

The upstream candidate file is not the queue. It should only be used to show provenance when a queue item references a candidate.

## Proposed Read-Only API Route

Future route:

```text
GET /api/ghoti/money/manual-decision-queue/summary
```

Required behavior:

- read local repo files only
- parse `manual_decision_queue.jsonl` line by line
- tolerate missing queue file
- tolerate empty queue file
- tolerate malformed JSONL lines
- tolerate missing optional fields
- return warnings instead of crashing
- never write to queue files
- never call external APIs
- never execute model output
- never create approval records
- never trigger live/public/money-facing actions

## Response Shape

Suggested response fields:

- `status`
- `ok`
- `read_only`
- `generated_at`
- `queue_file`
- `queue_exists`
- `total_items`
- `valid_items`
- `parse_errors`
- `by_status`
- `by_decision_type`
- `by_risk_level`
- `approval_required_count`
- `blocked_count`
- `latest_items`
- `top_local_work_items`
- `warnings`
- `source_files`
- `safety`

Required safety flags:

```json
{
  "mutation_enabled": false,
  "approval_enabled": false,
  "execution_enabled": false,
  "posting_enabled": false,
  "selling_enabled": false,
  "outreach_enabled": false,
  "payment_actions_enabled": false,
  "scraping_enabled": false,
  "live_account_actions_enabled": false
}
```

## Dashboard Card Proposal

Card title:

```text
Money OS - Manual Decision Queue
```

Subtitle:

```text
Local reviewed work queue. Read-only. No approval or execution.
```

Card sections:

- queue health summary
- counts by status
- counts by decision type
- risk level counts
- approval-required count
- blocked items count
- latest queue items
- top local work candidates
- warnings and malformed-line count
- source file paths

## Display Fields Per Item

Each item row should show:

- queue item id, usually `decision_id`
- `created_at`
- source, such as `source_type`, `source_run_id`, `candidate_id`, or `source_id`
- title or recommendation
- category, usually `decision_type`
- status
- risk level
- approval required yes/no
- next local step
- blocked reason
- human review note
- related files

If the source record uses older field names, the route should normalize:

- `recommendation` or `next_manual_action` can become display title
- `reason` can become human review context
- `source_id` can be displayed when `source_run_id` is missing
- `related_files` or `files` can become source links

## Empty-State Behavior

Queue file missing:

```text
No manual decision queue exists yet. Generate decision candidates first, then use dry-run intake before appending local queue items.
```

Queue file empty:

```text
Manual decision queue exists but has no items yet.
```

No actionable local items:

```text
No safe local work items are ready. Review blocked or approval-required items manually.
```

## Malformed JSONL Behavior

The parser should:

- count malformed lines
- skip malformed lines
- include line numbers in warnings
- cap warning details, for example first 10 malformed lines
- never rewrite the file
- never fail the whole route because one line is bad

## Max Items And Sorting

Recommended defaults:

- parse all lines up to a practical cap, such as 1000 records
- return latest 25 items
- return top 10 local work candidates
- sort latest items by `created_at` descending
- sort top local work candidates by safe status first, low risk first, and approval blockers last

Suggested safe local statuses for top local work:

- `candidate`
- `accepted_for_manual_work`
- `in_progress`

Statuses such as `paused`, `killed`, `superseded`, and `completed` should be visible but not promoted as next work.

## Copy-Only UX Actions

Allowed:

- refresh
- copy queue file path
- copy item JSON
- copy related file path
- copy local next-step text
- expand item details

Not allowed:

- approve
- execute
- append
- reject
- delete
- reorder and save
- post
- sell
- email
- pay
- scrape
- upload
- launch
- log into accounts

## No Approval Or Execute Semantics

The dashboard must not make a manual queue item look like an approval request. Approval is a separate concept with higher risk and separate human intent.

The queue item may say "approval required", but the card must not provide an approval button.

## Verdict

The N+3.32 read view should make local manual decisions visible and sortable without turning them into actions.
