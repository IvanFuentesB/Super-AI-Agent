# N+3.29 — Weekly Money Review Artifact Generator

Status: DELIVERED
Date: 2026-05-05
Branch: feat/ghoti-visible-operator-stack
Lane: Claude

## Summary

`03_scripts/weekly_money_review.py` implemented — stdlib only, local only, no external API, no model output execution, no live actions.

## What It Does

- Reads `14_context/money_workflows/experiment_tracker.jsonl` (tolerant JSONL parser, warns on malformed lines)
- Reads `05_logs/money_runs/*/run_summary.json` and `experiment_candidates.jsonl` from all money run dirs
- Merges tracker experiments + run candidates (dedup by experiment_id)
- Generates heuristic review artifacts under `05_logs/money_reviews/<run_id>/`

## Output Artifacts

| File | Description |
|------|-------------|
| `weekly_review.json` | Machine-readable summary with all required spec fields |
| `weekly_review.md` | Human-readable draft review |
| `decisions_recommended.jsonl` | Heuristic decision candidates, all approval_required=true |
| `source_index.json` | Source file inventory and parse counts |
| `tracker_snapshot.json` | Experiment snapshot with parse warnings |
| `request.json` | Run metadata and safety flags |

## CLI

```
python 03_scripts/weekly_money_review.py --help
python 03_scripts/weekly_money_review.py --dry-run
python 03_scripts/weekly_money_review.py --since-days 14
python 03_scripts/weekly_money_review.py --since-days 30 --output-root 05_logs/money_reviews
```

## Safety Gates

All safety flags permanently false:
- external_api_used: false
- scraping_enabled: false
- live_account_actions_enabled: false
- posting_enabled: false
- selling_enabled: false
- outreach_enabled: false
- payment_actions_enabled: false
- tracker_mutated: false
- queue_mutated: false
- model_output_executed: false
- manual_review_required: true
- approval_required_for_public_actions: true

All decisions_recommended.jsonl entries force approval_required=true, public_or_money_facing=false.

## Validation Results

- AST parse: PASS
- git diff --check: PASS (no whitespace errors)
- JSONL validation (experiment_tracker.jsonl): PASS
- --help smoke: PASS
- --dry-run smoke: PASS (5 experiments found, 0 warnings)
- --since-days 30 smoke (temp output): PASS
  - 6 artifact files written
  - weekly_review.json all required fields present
  - decisions_recommended.jsonl 5 lines, all fields present, approval_required=true, public_or_money_facing=false
  - source_index.json valid

## Windows Write Permission Note

Python/bash via Claude Code's Bash tool runs as user `Navif` and cannot write to `C:\Users\ai_sandbox\...` paths directly. Smoke was run with `--output-root` pointing to `C:\Users\Navif\AppData\Local\Temp\mrev_smoke_out` and validated there. When run by the `ai_sandbox` user session (e.g. from PowerShell), the script will write to `05_logs/money_reviews/<run_id>/` correctly.

## What This Is Not

- No Gemma/LLM inference — heuristic only in this milestone
- No dashboard read card — that is N+3.30
- No manual queue intake — that is N+3.31
- No Obsidian scaffolding — that is N+3.34

## Next Milestone

N+3.30 — Weekly Review Dashboard Reads Generated Artifacts
Connect the read-only dashboard card to `05_logs/money_reviews/<run_id>/` artifacts.
