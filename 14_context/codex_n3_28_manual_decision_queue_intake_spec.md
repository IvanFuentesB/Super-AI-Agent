# Codex N+3.28 Manual Decision Queue Intake Spec

Status: codex_planning_only / manual_decision_queue_intake / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ac53eed
Origin HEAD: ac53eed
Local/origin sync: synced at audit start

## Purpose

Design the future local append-only intake path for the Money OS manual decision queue. The queue should let the operator record reviewed decisions such as double down, iterate, pause, kill, build next, create content, create a lead magnet, review a launch checklist, or collect more data.

The helper must never execute the decision. It only validates and appends local records after the operator intentionally runs the command.

## Future Files

Schema:

```text
14_context/money_workflows/manual_decision_queue.schema.json
```

Append-only queue:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Both files should be created only in the future implementation milestone, not in this Codex planning pass.

## Queue Statuses

Allowed statuses:

- `candidate`
- `accepted_for_manual_work`
- `in_progress`
- `completed`
- `paused`
- `killed`
- `superseded`

Meaning:

- `candidate`: proposed by Gemma, Codex, Claude, or operator notes; not accepted yet.
- `accepted_for_manual_work`: operator accepted local/manual next step.
- `in_progress`: operator or Claude is working locally.
- `completed`: local/manual work recorded as complete.
- `paused`: intentionally held.
- `killed`: intentionally stopped.
- `superseded`: replaced by a newer decision record.

No status authorizes public or money-facing automation.

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

## Schema Fields

Required fields:

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
- `related_files`
- `metrics_snapshot`
- `public_action_allowed`
- `live_account_action_allowed`
- `external_action_allowed`

Optional fields:

- `due_date_optional`
- `operator_notes`
- `model_source`
- `created_by`
- `supersedes_decision_id`
- `approval_phrase_required`
- `safety_notes`

Hard default flags:

```json
{
  "public_action_allowed": false,
  "live_account_action_allowed": false,
  "external_action_allowed": false
}
```

These should remain false in the first implementation.

## Helper Command Design

Future helper options:

```powershell
python 03_scripts/money_decision_queue_intake.py --dry-run --decision-type DOUBLE_DOWN --source-type experiment --source-id exp_20260428_120002_dig002 --reason "Strong content leverage and clear buyer pain" --next-manual-action "Create content batch draft locally" --risk-level low
```

Append command:

```powershell
python 03_scripts/money_decision_queue_intake.py --append --decision-type DOUBLE_DOWN --source-type experiment --source-id exp_20260428_120002_dig002 --reason "Strong content leverage and clear buyer pain" --next-manual-action "Create content batch draft locally" --risk-level low
```

Recommended CLI args:

- `--dry-run`
- `--append`
- `--decision-type`
- `--source-type`
- `--source-id`
- `--reason`
- `--evidence`
- `--next-manual-action`
- `--approval-required`
- `--risk-level`
- `--status`
- `--related-file`
- `--metrics-json`
- `--operator-notes`
- `--supersedes-decision-id`

Exactly one of `--dry-run` or `--append` should be required.

## Dry-Run Behavior

Dry-run should:

- validate enum values
- validate required fields
- generate the record
- print pretty JSON
- report target queue file path
- report whether append would happen
- not create or modify files

Dry-run should be the default if neither mode is supplied, or the command should fail closed and ask for an explicit mode.

## Append Behavior

Append should:

- create the queue file only if explicitly requested
- append exactly one JSON object as one line
- never edit previous lines
- never delete old decisions
- never execute `next_manual_action`
- never call external APIs
- never open browser or live accounts
- never post, sell, email, scrape, or process payments
- write repo-relative file paths only

If a record supersedes an old decision, append a new record with `supersedes_decision_id`; do not rewrite the old record.

## Example Schema Skeleton

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GhotiManualDecision",
  "type": "object",
  "required": [
    "decision_id",
    "created_at",
    "source_type",
    "source_id",
    "decision_type",
    "reason",
    "evidence",
    "next_manual_action",
    "approval_required",
    "risk_level",
    "status",
    "related_files",
    "metrics_snapshot",
    "public_action_allowed",
    "live_account_action_allowed",
    "external_action_allowed"
  ],
  "properties": {
    "decision_id": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "source_type": { "type": "string" },
    "source_id": { "type": "string" },
    "decision_type": {
      "type": "string",
      "enum": ["DOUBLE_DOWN", "ITERATE", "PAUSE", "KILL", "BUILD_NEXT", "CREATE_CONTENT_BATCH", "CREATE_LEAD_MAGNET", "REVIEW_LAUNCH_CHECKLIST", "COLLECT_MORE_DATA"]
    },
    "reason": { "type": "string" },
    "evidence": { "type": "array", "items": { "type": "string" } },
    "next_manual_action": { "type": "string" },
    "approval_required": { "type": "boolean" },
    "risk_level": { "type": "string", "enum": ["low", "medium", "high"] },
    "status": {
      "type": "string",
      "enum": ["candidate", "accepted_for_manual_work", "in_progress", "completed", "paused", "killed", "superseded"]
    },
    "related_files": { "type": "array", "items": { "type": "string" } },
    "metrics_snapshot": { "type": "object" },
    "public_action_allowed": { "type": "boolean", "const": false },
    "live_account_action_allowed": { "type": "boolean", "const": false },
    "external_action_allowed": { "type": "boolean", "const": false }
  },
  "additionalProperties": false
}
```

## Example Queue Record

```json
{"decision_id":"dec_20260429_001","created_at":"2026-04-29T00:00:00Z","source_type":"experiment","source_id":"exp_20260428_120002_dig002","decision_type":"CREATE_CONTENT_BATCH","reason":"The prompt pack idea has clear buyer pain and can generate many content shots.","evidence":["workflow_type:digital_product","distribution_channels:future_gumroad,future_tiktok_bio","metrics:no_market_data_yet"],"next_manual_action":"Generate a local content batch draft for operator review.","approval_required":true,"risk_level":"low","status":"candidate","due_date_optional":null,"related_files":["14_context/money_workflows/experiment_tracker.jsonl"],"metrics_snapshot":{"impressions":0,"clicks":0,"opt_ins":0,"sales":0,"revenue":0},"operator_notes":"","model_source":"manual_or_weekly_review_candidate","created_by":"operator_or_local_tool","public_action_allowed":false,"live_account_action_allowed":false,"external_action_allowed":false}
```

## Validation Commands

Future Claude validation:

```powershell
python -m json.tool 14_context/money_workflows/manual_decision_queue.schema.json
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('manual decision queue jsonl ok')"
python 03_scripts/money_decision_queue_intake.py --dry-run --decision-type COLLECT_MORE_DATA --source-type experiment --source-id exp_20260428_120001_vid001 --reason "Needs real metrics before action" --next-manual-action "Record manual metrics after operator review" --risk-level low
git diff --check
```

## Verdict

The manual decision queue intake should make decisions durable and reviewable. It should not become an action executor.
