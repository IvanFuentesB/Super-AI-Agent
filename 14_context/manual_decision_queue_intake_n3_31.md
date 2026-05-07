# N+3.31 -- Manual Decision Queue Intake

Status: delivered / local_only / draft_intake_only / not_approved / no_live_actions

Date: 2026-05-05
Branch: feat/ghoti-visible-operator-stack
Lane: Claude
Starting HEAD: 81b8a7e

## Purpose

Implements the local helper that converts a reviewed weekly review decision candidate
into an append-only draft queue entry in `14_context/money_workflows/manual_decision_queue.jsonl`.

This is a read-and-draft bridge only. It does not approve, execute, post, sell, email,
scrape, call external APIs, or touch live accounts.

## Files Created

- `03_scripts/manual_decision_queue_new_item.py` -- main helper script
- `14_context/money_workflows/manual_decision_queue.schema.json` -- queue entry schema
- `14_context/manual_decision_queue_intake_n3_31.md` -- this doc

## Script Summary

`03_scripts/manual_decision_queue_new_item.py`

- stdlib only, no external dependencies
- reads `decisions_recommended.jsonl` from the latest run under `05_logs/money_reviews/`
- selects a candidate by `--candidate-id`, `--index`, or first candidate by default
- builds a draft queue entry with all safety flags set to false/true
- validates decision_type, risk_level, next_action (rejects forbidden live-action phrases)
- rejects non-local file paths in the files list
- dry-run mode prints the entry without writing (default when neither flag given)
- `--append` mode appends exactly one JSONL line to the queue file
- validates queue JSONL before and after append
- never marks anything approved
- never executes model output
- never posts, sells, emails, scrapes, or touches live accounts

## CLI

```powershell
# Help
python 03_scripts/manual_decision_queue_new_item.py --help

# Dry-run latest candidate from latest run
python 03_scripts/manual_decision_queue_new_item.py --latest --dry-run

# Dry-run by index
python 03_scripts/manual_decision_queue_new_item.py --latest --index 1 --dry-run

# Dry-run by candidate ID
python 03_scripts/manual_decision_queue_new_item.py --latest --candidate-id cand_mrev_sample_001 --dry-run

# Append to queue
python 03_scripts/manual_decision_queue_new_item.py --latest --index 1 --append

# Custom paths (for testing without real artifacts)
python 03_scripts/manual_decision_queue_new_item.py --reviews-root C:\tmp\reviews --queue-path C:\tmp\queue.jsonl --dry-run
```

## Queue Entry Format

Each appended record contains:

| Field | Type | Notes |
|-------|------|-------|
| queue_item_id | string | qdec_<timestamp>_<hash> |
| created_at | ISO-8601 | UTC |
| source_type | string | always "weekly_review_candidate" |
| source_review_run_id | string | run directory name |
| source_decision_id | string | from source candidate |
| source_file | string | repo-relative path |
| title | string | from candidate |
| decision_type | string | one of ALLOWED_DECISION_TYPES |
| recommendation | string | from candidate |
| reason / rationale | string | from candidate |
| risk_level | string | low / medium / high |
| next_manual_action | string | local step only |
| approval_required | bool | always true |
| status | string | always "draft" at intake |
| public_action_allowed | bool | always false |
| live_account_action_allowed | bool | always false |
| external_action_allowed | bool | always false |
| model_output_executed | bool | always false |
| artifact_only | bool | always true |
| no_live_action_taken | bool | always true |
| safety_flags | object | all false / manual_review_required=true |
| metrics_snapshot | object | zeros at intake |
| files | list | repo-relative only |

## Validation

- `python -m py_compile 03_scripts/manual_decision_queue_new_item.py` -- PASS
- AST parse: PASS
- `--help` smoke: PASS
- `--latest --dry-run` smoke: PASS (no review artifacts staged; handled gracefully)
- `git diff --check`: PASS

## Safety Truth

- no external API calls
- no scraping
- no posting, selling, outreach, payment, login
- no model output executed
- no live accounts touched
- approval_required=true enforced on every entry
- status="draft" enforced at intake
- public/live/external action flags locked to false
- forbidden action phrases rejected at validation time

## Non-Goals (N+3.31)

- NO dashboard read view for queue (that is N+3.32)
- NO Obsidian scaffolding (that is N+3.34)
- NO approval execution
- NO external tool connections

## Next Milestone

N+3.32 -- Manual Decision Queue Read View And Operator Work Session Planner
