# Contributing

Ghoti is source-visible for demonstration and review, but it is not open source
yet. Contributions are by explicit owner invitation only until the license is
changed.

## Ground Rules

- Do not submit secrets, credentials, private documents, raw imports, account
  screenshots, browser sessions, cookies, provider tokens, or `.env` files.
- Do not add package installs, external repo execution, live account actions,
  Telegram actions, desktop control, or provider runtime wiring without a
  dedicated audited milestone.
- Do not weaken approval gates or local-only safety claims.
- Keep tests and public docs aligned with real current capability.
- Keep commits human-authored and do not add AI co-author trailers unless the
  owner explicitly changes the attribution policy.

## Local Checks

```powershell
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/hermes_local_bootstrap.py --status --json
python 03_scripts/model_council_tool_intake.py --scan --json
python -m unittest 01_projects.runtime_mvp.tests.test_n5_2a_hermes_local_bootstrap_public_readiness_model_provider -v
```

Human review is required before any public visibility change or provider setup.
