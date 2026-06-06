# Claude Code: Skills vs Agents vs Commands vs Hooks (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: guidance-only static notes. Nothing here is wired to runtime or granted
execution permissions for Ghoti.

The four building blocks of Claude Code are easy to confuse. They are different
mechanisms with different triggers, scopes, and risk.

## 1. Skills

- **What:** a folder with a `SKILL.md` (name + description frontmatter, then
  instructions) plus optional bundled scripts/resources. The model reads the short
  description and **chooses** to load the full skill when relevant (progressive
  disclosure).
- **Trigger:** model-invoked (the agent decides), surfaced through a Skill tool.
- **Scope:** shapes how the current agent works - adds instructions/knowledge/recipes.
- **Risk:** a skill is *instructions*, not new permissions. Risk comes only from any
  scripts it bundles and from what it tells the agent to do.
- **Ghoti use:** `goal`, `ultraplan`, `ghoti-status`, `prompt-bus` (repo playbooks,
  manual) and `karpathy-guidelines` (external guidance). All guidance/manual.

## 2. Agents (subagents)

- **What:** a separate worker with its **own context window**, system prompt, and tool
  set, spawned to handle a sub-task and return a final result.
- **Trigger:** invoked by the main agent (a Task/Agent tool) for fan-out, parallelism, or
  isolation; can also be predefined agent types.
- **Scope:** an independent unit of work; it does not share the parent's live context
  except through the prompt it is given and the result it returns.
- **Risk:** inherits whatever tools it is granted; parallel agents can touch many files.
- **Ghoti use:** the *roles* ("Claude builder", "Codex auditor") are modeled this way,
  but Ghoti runs them **manually, one agent per task on its own branch/worktree** - it
  does not auto-spawn live agents yet. This is exactly the swarm-launcher target that
  stays gated.

## 3. Commands (slash commands)

- **What:** a named prompt template (markdown) stored in a commands directory or shipped
  by a plugin; can take arguments and expand into a full prompt.
- **Trigger:** user-invoked (a person types `/name`).
- **Scope:** injects a prepared prompt into the conversation; it is a convenience, not a
  new capability.
- **Risk:** low by itself (it is a prompt), but a command can *instruct* risky actions, so
  the contents still get reviewed.
- **Ghoti use:** the repo playbooks are exposed as slash-style commands and run manually.

## 4. Hooks

- **What:** shell commands wired to lifecycle events (for example before/after a tool
  runs, on session start/stop) via settings.
- **Trigger:** **event-triggered automation** - they fire deterministically, not by model
  choice.
- **Scope:** can run arbitrary code with the user's permissions; can block or modify tool
  calls.
- **Risk:** **highest of the four.** A hook executes code, so an unaudited hook could
  paste into apps, push branches, install packages, or take live actions.
- **Ghoti use:** **NOT enabled as executable.** Only the *hook-as-validator/report-writer*
  idea is recorded (from the N+6.19A ECC plan). Any executable hook needs a separate,
  audited, human-approved milestone.

## Quick comparison

| | Trigger | Grants new permissions? | Executes code? | Ghoti status |
|---|---|---|---|---|
| Skill | model chooses | no | only via bundled scripts | guidance/manual |
| Agent | parent invokes | inherits granted tools | yes, within its tools | manual, role-modeled |
| Command | user types | no | no (it is a prompt) | manual |
| Hook | lifecycle event | n/a (runs as user) | **yes** | NOT enabled |

## Why this matters for swarms

A real Ghoti swarm launcher is the **Agent** mechanism turned on: a coordinator that
spawns Claude/Codex/local-worker subagents on tasks. That is powerful and therefore
gated. Skills/commands shape those agents safely; hooks are the part most likely to take
unsafe live actions, so hooks stay off until separately audited.
