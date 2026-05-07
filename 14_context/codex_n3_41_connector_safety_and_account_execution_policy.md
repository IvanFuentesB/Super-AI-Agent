# N+3.41 Connector Safety And Account Execution Policy

Status: Codex policy expansion only.
Date: 2026-05-05

Ghoti can eventually use connectors and account identities, including an agent-owned email/account identity, but every external side effect must remain approval-gated.

## Account Identity

Future account types:

- operator's personal email
- agent-owned email/account identity for Ghoti after approval
- dedicated Ghoti sandbox email
- dedicated Ghoti production email
- sandbox social/content accounts
- production content channels
- job portal accounts
- CRM/sales accounts
- marketplace/payment accounts

None are created, connected, or used in N+3.41.

## Sandbox Vs Production

- Sandbox accounts are for testing local drafts and connector permissions.
- Production accounts are for real public, customer, job, email, social, or money workflows.
- Sandbox and production must never share passwords, tokens, or recovery codes.
- Sandbox activity must still follow ToS and law.

## Connector Inventory

Future connector inventory fields:

- connector_id
- platform
- account_id
- sandbox_or_production
- scopes
- read_tools
- write_tools
- created_at
- approved_by
- last_reviewed_at
- revocation_steps
- data_access_level
- external_side_effects_possible
- allowed_actions
- forbidden_actions

## OAuth Approval Gate

Human approval required before:

- OAuth authorization
- token refresh setup
- connector install
- MCP connection
- granting write scopes
- connecting email/calendar/social/CRM/drive/payment/job accounts
- using browser automation with logged-in sessions

Approval must show:

- platform
- requested scopes
- exact tool/connector
- account affected
- read/write capabilities
- revocation steps
- risk level

## Credential Rules

- No secrets in repo.
- No OAuth tokens in markdown.
- No cookies/session dumps in logs.
- No service-role keys client-side.
- No API keys in committed files.
- Store credentials in approved secret storage only.
- Rotate and revoke after suspected exposure.

## External Side Effect Rule

Human approval required for every external side effect:

- sending email
- submitting job applications
- posting or scheduling content
- commenting, liking, following, DMing
- creating accounts
- uploading files to platforms
- publishing listings
- processing payments
- starting subscriptions
- running ads
- scraping platform data
- changing live CRM records

## Email Client Policy

Email client can be:

- draft-only by default
- read-only only after explicit account approval
- send-enabled only for one reviewed message at a time

Before sending, show:

- from account
- recipients
- subject
- body
- attachments
- purpose
- legal/TOS risk
- approval phrase

No mass spam. No hidden sends. No private email harvesting.

This preserves the email outreach workflow with human approval only: drafts can be prepared locally, but the operator approves every send.

## Content Posting Policy

Content workflow can:

- draft scripts
- draft metadata
- draft thumbnails
- draft calendars
- prepare local files

It cannot:

- create accounts
- post
- schedule
- comment
- DM
- buy engagement
- use fake accounts

Publishing is manual unless a future explicit approval-gated mutation milestone is approved.

## Jobs Workflow Policy

Jobs workflow can:

- research companies locally
- draft application material
- draft emails
- track status
- rank fit

It cannot:

- scrape job boards without legal/TOS review
- send applications
- send outreach
- use private email harvesting
- create fake recruiter/applicant accounts
- bypass captchas/auth/rate limits

Human approval is required before every send/application.

## Routine Agent Policy

Routine agents may execute safe local tasks only:

- summarize files
- generate local drafts
- update local draft artifacts if explicitly assigned
- run read-only checks
- produce reports

Routine agents may not perform public/live/money/account actions without human approval.

## Audit Logging

Every connector or account-related action should log:

- requester
- approver
- account
- connector
- action
- scopes
- input artifact
- output artifact
- timestamp
- result
- revocation path

Never log secrets.

## Current Verdict

Connector accounts and agent-owned email identity are important future infrastructure, but N+3.41 keeps them planning-only. Draft/read-only first, explicit approval for every external side effect.
