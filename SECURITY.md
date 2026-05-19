# Security Policy

Ghoti is local-first and approval-gated. Treat this repository as public-facing
only after the public release audit reports no blockers and a human reviews the
remaining warnings.

## Supported Security Posture

- Do not commit real secrets, private keys, browser sessions, account exports,
  resumes, school records, private screenshots, or raw imported files.
- Keep `.env` files local. Use `.env.example` for placeholder names only.
- Keep external repos in ignored sandbox folders unless a future milestone
  explicitly approves curated source changes.
- Keep UI-TARS observation-only unless a later audited milestone adds safe
  controls.
- Keep live accounts, posting, money, trading, and public actions disabled by
  default.

## Reporting

If you find a vulnerability, do not open a public issue with exploit details or
secret values. Contact the owner privately and include:

- affected file or feature
- reproduction steps that do not expose secrets
- expected safe behavior
- observed risk

## Public Release Gate

Run:

```powershell
python 03_scripts/public_repo_security_audit.py --write-report --json
```

Public release remains blocked if `safe_to_make_public` is false.
