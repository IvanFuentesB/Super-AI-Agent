# Codex N+3.20 Weekly Money Review Generator Spec

Status: codex_planning_only / weekly_review_spec / not_runtime_wired
Date: 2026-04-29

## Goal

Design a local-only Gemma weekly review generator that reads Ghoti's money workflow tracker and produces decision-oriented artifacts. This is an artifact generator, not an execution system.

The weekly review should help the operator answer:

- Which shots should get more effort?
- Which shots should be paused or killed?
- Where are the distribution gaps?
- Where are the email-list opportunities?
- What content batch should be drafted next?
- What are the next 10 shots/products to create?
- What risks or approval gates block public action?

## Command Proposal

Future command for Claude Code to implement after N+3.18 is stable:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 20000
```

## Inputs

Required input:

- `14_context/money_workflows/experiment_tracker.jsonl`

Optional context inputs:

- recent `05_logs/money_runs/<run_id>/run_summary.json`
- recent `05_logs/money_runs/<run_id>/product_ideas.md`
- recent `05_logs/money_runs/<run_id>/distribution_plan.md`
- recent `05_logs/local_brain_runs/<run_id>/summary.md`
- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/distribution_and_exposure_checklist.md`
- `14_context/money_workflows/content_batch_template.md`
- `14_context/money_workflows/digital_product_shot_template.md`

Current observed truth:

- `experiment_tracker.jsonl` exists and currently has 3 sample records.
- `05_logs/money_runs/` was not present during this Codex audit.
- `05_logs/local_brain_runs/` exists with local artifacts.
- N+3.18 video-to-money/scoring remains dirty and uncommitted.

## Required Behavior

The future `weekly_money_review` task must:

- Resolve input through the repo-root-only path validator.
- Accept local `.jsonl`, `.md`, `.txt`, or `.json` input only if explicitly approved by policy.
- Use local Gemma/Ollama only.
- Make no external API calls.
- Use no internet.
- Do no scraping.
- Use no live accounts.
- Perform no posting, selling, emailing, outreach, payments, app-store actions, browser actions, Docker actions, or CUA actions.
- Never execute model output.
- Never auto-commit model output.
- Tolerate malformed JSONL lines.
- Tolerate missing scoring.
- Tolerate empty metrics.
- Count total experiments/shots.
- Compute workflow, status, and score bucket summaries when available.
- Produce decision-oriented recommendations as local artifacts only.

## Proposed Output Artifacts

Output root:

```text
05_logs/money_reviews/<run_id>/
```

Required artifacts:

- `request.json`
- `tracker_excerpt.jsonl`
- `weekly_review.md`
- `top_experiments.md`
- `kill_or_pause.md`
- `distribution_gaps.md`
- `email_list_opportunities.md`
- `next_10_shots.md`
- `risk_review.md`
- `run_summary.json`

Suggested `request.json` fields:

```json
{
  "run_id": "mrev_YYYYMMDD_HHMMSS_ab12cd",
  "task_type": "weekly_money_review",
  "input_file": "14_context/money_workflows/experiment_tracker.jsonl",
  "max_chars": 20000,
  "provider": "ollama",
  "model": "gemma3:4b",
  "api_usage": "none",
  "external_calls": "none",
  "live_actions_enabled": false,
  "model_output_executed": false,
  "auto_commit_from_model": false,
  "timestamp_utc": "..."
}
```

Suggested `run_summary.json` fields:

```json
{
  "run_id": "...",
  "status": "PASS",
  "task_type": "weekly_money_review",
  "experiments_count": 3,
  "parse_errors": 0,
  "input_clipped": false,
  "artifacts": [],
  "api_usage": "none",
  "external_calls": "none",
  "model_output_executed": false,
  "auto_post": false,
  "auto_sell": false,
  "auto_email": false,
  "auto_outreach": false,
  "approval_required_for_any_public_or_money_action": true
}
```

## Pre-Model Local Summary

Before calling Gemma, the runner should compute a compact deterministic summary:

- total valid experiments.
- parse error count.
- workflow type counts.
- status counts.
- scoring bucket counts if present.
- revenue/time totals from metrics.
- distribution channel counts.
- approval required count.
- latest 10 experiments.

This summary should be included in the prompt so Gemma does not need to infer basic counts from raw JSONL.

## Validation Plan

Static validation:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
git diff --check
```

Dry-run/smoke validation after implementation:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 20000
```

Verify:

- output folder exists under `05_logs/money_reviews/`.
- all required artifacts exist.
- `run_summary.json` records no live action capability.
- malformed JSONL is counted, not fatal.
- missing scoring does not fail.
- no tracker mutation occurs.

## Done Definition

N+3.20 is complete only when Claude Code implements the local artifact generator, runs the smoke, validates artifacts, updates state docs, stages only intentional files, commits, and pushes.
