# Codex N+3.30 Dashboard Safety Gate Review

Status: codex_planning_only / dashboard_safety_gate / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Document the safety boundaries for a dashboard that reads generated weekly review artifacts. This is especially important because weekly reviews may include action-like language from Gemma. The dashboard must display draft recommendations without turning them into automation.

## Read-Only Only

N+3.30 must be read-only.

Allowed:

- scan `05_logs/money_reviews/`
- read known artifact files
- summarize counts and excerpts
- show warnings
- copy artifact path text
- refresh the dashboard card

Not allowed:

- write files
- edit trackers
- append decisions
- approve decisions
- execute recommendations
- run Gemma
- generate new reviews
- post, sell, outreach, email, pay, upload, scrape, or log into accounts

## No Auto-Append

The dashboard must not append `decisions_recommended.jsonl` to:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Moving a recommendation into the manual queue requires a separate future mutation milestone with explicit approval gates. N+3.30 is not that milestone.

## No Model Output Execution

Generated artifacts may contain model text. The route and dashboard must treat all model text as untrusted content.

Rules:

- escape text in UI
- do not render markdown as trusted HTML
- do not execute shell snippets
- do not parse model text into actions
- do not create buttons from suggested next actions
- do not treat confidence as proof

## No Public Or Money-Facing Actions

Blocked:

- posting
- publishing
- product upload
- marketplace listing
- checkout activation
- price changes
- payment setup
- email sending
- outreach
- app-store actions
- affiliate setup
- account login
- scraping platform metrics

All public or money-facing actions require human approval and manual execution.

## No Deceptive Growth

Blocked:

- fake proof
- fake scarcity
- fake testimonials
- fake income screenshots
- fake engagement
- bots
- purchased followers/views/comments
- spam
- scraped email lists
- misleading claims

The dashboard should surface these as risk flags if the artifact mentions them.

## Safety Flags To Display

If present in `run_summary.json`, display warnings when any are true:

- `tracker_mutated`
- `queue_mutated`
- `live_actions_taken`
- `external_api_used`
- `scraping_enabled`
- `posting_enabled`
- `selling_enabled`
- `outreach_enabled`
- `payment_actions_enabled`
- `model_output_executed`

If safety flags are missing, display:

```text
Run summary did not confirm no-live-action safety. Review manually.
```

## Human Approval Rule

Recommended dashboard label:

```text
Draft review only. Human approval and manual execution required before public or money-facing action.
```

This label should appear near decision candidates.

## Relationship To Other Milestones

N+3.29:

- generates weekly review artifacts
- may call local Gemma
- writes draft artifacts

N+3.30:

- reads generated artifacts
- displays summaries
- does not generate or mutate

Future mutation milestone:

- may add explicit queue intake or approval flows
- requires separate approval
- must remain narrow and auditable

## Verdict

The dashboard can make weekly review recommendations visible, but it must not become a launch panel, sales console, outreach bot, or autonomous decision system.
