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
- External tools stay in static-scan or planning mode.

## Later Milestones

1. Add richer local observation packets with explicit approval tokens.
2. Add compliant browser QA recipes that never bypass service controls.
3. Add small allowlisted desktop recipes with preflight, dry-run, approval, and
   logged local output.
4. Add rollback and interruption checks before any broader local control.

## Always Blocked

- Captcha, cloak, or anti-abuse bypass.
- Fake engagement, spam, account abuse, or unauthorized scraping.
- Live posting, money movement, trading, legal actions, or provider setup.
- Claims that the system acts independently without human supervision.
