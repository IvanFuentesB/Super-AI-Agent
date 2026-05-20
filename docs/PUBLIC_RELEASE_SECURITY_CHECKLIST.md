# Public Release Security Checklist

Use this checklist before relying on the public repo presentation.

## Blocking Checks

- Run `python 03_scripts/public_repo_security_audit.py --write-report --json`.
- Confirm `safe_to_make_public` is true before a visibility/presentation push.
- Resolve likely secrets, private keys, credentials, browser sessions, raw
  imports, account screenshots, school/private documents, CV/private documents,
  and hidden env files.
- Confirm raw user imports remain ignored.
- Confirm generated artifacts, runtime output, reports, videos, archives, DB
  dumps, and model weights are not accidentally committed.
- Confirm no provider or Telegram token is committed.
- Confirm Hermes/model-council materials remain planning/local-bootstrap only.

## Runtime Checks

- No external repo execution by default.
- No Hermes provider wiring without verification.
- No Telegram action without manual user token/chat setup and approval.
- No bot-detection bypass.
- No live account/posting/money/trading/legal action.

## Portfolio Checks

- Pin the right repos.
- Add topics.
- Add demo GIFs where safe.
- Add Actions checks.
- Create portfolio releases.
