# GitHub Adapter

## Current Scope

The first live adapter is local repo plus local `git` and optional `gh` CLI backed project checks.

## Safe Capabilities First

- repo status summary
- branch summary
- recent commits
- remote info if available

## Future Capabilities

- issue and PR scaffolding
- repo metadata updates
- approval-gated remote write actions

## Approval Rule

Anything that changes remote state should require explicit approval.
