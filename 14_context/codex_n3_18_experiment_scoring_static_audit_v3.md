# Codex N+3.18 Experiment Scoring Static Audit v3

Status: codex_static_audit_only / scoring_review / dirty_implementation_not_staged

## Scoring Dimensions

The dirty `03_scripts/money_workflow_new_experiment.py` implementation adds exactly ten scoring dimensions:

| Dimension | Direction | Purpose |
| --- | --- | --- |
| `speed_to_ship` | higher is better | Prioritizes shots that can be tested quickly |
| `pain_intensity` | higher is better | Prioritizes urgent buyer pain |
| `buyer_access` | higher is better | Prioritizes reachable buyers |
| `distribution_leverage` | higher is better | Prioritizes ideas with multiple exposure lanes |
| `proof_difficulty` | lower is better | Penalizes hard-to-prove claims |
| `build_complexity` | lower is better | Penalizes difficult MVPs |
| `legal_tos_risk_score` | lower is better | Penalizes legal, claims, and platform risk |
| `monetization_clarity` | higher is better | Prioritizes clear revenue path |
| `content_volume_potential` | higher is better | Prioritizes repeatable content production |
| `email_list_potential` | higher is better | Prioritizes owned-audience capture |

## Validation Logic

Static inspection shows:

- If no scoring args are provided, no `scoring` object is added.
- If any scoring arg is provided, all ten scoring args are required.
- Each scoring value is converted to an integer.
- Values outside 1-5 are rejected.
- The script remains local-only and says it does not post, sell, email, scrape, or call external APIs.

## Inversion Logic

Lower-is-better fields:

- `proof_difficulty`
- `build_complexity`
- `legal_tos_risk_score`

The dirty implementation inverts lower-is-better fields with:

```text
adjusted = 6 - raw
```

Higher-is-better fields use the raw value.

## Bucket Logic

Static inspection shows:

- `total_score` is the sum of all adjusted scores.
- `A` bucket is `total_score >= 40`.
- `B` bucket is `total_score >= 32`.
- `C` bucket is `total_score >= 24`.
- `D` bucket is anything below 24.

This matches the N+3.18 target.

## Schema Compatibility Risks

`14_context/money_workflows/experiment_tracker.schema.json` adds an optional `scoring` object with:

- `raw_scores`
- `adjusted_scores`
- `total_score`
- `priority_bucket`

The schema parses as JSON. Remaining risk: Claude still needs to run a dry-run command and compare the emitted record shape to the schema. Static inspection suggests the shape should match, but this is not proven until the helper emits a real record.

## Required Claude Dry-Run

Claude should run this dry-run before committing implementation:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "sample_video_notes_n3_18" --product-idea "AI operator prompt pack" --target-customer "solo founders and AI builders" --pain-point "They waste time rebuilding prompts from scratch" --offer "A reusable operator prompt pack with content and business prompts" --next-action "Draft the first 10 prompts and one opt-in page outline" --risk-level low --channel "short-form video" --channel "email list" --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

Expected dry-run result:

- Prints a JSON record.
- Does not append to `experiment_tracker.jsonl`.
- Includes `scoring.raw_scores`.
- Includes `scoring.adjusted_scores`.
- Includes `scoring.total_score`.
- Includes `scoring.priority_bucket`.
- Prints a dry-run scoring summary line.
- Does not call external APIs.
- Does not post, sell, email, scrape, or use live accounts.

## Review Verdict

The dirty scoring implementation is directionally complete from static inspection, but it is still unproven. Claude must run the dry-run, verify schema compatibility, and document the scoring system before staging the helper script or schema.
