# Ghoti Money OS (Compact)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/money_workflows/money_os_index.md`, N+3.18–N+3.32 milestone docs

---

## Purpose

High-level memory for the ethical money workflow system (through N+3.32).
No live revenue, no unverified proof, no private account data, no live-action instructions.

## Source of Truth

- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/experiment_tracker.jsonl`
- N+3.18 through N+3.32 milestone docs in `14_context/`
- `05_logs/money_reviews/` — generated review artifacts (NOT canonical memory)

## Update Rules

- Update after Money OS implementation milestones.
- After manual metrics are recorded by operator.
- Do not invent revenue, sales, proof, or results.
- Mark unknowns as unknown.

---

## Numbers-Game Principle

Ethical effort-multiplied workflows:
- Many small bets → track results honestly → validate before scaling
- No fake proof, testimonials, or engagement
- No live scraping, mass posting, fake account farming
- Operator review required before any public/money-facing action

## Current Money Workflow Files

| File | Purpose |
|------|---------|
| `14_context/money_workflows/money_os_index.md` | Index of all money workflow docs |
| `14_context/money_workflows/experiment_tracker.jsonl` | Experiment tracking JSONL |
| `14_context/money_workflows/experiment_tracker.schema.json` | Schema |
| `14_context/money_workflows/video_to_money_intake_template.md` | Video intake template |
| `14_context/money_workflows/digital_product_shot_template.md` | Product shot template |
| `14_context/money_workflows/content_batch_template.md` | Content batch template |
| `14_context/money_workflows/manual_decision_queue.jsonl` | Manual decision queue |
| `14_context/money_workflows/manual_decision_queue.schema.json` | Queue schema |

## Implemented Scripts

| Script | Milestone | Status |
|--------|-----------|--------|
| `03_scripts/money_workflow_new_experiment.py` | N+3.17 | smoke_pass |
| `03_scripts/weekly_money_review.py` | N+3.29 | smoke_pass |
| `03_scripts/manual_decision_queue_new_item.py` | N+3.31 | smoke_pass |

## Dashboard Routes (read-only)

- `GET /api/ghoti/money/weekly-review/latest` — latest review artifacts (N+3.30)
- `GET /api/ghoti/money/queue/items` — manual decision queue read view (N+3.32)

## Manual Approval Rules

- All decisions in `manual_decision_queue.jsonl` require `approval_required: true`
- No script auto-approves, auto-executes, auto-posts, or auto-pays
- Operator must review and explicitly approve before any distribution action
- Forbidden decision types: `post_live`, `email_send`, `scrape_contacts`
- All money workflow artifacts are local only unless operator explicitly pushes

## Log Artifacts (NOT canonical memory)

- `05_logs/money_reviews/<run_id>/` — weekly review run artifacts
- `05_logs/money_runs/<run_id>/` — video-to-money run artifacts
- `05_logs/operator_work_sessions/<run_id>/` — operator work session artifacts

## Experiment Status

- Experiments tracked in `14_context/money_workflows/experiment_tracker.jsonl`
- Current count: unknown (check JSONL directly)
- Verified revenue: none
- All runs artifact-only; no live distribution

---

## Review Status

**status:** draft
**review_required:** yes — before any money-facing use, verify against source JSONL and milestone docs
**unknown:** exact experiment count, video-to-money run count, operator session run count

## Related Files

- `14_context/money_workflows/money_os_index.md`
- `14_context/obsidian_vault/06_Safety_Gates.md`
- `14_context/compact_memory/money_os_memory.md`
