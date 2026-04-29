# Codex N+3.30 Weekly Review Artifact Summary Route Spec

Status: codex_planning_only / weekly_review_artifact_summary_route / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: e4c7f50
Origin HEAD: e4c7f50
Local/origin sync: synced at audit start

## Purpose

Design a future read-only backend route that summarizes generated weekly Money OS review artifacts under `05_logs/money_reviews/<run_id>/`.

This route should read generated files only. It must not run the weekly review generator, call Gemma, execute model output, append decisions, mutate trackers, post, sell, outreach, pay, scrape, or use live accounts.

## Future Route

```text
GET /api/ghoti/money/weekly-review/artifacts/summary
```

## Source Directory

Primary root:

```text
05_logs/money_reviews/
```

Expected run directory shape:

```text
05_logs/money_reviews/<run_id>/
```

Expected files from N+3.29:

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

Optional files:

- `source_excerpt.md`
- `manual_notes_excerpt.md`
- `parse_warnings.json`
- `prompt.txt`
- `raw_model_response.txt`

## Route Behavior

The route should:

- resolve `05_logs/money_reviews/` under repo root
- tolerate missing directory
- list run directories only
- ignore files directly under the root
- sort latest runs by timestamp-like name first, then filesystem mtime fallback
- cap returned runs, for example latest 10
- read `run_summary.json` if present
- read `weekly_summary.md` if present
- read `decisions_recommended.jsonl` if present
- read `next_10_shots.md` if present
- read `risk_review.md` if present
- tolerate malformed JSON and JSONL
- return zero-state safely
- never mutate files
- never execute model output
- never trigger live actions

## Response Shape

The response should include:

- `status`
- `ok`
- `read_only`
- `generated_at`
- `runs_total`
- `runs_returned`
- `latest_run`
- `latest_summary_excerpt`
- `decision_candidate_counts`
- `top_decision_candidates`
- `next_10_shots_excerpt`
- `risk_flags`
- `warnings`
- `source_files`
- `safety`

## Example Zero-State Response

```json
{
  "status": "zero_state",
  "ok": true,
  "read_only": true,
  "generated_at": "2026-04-29T00:00:00Z",
  "runs_total": 0,
  "runs_returned": 0,
  "latest_run": null,
  "latest_summary_excerpt": "",
  "decision_candidate_counts": {},
  "top_decision_candidates": [],
  "next_10_shots_excerpt": "",
  "risk_flags": [],
  "warnings": ["05_logs/money_reviews/ missing; no weekly review artifacts generated yet"],
  "source_files": {
    "money_reviews_root": {
      "path": "05_logs/money_reviews",
      "exists": false
    }
  },
  "safety": {
    "mutation_enabled": false,
    "model_execution_enabled": false,
    "external_api_used": false,
    "scraping_enabled": false,
    "posting_enabled": false,
    "selling_enabled": false,
    "outreach_enabled": false,
    "payment_actions_enabled": false,
    "live_account_actions_enabled": false
  }
}
```

## Example Populated Response

```json
{
  "status": "ok",
  "ok": true,
  "read_only": true,
  "generated_at": "2026-04-29T00:00:00Z",
  "runs_total": 2,
  "runs_returned": 2,
  "latest_run": {
    "run_id": "mrev_20260429_153000_ab12cd",
    "path": "05_logs/money_reviews/mrev_20260429_153000_ab12cd",
    "created_at_utc": "2026-04-29T15:30:00Z",
    "status": "PASS",
    "artifact_files": [
      "weekly_summary.md",
      "decisions_recommended.jsonl",
      "next_10_shots.md",
      "risk_review.md",
      "run_summary.json"
    ],
    "tracker_mutated": false,
    "queue_mutated": false,
    "live_actions_taken": false
  },
  "latest_summary_excerpt": "Weekly review excerpt...",
  "decision_candidate_counts": {
    "DOUBLE_DOWN": 1,
    "CREATE_CONTENT_BATCH": 2,
    "COLLECT_MORE_DATA": 1
  },
  "top_decision_candidates": [
    {
      "decision_id": "cand_mrev_20260429_001",
      "decision_type": "CREATE_CONTENT_BATCH",
      "confidence": "medium",
      "experiment_id": "exp_20260428_120002_dig002",
      "suggested_next_action": "Draft a local content batch for operator review.",
      "approval_required": true,
      "risk_level": "low"
    }
  ],
  "next_10_shots_excerpt": "1. Draft a content batch...",
  "risk_flags": [
    "Approval required before public posting",
    "No real market metrics yet"
  ],
  "warnings": [],
  "source_files": {
    "latest_run_summary": "05_logs/money_reviews/mrev_20260429_153000_ab12cd/run_summary.json",
    "latest_weekly_summary": "05_logs/money_reviews/mrev_20260429_153000_ab12cd/weekly_summary.md",
    "latest_decisions": "05_logs/money_reviews/mrev_20260429_153000_ab12cd/decisions_recommended.jsonl"
  },
  "safety": {
    "mutation_enabled": false,
    "model_execution_enabled": false,
    "external_api_used": false,
    "scraping_enabled": false,
    "posting_enabled": false,
    "selling_enabled": false,
    "outreach_enabled": false,
    "payment_actions_enabled": false,
    "live_account_actions_enabled": false
  }
}
```

## Excerpt Limits

Recommended limits:

- `weekly_summary.md`: first 1200 characters
- `next_10_shots.md`: first 1200 characters
- `risk_review.md`: first 1200 characters or extracted risk bullets
- `decisions_recommended.jsonl`: parse up to first 100 valid candidates, return top 3 to UI

Do not return full raw model response by default.

## Source File Rules

All returned paths should be repo-relative strings. The route should not provide arbitrary file serving.

If an existing artifact preview system is reused later, `05_logs/money_reviews/` must be deliberately added to allowed read-only roots with careful extension filtering. Do not add broad `05_logs/` access without review.

## Validation Plan

Future Claude validation:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
git diff --check
```

Optional route smoke only when dashboard server is intentionally running:

```powershell
Invoke-RestMethod http://localhost:3210/api/ghoti/money/weekly-review/artifacts/summary
```

## Verdict

The route should make generated weekly review packets visible without converting them into actions.
