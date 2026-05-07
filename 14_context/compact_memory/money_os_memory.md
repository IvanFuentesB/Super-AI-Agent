---
memory_type: compact_pointer
status: draft
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - 14_context/money_workflows/money_os_index.md
  - 14_context/money_workflows/experiment_tracker.jsonl
  - 14_context/obsidian_vault/05_Money_OS.md
generated_by: claude
reviewed_by: none
review_required_before_canonical_use: true
---

# Compact: Money OS Memory

> **WARNING:** Compressed pointer layer. No live revenue, no verified proof, no private account data.
> All money workflow files are artifact/template only through N+3.32.
> **Max target size:** 500–900 words

---

## Numbers-Game Principle

Ethical effort-multiplied workflows: many small bets, honest tracking, validate before scaling.
No fake proof, testimonials, engagement. No scraping, mass posting.
Operator review + approval required before any distribution action.

## Implemented Scripts (through N+3.34)

| Script | Milestone | Purpose |
|--------|-----------|---------|
| `03_scripts/money_workflow_new_experiment.py` | N+3.17 | JSONL experiment append + 10-dim scoring |
| `03_scripts/weekly_money_review.py` | N+3.29 | Weekly review artifacts from JSONL + logs |
| `03_scripts/manual_decision_queue_new_item.py` | N+3.31 | Draft queue entry from review candidates |

## Money Workflow Data Files

| File | Purpose |
|------|---------|
| `14_context/money_workflows/money_os_index.md` | Index |
| `14_context/money_workflows/experiment_tracker.jsonl` | Experiment tracking |
| `14_context/money_workflows/experiment_tracker.schema.json` | Schema |
| `14_context/money_workflows/video_to_money_intake_template.md` | Video intake |
| `14_context/money_workflows/manual_decision_queue.jsonl` | Decision queue |
| `14_context/money_workflows/manual_decision_queue.schema.json` | Queue schema |

## Dashboard Routes (read-only)

- `GET /api/ghoti/money/weekly-review/latest` — latest review artifacts (N+3.30)
- `GET /api/ghoti/money/queue/items` — manual decision queue read view (N+3.32)

## Log Artifacts (NOT canonical memory)

- `05_logs/money_reviews/<run_id>/` — weekly review artifacts
- `05_logs/money_runs/<run_id>/` — video-to-money artifacts
- `05_logs/operator_work_sessions/<run_id>/` — operator session artifacts

## No-Live-Action Rules

- All scripts: local-only, no external API, no model output execution
- All decisions: `approval_required: true`
- Forbidden: `post_live`, `email_send`, `scrape_contacts`
- No auto-approve, auto-execute, auto-post, auto-pay in any script

## Experiment Status

- Experiment count: unknown — check `14_context/money_workflows/experiment_tracker.jsonl`
- Live distribution runs: 0 (all artifact-only)
- Verified revenue: none

---

## Source Pointers

- Index: `14_context/money_workflows/money_os_index.md`
- Vault note: `14_context/obsidian_vault/05_Money_OS.md`
- N+3.18: `14_context/gemma_video_to_money_runner_n3_18.md`
- N+3.29: `14_context/weekly_money_review_n3_29.md`
- N+3.31: `14_context/manual_decision_queue_intake_n3_31.md`

## Next Update Instructions

Update after Money OS implementation milestones or after manual metrics recorded.
Human or Codex review before use in money-facing prompts.
