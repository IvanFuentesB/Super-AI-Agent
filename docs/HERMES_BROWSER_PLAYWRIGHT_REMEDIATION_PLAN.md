# Hermes Browser / Playwright Remediation Plan

Hermes browser/Playwright support is degraded/not claimed in the current Ghoti baseline.

## Current Rule

Do not claim browser automation works. Do not run browser automation beyond local dashboard checks in audited Codex validation.

## Later Remediation

- Inspect Hermes browser diagnostics with safe local commands only.
- Confirm Ubuntu/Playwright compatibility.
- Verify a local-only browser check that does not log in, post, bypass detection, scrape credentials, or control accounts.
- Update dashboard truth only after evidence exists.

## Still Blocked

- No CAPTCHA bypass.
- No bot-detection or cloak bypass.
- No credential/session scraping.
- No uncontrolled click/type.
- No live provider/browser workflow without human approval.
