# Codex N+3.19 Dashboard Safety Gate Review

Status: codex_planning_only / dashboard_safety_review / approval_gated

## Safety Boundary

N+3.19 should be a read-only visibility milestone. The dashboard may summarize money workflow records, but it must not perform money workflow actions.

Allowed:

- Read `experiment_tracker.jsonl`.
- Count records.
- Summarize workflow types, statuses, score buckets, channels, and approvals.
- Display latest experiments and next actions.
- Display reminders about distribution and approval gates.
- Refresh local dashboard state.

Forbidden:

- Delete records.
- Edit records.
- Append records.
- Execute model output.
- Trigger Gemma/Ollama generation.
- Fetch YouTube URLs.
- Scrape any platform.
- Post content.
- Send email or outreach.
- Create product listings.
- Start payments, purchases, trades, subscriptions, or account actions.
- Submit app-store or marketplace items.
- Use live accounts.
- Trigger browser/CUA actions.
- Fake engagement, botting, purchased views, fake testimonials, or deceptive claims.

## Human Approval Gates

Human approval is required before:

- Any public post.
- Any product listing.
- Any price test visible to buyers.
- Any email send.
- Any outreach or DM.
- Any account creation or login.
- Any payment or ad spend.
- Any app-store or marketplace submission.
- Any scraping or third-party data collection.
- Any claim about earnings, proof, guarantees, legal, tax, financial, medical, or regulated outcomes.

## Why Read-Only Dashboard Is Safe Next

The current money workflow system has templates and tracker records, but it is hard to see the whole experiment queue at a glance. A read-only dashboard improves operator judgment without adding action authority.

Safe benefits:

- More visibility.
- Less babysitting.
- Better prioritization.
- Faster weekly review.
- Easier approval decisions.
- No live action surface.

## UI Safety Labels

The dashboard card should show an explicit label:

```text
Money OS is read-only. No posting, selling, outreach, payments, scraping, app-store actions, or live account actions can be triggered from this card.
```

If future buttons are shown, they must be disabled and labeled:

```text
Future approval-gated action - not wired
```

## Route Safety Requirements

The server route must:

- Use repo-local file paths only.
- Read only `14_context/money_workflows/experiment_tracker.jsonl`.
- Not call external APIs.
- Not call `spawn` for this route.
- Not write files.
- Not mutate runtime data.
- Not touch credentials.
- Not inspect browser/session/account state.

## Safety Verdict

N+3.19 is safe if it remains a read-only summary route and UI card. It becomes unsafe if the dashboard adds mutation buttons, live platform actions, account automation, or model-output execution.
