# Safe Computer-Use Observation Harness

This folder stores local fixtures for the N+6.5A observation harness. The
harness is local-only and fixture-only. It does not open Chrome, does not visit
Apple, does not click, does not type, and does not use a live network.

## Current Fixture

- `fixtures/apple_mac_compare_fixture.json`

The fixture represents a mocked Apple Mac comparison scenario for planning
purposes. It is not scraped from a live website and must not be treated as
current product truth.

## Allowed Now

- Summarize the fixture.
- Extract mocked product names and comparison axes.
- Propose a next-step plan for a human to review.

## Not Enabled

- Live browser or computer-use control.
- Accounts, login, cart, purchase, payment, or scraping.
- CAPTCHA, cookie, bot, or cloak bypass.
- External telemetry.

Any future real browser observation must be a separate audited milestone with
explicit human approval.
