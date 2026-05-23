# Security Policy

Ghoti is local-first and approval-gated. Treat this repository as public-facing
only after the public release audit reports no blockers and a human reviews the
remaining warnings.

## Supported Security Posture

- Do not commit real secrets, private keys, browser sessions, account exports,
  resumes, school records, private screenshots, raw imported files, or `.env`
  files.
- Keep external repos in ignored sandbox folders unless a future milestone
  explicitly approves curated source changes.
- Keep Hermes, model-council providers, Telegram, UI-TARS, and browser-control
  lanes behind manual setup and approval gates.
- Keep live accounts, posting, money, trading, legal actions, and public actions
  disabled by default.
- Keep bot-detection bypass, captcha bypass, fake engagement, spam, and account
  abuse blocked.

## Reporting

If you find a vulnerability, do not open a public issue with exploit details or
secret values. Contact the owner privately and include the affected file,
reproduction steps that do not expose secrets, expected safe behavior, and the
observed risk.

## Public Release Gate

Run:

```powershell
python 03_scripts/public_repo_security_audit.py --write-report --json
```

Public release remains blocked if `safe_to_make_public` is false.
