# N+3.45B Ruflo / OpenClaw / Paperclip / n8n Comparison

Status: Codex source-check/audit lane only.
Date: 2026-05-05

## Comparison Table

| Candidate | Problem it solves | What it does not solve | How it could fit Ghoti | Safety boundary | Required approvals | Later test path | Live accounts now? |
|---|---|---|---|---|---|---|---|
| Ruflo | Claude Code multi-agent orchestration, skills/plugins, MCP-style coordination | Does not remove need for branch locks, human review, or trusted source auditing | Possible agent swarm layer after Ghoti lane locks and prompt bus prove stable | Isolated clone only; no MCP connection, no global install, no `curl | bash` | Explicit approval to clone; separate approval to run; security review before MCP | Clone in quarantine folder, inspect package scripts, no execution first | No |
| OpenClaw | Action-capable personal AI/agent runtime with channels/tools | Does not guarantee safe behavior; action capability raises account/shell/browser risk | Future worker/operator layer after sandbox and connector policy | Sandbox-only; no real accounts, no shell privileges beyond approved workspace | Approval for clone, install, run, tools, and each connector | Read docs, isolated source audit, local no-account smoke only | No |
| PaperclipAI/paperclip | Control plane for teams of agents, budgets, org charts, heartbeats, work/cost tracking | Does not make agent work safe by itself; can amplify bad goals/actions | Future business/control-plane candidate managing Claude/Codex/Gemma/shell workers | Local-only dashboard first; no live companies, accounts, payments, or auto-spend | Approval for clone/run, budgets, adapters, and every external agent | Compare architecture against Ghoti prompt bus after local pilot | No |
| n8n | Low-code/API workflow automation, credentialed integrations, MCP-exposed workflows | Not a general safety policy; workflows can mutate external services | Future automation rails for approved repeatable workflows | Local/self-hosted, disabled credentials, read-only examples first | Approval for install, credentials, exposed workflows, and each execution | Plan-only workflow JSON, then local instance with fake credentials | No |
| CUA/browser layer | Desktop/browser operation and visual validation | Does not solve legal/TOS, login, account, or action safety | Later browser/operator lane for localhost/dashboard and sandbox-only tasks | Screenshot/localhost first; no logged-in sites | Approval for target, action type, and sandbox profile | Local dashboard screenshot smoke; then test-only forms | No |

## Fit By Layer

### Ruflo

Ruflo is closest to a Claude Code swarm/orchestration layer. Its public README includes plugin, CLI, global npm, npx, and MCP server paths, which is useful but raises supply-chain and execution risk. It should be evaluated only in a quarantined source-audit lane first.

### OpenClaw

OpenClaw is a possible action-capable worker layer. That is exactly why it is risky: any agent that can operate channels, shell, files, or browsers must sit behind Ghoti approval gates and sandboxing. Treat as important, not immediate.

### Paperclip

Paperclip is the strongest control-plane metaphor: agents as employees, heartbeats, budgets, activity trails, and governance. It fits Ghoti's long-term "local company OS" idea, but only after the local prompt bus and agent lane locks prove that Ghoti can coordinate humans and agents safely.

### n8n

n8n is best for deterministic integrations and business automations after human-reviewed workflows exist. It can handle APIs and credentials, so it belongs after the connector/account policy, not before.

### CUA / Browser Layer

CUA, Chrome DevTools MCP, Firecrawl, Glif, and Camofox all touch the outside world more directly than docs or local scripts. They should stay behind a browser/operator lane with target-specific approvals.

## Install Steps To Test Later

Do not run these now. These are future review notes only.

- Ruflo: inspect GitHub source; inspect package scripts; only then consider `npx ruflo@latest` in a disposable sandbox.
- OpenClaw: inspect repo/docs; identify minimal no-account local mode; run only in sandbox.
- Paperclip: inspect repo/docs; test local dashboard with fake agents and no credentials.
- n8n: test self-hosted local instance with no real credentials and no exposed workflows.
- Browser layer: start with localhost-only Chrome DevTools or CUA screenshot smoke; no account sessions.

## Why None Should Control Live Accounts Yet

- Live accounts introduce irreversible side effects.
- Agent output can contain unsafe or hallucinated instructions.
- Browser/scraping tools can violate platform terms.
- Workflow tools can leak credentials or mutate services.
- Orchestrators can amplify mistakes across multiple agents.

## Required Pre-Integration Gates

- N+3.45 prompt bus/local-worker audit passes.
- Agent lane dashboard/read view exists.
- Active lock/status workflow is used successfully at least once.
- Connector/account policy is implemented as local inventory/checklist.
- Secrets policy is verified.
- Dry-run-only local smoke passes.
- Human approves each install/run/connect step.
