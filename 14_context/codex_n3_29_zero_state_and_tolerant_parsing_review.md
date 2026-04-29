# Codex N+3.29 Zero-State And Tolerant Parsing Review

Status: codex_planning_only / zero_state_tolerant_parsing / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define how the future weekly review artifact generator should behave when Money OS files are missing, empty, malformed, partially implemented, or still evolving. This is important because N+3.18 remains dirty and future N+3.28 queue/summary files may not exist yet.

## Current Repo Truth

At audit time:

- `experiment_tracker.jsonl` exists with three sample planning records.
- `manual_decision_queue.jsonl` does not exist yet.
- `product_metrics.jsonl` does not exist yet.
- `product_drafts.jsonl` does not exist yet.
- `product_build_packs.jsonl` does not exist yet.
- N+3.18 runtime/scoring work remains dirty and unfinished.

The generator must treat missing future files as zero-state, not failure.

## Tolerant JSONL Reader

Future helper behavior:

- accept absolute internal path or repo-relative path
- resolve path under repo root
- if file missing, return `exists: false`, `records: []`, and warning
- if file empty, return `exists: true`, `records: []`, and warning
- skip blank lines
- parse line by line
- continue after bad lines
- cap parse error samples to five
- cap record count in prompt snapshot to avoid huge prompts
- never rewrite malformed files

Suggested return shape:

```json
{
  "label": "experiment_tracker",
  "path": "14_context/money_workflows/experiment_tracker.jsonl",
  "exists": true,
  "valid_count": 3,
  "records_included": 3,
  "parse_errors_count": 0,
  "parse_error_samples": [],
  "warnings": []
}
```

## Missing File Warnings

Examples:

- `manual_decision_queue.jsonl missing; decision queue summary is zero-state`
- `product_metrics.jsonl missing; manual launch metrics unavailable`
- `product_drafts.jsonl missing; product draft counts unavailable`
- `product_build_packs.jsonl missing; build pack counts unavailable`
- `content_shots.jsonl missing; content shot counts unavailable`

Warnings should appear in:

- `tracker_snapshot.json`
- `run_summary.json`
- optionally `weekly_summary.md`

## Malformed Line Handling

If a line fails to parse:

- continue processing later lines
- increment parse error count
- record line number
- record short error message
- do not include full huge line in prompts
- do not fail the whole review unless every primary source is unusable

Example parse warning:

```json
{
  "file": "14_context/money_workflows/experiment_tracker.jsonl",
  "line": 7,
  "error": "Expecting ',' delimiter",
  "sample": "{\"experiment_id\":\"broken\""
}
```

## Empty Tracker Behavior

If the experiment tracker exists but has no valid records:

- write all artifacts
- set counts to zero
- ask Gemma for a bootstrap review
- recommend creating the next 10 local shots
- do not invent metrics

Bootstrap recommendation should focus on:

- video-to-money intake
- digital product draft
- content batch draft
- lead magnet draft
- manual metrics plan

## Field Drift Behavior

The generator should tolerate:

- missing `scoring`
- missing `priority_bucket`
- missing `metrics`
- `revenue` vs `revenue_usd`
- `distribution_channels` absent or string instead of array
- missing `files`
- missing `risk_level`

Rules:

- use defaults
- include warnings
- do not crash
- never infer revenue or proof
- mark confidence lower when important fields are missing

## Zero-State Snapshot Example

```json
{
  "experiment_count": 3,
  "manual_decision_count": 0,
  "manual_metrics_count": 0,
  "product_draft_count": 0,
  "product_build_pack_count": 0,
  "content_shot_count": 0,
  "parse_errors_by_file": {},
  "warnings": [
    "manual_decision_queue.jsonl missing; decision queue summary is zero-state",
    "product_metrics.jsonl missing; manual launch metrics unavailable"
  ],
  "manual_sales_total": 0,
  "manual_revenue_total": 0,
  "manual_opt_ins_total": 0
}
```

## Failure Conditions

The future generator should fail only for:

- input path outside repo root
- disallowed input extension for optional notes
- unable to create artifact directory
- unable to write required artifacts
- local model command unavailable when model execution is requested
- malformed prompt assembly causing implementation error

It should not fail because optional future tracker files are missing.

## Safety Defaults

When data is missing:

- recommend `COLLECT_MORE_DATA`
- require manual review
- mark confidence low
- avoid double-down recommendations unless clear local evidence exists
- never generate public-action instructions

## Validation Plan

Future Claude should test:

- normal tracker with three sample records
- missing `manual_decision_queue.jsonl`
- empty temporary JSONL fixture
- malformed-line fixture
- record missing `metrics`
- record missing `scoring`

No test should require Docker, browser automation, live accounts, scraping, posting, selling, or real Gemma if a parser unit test can cover it.

## Verdict

Tolerant parsing is what lets Money OS evolve without breaking the dashboard or weekly review. Missing data should produce honest warnings and safe next steps, not crashes or hallucinated certainty.
