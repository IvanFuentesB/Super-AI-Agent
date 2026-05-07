# Codex N+3.23 Approval Queue Model

Status: codex_planning_only / approval_queue_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The product approval queue should keep product-shot momentum high while preventing accidental public or money-facing action. Gemma can draft, Codex can audit, Claude Code can build local artifacts, and the operator must approve anything that touches the outside world.

## Approval States

Recommended `approval_status` values:

- `draft_created`
- `needs_review`
- `approved_for_build`
- `approved_for_listing_draft`
- `approved_for_content_test`
- `approved_for_manual_publish`
- `rejected`
- `paused`

## State Meanings

| State | Meaning | Live action allowed |
| --- | --- | --- |
| `draft_created` | A local draft artifact exists. | No. |
| `needs_review` | Operator or reviewer must inspect claims, pricing, offer, and risk. | No. |
| `approved_for_build` | Local product files may be built. | No public action. |
| `approved_for_listing_draft` | Local listing copy may be drafted. | No upload or publish. |
| `approved_for_content_test` | Local content drafts may be created for review. | No posting unless separately approved. |
| `approved_for_manual_publish` | Operator has approved a specific manual publish/listing action. | Manual action only, not autonomous. |
| `rejected` | Do not pursue. | No. |
| `paused` | Keep record but stop active work. | No. |

## Role Boundaries

Gemma/Ollama:

- Draft local product copy.
- Summarize notes.
- Generate offer ideas.
- Generate risk labels.
- Generate checklists.
- Never publish, sell, email, post, scrape, or execute output.

Codex:

- Audit plans and specs.
- Review source/data models.
- Produce independent safety reviews.
- Do not stage Claude implementation files.
- Do not use live accounts.

Claude Code:

- Implement local artifact generators.
- Implement read-only dashboard routes/cards.
- Validate code and data formats.
- Commit and push intentional repo changes.
- Do not use Whop/Gumroad/Stripe/social/email accounts unless a later milestone explicitly approves the exact action.

ChatGPT/operator:

- Set strategy.
- Prepare prompts.
- Decide priorities.
- Approve or reject public/money-facing actions.

Human operator:

- Must approve anything public, platform, money, account, outreach, payment, app-store, or legal/tax/finance related.

## Public / Money Action Restrictions

These require separate explicit approval:

- publishing a landing page
- creating a Whop/Gumroad/Stripe/Shopify account action
- uploading product files
- setting price
- activating payment or payout
- posting on social media
- sending email
- outreach
- affiliate/referral setup
- app-store action
- paid ads
- collecting customer data
- using live account credentials

## Queue Transition Rules

Recommended safe transitions:

- `draft_created` -> `needs_review`
- `needs_review` -> `approved_for_build`
- `needs_review` -> `paused`
- `needs_review` -> `rejected`
- `approved_for_build` -> `approved_for_listing_draft`
- `approved_for_listing_draft` -> `approved_for_content_test`
- `approved_for_content_test` -> `approved_for_manual_publish`
- any active state -> `paused`
- any review state -> `rejected`

Avoid automatic transitions into `approved_for_manual_publish`. That state should require a recorded human approval note.

## Approval Record Fields

Future records should include:

- `approval_status`
- `approval_required`
- `approval_notes`
- `approved_by`
- `approved_at`
- `approval_scope`
- `expires_at`

If no approval exists:

- `approval_required` should remain true.
- `approved_by` should be null.
- `approved_at` should be null.

## Dashboard Behavior

Dashboard should show approval queue counts but not mutate states in N+3.23.

Allowed:

- read queue state
- display missing approval warnings
- display drafts awaiting review
- display drafts with risky states

Not allowed:

- approve
- reject
- publish
- upload
- delete
- send
- sell
- post
- change price

## Verdict

The approval queue should start as read-only state visibility. Write actions can be considered later only after the operator explicitly approves a narrow approval-update workflow.
