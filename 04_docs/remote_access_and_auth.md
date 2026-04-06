# Remote Access And Auth

## Current Usage Model

- Codex app for execution
- Continue for local context and rule pickup
- local CLI and runtime for inspectable file-backed behavior

## Near-Term Usage Model

- local control app or local dashboard
- local-only by default
- no exposed public server

## Only-Me-First Stance

- local-only by default
- no client-side secrets
- approval gate before dangerous actions
- keep auth and execution boundaries explicit

## Future Approved-User Model

- real auth first
- role separation before shared use
- audit logging for sensitive actions
- no remote access without deliberate authentication and permission design

## Important Boundary

The public core repo is not the same thing as a public control plane.
