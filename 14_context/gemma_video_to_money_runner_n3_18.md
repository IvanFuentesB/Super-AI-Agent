# Gemma Video-to-Money Runner — N+3.18

Status: implemented / artifact_only / no_external_api / approval_required_for_any_use

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.18

## What This Is

A local-only Gemma/Ollama task path in `local_brain_router.py` that:

- Accepts a `.md` or `.txt` file of local video notes or transcript notes
- Sends the content to the local Gemma model via `ollama run`
- Writes structured draft artifacts to `05_logs/money_runs/<run_id>/`
- Never posts, sells, emails, scrapes, or touches live accounts
- Never executes model output
- Marks all outputs as drafts requiring human approval before any use

## Entry Point

```bash
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py \
  --task video_to_money \
  --input 14_context/money_workflows/sample_video_notes_n3_18.md \
  --max-chars 12000
```

## Artifacts Written Per Run

Under `05_logs/money_runs/<run_id>/`:

| File | Contents |
|------|---------|
| `request.json` | Input metadata + all safety flags |
| `source_excerpt.md` | Input text (clipped at max_chars) |
| `source_summary.md` | Model-extracted summary bullets |
| `product_ideas.md` | Draft product idea list |
| `content_angles.md` | Draft content angle list |
| `experiment_candidates.jsonl` | Parsed experiment candidate records |
| `distribution_plan.md` | Draft distribution channel plan |
| `risk_review.md` | Model risk labels per category |
| `run_summary.json` | Run outcome + all safety flags |

## Safety Flags in Every Run

All runs record in `request.json` and `run_summary.json`:

```json
{
  "api_usage": "none",
  "external_calls": "none",
  "model_output_executed": false,
  "auto_post": false,
  "auto_sell": false,
  "auto_email": false,
  "auto_commit_from_model": false,
  "approval_required_for_any_use": true
}
```

## Input Constraints

- Must be `.md` or `.txt` (other extensions are rejected at path check)
- Must be inside the repo root (path resolver blocks traversal)
- Clipped at `--max-chars` (default 12000) to bound token usage

## Graceful Failure

If Ollama is unavailable or the model is missing:
- Run exits nonzero
- `run_summary.json` is written with `status=FAIL` and error reason
- No partial artifacts remain without a `run_summary.json`

## Parser Notes

The `_candidates_to_jsonl` parser:
- Splits candidates on repeated anchor keys (`workflow_type`, `product_idea`, `name`) when the model omits blank separators
- Forces `approval_required` to boolean `True` regardless of any model-emitted value
- Writes `_parse_warnings` into candidate records when anchor-key splitting occurred

## Sample Input

`14_context/money_workflows/sample_video_notes_n3_18.md` — fictional local test notes; not scraped from YouTube; not real business advice.

## What This Is Not

- Not a revenue generator
- Not a product launcher
- Not a live account operator
- Not an autonomous decision maker
- All outputs are planning drafts only; none are results, proof, or testimonials
