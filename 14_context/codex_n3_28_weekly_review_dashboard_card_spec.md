# Codex N+3.28 Weekly Review Dashboard Card Spec

Status: codex_planning_only / weekly_review_dashboard_card / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design the future read-only dashboard card for the Money OS weekly review. The card should make the operator's next manual decisions visible while preserving the hard boundary: no live actions from the dashboard.

## Future Card

Card title:

```text
Money OS - Weekly Review
```

Optional subtitle:

```text
Read-only scoreboard. Manual decisions only.
```

## Data Source

Future route:

```text
GET /api/ghoti/money/weekly-review/summary
```

The UI should treat the response as read-only.

## Card Sections

### 1. Weekly Shot Snapshot

Show:

- experiments
- manual decisions
- product drafts
- product build packs
- manual metric records
- manual sales
- manual revenue
- opt-ins

Use honest labels:

- "manual revenue recorded"
- "manual sales recorded"
- "drafts, not launches"

### 2. Decisions Pending

Show:

- decisions by status
- decisions by type
- pending operator review count
- accepted local work count
- paused/killed count

If no decision queue exists, show:

```text
No manual decision queue yet. N+3.28 implementation can add a local append-only queue.
```

### 3. Top 5 Next Manual Actions

Each row:

- source type
- source ID
- next manual action
- approval required yes/no
- risk level if known
- related file path if present

No action buttons.

### 4. Blocked Items

Show:

- blocked experiments
- paused decisions
- missing metrics
- items missing distribution
- items missing email-list angle
- items missing CTA
- items requiring approval

### 5. Distribution Gaps

Show summary warnings:

- no distribution channels
- no email-list angle
- no CTA
- no content assets
- no manual metrics after launch

### 6. Email-List Opportunities

Show:

- lead magnet candidates
- opt-in angle missing/present
- manual opt-ins recorded
- email-list growth manually recorded

### 7. Latest Review Artifacts

Show latest review run if present:

- run ID
- artifact directory
- weekly summary path
- decision candidate path
- run summary path

If missing:

```text
No weekly money review artifact has been generated yet.
```

## Safe Interactions

Allowed UI interactions:

- refresh
- copy file path
- open local artifact path if existing dashboard pattern supports safe local preview
- collapse/expand card sections

Not allowed:

- approve decision
- append decision
- edit tracker
- delete tracker line
- publish
- post
- send email
- outreach
- sell
- upload
- set price
- process payment
- scrape metrics
- log into accounts
- run Gemma
- run Docker
- run CUA

Any future mutation button requires a separate approval-gated milestone.

## Empty States

Experiment tracker missing:

```text
Experiment tracker missing. Money OS cannot count experiments yet.
```

Manual decision queue missing:

```text
Manual decision queue missing. Showing experiment next actions only.
```

Product metrics missing:

```text
No manual launch metrics file yet. Sales, revenue, opt-ins, and channel results are zero-state.
```

Weekly review artifacts missing:

```text
No weekly review run found. Generate an artifact-only weekly review before expecting recommendations.
```

## Visual Priority

The card should emphasize:

- the next 5 manual actions
- blocked/approval-required items
- whether distribution and email capture are missing
- whether there are enough shots this week

Avoid over-emphasizing revenue before real manual data exists.

## Safety Label

Include a visible label:

```text
Read-only: no posting, selling, outreach, payments, scraping, or account actions.
```

## Implementation Notes For Claude

In `public/app.js`, prefer small rendering helpers:

- render metric pills
- render warning list
- render next manual actions
- render source file status
- render latest artifact links

Keep logic simple and defensive because source files may not exist yet.

## Validation

Future Claude should run:

```powershell
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/server.js
git diff --check
```

If the dashboard is already running, manually verify that the card renders a zero-state without breaking the rest of the page.

## Verdict

The dashboard card should make weekly Money OS decisions obvious without turning the dashboard into a control panel for public or money-facing actions.
