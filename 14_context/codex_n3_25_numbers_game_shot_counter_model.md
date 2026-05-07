# Codex N+3.25 Numbers-Game Shot Counter Model

Status: codex_planning_only / numbers_game_shot_counter / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Ghoti's money system should make progress visible as a numbers game. The dashboard should count how many ideas, drafts, product packs, local MVPs, content batches, distribution attempts, email-list assets, manual launches, and manually recorded sales exist.

The counter should be honest. It must not hallucinate revenue, scrape metrics, fetch platform data, or imply that a draft has been launched.

## Shot Categories

Recommended categories:

- product ideas
- product drafts
- product build packs
- locally built MVPs
- content batches
- content shots
- distribution attempts
- email-list assets
- manual launches
- sales manually recorded

## Source Files

Potential sources:

- `14_context/money_workflows/experiment_tracker.jsonl`
- future `14_context/money_workflows/product_drafts.jsonl`
- future `14_context/money_workflows/product_build_packs.jsonl`
- future `14_context/money_workflows/content_shots.jsonl`
- future `14_context/money_workflows/content_batches.jsonl`
- future manual metrics files

If a source file is missing, the counter should report zero and include a warning, not fail.

## Honest Count Rules

Product ideas:

- count experiment tracker records with product-related workflow types
- include `digital_product`, `prompt_pack`, `email_lead_magnet`, `productized_service`, and `whop_community`

Product drafts:

- count valid `product_drafts.jsonl` records only

Product build packs:

- count valid `product_build_packs.jsonl` records only

Locally built MVPs:

- count product build packs where `build_status` is `built_local`, `needs_distribution`, `ready_for_manual_launch_review`, or `launched_manual`

Content batches:

- count future content batch tracker records or artifact runs when a tracker exists

Content shots:

- count future `content_shots.jsonl` records

Distribution attempts:

- count only manually recorded attempts
- do not infer attempts from drafts

Email-list assets:

- count lead magnets, opt-in drafts, and email sequences when recorded locally
- do not count subscribers unless manually recorded

Manual launches:

- count only records explicitly marked `launched_manual`

Sales:

- count only manually recorded sales fields
- no automated revenue scraping
- no dashboard hallucinated revenue

## Dashboard Snapshot

Suggested snapshot fields:

```json
{
  "product_ideas": 0,
  "product_drafts": 0,
  "product_build_packs": 0,
  "locally_built_mvps": 0,
  "content_batches": 0,
  "content_shots": 0,
  "distribution_attempts": 0,
  "email_list_assets": 0,
  "manual_launches": 0,
  "manual_sales_recorded": 0,
  "manual_revenue_usd": 0,
  "warnings": []
}
```

## Progress Ladder

The numbers-game ladder:

1. Idea captured.
2. Experiment scored.
3. Product draft created.
4. Build pack generated.
5. MVP built locally.
6. Content batch drafted.
7. Distribution plan drafted.
8. Email-list asset drafted.
9. Manual launch approved.
10. Metrics manually recorded.
11. Iterate, kill, or scale.

## What Not To Count

Do not count:

- generated copy as a sale
- draft listing as a published listing
- product folder as customer delivery
- social draft as a post
- lead magnet draft as email subscribers
- price hypothesis as revenue
- fake proof
- unverified screenshots as results
- scraped metrics
- platform claims without manual record

## Decision Use

The shot counter should help answer:

- Are we creating enough shots?
- Are too many drafts stuck without build packs?
- Are too many products built without distribution?
- Are we neglecting email-list assets?
- Are launches blocked by approvals?
- Which stage is the bottleneck this week?

## Safety Gates

Every count should remain separate from action. A dashboard number never authorizes:

- posting
- upload
- listing
- selling
- payment
- outreach
- email send
- customer data use
- app-store action

## Shot Counter Verdict

The counter should turn the money OS into a scoreboard: honest counts, visible bottlenecks, and no live actions.
