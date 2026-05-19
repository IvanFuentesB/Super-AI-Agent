# Contributing

Ghoti is source-visible for demonstration and review, but it is not open source
yet. Contributions are by explicit owner invitation only until the license is
changed.

## Ground Rules

- Do not submit secrets, credentials, private documents, raw imports, or account
  screenshots.
- Do not add package installs, external repo execution, live account actions, or
  desktop control without a dedicated audited milestone.
- Do not weaken approval gates or local-only safety claims.
- Keep tests and public docs aligned with the real current capability.
- If a README diagram or screenshot changes, update the related docs and audit
  report in the same branch.

## Local Checks

```powershell
python 03_scripts/public_repo_security_audit.py --run --json
python -m unittest 01_projects.runtime_mvp.tests.test_n5_1a_public_github_readiness_image_backed_presentation -v
```

Human review is required before any public visibility change.
