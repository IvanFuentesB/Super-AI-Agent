# Public Repo Split Plan

## Future Public Core Repo

- generic runtime code
- generic CLI scaffolding
- approval, memory, and workflow examples
- provider profile examples and routing docs
- non-user-specific templates and research notes

## Must Stay Private

- ops and integration code tied to real accounts
- secrets, tokens, and auth material
- runtime data, logs, exports, and handoff artifacts
- user-specific workflows, browser state, and business operating notes
- deployment and remote access configuration

## Release Review Summary

- run secrets and history review
- review generated artifacts and logs
- review runtime data and session data
- review third-party licenses and notices
- confirm final repo visibility before publication

## Recommended Default License

Apache-2.0 for the future public core repo unless changed later.
