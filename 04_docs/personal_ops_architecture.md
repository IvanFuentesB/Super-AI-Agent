# Personal Ops Architecture

## Goal

The personal-ops layer packages legitimate owned-account workflows into inspectable draft packs, runbooks, and handoff-ready outputs.

## Why These Workflows Belong Here

- mail and inbox work needs triage summaries and draft packs
- LinkedIn and CV work needs structured update packs
- GitHub and Notion work needs planning and documentation support
- all of them benefit from approval gates, durable context, and reusable scaffolds

## Current State

- planning and scaffold generation only
- no live mail adapter
- no live LinkedIn adapter
- no live Notion adapter

## Future State

- real adapters behind approval gates
- clearer account scoping and audit logs
- outbound actions only after explicit approval

## Important Boundary

The public core repo is not the same thing as the private ops execution layer.
