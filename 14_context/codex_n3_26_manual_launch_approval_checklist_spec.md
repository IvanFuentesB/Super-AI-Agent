# Codex N+3.26 Manual Launch Approval Checklist Spec

Status: codex_planning_only / manual_launch_approval_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.26 should define the local checklist that must exist before a product can be manually launched by the operator. This checklist does not authorize Ghoti to publish, upload, sell, send, scrape, or use live accounts. It only documents that the operator reviewed the launch pack and may choose to act manually outside Ghoti.

## Strict No-Auto-Launch Rule

Ghoti must not launch products automatically.

Not allowed:

- posting
- selling
- payment setup
- checkout activation
- product upload
- outreach
- app-store submission
- live account action
- email sending
- marketplace publishing
- social publishing
- scraping

Allowed:

- local checklist
- risk review
- content drafts
- listing drafts
- metrics forms
- review artifacts

## Approval Phrase Format

Required phrase:

```text
APPROVE MANUAL PRODUCT LAUNCH REVIEW FOR <product_id>
```

Meaning:

- The operator has reviewed the launch pack.
- The operator may manually perform external actions outside Ghoti.
- Ghoti is still not authorized to perform any external launch action.

This phrase is not enough to authorize automation. Any future automation would require a separate exact approval phrase for a narrow action.

## Checklist Artifact Location

Future local checklist artifact:

```text
05_logs/manual_launch_reviews/<run_id>/operator_approval_checklist.md
```

Optional future tracker:

```text
14_context/money_workflows/manual_launch_reviews.jsonl
```

## Checklist Sections

### Product Identity

- product ID
- product name
- product type
- source experiment ID
- source product draft ID
- source build pack ID
- artifact directory
- current version

### MVP Deliverables Included

- README
- quick-start guide
- product files
- examples
- bonuses if promised
- support/FAQ notes
- changelog/version file
- no secrets/private data

### Customer And Pain Point

- target customer
- specific painful problem
- buyer awareness level
- why this product is useful
- who it is not for

### Offer And Price Test

- offer statement
- price hypothesis
- value stack
- refund/support notes
- what is included
- what is excluded

### Platform / Listing Draft Status

- Whop listing draft reviewed
- Gumroad-style listing draft reviewed
- landing page draft reviewed
- CTA reviewed
- platform account action required yes/no
- payment setup required yes/no

### Fulfillment / Delivery Status

- delivery format
- local product folder path
- version label
- update expectations
- support boundary
- customer data handling plan

### Refund / Support Boundary

- refund policy draft
- support channel draft
- response expectation
- support includes
- support excludes
- no unlimited support unless explicitly intended

### Legal / ToS Risk Review

- platform ToS risks
- IP/copyright risks
- affiliate disclosure needs
- privacy/cookie needs if collecting emails
- CAN-SPAM/GDPR needs if email list is used
- regulated advice risks

### Claims / Proof Review

- claims present
- proof available
- proof missing
- claims softened
- claims removed
- no guaranteed income/results
- no fake testimonials

### Fake Scarcity / Fake Proof / Spam Check

- no fake scarcity
- no fake urgency
- no fake engagement
- no purchased followers/views/comments
- no scraped or purchased email lists
- no spam outreach
- no deceptive testimonials

### Distribution Plan

- channels
- content pieces
- community rules checked
- posting requires manual approval/action
- no automated posting
- no TOS-breaking growth tactics

### Email List / Lead Magnet Plan

- lead magnet
- opt-in copy
- welcome email draft
- email tool approval status
- no email send before approval
- no list import without approval

### Metrics Intake Plan

- metrics file path
- first review date
- expected metrics
- decision options
- manual entry only

### Operator Final Approval

- operator name or handle
- approval phrase
- approval scope
- approval timestamp
- expiration or review date
- notes

## Checklist Verdict

The manual launch checklist is a gate, not a launcher. It gives the operator confidence to act manually while keeping Ghoti safely out of live commerce and public distribution.
