# Codex N+3.23 Product Draft Read View Spec

Status: codex_planning_only / product_draft_read_view / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.23 should make product drafts visible without giving Ghoti any live selling capability. The dashboard should help the operator see product-shot volume, approval state, distribution readiness, fulfillment readiness, and risk flags while keeping all public and money-facing actions human-approved.

This is a planning package only. Codex did not edit dashboard or runtime files.

## Dashboard Card

Future dashboard card name:

```text
Money OS — Product Drafts
```

Suggested placement:

- Money OS dashboard section when it exists.
- Or the main dashboard overview as a read-only subcard.
- It should visually match the existing dashboard card pattern and use a clear safety label.

## Required Summary Fields

The card should show:

- total product drafts
- drafts by status
- drafts by workflow/source
- drafts by score bucket
- approval-required count
- latest 10 product drafts
- top 5 highest-scoring draft ideas
- missing fields warnings
- distribution readiness
- email-list readiness
- fulfillment readiness
- risk flags
- parse errors
- tracker path
- updated timestamp

## Suggested Layout

Top strip:

- `Total drafts`
- `Needs approval`
- `A/B/C/D buckets`
- `Risk flags`

Middle sections:

- `Latest product drafts` table.
- `Top scoring drafts` table.
- `Approval queue counts`.
- `Distribution readiness`.
- `Email-list readiness`.
- `Fulfillment readiness`.

Safety footer:

```text
Read-only. No publish, upload, payment, listing, outreach, posting, or live account action from this dashboard.
```

## Latest Draft Row Fields

Each latest draft row should include:

- `draft_id`
- `created_at`
- `product_name`
- `target_customer`
- `approval_status`
- `priority_bucket`
- `recommended_action`
- `approval_required`
- `artifact_dir`

If `artifact_dir` is displayed as a path, it should remain local text only. The first version does not need file-open buttons.

## Top Draft Row Fields

Each top draft row should include:

- `draft_id`
- `product_name`
- `total_score`
- `priority_bucket`
- `recommended_action`
- `buyer_pain`
- `distribution_fit`
- `email_list_fit`
- `legal_tos_risk`

The dashboard should not recompute product score in the first pass. It should read the score from `product_drafts.jsonl` if present.

## Readiness Indicators

Distribution readiness should check:

- `distribution_channels` exists and has at least one channel.
- Stronger readiness if three or more channels are present.
- Missing channels should produce a warning, not a failure.

Email-list readiness should check:

- `email_list_angle` exists and is non-empty.
- Lead magnet fields can be added later.

Fulfillment readiness should check:

- `fulfillment_plan` exists.
- `deliverables` is non-empty.
- `files` or `artifact_dir` points to local artifact paths.

Risk readiness should check:

- `risk_flags` exists.
- Claims and proof review are present when possible.
- High-risk drafts should remain blocked from public action.

## Missing Field Warnings

Warnings should be compact and non-fatal:

- missing `product_name`
- missing `target_customer`
- missing `offer`
- missing `deliverables`
- missing `approval_status`
- missing `distribution_channels`
- missing `email_list_angle`
- missing `fulfillment_plan`
- missing `risk_flags`
- missing `score`

## Read-Only Safety Rules

The dashboard must not include:

- delete buttons
- publish buttons
- upload buttons
- pricing activation
- payment actions
- live Whop/Gumroad/Stripe actions
- email send actions
- outreach actions
- social posting
- app-store actions
- browser automation
- model output execution

Allowed first-version control:

- refresh only.

Future approval buttons may be planned later, but N+3.23 should specify read-only visibility first.

## Product Draft Read-View Recommendation

Build the read-only product draft card only after N+3.18 is finished or consciously paused and after product draft data exists or sample data is approved. The first dashboard slice should prove visibility and safety before any approval-write workflow is added.
