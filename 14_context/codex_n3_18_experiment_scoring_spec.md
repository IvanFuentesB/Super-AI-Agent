# Codex N+3.18 Experiment Scoring Spec

Status: codex_audit_only / scoring_spec / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 6be07a5

## Purpose

Define a simple scoring system for ranking many money experiments. The goal is to help Ghoti pick high-speed, high-upside, ethical shots while avoiding risky, expensive, or unclear ideas.

## Scoring Fields

All fields use a 1 to 5 score.

Positive fields:

- `speed_to_ship`
- `pain_intensity`
- `buyer_access`
- `distribution_leverage`
- `monetization_clarity`
- `content_volume_potential`
- `email_list_potential`

Negative fields:

- `proof_difficulty`
- `build_complexity`
- `legal_tos_risk`

Computed fields:

- `total_score`
- `priority_bucket`

## Rubric

### `speed_to_ship`

| Score | Meaning |
| --- | --- |
| 1 | Requires weeks/months or new tools. |
| 2 | Several days plus unfamiliar work. |
| 3 | 1 to 3 days. |
| 4 | Same day with current templates. |
| 5 | Under 2 hours from existing notes. |

### `pain_intensity`

| Score | Meaning |
| --- | --- |
| 1 | Mild curiosity. |
| 2 | Annoying but not urgent. |
| 3 | Clear recurring pain. |
| 4 | Expensive or time-consuming pain. |
| 5 | Urgent pain tied to money, school, health, or identity. |

### `buyer_access`

| Score | Meaning |
| --- | --- |
| 1 | No clear place to reach buyers. |
| 2 | Buyers exist but channels are uncertain. |
| 3 | 1 to 2 reachable channels. |
| 4 | Several reachable communities/platforms. |
| 5 | Existing user access, audience, or obvious communities. |

### `distribution_leverage`

| Score | Meaning |
| --- | --- |
| 1 | One-off manual sharing only. |
| 2 | One platform, weak repurposing. |
| 3 | 2 to 3 channels. |
| 4 | Short-form + email + community/SEO angle. |
| 5 | Strong multi-channel flywheel with repurposable content. |

### `proof_difficulty`

| Score | Meaning |
| --- | --- |
| 1 | Easy to show proof with sample/demo. |
| 2 | Needs one small example. |
| 3 | Needs case study or user feedback. |
| 4 | Needs multiple outcomes/testimonials. |
| 5 | Hard to prove without real sales, regulated results, or long timeline. |

### `build_complexity`

| Score | Meaning |
| --- | --- |
| 1 | Markdown/checklist only. |
| 2 | Template bundle or small script. |
| 3 | Static page or simple workflow. |
| 4 | Multi-file app, media production, or external tool. |
| 5 | Platform integration, app-store, payments, or complex runtime. |

### `legal_tos_risk`

| Score | Meaning |
| --- | --- |
| 1 | Local artifact only, no external action. |
| 2 | Public content draft, no claims. |
| 3 | Platform posting or affiliate disclosure needed. |
| 4 | Outreach, paid tools, user data, finance/fitness claims. |
| 5 | Legal/tax/financial advice, app-store/payment workflows, scraping risk, or account automation. |

### `monetization_clarity`

| Score | Meaning |
| --- | --- |
| 1 | No obvious buyer or offer. |
| 2 | Possible monetization but fuzzy. |
| 3 | Clear product or lead magnet path. |
| 4 | Clear price range and buyer. |
| 5 | Clear buyer, price, delivery, and upsell path. |

### `content_volume_potential`

| Score | Meaning |
| --- | --- |
| 1 | Hard to make content around it. |
| 2 | A few posts. |
| 3 | 10+ content ideas. |
| 4 | 30+ content ideas across formats. |
| 5 | Ongoing content engine with recurring themes. |

### `email_list_potential`

| Score | Meaning |
| --- | --- |
| 1 | No obvious opt-in. |
| 2 | Weak checklist. |
| 3 | Useful lead magnet. |
| 4 | Strong lead magnet tied to product. |
| 5 | Lead magnet naturally feeds a sequence, product, and community. |

## Formula

Recommended total:

```text
positive = speed_to_ship + pain_intensity + buyer_access + distribution_leverage + monetization_clarity + content_volume_potential + email_list_potential
negative = proof_difficulty + build_complexity + legal_tos_risk
total_score = positive - negative
```

Range:

- best realistic scores: 20+
- average workable scores: 12 to 19
- weak scores: under 12

## Priority Buckets

| Bucket | Criteria | Meaning |
| --- | --- | --- |
| `A_now` | total_score >= 20 and legal_tos_risk <= 2 and build_complexity <= 2 | Build this week. |
| `B_test` | total_score 14 to 19 and legal_tos_risk <= 3 | Create a small test. |
| `C_research` | total_score 8 to 13 or uncertainty high | Research or compress notes first. |
| `D_defer` | total_score < 8 or build_complexity >= 4 | Defer until stronger resources. |
| `BLOCKED_APPROVAL` | legal_tos_risk >= 4 or live action needed | Requires explicit human approval before external action. |

## Ranking Shots

Rank in this order:

1. Remove anything unsafe, spammy, deceptive, or illegal.
2. Mark approval-blocked items.
3. Sort by `priority_bucket`.
4. Sort by `total_score` descending.
5. Tie-break with lowest `build_complexity`.
6. Tie-break with highest `email_list_potential`.
7. Tie-break with operator energy/interest.

## JSON Shape

Suggested future scoring object:

```json
{
  "scores": {
    "speed_to_ship": 5,
    "pain_intensity": 4,
    "buyer_access": 4,
    "distribution_leverage": 4,
    "proof_difficulty": 2,
    "build_complexity": 1,
    "legal_tos_risk": 1,
    "monetization_clarity": 4,
    "content_volume_potential": 5,
    "email_list_potential": 4,
    "total_score": 26,
    "priority_bucket": "A_now"
  }
}
```

## Recommended First Use

Use scoring on runner-generated `experiment_candidates.jsonl`, not on the canonical tracker directly. Operator reviews the top candidates, then uses `money_workflow_new_experiment.py` to append selected entries.

## Safety Rule

High score never overrides approval gates. A high-scoring idea that requires posting, outreach, paid tools, accounts, app-store action, or payments is still blocked until the operator approves that exact action.
