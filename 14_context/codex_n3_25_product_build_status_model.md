# Codex N+3.25 Product Build Status Model

Status: codex_planning_only / product_build_status_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The build status model should make local product MVP progress visible while keeping all public and money-facing actions blocked until the operator approves them. It should describe product-build state, approval state, blocked reasons, and safe transitions.

## Build Statuses

Recommended `build_status` values:

- `idea`
- `draft_ready`
- `build_pack_generated`
- `operator_review`
- `build_in_progress`
- `built_local`
- `needs_distribution`
- `ready_for_manual_launch_review`
- `launched_manual`
- `paused`
- `killed`

## Approval Statuses

Recommended `approval_status` values:

- `draft_only`
- `needs_operator_review`
- `approved_to_build_local`
- `approved_to_prepare_listing_draft`
- `approved_to_launch_manual`
- `rejected`

## Status Meanings

| Build status | Meaning | Live action allowed |
| --- | --- | --- |
| `idea` | Product exists as an idea only. | No. |
| `draft_ready` | Product draft exists. | No. |
| `build_pack_generated` | Local build pack artifacts exist. | No. |
| `operator_review` | Operator should review claims, deliverables, and risk. | No. |
| `build_in_progress` | Local MVP files are being assembled. | No. |
| `built_local` | Local product folder exists. | No. |
| `needs_distribution` | Product needs content, lead magnet, or channel plan. | No. |
| `ready_for_manual_launch_review` | Candidate for manual launch approval. | No automatic action. |
| `launched_manual` | Operator manually launched after approval. | Record only. |
| `paused` | Stop active work for now. | No. |
| `killed` | Stop pursuing this product. | No. |

## Approval Meanings

| Approval status | Meaning |
| --- | --- |
| `draft_only` | Local draft only; no build or public action approved. |
| `needs_operator_review` | Human review required before next step. |
| `approved_to_build_local` | Local product files may be built. |
| `approved_to_prepare_listing_draft` | Listing drafts may be prepared locally. |
| `approved_to_launch_manual` | Operator may manually publish/list, but no autonomous action. |
| `rejected` | Do not pursue unless revived later. |

## Safe Transitions

Recommended build transitions:

- `idea` -> `draft_ready`
- `draft_ready` -> `build_pack_generated`
- `build_pack_generated` -> `operator_review`
- `operator_review` -> `build_in_progress`
- `build_in_progress` -> `built_local`
- `built_local` -> `needs_distribution`
- `needs_distribution` -> `ready_for_manual_launch_review`
- `ready_for_manual_launch_review` -> `launched_manual`
- any active state -> `paused`
- any active state -> `killed`

Recommended approval transitions:

- `draft_only` -> `needs_operator_review`
- `needs_operator_review` -> `approved_to_build_local`
- `approved_to_build_local` -> `approved_to_prepare_listing_draft`
- `approved_to_prepare_listing_draft` -> `approved_to_launch_manual`
- any review state -> `rejected`

No script should automatically transition into `approved_to_launch_manual`.

## Blocked States

An item is blocked if:

- `approval_status` is `draft_only` and the next step is build
- `approval_status` is `needs_operator_review`
- `approval_status` is `rejected`
- `build_status` is `paused` or `killed`
- risk level is `high`
- required product files are missing
- claim review is missing
- distribution plan is missing
- email-list angle is missing when audience building is required

## Human Approval Gates

Explicit approval is required before:

- building local product files from a draft
- preparing product for public candidate review
- publishing a listing
- uploading product files
- setting a price
- enabling payment
- sending emails
- posting content
- using Whop/Gumroad/Stripe/Shopify/social/email accounts
- collecting customer data
- app-store actions

## Dashboard Behavior

N+3.25 dashboard behavior should be read-only:

- display statuses
- display blocked reasons
- display next manual action
- display missing fields
- display risk warnings

It must not mutate state or approve anything.

## Build Status Model Verdict

The status model should encourage many local product shots while preventing accidental launch. Build locally, review carefully, and only then ask the operator for explicit manual-launch approval.
