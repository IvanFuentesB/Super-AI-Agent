# Codex N+3.31 Manual Queue Draft Intake Spec

Status: codex_planning_only / manual_queue_draft_intake / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Specify a future local helper that lets the operator convert a reviewed decision candidate into an append-only manual decision queue entry. The helper should be boring, explicit, dry-run first, and standard-library-only.

Future helper:

```text
03_scripts/manual_decision_queue_new_item.py
```

Future queue file:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

## Non-Goals

The helper must not:

- post
- sell
- email
- outreach
- upload
- scrape
- process payments
- open browsers
- log into accounts
- call external APIs
- execute model output
- mutate generated weekly review artifacts
- approve public actions

## Required Behavior

The helper should:

- use Python standard library only
- stay inside repo root
- support dry-run mode
- require explicit append mode for writes
- append exactly one JSON object per line
- never edit or delete previous queue records
- write only to `14_context/money_workflows/manual_decision_queue.jsonl`
- validate enum values before output
- generate a stable `decision_id`
- set public/live/external action flags to false
- print the generated record in dry-run mode
- fail closed if required fields are missing

## Suggested CLI

Dry-run first:

```powershell
python 03_scripts/manual_decision_queue_new_item.py --dry-run --source-type weekly_review_candidate --source-run-id mrev_20260429_153000_ab12cd --candidate-id cand_mrev_20260429_001 --decision-type CREATE_CONTENT_BATCH --linked-experiment-id exp_20260428_120002_dig002 --recommendation "Create a local content batch draft for operator review" --reason "Clear buyer pain and content-volume potential; no public metrics yet" --risk-level low --next-manual-action "Generate local content batch artifacts only"
```

Explicit append:

```powershell
python 03_scripts/manual_decision_queue_new_item.py --append --source-type weekly_review_candidate --source-run-id mrev_20260429_153000_ab12cd --candidate-id cand_mrev_20260429_001 --decision-type CREATE_CONTENT_BATCH --linked-experiment-id exp_20260428_120002_dig002 --recommendation "Create a local content batch draft for operator review" --reason "Clear buyer pain and content-volume potential; no public metrics yet" --risk-level low --next-manual-action "Generate local content batch artifacts only"
```

Exactly one of `--dry-run` or `--append` should be accepted. If neither is supplied, the helper should fail closed or default to dry-run with a clear message.

## Suggested Fields

Each appended queue record should include:

- `decision_id`
- `created_at`
- `source_type`
- `source_run_id`
- `candidate_id`
- `decision_type`
- `linked_experiment_id`
- `linked_product_id`
- `recommendation`
- `reason`
- `risk_level`
- `next_manual_action`
- `deadline_optional`
- `approval_required`
- `status`
- `metrics_snapshot`
- `files`
- `public_action_allowed`
- `live_account_action_allowed`
- `external_action_allowed`
- `model_output_executed`

Recommended first-version defaults:

```json
{
  "approval_required": true,
  "status": "candidate",
  "public_action_allowed": false,
  "live_account_action_allowed": false,
  "external_action_allowed": false,
  "model_output_executed": false
}
```

## Allowed Decision Types

- `DOUBLE_DOWN`
- `ITERATE`
- `PAUSE`
- `KILL`
- `BUILD_NEXT`
- `CREATE_CONTENT_BATCH`
- `CREATE_LEAD_MAGNET`
- `REVIEW_LAUNCH_CHECKLIST`
- `COLLECT_MORE_DATA`

## Allowed Statuses

For N+3.31 intake, prefer:

- `candidate`
- `accepted_for_manual_work`
- `in_progress`
- `completed`
- `paused`
- `killed`
- `superseded`

The initial append from candidate review should normally use `candidate` or `accepted_for_manual_work`. Neither status permits live action.

## Validation Rules

The helper should reject:

- missing `decision_type`
- unsupported decision type
- unsupported status
- missing recommendation or reason
- missing next manual action
- non-local file paths in `files`
- `approval_required=false` when action is public, money-facing, account-based, or external
- attempts to set public/live/external action flags true
- action text that implies auto-posting, selling, outreach, payment, scraping, upload, launch, or login

## Example Record

```json
{"decision_id":"dec_20260430_001","created_at":"2026-04-30T00:00:00Z","source_type":"weekly_review_candidate","source_run_id":"mrev_20260429_153000_ab12cd","candidate_id":"cand_mrev_20260429_001","decision_type":"CREATE_CONTENT_BATCH","linked_experiment_id":"exp_20260428_120002_dig002","linked_product_id":null,"recommendation":"Create a local content batch draft for operator review.","reason":"The experiment has clear buyer pain and can produce many content shots, but has no public metrics yet.","risk_level":"low","next_manual_action":"Generate local content batch artifacts only; do not post.","deadline_optional":null,"approval_required":true,"status":"candidate","metrics_snapshot":{"impressions":0,"clicks":0,"opt_ins":0,"sales":0,"revenue_usd":0},"files":["05_logs/money_reviews/mrev_20260429_153000_ab12cd/decisions_recommended.jsonl","14_context/money_workflows/experiment_tracker.jsonl"],"public_action_allowed":false,"live_account_action_allowed":false,"external_action_allowed":false,"model_output_executed":false}
```

## Future Validation Commands

```powershell
python -m py_compile 03_scripts/manual_decision_queue_new_item.py
python 03_scripts/manual_decision_queue_new_item.py --dry-run --source-type weekly_review_candidate --source-run-id mrev_sample --candidate-id cand_sample --decision-type COLLECT_MORE_DATA --recommendation "Collect manual metrics" --reason "No real metrics yet" --risk-level low --next-manual-action "Record manual observations locally"
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); print('missing ok' if not p.exists() else sum(1 for line in p.read_text(encoding='utf-8').splitlines() if line.strip() and json.loads(line)))"
git diff --check
```

## Verdict

Manual queue draft intake should preserve the operator's agency. It records reviewed next actions locally, but it never performs them.
