# Memory Architecture

## Goal

Keep memory compact, low-bloat, easy to hand off, and usable across Continue, Codex, Gemma local, and future agents.

## Memory Layers

### 1. Global / Workspace Memory

Purpose:
- stable facts about the whole project

Primary location:
- `14_context/`

Examples:
- `current_state.md`
- `next_actions.md`
- `decisions.md`
- `open_questions.md`
- `recent_failures.md`

### 2. Project Memory

Purpose:
- memory specific to a project or subsystem

Suggested location:
- `01_projects/<project_name>/memory/`

Contents:
- `summary.md`
- `decisions.md`
- `open_questions.md`
- `failures.md`

### 3. Agent / Automation Memory

Purpose:
- narrow memory for one specialized agent or automation

Suggested location:
- `20_agents/<agent_name>/memory/`
- or `02_automation/<automation_name>/memory/`

Contents:
- `role.md`
- `state.md`
- `constraints.md`
- `recent_runs.md`

## Rules

- prefer summaries over raw logs
- avoid endless append-only memory
- keep memory scoped
- archive stale memory
- handoff files are the source of truth for chat resets

## Update Pattern

- do work
- summarize what changed
- update the relevant memory layer
- then start a fresh chat/session if needed

## Current Default

- for now, `14_context` is the primary active memory layer
- deeper per-project and per-agent memory will be added as needed
