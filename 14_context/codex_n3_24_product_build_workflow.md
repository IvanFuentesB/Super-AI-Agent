# Codex N+3.24 Product Build Workflow

Status: codex_planning_only / product_build_workflow / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

This workflow turns a product draft into a local MVP build pack, then into manually reviewed assets, and only later into a public launch if the operator explicitly approves. It is designed for many product shots, fast feedback, and safe boundaries.

## Step 1: Choose Product Draft

Input:

- product draft artifact
- product draft JSONL record
- experiment tracker record
- operator notes

Decision:

- build now
- test with content
- needs research
- pause
- kill

Approval gate:

- If the product is not approved for local build, do not generate a build pack.

## Step 2: Generate Build Pack

Future command:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task product_build_pack --input 14_context/money_workflows/product_build_pack_input_n3_24.md --max-chars 20000
```

Output:

- product brief
- customer avatar
- offer stack
- MVP deliverables
- build steps
- local folder structure
- sales drafts
- lead magnet draft
- content launch pack
- risk review
- approval checklist

Approval gate:

- Generated artifacts are drafts only.

## Step 3: Operator Reviews

Review:

- buyer clarity
- claim safety
- deliverables
- pricing hypothesis
- fulfillment burden
- support expectations
- risk flags
- public approval requirements

Decision:

- build MVP locally
- request edits
- pause
- reject

## Step 4: Build MVP Locally

Create local folder:

```text
11_exports/products/<product_slug>/
```

Build:

- README
- quick-start guide
- product files
- examples
- bonuses if useful
- sales assets
- support notes
- changelog

Approval gate:

- Still no upload, listing, sale, public page, email send, or account action.

## Step 5: Create Listing Draft

Use local artifacts to prepare:

- Whop listing draft
- Gumroad listing draft
- lead magnet landing page draft
- FAQ
- refund/support notes
- CTA variants

Approval gate:

- Listing copy may be drafted, but no marketplace action occurs.

## Step 6: Create Content Batch

Generate or manually draft:

- short-form hooks
- launch posts
- email drafts
- community post drafts
- YouTube/short-form ideas
- repurposing map

Approval gate:

- No posting or email sending without explicit approval.

## Step 7: Collect Emails Later Only With Approval

Future approved options:

- manual opt-in page
- email service provider
- lead magnet form

Not allowed in this workflow:

- purchased lists
- scraped emails
- unsolicited adds
- automated outreach
- sending emails without approval

## Step 8: Launch Manually Only After Explicit Approval

Required approvals:

- product files reviewed
- claims reviewed
- pricing approved
- refund/support policy approved
- platform account action approved
- payment setup approved
- publication approved
- distribution plan approved

The launch remains manual unless a future milestone explicitly approves a narrow automation.

## Step 9: Record Metrics

Track:

- impressions
- clicks
- opt-ins
- replies
- sales
- refunds
- revenue
- time spent
- support requests
- qualitative feedback

Metrics should be manually entered at first. No live platform scraping or account integrations.

## Step 10: Iterate, Kill, Or Scale

Decision outcomes:

- scale: build more content or improve product
- iterate: adjust offer, price, proof, or audience
- pause: hold until more data exists
- kill: stop spending time

## Safety Rules

- No fake proof.
- No fake urgency.
- No income guarantees.
- No platform account automation.
- No payment action.
- No uploads.
- No public posts.
- No outreach.
- No scraping.
- No customer data.
- Human approval required before public use.

## Workflow Verdict

This workflow keeps the user moving from ideas to local MVPs without crossing the dangerous line into unapproved commerce. It supports the numbers game by making product creation repeatable and reviewable.
