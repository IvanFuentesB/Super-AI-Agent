# Codex N+3.27 Weekly Review Generator Spec

Status: codex_planning_only / weekly_money_review_generator / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design the future local Gemma task that turns Money OS tracker files into weekly review artifacts and manual decision queue candidates. This extends the N+3.20 weekly review plan with product drafts, product build packs, manual launch metrics, content shots, and decision queue candidates.

## Future Task

Task name:

```text
weekly_money_review
```

Future command:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 25000
```

The command should use local Gemma/Ollama only after Claude confirms the router is stable. It must remain artifact-only.

## Inputs

Primary inputs:

- `14_context/money_workflows/experiment_tracker.jsonl`
- future `14_context/money_workflows/product_drafts.jsonl`
- future `14_context/money_workflows/product_build_packs.jsonl`
- future `14_context/money_workflows/product_metrics.jsonl`
- future `14_context/money_workflows/content_shots.jsonl`
- optional `14_context/money_workflows/manual_decision_queue.jsonl`
- optional manual notes markdown

Optional artifact inputs:

- `05_logs/money_runs/<run_id>/run_summary.json`
- `05_logs/product_drafts/<run_id>/run_summary.json`
- `05_logs/product_build_packs/<run_id>/run_summary.json`
- `05_logs/content_batches/<run_id>/run_summary.json`
- `05_logs/money_reviews/<previous_run_id>/run_summary.json`

## Output Directory

```text
05_logs/money_reviews/<run_id>/
```

Required artifacts:

- `request.json`
- `source_snapshot.md`
- `weekly_summary.md`
- `double_down.md`
- `iterate.md`
- `pause_or_kill.md`
- `next_10_shots.md`
- `distribution_gaps.md`
- `email_list_opportunities.md`
- `manual_decision_queue_candidates.jsonl`
- `risk_review.md`
- `run_summary.json`

## No-Auto-Append Rule

`manual_decision_queue_candidates.jsonl` is a draft artifact only.

The weekly review generator must not append to:

- `manual_decision_queue.jsonl`
- `experiment_tracker.jsonl`
- `product_drafts.jsonl`
- `product_build_packs.jsonl`
- `product_metrics.jsonl`
- `content_shots.jsonl`

The operator or a future explicitly approved local CLI should review candidates before any append happens.

## Prompt Structure

The future Gemma prompt should force these sections:

```text
You are Ghoti's local weekly Money OS reviewer.

Use only the local source snapshot below. Do not invent metrics, revenue, proof, customers, testimonials, or platform results. Treat missing data as missing.

Goal:
- help the operator create more ethical shots
- increase exposure
- build email-list assets
- find bottlenecks
- decide what to double down, iterate, pause, kill, or build next

Hard rules:
- no posting
- no selling
- no outreach
- no payments
- no live accounts
- no scraping
- no fake proof
- no fake scarcity
- no spam
- no misleading claims
- all public or money-facing actions require human approval

Required output sections:
1. WEEKLY SUMMARY
2. NUMBERS SNAPSHOT
3. DOUBLE DOWN
4. ITERATE
5. PAUSE OR KILL
6. DISTRIBUTION GAPS
7. EMAIL LIST OPPORTUNITIES
8. NEXT 10 SHOTS
9. MANUAL DECISION QUEUE CANDIDATES
10. RISKS / APPROVAL GATES
11. NEXT ACTIONS FOR OPERATOR

Source snapshot:
<SOURCE_SNAPSHOT>
```

## Candidate Decision JSONL Shape

Each candidate line in `manual_decision_queue_candidates.jsonl` should follow the model from `codex_n3_27_manual_decision_queue_model.md`, with:

- `status: "candidate"`
- `public_action_allowed: false`
- `live_account_action_allowed: false`
- `external_action_allowed: false`

## Deterministic Pre-Summary

Before calling Gemma, the future implementation should compute a deterministic local summary:

- source file existence
- valid line counts
- parse error counts
- total experiments
- total product drafts
- total build packs
- total manual metric records
- weekly created counts
- status counts
- priority bucket counts
- approval required count
- distribution channel counts
- total manually recorded opt-ins
- total manually recorded sales
- total manually recorded revenue

Gemma should review this pre-summary rather than guessing counts from raw JSONL.

## Run Summary Fields

`run_summary.json` should include:

- `run_id`
- `created_at_utc`
- `task`
- `input_files`
- `artifact_dir`
- `artifact_files`
- `valid_record_counts`
- `parse_error_counts`
- `weekly_counts`
- `decision_candidate_count`
- `external_api_used: false`
- `live_actions_taken: false`
- `model_output_executed: false`
- `tracker_mutated: false`
- `manual_review_required: true`

## Safety Rules

Allowed:

- read repo-local files
- summarize local trackers
- create markdown artifacts
- create candidate JSONL artifacts
- classify local risk
- suggest local next steps

Not allowed:

- fetch URLs
- scrape platforms
- post content
- send email
- perform outreach
- publish listings
- upload files to marketplaces
- set prices
- process payments
- use live accounts
- append to trackers without explicit future approval
- execute model output

## Validation Plan

Future Claude validation:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 25000
python -c "import json, pathlib; p=pathlib.Path('05_logs/money_reviews'); print('money review dirs', len(list(p.glob('*'))) if p.exists() else 0)"
git diff --check
```

## Verdict

The weekly review generator should create the thinking artifacts for the operator, not execute decisions. It is the bridge between raw shots and deliberate weekly action.
