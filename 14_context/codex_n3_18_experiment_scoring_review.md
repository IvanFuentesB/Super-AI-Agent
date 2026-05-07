# Codex N+3.18 Experiment Scoring Review

Status: codex_followup_audit_only / scoring_review / not_runtime_wired

## Expected Scoring Rubric

N+3.18 scoring should help Ghoti prioritize money experiments in a numbers-game workflow. It should rank shots by speed, pain intensity, reachable buyers, distribution leverage, proof difficulty, build complexity, legal/TOS risk, monetization clarity, content volume, and email-list potential.

Expected fields:

| Field | Direction | Meaning |
| --- | --- | --- |
| `speed_to_ship` | higher is better | How quickly the experiment can reach a public-ready draft |
| `pain_intensity` | higher is better | How urgent the buyer problem feels |
| `buyer_access` | higher is better | How reachable the target buyer is through existing channels |
| `distribution_leverage` | higher is better | How much one asset can spread across channels |
| `proof_difficulty` | lower is better | How hard it is to support claims honestly |
| `build_complexity` | lower is better | How hard the MVP is to create |
| `legal_tos_risk_score` | lower is better | Legal, platform, claims, or TOS exposure |
| `monetization_clarity` | higher is better | How obvious the path to revenue is |
| `content_volume_potential` | higher is better | How many useful content pieces the idea can generate |
| `email_list_potential` | higher is better | How naturally the idea creates opt-ins and owned audience |

## Expected Inversion Logic

The dirty helper script correctly treats these fields as lower-is-better:

- `proof_difficulty`
- `build_complexity`
- `legal_tos_risk_score`

For those fields, adjusted score should be:

```text
adjusted = 6 - raw
```

All other fields should use the raw score directly. Total score is the sum of the ten adjusted values.

Expected buckets:

- `A`: total score 40 or higher
- `B`: total score 32-39
- `C`: total score 24-31
- `D`: total score below 24

## Dirty Implementation Truth

`03_scripts/money_workflow_new_experiment.py` currently includes:

- A complete list of ten scoring keys.
- CLI flag mapping for all ten scoring fields.
- Validation that if any scoring arg is provided, all ten must be provided.
- Integer validation from 1 to 5.
- Inversion for lower-is-better fields.
- Total score and bucket calculation.
- `scoring` included in the generated record only when provided.
- Dry-run output that prints total score and bucket.

## Schema Requirements

`14_context/money_workflows/experiment_tracker.schema.json` currently includes an optional `scoring` object with:

- `raw_scores`
- `adjusted_scores`
- `total_score`
- `priority_bucket`

The schema parses as valid JSON. Claude still needs to verify a real dry-run record matches the schema shape exactly.

## Required Claude Dry-Run Command

Claude should run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "sample_video_notes_n3_18" --product-idea "AI operator prompt pack" --target-customer "solo founders and AI builders" --pain-point "They waste time rebuilding prompts from scratch" --offer "A reusable operator prompt pack with content and business prompts" --next-action "Draft the first 10 prompts and one opt-in page outline" --risk-level low --channel "short-form video" --channel "email list" --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

Expected output:

- Prints `[dry-run] Would append the following record:`.
- Outputs valid JSON.
- Includes `approval_required`.
- Includes `scoring.raw_scores`.
- Includes `scoring.adjusted_scores`.
- Includes `scoring.total_score`.
- Includes `scoring.priority_bucket`.
- Prints the dry-run scoring summary line.
- Does not append to `experiment_tracker.jsonl`.
- Does not call any external API.
- Does not post, sell, email, scrape, or use live accounts.

## Review Verdict

The dirty scoring implementation is structurally present and static validation passes. It should remain uncommitted until Claude runs the dry-run, verifies schema compatibility, documents the scoring rules, and confirms no unintended live action capability was introduced.
