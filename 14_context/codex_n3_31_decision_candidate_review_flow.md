# Codex N+3.31 Decision Candidate Review Flow

Status: codex_planning_only / decision_candidate_review_flow / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 6c51eae
Origin HEAD: 6c51eae
Local/origin sync: synced at audit start

## Purpose

Design the local-only flow that turns generated weekly review decision candidates into human-reviewed draft queue entries. This milestone is deliberately a review bridge, not an executor.

The source candidate file is:

```text
05_logs/money_reviews/<run_id>/decisions_recommended.jsonl
```

The future queue target is:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Generated candidates must never be auto-appended to the queue. The operator reviews, rejects, or manually copies candidates into a draft intake command.

## Repo Truth At Audit Start

- Branch: `feat/ghoti-visible-operator-stack`
- Local HEAD: `6c51eae`
- Origin HEAD: `6c51eae`
- Local/origin state: synced
- Staged files before Codex work: none
- Dirty implementation files preserved: `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`, `03_scripts/money_workflow_new_experiment.py`, `14_context/money_workflows/experiment_tracker.schema.json`, `14_context/money_workflows/sample_video_notes_n3_18.md`
- Unrelated/local dirty files intentionally excluded: `.claude/skills/`, local brain logs, CV files, `output/`, prompt scratch files, third-party `.gitkeep`, and external repo intake notes

## Future Flow

1. Weekly review generator writes draft candidates under `05_logs/money_reviews/<run_id>/decisions_recommended.jsonl`.
2. Dashboard or CLI reads candidates as local artifacts only.
3. Operator reviews each candidate.
4. Operator may reject the candidate, leave it generated-only, or copy it into a dry-run queue intake command.
5. Operator runs the dry-run command and checks the generated local queue record.
6. Operator may then run an explicit append command to add one reviewed record to `manual_decision_queue.jsonl`.
7. The queued record remains a local manual decision. It still does not authorize posting, selling, outreach, payment, uploading, scraping, or live account action.

## Candidate States

Recommended local metadata states:

- `generated`: candidate exists in `decisions_recommended.jsonl`.
- `reviewed`: operator inspected the candidate.
- `rejected`: operator decided not to queue it.
- `copied_to_draft`: operator copied candidate data into a local draft command or draft file.
- `manually_queued`: operator intentionally appended a reviewed local queue record.

These states are local metadata only. They should not be interpreted as launch approval, public action approval, or live account approval.

## State Ownership

The first implementation should not edit the generated artifact file. If status tracking is needed later, prefer one of these safer patterns:

- append a separate local review metadata JSONL file under the same run directory
- append an explicit reviewed item to `manual_decision_queue.jsonl`
- keep review state in dashboard memory only until a future persistence milestone

Do not rewrite `decisions_recommended.jsonl` in the first version. Generated model artifacts should stay immutable for auditability.

## Candidate Review Checklist

Before a candidate can be copied into a queue draft, verify:

- decision type is one of the allowed Money OS decision types
- source run exists or is clearly marked missing
- source experiment/product/build pack ID is present when relevant
- reason is specific and not just generic model advice
- suggested next action is local/manual only
- risk level is present
- approval is required for any public or money-facing step
- evidence is based on local artifacts or manually recorded metrics
- no fake proof, fake scarcity, fake engagement, or unsupported claim appears
- no live account, payment, outreach, posting, scraping, upload, or launch action is implied

## Hard Non-Automation Boundary

Generated candidates may inform local planning. They must not:

- auto-append to `manual_decision_queue.jsonl`
- become approval records
- execute next actions
- run Gemma again
- mutate trackers
- post, sell, email, upload, scrape, pay, launch, or log into accounts

## Verdict

N+3.31 should make generated weekly review candidates usable without making them dangerous. The right first bridge is human review plus explicit local draft intake, not one-click approval.
