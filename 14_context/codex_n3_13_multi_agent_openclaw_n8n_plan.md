# Codex N+3.13 Multi-Agent / OpenClaw / n8n Plan

Status: codex_parallel_audit / architecture_plan_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## 1. Goal

Build many specialized agents without making Ghoti chaotic. The safe pattern is a small registry of named agents, compact shared memory, explicit tool permissions, approval gates, and visible status. External systems such as OpenClaw and n8n should remain references or workflow glue until Ghoti has a proven local routing and approval model.

## 2. Agent Roles To Define First

| Agent | First responsibility | Default boundary |
| --- | --- | --- |
| Router Agent | Classify task difficulty, risk, and suggested brain | Preview-only |
| Local Brain Worker | Summaries, compact notes, TODO extraction | Gemma/Ollama after smoke |
| Research Agent | Public/source-backed research plans | No scraping or live accounts |
| Coding Agent | Repo-local implementation tasks | Claude Code/Codex, approval-aware |
| Code Review Agent | Find regressions, risks, missing tests | Codex/Claude |
| Documentation Agent | Update docs, handoffs, finish-line summaries | Codex/Claude/Gemma draft |
| Memory Curator Agent | Compact state, vault summaries, shared memory | Local files only |
| Business Workflow Agent | Legal/TOS-aware market research drafts | Human review, no outreach |
| Browser/CUA Operator Agent | Future approved observe/action proposals | No runtime execution yet |
| Safety/Approval Gate Agent | Check policy, approval phrases, risk labels | Human remains final gate |
| Notification/Workflow Agent | Future local notifications and queue triggers | n8n only after approval |

## 3. Default Brain Per Agent

| Work type | Default brain/tool |
| --- | --- |
| Easy local text work | Gemma/Ollama after model smoke |
| Hard repo edits | Claude Code |
| Parallel audits, skeptical reviews, plan verification | Codex |
| High-level strategy, roadmap, cross-milestone coordination | ChatGPT/Claude/Gemini-style council later |
| Browser/CUA operation | Not enabled yet; future ActionIntent + approval + adapter only |

## 4. OpenClaw-Style Architecture Idea

OpenClaw should remain a reference until Ghoti's own local operator core is stable. Useful patterns to borrow:

- Task decomposition into small specialist jobs.
- Specialist agents with narrow tool permissions.
- Shared compact memory rather than repeated giant prompts.
- Operator-visible status dashboard.
- Approval inbox before risky actions.
- Handoff files that allow fresh-session resumability.
- Per-agent output artifacts and short summaries.
- Clear separation between reasoning, proposing, approving, and executing.

Do not wire OpenClaw as a runtime dependency yet. It should be evaluated as architecture inspiration and possibly a future control surface after security, account, and local-sandbox boundaries are understood.

## 5. n8n Integration Idea

n8n can become boring workflow glue, not Ghoti's decision maker.

- n8n handles triggers, webhooks, scheduled checks, and notifications.
- Ghoti remains the decision, approval, operator, and audit layer.
- n8n should send proposed tasks into Ghoti's queue, not execute risky actions directly.
- n8n workflows should default to local-only and no credentials.
- Live account, posting, outreach, paid API, or credential workflows require explicit later approval.

## 6. Safe First n8n Candidates

- Local webhook that adds a task proposal to a Ghoti queue.
- Scheduled health check of dashboard, Docker, Ollama, and Screenpipe status.
- Local notification when Docker/Ollama/dashboard status changes.
- File watcher for compact `14_context` updates.
- Daily compact summary generation from local markdown files.
- Manual "send to Ghoti" workflow that creates a draft task only.

## 7. Unsafe / Later n8n Candidates

- Sending emails or messages.
- Posting content.
- Scraping sites.
- Paid API workflows.
- Live business outreach.
- Anything with credentials, account sessions, or secrets.
- Purchases, trades, filings, permit/legal/tax submissions.
- Browser/CUA actions beyond observe-only proposals.

## 8. Proposed Folder / Config Structure

These are future docs/configs, not runtime wiring:

- `20_agents/agent_registry.example.json`
- `23_configs/brain_routing_policy.example.json`
- `17_integrations/n8n_plan.md`
- `02_automation/workflow_intake_plan.md`

Suggested registry shape:

```json
{
  "agent_id": "local-brain-worker",
  "status": "planned",
  "default_brain": "gemma_local_after_smoke",
  "allowed_tools": ["read_local_docs", "write_draft_artifact"],
  "forbidden_tools": ["external_api", "browser_action", "git_push", "docker_run"],
  "approval_required_for": ["writes", "external_actions", "installs"],
  "runtime_wiring_truth": "not_runtime_wired"
}
```

## 9. Verdict

Next milestone should create registry/config docs only. Do not install n8n yet. Do not wire OpenClaw. Do not create autonomous dispatch. The useful next step is to define the agent registry and preview-only brain routing so Ghoti can decide cheaply before executing safely.
