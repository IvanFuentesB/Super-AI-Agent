# Super-AI-Agent

Local-first, approval-gated AI agent framework with durable memory, context handoff, logging, rollback, and future multi-model orchestration.

## Current Purpose

This repo is the foundation workspace for building a modular personal and business agent system with local-first operation where practical, approval gates before risky actions, compact durable memory, context handoff for long chats, logging and rollback, and future multi-model routing across local and cloud models.

## Current Stack

- Windows
- Ollama
- Gemma local
- Continue as the current local control layer
- Codex as the execution layer
- Git + GitHub
- Notion not integrated yet

## Current Status

- Workspace initialized
- Continue config works
- Workspace rules are active
- Handoff files exist under `14_context`
- Private GitHub repo exists
- Claw Code is only a temporary reference

## Repo Structure

- `13_prompts`: reusable prompts, including handoff prompts
- `14_context`: durable project state, decisions, open questions, and handoff files
- `20_agents`: agent templates, shared patterns, and future agent-specific memory
- `21_repos`: repo references, core repos, and later external evaluations
- `23_configs`: local configuration files and setup state

## Working Method

- Use summarized context files instead of relying on long chats
- Keep changes small and reversible
- Require approval for risky actions

## Next Priorities

- Refine Continue workflow
- Define approval system
- Improve memory architecture
- Evaluate future model routing
- Add Notion later
