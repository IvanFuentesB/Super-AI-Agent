# Money Experiment Scoring — N+3.18

Status: implemented / local_heuristic_only / scores_are_planning_estimates_not_proof

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.18

## What This Is

An optional scoring extension to `03_scripts/money_workflow_new_experiment.py` that:

- Accepts 10 integer scores (1-5 each) when recording a new experiment
- Inverts lower-is-better dimensions
- Sums adjusted scores into a priority bucket (A/B/C/D)
- Stores the scoring object inside the experiment record in `experiment_tracker.jsonl`

## Scoring Dimensions

| Dimension | Direction | CLI Flag |
|-----------|-----------|---------|
| speed_to_ship | higher=better | `--speed-to-ship` |
| pain_intensity | higher=better | `--pain-intensity` |
| buyer_access | higher=better | `--buyer-access` |
| distribution_leverage | higher=better | `--distribution-leverage` |
| proof_difficulty | lower=better (inverted) | `--proof-difficulty` |
| build_complexity | lower=better (inverted) | `--build-complexity` |
| legal_tos_risk_score | lower=better (inverted) | `--legal-tos-risk` |
| monetization_clarity | higher=better | `--monetization-clarity` |
| content_volume_potential | higher=better | `--content-volume-potential` |
| email_list_potential | higher=better | `--email-list-potential` |

Inversion formula: `adjusted = 6 - raw` for lower-is-better fields.

## Priority Buckets

| Bucket | Adjusted Total |
|--------|---------------|
| A | 40+ |
| B | 32–39 |
| C | 24–31 |
| D | <24 |

Maximum possible adjusted total: 50 (all 5s after inversion).

## All-or-Nothing Rule

Scoring is optional. If any scoring flag is provided, all 10 must be provided. Partial scoring exits with an error.

## Important Caveat

**Scores are planning heuristics only.** They are entered by the operator based on personal judgement with no market data, no validation results, no sales proof, and no testimonials behind them. A bucket-A score does not mean the idea is validated or that revenue will follow.

## Example Usage

```bash
python 03_scripts/money_workflow_new_experiment.py \
  --dry-run \
  --workflow-type digital_product \
  --source "local notes" \
  --product-idea "AI operator prompt pack" \
  --target-customer "solo AI builders" \
  --pain-point "wasting time rebuilding prompts daily" \
  --offer "30 operator-level AI prompt templates" \
  --next-action "draft outline locally" \
  --risk-level low \
  --channel manual_review_first \
  --speed-to-ship 5 --pain-intensity 4 --buyer-access 3 \
  --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 \
  --legal-tos-risk 2 --monetization-clarity 4 \
  --content-volume-potential 5 --email-list-potential 4
```

Expected dry-run output includes `total_score=41  priority_bucket=A`.

## Schema Alignment

The `scoring` object in `experiment_tracker.schema.json` requires all 10 fields in both `raw_scores` and `adjusted_scores`, matching the all-or-nothing script-level enforcement.
