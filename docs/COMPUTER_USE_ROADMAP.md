# Computer-Use Roadmap

Computer-use features must be narrow, visible, and supervised. The MVP supports
status, dry-runs, local previews, and observation packets. It does not grant
general desktop control.

## Current MVP

- Dashboard runs locally at `http://127.0.0.1:3210`.
- UI-TARS is observation-only and dry-run by default.
- Approved adapters run local demo dry-runs only.
- Browser and Playwright status may be degraded and must be reported
  truthfully.
- Hermes Agent / Manual Bridge is status/readiness only. It does not run
  browser automation or provider setup.
- External tools stay in static-scan or planning mode.

## Later Milestones

1. N+6.1B first: constrained Gemma worker routing is now on main.
2. N+6.2A next: verify Hermes Agent manual bridge workflow, WSL path mapping,
   safe commands, blocked commands, and guide files. This remains
   probes/readiness only; no provider config, tokens, Telegram, live APIs,
   browser automation, or computer-use click/type.
3. N+6.3A next: prepare safe computer-use with Gemma, Hermes, UI-TARS
   observation, Browser Harness, and Vercel agent-browser roadmap. Observation
   comes first; every click/type/live-account action requires explicit future
   approval.
4. Add richer local observation packets with explicit approval tokens.
5. Add compliant browser QA recipes that never bypass service controls.
6. Add small allowlisted desktop recipes with preflight, dry-run, approval, and
   logged local output.
7. Add rollback and interruption checks before any broader local control.

## Boring Long Task Direction

The target use case is long runs of individually simple tasks, such as reading
local reports, summarizing status, selecting known context bundles, preparing
draft prompts, and classifying safety risk. These can be accelerated with Gemma
and Hermes only when each step remains local, inspectable, and approval-gated.
Ghoti must not convert this into uncontrolled browser/account automation.

## Future Apple Comparison Test

N+6.2A maintains a future observation/manual-approval test plan at
`docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md`. The plan is to use
Chrome in Incognito mode on the Apple website to compare the newest Mac laptop
option with Mac mini and write a local decision packet. Do not execute it yet.

N+6.3A may build an observation/manual-approval harness for that test. It must
start observation-only, require human approval for every click/type, avoid
login/cart/purchase/account actions, avoid CAPTCHA/bot/cloak bypass, and use
Gemma only to summarize visible page text. No live APIs.

## Always Blocked

- Captcha, cloak, or anti-abuse bypass.
- Fake engagement, spam, account abuse, or unauthorized scraping.
- Live posting, money movement, trading, legal actions, or provider setup.
- Claims that the system acts independently without human supervision.
