# Codex N+3.22 Product Scoring Model

Status: codex_planning_only / product_scoring_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The product scoring model should help Ghoti rank digital product shots before building or publishing anything. It should reward fast, useful, reachable, easy-to-distribute offers and penalize proof burden, build complexity, legal/TOS risk, and fulfillment load.

## Scoring Dimensions

Use 1 to 5 scores.

Higher is better:

- `speed_to_ship`
- `buyer_pain`
- `buyer_access`
- `distribution_fit`
- `email_list_fit`
- `content_volume_fit`
- `monetization_clarity`

Lower is better but should be inverted in total score:

- `proof_required`
- `build_complexity`
- `legal_tos_risk`
- `fulfillment_burden`

## Dimension Rubric

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| `speed_to_ship` | More than 2 weeks. | 3 to 7 days. | 1 day or less. |
| `buyer_pain` | Mild annoyance. | Clear recurring pain. | Urgent, expensive, or emotionally strong pain. |
| `buyer_access` | Hard to reach buyer. | Some reachable channels. | Buyer is already reachable through content/community/email. |
| `distribution_fit` | No obvious channel. | One to two channels. | Three or more clear channels. |
| `email_list_fit` | No lead magnet angle. | Possible opt-in. | Strong free sample or checklist angle. |
| `content_volume_fit` | Few content angles. | 10 to 20 angles. | 30+ obvious content shots. |
| `monetization_clarity` | Unclear why anyone pays. | Plausible purchase reason. | Clear buyer, pain, deliverable, and price. |
| `proof_required` | Needs major proof, testimonials, or results. | Needs examples and screenshots. | Can be useful with a sample/template. |
| `build_complexity` | Requires complex app or integrations. | Requires polished bundle. | Markdown/PDF/template can ship. |
| `legal_tos_risk` | Regulated, platform-sensitive, or risky claims. | Manageable with disclaimers. | Low-risk educational/template product. |
| `fulfillment_burden` | Requires ongoing manual service. | Some updates/support. | Mostly self-serve product. |

## Total Score

Invert lower-is-better dimensions:

```text
inverted_proof_required = 6 - proof_required
inverted_build_complexity = 6 - build_complexity
inverted_legal_tos_risk = 6 - legal_tos_risk
inverted_fulfillment_burden = 6 - fulfillment_burden

total_score =
  speed_to_ship
  + buyer_pain
  + buyer_access
  + distribution_fit
  + email_list_fit
  + content_volume_fit
  + monetization_clarity
  + inverted_proof_required
  + inverted_build_complexity
  + inverted_legal_tos_risk
  + inverted_fulfillment_burden
```

Maximum score is 55.

## Priority Buckets

Suggested buckets:

- `A`: 44 to 55, strong candidate
- `B`: 35 to 43, worth testing with content
- `C`: 26 to 34, needs research or repositioning
- `D`: 25 or below, pause or kill

## Recommended Action

| Condition | Action |
| --- | --- |
| A bucket, low legal risk, low build complexity | `BUILD_NOW` |
| A or B bucket, strong content fit, weak proof | `TEST_WITH_CONTENT` |
| B or C bucket, unclear buyer or price | `NEEDS_RESEARCH` |
| C bucket with high complexity | `PAUSE` |
| D bucket or high legal/TOS risk | `KILL` |

## Example

```json
{
  "product_id": "prod_ai_operator_starter_kit",
  "speed_to_ship": 5,
  "buyer_pain": 4,
  "buyer_access": 3,
  "distribution_fit": 4,
  "email_list_fit": 5,
  "content_volume_fit": 5,
  "monetization_clarity": 4,
  "proof_required": 2,
  "build_complexity": 2,
  "legal_tos_risk": 1,
  "fulfillment_burden": 2,
  "total_score": 47,
  "priority_bucket": "A",
  "recommended_action": "BUILD_NOW"
}
```

## Connection To Trackers

The product score should connect to:

- `experiment_tracker.jsonl` through `experiment_id`
- future `content_shots.jsonl` through content validation data
- future `product_drafts.jsonl` through `product_id`

Recommended fields in `product_drafts.jsonl`:

- `product_id`
- `source_experiment_id`
- `source_content_shot_ids`
- `product_name`
- `buyer`
- `pain`
- `offer`
- `score`
- `priority_bucket`
- `recommended_action`
- `artifact_dir`
- `approval_required`
- `status`

## Safety Notes

Scores are decision support, not permission to publish. Any product with public claims, pricing, platform upload, payment setup, or account action still needs explicit human approval.

## Verdict

Use this product scoring model to decide which product drafts deserve more effort. It keeps the numbers-game system practical by ranking shots before the user spends time polishing or listing them.
