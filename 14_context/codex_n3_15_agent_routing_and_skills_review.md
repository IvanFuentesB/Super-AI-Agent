# Codex N+3.15 Agent Routing and Skills Review

Status: codex_parallel_audit / routing_review_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Current Routing Truth

N+3.14 introduced a local Gemma router preview and worker-card registry. The router is still preview-only and not automatic. The registry exists as markdown planning artifacts under:

- `14_context/agent_registry/`

Observed registry files:

- `active_worker_cards_n3_14.md`
- `agent_routing_policy_n3_14.md`
- `worker_card_template.md`

This is the right shape: many agents should share explicit worker cards before any external control plane coordinates them.

## Worker Cards

Every parallel Claude/Codex/Gemma/Paperclip/OpenClaw worker should have:

- Worker ID
- Tool/model
- Task
- Allowed files
- Forbidden files
- Expected output
- Status
- Handoff file
- Commit hash or artifact path

Worker cards reduce hidden-state chaos and make parallel execution safer. They also map naturally onto Paperclip concepts later.

## Skills Should Be Tracked Intentionally

Installed skills should be treated as operator-side capabilities, not automatic Ghoti runtime wiring.

Recommended tracking fields:

- skill name
- owner/tool surface (Codex app, Claude Code, repo-local skill, future Paperclip agent)
- intended use
- forbidden use
- required validation
- whether it is runtime-wired

Rules:

- Use skills intentionally when they match the milestone.
- Do not assume a skill is available inside Ghoti runtime.
- Do not stage `.claude/skills/` unless a milestone explicitly says so.
- Do not use skills to bypass approval gates or provider limits.

## Paperclip

Paperclip should remain a future control-plane candidate:

- useful for many agents
- useful for task registry/org chart/budgets/governance
- useful for Claude/Codex/OpenClaw adapter concepts
- not installed yet
- not runtime-wired
- not allowed to control host agents yet

Near-term use: architecture reference and mapping target for worker cards.

## OpenClaw

OpenClaw should remain a future worker/channel candidate:

- useful for personal assistant/channel surface later
- useful for skills and channel integration ideas
- higher risk if exposed or given broad credentials
- not runtime-wired
- not public
- no live credentials

OpenClaw should be supervised by Ghoti/Paperclip-style controls later, not used as the main safety layer.

## n8n

n8n should remain deterministic workflow rails later:

- scheduled checks
- local webhooks
- file watcher triggers
- notifications
- daily summaries

Do not install n8n yet. Do not use n8n for live sends, posting, scraping, purchases, legal/tax filing, credentials, or external account actions until a separate approval-gated workflow design exists.

## Many-Agent Memory Sharing

First memory-sharing layer should be markdown artifacts:

- `14_context/`
- `14_context/obsidian_vault/`
- `14_context/agent_registry/`
- `05_logs/local_brain_runs/`
- `05_logs/multi_agent_runs/`

Do not jump to a vector DB/RAG system yet. Markdown artifacts are inspectable, diffable, and safe for human review.

## Recommended N+3.15 Skill/Routing Update

Claude should update policy/config to show:

- `compress_context` is allowed only for repo-local text files.
- outputs are artifacts only.
- model output is never executed.
- route remains preview/manual until explicitly promoted.
- skills/plugins are operator surfaces, not runtime guarantees.

## Verdict

Ghoti should keep the next step boring and useful: use local Gemma to compress context into artifacts, then use worker cards to decide who reviews or applies the result. Paperclip/OpenClaw/n8n stay future layers, not active runtime systems.
