# Codex N+3.25 Product Pack Read View Spec

Status: codex_planning_only / product_pack_read_view / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.25 should make manual product build packs visible in the dashboard without enabling any live product, sales, platform, account, payment, or posting action. The view should help the operator see product-shot progress, local MVP build state, approval state, and numbers-game momentum.

This is a planning package only. Codex did not edit runtime code or dashboard code.

## Future Dashboard Card

Card name:

```text
Money OS — Product Packs
```

The card should be read-only and should visually fit the existing dashboard console card pattern.

## Proposed Route

```text
GET /api/ghoti/money/product-build-packs/summary
```

Primary input:

```text
14_context/money_workflows/product_build_packs.jsonl
```

Optional related inputs later:

- `14_context/money_workflows/product_drafts.jsonl`
- `14_context/money_workflows/experiment_tracker.jsonl`

## Zero-State Behavior

If `product_build_packs.jsonl` does not exist, the route should return:

- `ok: true`
- `tracker_exists: false`
- `total_build_packs: 0`
- empty counts
- empty latest list
- a warning that no product build packs have been generated yet
- `read_only: true`
- `live_actions_enabled: false`

The dashboard should display a calm zero-state message:

```text
No product build packs yet. Generate local drafts only after product drafts are reviewed. No live commerce actions are enabled.
```

## Dashboard Sections

The card should show:

- Total product packs
- Ready to build
- Needs approval
- Built locally
- Needs distribution plan
- Needs email-list angle
- Risk warnings
- Latest packs
- Next manual action

## Suggested Layout

Top stats:

- `Total packs`
- `Ready to build`
- `Needs approval`
- `Built locally`

Middle panels:

- build status counts
- approval status counts
- distribution status counts
- email-list status counts
- risk level counts

Tables:

- latest build packs
- top ready-to-build items
- blocked items

Safety footer:

```text
Read-only. No publish, upload, sell, email, outreach, payment, account, or app-store action from this dashboard.
```

## Latest Pack Row Fields

Each latest pack row should include:

- `build_pack_id`
- `created_at`
- `product_name`
- `product_type`
- `approval_status`
- `build_status`
- `distribution_status`
- `email_list_status`
- `risk_level`
- `artifact_dir`
- `next_manual_action`

## Top Ready-To-Build Logic

Top ready-to-build items should prioritize:

1. `approval_status` is `approved_to_build_local`.
2. `build_status` is `pack_generated` or `not_started`.
3. `risk_level` is not `high`.
4. product has deliverables.
5. product has an artifact directory.

If no such records exist, the route should return an empty list and a recommendation to review product drafts first.

## Blocked Items Logic

Items should be marked blocked when:

- approval is missing
- risk is high
- deliverables are missing
- artifact directory is missing
- distribution plan is missing for launch candidates
- email-list angle is missing for products intended to build audience
- status is `paused` or `killed`

Blocked means "needs human review or more local work," not "failed."

## Read-Only Rule

The card must not include:

- state mutation buttons
- approve/reject controls
- publish buttons
- upload buttons
- listing buttons
- payment controls
- email send controls
- social posting controls
- app-store controls
- account login controls
- delete buttons

Allowed first-version control:

- refresh only

## Product Pack Read-View Recommendation

Build this view after the product build pack generator exists or after approved sample `product_build_packs.jsonl` data exists. The first dashboard version should prove visibility and safety before any approval-write or product-building automation is considered.
