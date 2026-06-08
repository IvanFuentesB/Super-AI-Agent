# Agent System Adapter Context (N+6.36A)

## What this directory contains

| File | Purpose |
|------|---------|
| `agent_system_adapter_status_schema.json` | JSON Schema for adapter output shape |
| `README.md` | This file |

## Selected system: claude_swarm

Primary target for N+6.36A. Selected because it is MOST_READY:
- Pure Python ≥3.11, MIT license
- No Docker, no MCP server, no hooks
- Has a native `--dry-run` flag that shows a decomposed task plan without launching real agents
- Entry point: `claude-swarm = "claude_swarm.cli:main"`

`Runnable` refers to the Ghoti-native metadata adapter and smoke validation.
The external CLI remains blocked pending provider/API audit.

## Candidate external command (not approved)

```
claude-swarm --dry-run "task description"
```

This avoids worker-agent execution, but static source inspection confirmed it
requires `ANTHROPIC_API_KEY`, calls the decomposition model, and writes a
session record. It remains blocked pending a separate provider/API audit.

## Blocked command (NEVER in Ghoti environment)

```
claude-swarm "task description"   # launches real agents
```

## Deferred systems

| System | Reason |
|--------|--------|
| `am_will_swarms` | SECOND_READY; no license confirmed |
| `clawteam` | Ships MCP server — CLI only, MCP must not be enabled |
| `ruflo` | MCP server + hooks daemon; install scripts require review |
| `ecc` | Ships hooks.json (PreToolUse/PreToolWrite); never install |
| `paperclip` | Docker required |
| `hermes_paperclip_adapter` | Needs Hermes + Paperclip reviewed first |

## What is real

- The pinned source was statically inspected in the gitignored sandbox during validation; clone contents are not committed or guaranteed in fresh worktrees.
- Adapter reads `pyproject.toml`, `README.md`, `LICENSE` as text files.
- No claude_swarm code imported or executed.
- No-op plan built from metadata and validated through the N+6.33A dual gate.

## What is NOT live

- No agent launched. No API calls. No real task submitted.
- No hooks, no MCP, no Docker, no browser.
- No third-party code committed or imported.
- No secrets committed.

## Next human approval gate

Before considering `claude-swarm --dry-run` in an isolated environment:
1. Separate Claude profile / isolated sandbox (not the Ghoti working profile)
2. No Ghoti repo access from that environment
3. API key approved for that environment only
4. No real accounts, no external services
5. Separate audited milestone reviewed by human operator
6. Dual-gate green + human approval recorded in milestone doc
