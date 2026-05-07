# Codex N+3.31 Decision Queue Safety Gate Review

Status: codex_planning_only / decision_queue_safety_gate / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define the safety gates for moving from generated decision candidates to local manual queue drafts. The risk is subtle: a model-generated recommendation can feel like an instruction. N+3.31 must keep that recommendation as draft text until the operator deliberately reviews it.

## Core Safety Rule

Generated candidates do not equal approval.

Manual queue records do not equal launch approval.

Approval for public or money-facing action must remain explicit, human, and separate.

## Blocked Automations

N+3.31 must not allow:

- auto-append from `decisions_recommended.jsonl` to `manual_decision_queue.jsonl`
- auto-approval
- one-click approval
- one-click execution
- posting
- selling
- outreach
- emailing
- payment processing
- marketplace publishing
- product uploading
- app-store submission
- scraping
- browser automation
- live account login
- model-output execution

## Model Output Boundary

Gemma output may be stored as:

- `weekly_summary.md`
- `top_experiments.md`
- `decisions_recommended.jsonl`
- `next_10_shots.md`
- `risk_review.md`

It must not be:

- executed as commands
- treated as ground truth
- silently appended to queue files
- used as public copy without review
- used as legal, financial, medical, or tax advice
- used as proof of results

## Candidate Review Requirements

Before a candidate becomes a queue draft, the operator should verify:

- the recommendation is local/manual
- the evidence is real and repo-local or manually recorded
- no fake proof is implied
- no fake scarcity is implied
- no fake engagement is implied
- no spam or unsolicited mass outreach is implied
- no scraping or ToS-breaking tactic is implied
- no live account or payment action is implied
- all public/money-facing steps remain approval-gated

## Manual Queue Record Safety Flags

Future queue records should include these false flags:

```json
{
  "public_action_allowed": false,
  "live_account_action_allowed": false,
  "external_action_allowed": false,
  "model_output_executed": false
}
```

Any attempt to set one of these true should be rejected in the first implementation.

## Human Approval Gates

Explicit human approval is still required before:

- publishing content
- sending email
- performing outreach
- uploading a product
- listing on Whop, Gumroad, Lemon Squeezy, Shopify, or similar
- setting or changing price
- accepting payment
- using account credentials
- collecting customer data
- submitting an app
- buying ads

## Safe Local Actions

Candidates may lead to local-only work such as:

- draft a content batch
- draft a product build pack
- review a launch checklist
- collect manual metrics
- write a risk review
- create a lead magnet draft
- update local planning docs
- ask the operator for a public-action approval later

## Failure Modes To Avoid

- treating `DOUBLE_DOWN` as permission to publish
- treating `BUILD_NEXT` as permission to sell
- treating `CREATE_CONTENT_BATCH` as permission to post
- treating `REVIEW_LAUNCH_CHECKLIST` as launch approval
- treating revenue estimates as real revenue
- treating model-generated reasons as market proof
- turning dashboard review into an approvals panel

## Verdict

The safe version of N+3.31 is a local review funnel: generated candidate, human review, dry-run draft, explicit append. No public action, no money action, no live account action.
