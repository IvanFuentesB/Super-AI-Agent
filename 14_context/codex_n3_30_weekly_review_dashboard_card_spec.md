# Codex N+3.30 Weekly Review Dashboard Card Spec

Status: codex_planning_only / weekly_review_artifact_dashboard_card / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design the future read-only dashboard card that reads generated weekly review artifacts from `05_logs/money_reviews/<run_id>/` through the summary route.

The card should show the operator the latest weekly review packet: summary, decision candidate counts, top recommendations, next shots, risk flags, and artifact paths. It should not approve, execute, append, post, sell, scrape, or use accounts.

## Card Title

```text
Money OS - Weekly Review
```

Subtitle:

```text
Generated artifact reader. No live actions.
```

## Data Source

Future route:

```text
GET /api/ghoti/money/weekly-review/artifacts/summary
```

## Card Sections

### Latest Review Run

Show:

- run ID
- generated timestamp
- run status
- artifact directory path
- total review runs

If no run exists:

```text
No weekly review artifacts found yet. Generate a local weekly review artifact packet first.
```

### Summary Excerpt

Show a short excerpt from:

```text
weekly_summary.md
```

Keep it clearly labeled as model-generated draft review.

### Decision Candidate Counts

Show counts by:

- `DOUBLE_DOWN`
- `ITERATE`
- `PAUSE`
- `KILL`
- `BUILD_NEXT`
- `CREATE_CONTENT_BATCH`
- `CREATE_LEAD_MAGNET`
- `REVIEW_LAUNCH_CHECKLIST`
- `COLLECT_MORE_DATA`

If no candidates exist:

```text
No decision candidates generated.
```

### Top 3 Recommended Decisions

Each row:

- decision type
- experiment ID
- confidence
- risk level
- suggested next action
- approval required yes/no

No approve or execute buttons.

### Next 10 Shots Preview

Show excerpt from:

```text
next_10_shots.md
```

This should be a preview only, not a queue.

### Risk Flags

Show extracted or summarized risk flags from:

```text
risk_review.md
```

Important flags:

- approval required
- no market metrics
- claims/proof risk
- platform/ToS risk
- email compliance
- live account action blocked

### Warnings

Show:

- missing artifact files
- parse errors
- malformed JSON/JSONL
- run summary says mutation or live action occurred
- artifact root missing

Any safety warning should use urgent styling.

### Artifact Paths

Show text paths for:

- `weekly_summary.md`
- `decisions_recommended.jsonl`
- `next_10_shots.md`
- `risk_review.md`
- `run_summary.json`

Interaction:

- copy path text
- optional "copy path" control only

No direct open/execute button in first implementation unless an existing safe preview pattern is intentionally reused with allowed roots.

## Allowed UI Actions

Allowed:

- refresh
- copy artifact path
- expand/collapse sections

Not allowed:

- approve candidate
- append to decision queue
- execute next action
- run Gemma
- generate review
- post content
- sell product
- outreach
- send email
- upload files
- process payment
- scrape metrics
- log into account

## Empty States

Artifact directory missing:

```text
No weekly review artifacts yet. N+3.29 must generate local artifacts before this card can show review content.
```

Latest run missing `run_summary.json`:

```text
Latest review run exists but has no run_summary.json. Showing available text artifacts only.
```

Malformed decisions JSONL:

```text
Some decision candidate lines could not be parsed. They were ignored and counted as warnings.
```

Safety anomaly:

```text
Run summary did not confirm read-only/no-live-action safety. Review artifacts manually before trusting recommendations.
```

## Visual Priority

The card should make these obvious:

- latest weekly review exists yes/no
- what the top three draft recommendations are
- what risk gates block public action
- what the next 10 shots preview says
- where the artifact files live

Do not center revenue or sales unless manually recorded and present in the run summary.

## Implementation Notes

Future Claude should prefer small rendering helpers:

- `renderWeeklyReviewArtifactSummary(payload)`
- `renderDecisionCandidateCounts(counts)`
- `renderTopDecisionCandidates(items)`
- `renderArtifactPathList(sourceFiles)`
- `renderWeeklyReviewWarnings(warnings)`

The UI should degrade gracefully if elements are missing, consistent with the existing dashboard style.

## Verdict

The dashboard card should make generated weekly review artifacts easy to inspect while keeping all decisions manual and approval-gated.
