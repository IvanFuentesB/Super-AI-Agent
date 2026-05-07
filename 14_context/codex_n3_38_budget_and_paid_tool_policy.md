# N+3.38 Budget And Paid Tool Policy

Status: Codex policy/spec only.
Date: 2026-05-01

The user accepts spending money when it can reasonably make more money, but Ghoti must not spend autonomously.

## Current default spend

- ChatGPT is an approved baseline tool.
- Claude is an approved baseline tool.
- These existing subscriptions do not imply approval for any additional subscription, API spend, credit pack, ad spend, marketplace fee, or paid account.

## Approval rule

Ghoti may recommend paid tools, but every new paid action requires explicit human approval before:

- subscribing
- buying credits
- entering payment details
- running ads
- paying marketplace or app-store fees
- connecting a paid API
- upgrading a plan
- renewing a non-baseline tool

## Required paid-tool recommendation fields

Every paid-tool recommendation must include:

- Expected use case.
- Estimated cost.
- Expected ROI or learning hypothesis.
- Spending cap.
- Stop-loss or cancel condition.
- Review checkpoint.
- Free or local alternative if available.

## ROI hypothesis format

Use this format before any paid test:

```text
Tool:
Use case:
Expected cost:
Spending cap:
Expected output:
Expected learning:
Expected revenue or leverage hypothesis:
Free/local alternative:
Stop-loss/cancel condition:
Review date:
Human approval phrase:
```

## Stop-loss examples

- Cancel if no usable assets are produced after one capped test.
- Cancel if content cannot be exported without watermarks/rights issues.
- Cancel if tool quality is worse than local/Gemma/manual workflow.
- Cancel if the experiment does not create measurable views, opt-ins, leads, sales, or learning.
- Cancel if the tool pushes unsafe automation, fake engagement, scraping abuse, or account-risk behavior.

## Tracking recurring subscriptions

Future money workflow memory should track:

- tool name
- monthly cost
- renewal date
- owner account
- experiment tied to the spend
- expected value
- actual value
- cancel checkpoint
- cancellation instructions if known

No account passwords, API keys, payment details, or secrets should be stored in repo memory.

## Examples

- Viewmax, Higgsfield, Arcads, Kling, and Seedance may be worth paying for if a content pipeline has a clear offer, posting plan, email-list angle, and metrics loop.
- OpenRouter/API spend must be capped and logged per experiment.
- Ads spend should happen only after a validated offer, landing/listing draft, metrics intake plan, and human approval.
- App-store fees should happen only after the product is reviewed, risk-gated, and approved.
- Whop/Gumroad/Lemon Squeezy/Stripe setup must remain manual and human-approved.

## Absolute prohibitions

Ghoti must never autonomously:

- pay
- subscribe
- buy credits
- run ads
- enter payment details
- renew a tool
- upgrade a plan
- launch a listing
- process payments
- trade or invest real money
- bypass usage caps, auth, captchas, subscriptions, or platform rules
