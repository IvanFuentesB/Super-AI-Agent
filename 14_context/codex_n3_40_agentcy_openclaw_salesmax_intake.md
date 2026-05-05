# N+3.40 Agentcy, OpenClaw, And SalesMaxAI Intake

Status: Codex source-check/intake only.
Date: 2026-05-05

No install, clone, account connection, MCP connection, or runtime wiring is approved by this doc.

## Summary Table

| Tool/concept | Source-check status | How it might help Ghoti | Install/connect now? | Risk | Priority | Safe next step |
| --- | --- | --- | --- | --- | --- | --- |
| `msitarzewski/agentcy-agents` | Exact spelling unverified; likely source is `msitarzewski/agency-agents` on GitHub | Specialist agent roles, agency-style workflows, content/product roles, delivery checklists | no | Medium supply-chain; possible external-service dependencies | soon research | Read repo docs only; extract safe role patterns into local docs |
| OpenClaw | Source found: OpenClaw docs/repo ecosystem; high-autonomy agent platform | Future worker/channel/operator lane; possible agent coordination and tool execution layer | no | High because agents can take real actions with tools/accounts/files/network | later/soon research | Isolated security/source audit after lane/lock protocol |
| SalesMaxAI / Salesmax deals | Source found: Salesmax Intelligent CRM app and AI sales/deal-management references | Deal tracking, sales pipeline patterns, CRM workflow inspiration | no | Medium-high due call logs, contacts, payment links, CRM data, live customer actions | research | Compare deals/features/pricing; no account, no CRM import |

## Agency-Agents Notes

Search found `msitarzewski/agency-agents`, described as a complete AI agency with specialized agent personalities and deliverable-focused workflows. The user said `agentcy-agents`, so the exact requested spelling remains unverified, but the likely intended repo is `agency-agents`.

Potential Ghoti uses:

- Agent role taxonomy.
- Specialist prompts.
- Product/growth/content agents.
- Reality-check and review roles.
- Future multi-agent lane design.
- Agency-style deliverable templates.

Safety rules:

- Do not install or run scripts.
- Do not import agents into runtime automatically.
- Do not grant tools/accounts.
- Extract only safe patterns after source review.
- Preserve attribution and license review before reuse.

## OpenClaw Notes

OpenClaw remains important but high risk because it is intended to let agents act through tools and channels.

Potential Ghoti uses:

- Future worker layer.
- Channel integration ideas.
- Agent workspace patterns.
- Skill marketplace lessons.
- Multi-agent routing patterns.

Risks:

- Shell/file/network tool exposure.
- Account/tool permissions.
- Supply-chain risk from skills/plugins.
- Autonomous publishing or messaging.
- Bypassing platform/account controls if misused.
- Shared-state corruption without locks.

Must be true before integration:

- N+3.29 through N+3.32 Money OS local artifact/read-view flow stable.
- Agent lane/lock protocol implemented.
- Connector/account policy implemented.
- Read-only evaluation plan written.
- Install/run approval granted.
- Sandbox or isolated worktree ready.
- No live accounts connected.

## SalesMaxAI Deals Notes

Salesmax appears to be an intelligent CRM/sales automation product with deal-management, lead/call tracking, and AI automation claims. That makes it potentially useful as a pattern source, but risky as a live CRM.

Potential Ghoti uses:

- Deal pipeline data model inspiration.
- Sales follow-up stage language.
- CRM card templates.
- Manual metrics and pipeline design.
- Future approved sales dashboard reference.

Risks:

- Contacts and call logs are sensitive.
- Automated follow-up can become spam.
- Payment-link integrations are money actions.
- CRM automation can contact real people.
- Data export/import can leak private information.

Safe next step:

- Source-check pricing, privacy, and feature list.
- Extract only generic sales pipeline concepts.
- Do not create an account or connect contacts.
- Do not send outreach.
- Do not enter payment details.

## Interaction With Future Lanes

- Paperclip: possible control-plane candidate after safety rails.
- Ruflo: possible orchestration candidate after isolated audit.
- CUA: possible browser/operator lane after sandbox approval.
- n8n: deterministic rails for approved workflows later.
- OpenClaw: worker/channel layer only after locks, approval, and sandbox.
- agency-agents: role library inspiration; lowest-risk if used as docs-only patterns.
- SalesMaxAI: CRM/sales model inspiration; high-risk if connected live.

## Current Recommendation

Research only. Highest near-term value is extracting safe role and workflow patterns from `agency-agents`, while keeping OpenClaw and SalesMaxAI out of runtime until the agent lane and connector/account policies exist.
