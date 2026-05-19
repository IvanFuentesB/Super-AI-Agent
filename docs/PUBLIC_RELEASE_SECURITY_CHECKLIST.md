# Public Release Security Checklist

Use this checklist before any human changes repository visibility.

## Blocking Checks

- Run `python 03_scripts/public_repo_security_audit.py --write-report --json`.
- Confirm `safe_to_make_public` is true before a visibility change.
- Resolve every likely secret, private key, credential, browser session, raw import, account screenshot, school/private document, CV/private document, and hidden env file.
- Confirm raw user imports remain ignored.
- Confirm generated artifact policy keeps runtime output, logs, reports, videos, archives, DB dumps, and model weights out of git unless deliberately curated.

## Dependency And Runtime Checks

- Dependency lockfile review: confirm lockfiles do not contain private registries or tokens.
- Package scripts review: confirm scripts do not install external repos, run external repo code, or use unsafe command execution.
- Python requirements review: confirm requirements do not point at private package indexes or local private paths.
- Sandbox clone policy: third-party clones stay in ignored sandbox lanes.
- Adapter execution policy: adapter demos must create local artifacts only unless a later audited milestone expands scope.

## Presentation Checks

- README describes current capability honestly.
- README states the project is not open source yet.
- README images come from curated copies only.
- SECURITY.md and CONTRIBUTING.md are present.
- GitHub presentation checklist is complete.
- Issue template suggestion and pull request template suggestion are reviewed before public switch.

## Human Sign-Off

Human review remains required even when the automated audit passes.
