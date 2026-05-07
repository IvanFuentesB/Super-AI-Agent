# Codex N+3.31 Decision Candidates Dashboard Card Spec

Status: codex_planning_only / decision_candidates_dashboard_card / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design a future read-only dashboard card that helps the operator inspect generated weekly review decision candidates and copy safe draft intake commands. The card should improve review speed without adding mutation buttons.

Card title:

```text
Money OS - Decision Candidates
```

Subtitle:

```text
Generated recommendations for manual review. No approve or execute actions.
```

## Data Sources

Primary future source:

```text
05_logs/money_reviews/<run_id>/decisions_recommended.jsonl
```

Possible route source from N+3.30:

```text
GET /api/ghoti/money/weekly-review/artifacts/summary
```

Optional future dedicated route:

```text
GET /api/ghoti/money/decision-candidates/summary
```

All routes must be read-only and local-only.

## Card Summary Fields

Show:

- generated candidates count
- unreviewed count
- rejected count
- copied/drafted count
- manually queued count
- candidates by decision type
- candidates by risk level
- candidates by confidence
- latest review run ID
- latest candidate timestamp if available
- parse warning count

If review-state metadata does not exist yet, show generated count and mark the other state counts as `not_tracked_yet`.

## Candidate Row Fields

Each candidate row should show:

- decision ID
- decision type
- source run ID
- linked experiment ID
- linked product ID if present
- confidence
- risk level
- reason excerpt
- suggested next action excerpt
- approval required yes/no
- source file path

Rows should clearly label candidates as model-generated drafts.

## Safe Interactions

Allowed:

- refresh
- expand/collapse candidate details
- copy source artifact path
- copy draft intake command text
- copy candidate JSON text

Not allowed:

- approve button
- execute button
- append-to-queue button
- reject button that mutates files
- post button
- sell button
- send email button
- outreach button
- payment button
- upload button
- scrape button
- login/account button

The first card should be inspection-only. If review-state persistence is added later, it must be a separate explicitly approved mutation milestone.

## Copy Command Text

The card may render a copy-only command such as:

```powershell
python 03_scripts/manual_decision_queue_new_item.py --dry-run --source-type weekly_review_candidate --source-run-id <run_id> --candidate-id <candidate_id> --decision-type <type> --recommendation "<recommendation>" --reason "<reason>" --risk-level <risk> --next-manual-action "<action>"
```

This text must not run automatically. The operator must copy it into a terminal and review the dry-run output before any append.

## Empty States

No money review artifacts:

```text
No generated decision candidates yet. Run a local weekly money review artifact generator first.
```

Artifacts exist but no candidates:

```text
Latest weekly review has no decision candidates. Review weekly_summary.md and next_10_shots.md manually.
```

Malformed candidate JSONL:

```text
Some candidate lines could not be parsed. They are ignored and counted as warnings.
```

No manual queue exists:

```text
Manual decision queue has not been created yet. Candidate review remains copy-only.
```

## Safety Labels

The card should display a persistent label:

```text
Read-only review. Generated candidates are not approvals and do not authorize public or money-facing action.
```

Show warnings if a candidate implies:

- automatic posting
- automatic outreach
- payment action
- live account action
- scraping
- fake proof
- fake scarcity
- fake engagement
- unsupported income claim

## Implementation Notes For Future Claude

Future frontend implementation should reuse existing dashboard card helpers when possible. It should not reuse the approvals panel semantics because candidate review is not approval.

Recommended rendering helpers:

- `renderDecisionCandidatesSummary(payload)`
- `renderDecisionCandidateRows(items)`
- `buildDecisionCandidateDryRunCommand(item)`
- `renderDecisionCandidateWarnings(warnings)`

## Verdict

The dashboard card should make decision candidates easier to review, not easier to accidentally execute.
