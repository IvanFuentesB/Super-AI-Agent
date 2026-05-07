# Codex N+3.20 Money Review Scoring Model

Status: codex_planning_only / scoring_model_spec / not_runtime_wired
Date: 2026-04-29

## Purpose

The weekly review needs a practical scoring model that helps choose what to do next without pretending to know more than the data supports.

This scoring model is for weekly review recommendations. It should not replace the N+3.18 experiment scoring fields; it can use them when available.

## Scoring Dimensions

Each dimension should be scored from 1 to 5 when enough information exists.

| Dimension | Higher Means | Evidence Source |
| --- | --- | --- |
| velocity_score | Easy to move this week | status, next_action, time spent, asset readiness |
| distribution_score | Has clear exposure channels | `distribution_channels`, content assets, notes |
| monetization_clarity_score | Clear path to money | offer, price_test, product type |
| audience_pain_score | Clear painful problem | pain_point, target_customer |
| content_leverage_score | Can produce many content pieces | content assets, topic breadth |
| email_list_fit_score | Strong lead magnet or opt-in angle | notes, offer, distribution plan |
| execution_simplicity_score | Low complexity to draft/test | workflow type, next action, risk |
| risk_penalty | Legal/TOS/claims/platform risk | risk_level, approval_required, notes |

## Priority Formula

Suggested weekly priority score:

```text
total_priority_score =
  velocity_score
  + distribution_score
  + monetization_clarity_score
  + audience_pain_score
  + content_leverage_score
  + email_list_fit_score
  + execution_simplicity_score
  - risk_penalty
```

Score range:

- minimum practical score: 2
- maximum practical score: 34

This is a triage score, not a financial prediction.

## Action Buckets

| Bucket | Condition | Meaning |
| --- | --- | --- |
| `DOUBLE_DOWN` | high score and low/medium risk with clear next action | Push this harder this week |
| `ITERATE` | medium score or unclear offer/distribution | Improve the asset or angle |
| `PAUSE` | low velocity or missing critical info | Hold until better data exists |
| `KILL` | low score, high risk, or weak buyer pain | Stop investing, salvage learnings |
| `NEEDS_DATA` | missing metrics or unknown status | Collect local draft data or clarify assumptions |

Suggested deterministic bucket mapping:

```text
if risk_penalty >= 5 and no proof/approval path: KILL or PAUSE
else if missing core fields: NEEDS_DATA
else if total_priority_score >= 27: DOUBLE_DOWN
else if total_priority_score >= 20: ITERATE
else if total_priority_score >= 14: PAUSE
else: KILL
```

## Missing Metrics Policy

Current tracker records are mostly planning samples with zero metrics. The weekly review should not punish missing metrics too aggressively at the beginning.

Rules:

- If impressions/clicks/opt-ins/sales are all zero, say "no market data yet".
- If no scoring exists, say "unscored".
- If no distribution channels exist, flag distribution gap.
- If no email-list angle is visible, flag email-list opportunity.
- If the record is new and status is `idea`, recommend draft/test, not kill.
- If the record is old, unscored, and has no next action, recommend `NEEDS_DATA` or `PAUSE`.

## Avoid Fake Precision

The review must not claim:

- expected revenue certainty.
- guaranteed sales.
- platform performance predictions.
- conversion rates without data.
- proof that does not exist.
- testimonials or results that are not in the tracker.

Use language like:

- "best next draft candidate"
- "highest apparent leverage"
- "needs market data"
- "approval required before public test"
- "no real performance data yet"

Avoid language like:

- "this will make money"
- "guaranteed winner"
- "proven offer" unless proof exists.

## Output Shape For Future Implementation

Claude may later write a deterministic pre-score artifact:

```json
{
  "experiment_id": "...",
  "velocity_score": 3,
  "distribution_score": 2,
  "monetization_clarity_score": 4,
  "audience_pain_score": 4,
  "content_leverage_score": 5,
  "email_list_fit_score": 3,
  "execution_simplicity_score": 4,
  "risk_penalty": 2,
  "total_priority_score": 23,
  "action_bucket": "ITERATE",
  "confidence": "low_no_market_data"
}
```

This is optional for N+3.20; the first implementation may keep scoring inside the markdown artifacts.
