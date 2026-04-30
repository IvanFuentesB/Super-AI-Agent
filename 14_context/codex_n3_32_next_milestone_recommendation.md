# Codex N+3.32 Next Milestone Recommendation

Status: codex_planning_only / next_milestone_recommendation / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 557b624

## Current Truth

N+3.31 was planning-only and created specs for:

- decision candidate review flow
- manual queue draft intake
- decision candidates dashboard card
- decision queue safety gate
- Claude implementation checklist

N+3.32 is also planning-only. It designs:

- manual decision queue read view
- operator work session planner
- safety gates for local queue visibility
- future Claude implementation checklist

Claude's N+3.18 implementation remains dirty and unfinished. That dirty state still includes runtime/script/schema work that should not be mixed casually with later dashboard or queue milestones.

## Candidate Next Milestones

### Option A: Resolve Or Consciously Pause N+3.18

Recommended first.

Why:

- dirty runtime and script files are already present
- later Money OS implementation depends on video-to-money and scoring foundations
- leaving dirty implementation files unresolved increases staging and merge risk
- it keeps the branch understandable

Outcome:

- either finish and commit N+3.18
- or deliberately park/revert/branch it only with explicit operator approval

### Option B: Implement N+3.29 Weekly Money Review

Recommended after N+3.18 is resolved or paused.

Why:

- produces the `05_logs/money_reviews/<run_id>/` artifacts
- creates `decisions_recommended.jsonl`
- gives the later dashboard and queue review specs real inputs

### Option C: Implement N+3.30 Dashboard Weekly Review Card

Recommended after N+3.29.

Why:

- reads generated weekly review artifacts
- surfaces decision candidates and next shots
- should remain read-only

### Option D: Implement N+3.31 Manual Queue Intake Helper

Recommended after N+3.29 and optionally after N+3.30.

Why:

- gives the operator a dry-run first append-only path into `manual_decision_queue.jsonl`
- keeps generated candidates from becoming automatic actions

### Option E: Implement N+3.32 Manual Queue Read View And Work Session Planner

Recommended after N+3.31.

Why:

- needs queue records to be useful
- should read reviewed queue items, not raw model recommendations
- becomes more valuable once the queue has real local items

## Honest Recommendation

The real next implementation should be:

```text
N+3.18 Recovery - finish or consciously pause Gemma Video-to-Money Runner + Experiment Scoring
```

Then implement in order:

```text
N+3.29 - Weekly Money Review Artifact Generator
N+3.30 - Weekly Review Artifact Dashboard Read View
N+3.31 - Manual Decision Candidate Review To Queue Draft Intake
N+3.32 - Manual Decision Queue Read View And Operator Work Session Planner
```

This order keeps data flow honest:

1. create/score experiments
2. review weekly artifacts
3. inspect generated candidates
4. manually queue reviewed local work
5. read queue and plan local work sessions

## Why Not Jump Directly To N+3.32 Implementation

Jumping directly to N+3.32 would create a read view before the queue intake path and weekly review artifacts are stable. It would likely produce a polished empty state rather than a useful money workflow.

Empty states are useful, but the next scarce resource is implementation focus. Resolve the dirty base first.

## Safety Recommendation

Do not approve:

- live account actions
- posting
- selling
- email sending
- outreach
- payments
- scraping
- app-store actions
- hidden dashboard mutations
- model-output execution

Keep all future milestones local, artifact-only, and approval-gated until the operator explicitly authorizes a narrow live action.

## Exact Next Claude Recommendation

```text
Continue N+3.18 recovery. Finish or consciously pause the dirty video-to-money runner and experiment scoring work before implementing later Money OS dashboard/queue layers.
```

## Exact Next Future Milestone Recommendation

After N+3.18 is resolved:

```text
N+3.29 Claude - Weekly Money Review Artifact Generator
```

Then continue through N+3.30, N+3.31, and N+3.32 in order.

## Verdict

N+3.32 is a sound design target, but not the next implementation target while N+3.18 remains dirty. Finish the foundation, then stack the dashboard and queue layers on top.
