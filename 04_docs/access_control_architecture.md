# Access Control Architecture

## Default Model

- only-me-first operation
- local-only by default
- approval gate before dangerous actions
- no client-side secrets in public-facing code or browser logic

## Current Boundary

- this repo is a controllable local workspace first
- risky execution should require explicit approval
- remote access is not part of the current runtime

## Future Approved-User Model

- approved users should be explicit, named, and permission-scoped
- remote access should exist only behind real authentication
- privileged actions should stay gated and logged

## Repo Separation

- public core repo for generic runtime, workflow, and documentation code
- private ops repo for user-specific automations, secrets, integrations, and operating notes
