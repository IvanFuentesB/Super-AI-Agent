# Codex N+3.29 Weekly Review Artifact Generator Spec

Status: codex_planning_only / weekly_review_artifact_generator / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 12ce9c0
Origin HEAD: 12ce9c0
Local/origin sync: synced at audit start

## Purpose

Design the future local `weekly_money_review` task that reads Money OS files and writes weekly review artifacts under `05_logs/money_reviews/<run_id>/`.

This generator should help the operator decide what to double down, iterate, pause, kill, build next, or collect more data on. It must not mutate trackers, append decisions, post, sell, send, scrape, pay, log into accounts, or execute model output.

## Future Task

Task name:

```text
weekly_money_review
```

Future command:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 25000
```

Optional local notes input:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/weekly_operator_notes.md --max-chars 25000
```

The implementation should use local Gemma/Ollama only after the operator allows the implementation milestone. Codex must not run Gemma in this planning pass.

## Input Files

Required or primary input:

- `14_context/money_workflows/experiment_tracker.jsonl`

Future optional local files:

- `14_context/money_workflows/manual_decision_queue.jsonl`
- `14_context/money_workflows/product_metrics.jsonl`
- `14_context/money_workflows/product_drafts.jsonl`
- `14_context/money_workflows/product_build_packs.jsonl`
- `14_context/money_workflows/content_shots.jsonl`
- optional local notes file passed through `--input <path>`

All inputs must resolve inside repo root. No URLs should be fetched. URLs inside local notes are text only.

## Output Directory

Future artifact root:

```text
05_logs/money_reviews/<run_id>/
```

Run ID example:

```text
mrev_20260429_153000_ab12cd
```

## Required Artifacts

The generator should write:

- `request.json`
- `tracker_snapshot.json`
- `weekly_summary.md`
- `top_experiments.md`
- `decisions_recommended.jsonl`
- `distribution_gaps.md`
- `email_list_opportunities.md`
- `next_10_shots.md`
- `risk_review.md`
- `run_summary.json`

Optional artifacts:

- `source_excerpt.md`
- `manual_notes_excerpt.md`
- `parse_warnings.json`
- `prompt.txt`
- `raw_model_response.txt`

## Artifact Responsibilities

`request.json`:

- command inputs
- task name
- model/provider
- max chars
- source files considered
- safety flags

`tracker_snapshot.json`:

- deterministic local summary before the model call
- valid record counts
- parse error counts
- status counts
- workflow counts
- score buckets
- approval-required counts
- manually recorded metrics totals

`weekly_summary.md`:

- high-level summary of the week
- honest numbers snapshot
- no invented claims

`top_experiments.md`:

- best candidates to push based on available data
- include missing data caveats

`decisions_recommended.jsonl`:

- draft decision candidates only
- never auto-appended to `manual_decision_queue.jsonl`

`distribution_gaps.md`:

- missing channels
- missing CTA
- missing content assets
- missing manual metrics

`email_list_opportunities.md`:

- lead magnet opportunities
- opt-in angles
- email-list gaps

`next_10_shots.md`:

- next product/content/distribution shots
- local/manual next actions only

`risk_review.md`:

- claims/proof risks
- platform/ToS risks
- spam/fake engagement risks
- approval gates

`run_summary.json`:

- run status
- artifacts written
- parser warnings
- model return status
- safety booleans

## Required Safety Flags

Both `request.json` and `run_summary.json` should include:

```json
{
  "external_api_used": false,
  "scraping_enabled": false,
  "live_account_actions_enabled": false,
  "posting_enabled": false,
  "selling_enabled": false,
  "outreach_enabled": false,
  "payment_actions_enabled": false,
  "tracker_mutated": false,
  "queue_mutated": false,
  "model_output_executed": false,
  "manual_review_required": true
}
```

## Required Behavior

The generator must:

- read repo-local files only
- tolerate missing future files
- tolerate malformed JSONL with warnings
- cap source text by `--max-chars`
- compute deterministic counts before model call
- ask Gemma for advice only
- write artifacts only
- never mutate trackers
- never append the manual decision queue
- never execute model output
- never post, sell, outreach, email, pay, scrape, or log into accounts
- always mark public/money-facing actions as requiring human approval

## Deterministic Pre-Model Summary

Before calling Gemma, compute:

- `experiment_count`
- `manual_decision_count`
- `manual_metrics_count`
- `product_draft_count`
- `product_build_pack_count`
- `content_shot_count`
- `parse_errors_by_file`
- `experiments_by_status`
- `experiments_by_workflow_type`
- `priority_bucket_counts`
- `approval_required_count`
- `blocked_count`
- `distribution_channel_counts`
- `manual_sales_total`
- `manual_revenue_total`
- `manual_opt_ins_total`
- `latest_records`

Gemma should receive this deterministic summary, not be asked to infer all counts from raw JSONL.

## Done Definition For Future Implementation

N+3.29 implementation is done only when:

- `weekly_money_review` task exists
- artifact directory is created under `05_logs/money_reviews/<run_id>/`
- required artifacts are written
- malformed JSONL test is handled without crash
- missing future files produce warnings, not failure
- run summary records no live actions and no tracker mutation
- state docs are updated
- only intentional files are staged
- commit and push complete

## Verdict

The weekly review artifact generator should turn local Money OS trackers into a weekly operating packet. It is a thinking assistant, not a business autopilot.
