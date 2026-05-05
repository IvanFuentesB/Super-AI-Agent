# N+3.40 Connector And Account Strategy

Status: Codex planning only.
Date: 2026-05-05

Codex, Claude, and ChatGPT-style tools can connect to external tools/connectors. Ghoti should eventually use connectors and dedicated accounts, but not before identity, approval, credential, audit, and ToS rules are explicit.

## Dedicated Ghoti Identity Concept

Future concept:

- Dedicated Ghoti email address.
- Dedicated Ghoti calendar/account identity if useful.
- Dedicated social/content accounts only after channel workflow approval.
- Separate sandbox/testing accounts from production accounts.
- Clear account owner: the human operator, not the model.

This milestone does not create, connect, or use any account.

## Sandbox Vs Production Accounts

| Account type | Purpose | Allowed now? | Notes |
| --- | --- | --- | --- |
| Sandbox email | Test drafts, connector permissions, local workflows | no, plan only | Create only with explicit approval |
| Production Ghoti email | Official Ghoti identity | no, plan only | Requires security and recovery plan |
| Social sandbox | Test content/account workflow | no, plan only | No posting without approval |
| Production social channel | YouTube/TikTok/Reels publishing | no, plan only | Human must create/approve |
| Payment/marketplace | Whop/Gumroad/Stripe | no | High-risk money action |

## Credential Storage Rules

- No secrets in repo.
- No tokens in markdown docs.
- No OAuth refresh tokens in logs.
- Use environment variables or approved OS credential storage.
- Keep service keys server-side only.
- Rotate credentials after suspected exposure.
- Keep account recovery information outside the repo.
- Store only non-secret account inventory metadata in repo docs.

## Connector Approval Gates

Human approval required before:

- Adding a connector.
- Granting OAuth access.
- Creating an account.
- Connecting Gmail, Outlook, Slack, Drive, GitHub, calendar, social, CRM, Whop, Gumroad, Stripe, or ad accounts.
- Sending email.
- Posting content.
- Spending money.
- Reading private account data.
- Performing browser automation against logged-in accounts.
- Using connector write tools.

## Account Inventory

Future inventory fields:

- account_id
- platform
- purpose
- sandbox_or_production
- owner
- created_by_human
- connected_tools
- scopes_granted
- last_reviewed_at
- recovery_owner
- revoke_url_or_steps
- risk_level
- allowed_actions
- forbidden_actions

Store only metadata. Never store passwords, API keys, OAuth tokens, recovery codes, cookies, or session exports.

## Audit Logging

Every future connector/account action should log:

- requested_by
- approved_by
- account/platform
- connector/tool
- scopes
- action class
- timestamp
- reason
- result
- artifact paths
- revocation path

Logs must not contain secrets or private content beyond what is needed for audit.

## Revocation And Offboarding Checklist

For every connected account:

- List connected apps.
- Record scopes.
- Record how to revoke.
- Test revocation path before relying on the connector.
- Review monthly or after major milestones.
- Revoke unused connectors.
- Rotate credentials after revocation when appropriate.

## Platform ToS And Integrity Rules

- No fake accounts.
- No spam.
- No fake engagement.
- No giveaway or raffle abuse.
- No mass automation without legal and ToS review.
- No captcha/auth bypass.
- No account creation at scale.
- No deceptive identity.
- No public or money-facing action without human approval.

## Connector Sources Checked

- Claude connectors and Claude Code MCP documentation confirm connectors/MCP can link Claude to external tools, but setup and permissions matter.
- ChatGPT connector documentation confirms connected apps and custom MCP connectors exist for supported plans, with different read/write capabilities.
- OpenAI/Codex documentation confirms Codex can be configured with MCP servers, including documentation-only MCP examples.
- OpenAI docs MCP is documentation-only and does not call APIs on the user's behalf.

Safe interpretation: connectors are useful, but each connector is a new trust boundary. Ghoti should add them one at a time, starting read-only, with human approval and revocation notes.

## Current Verdict

Connector/account workflows are saved for later. Do not connect anything in N+3.40.
