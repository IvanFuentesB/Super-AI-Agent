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

## Safe command (Ghoti-approved dry-run)

```
claude-swarm --dry-run "task description"
```

Requires: install in an isolated profile/scratch environment (not the Ghoti working profile).
Does not launch real agents. Shows the decomposed task plan only.

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

- `claude_swarm` repo cloned into gitignored sandbox.
- Adapter reads `pyproject.toml`, `README.md`, `LICENSE` as text files.
- No claude_swarm code imported or executed.
- No-op plan built from metadata and validated through the N+6.33A dual gate.

## What is NOT live

- No agent launched. No API calls. No real task submitted.
- No hooks, no MCP, no Docker, no browser.
- No third-party code committed or imported.
- No secrets committed.

## Next human approval gate

To run `claude-swarm --dry-run` in a live isolated environment:
1. Separate Claude profile / isolated sandbox (not the Ghoti working profile)
2. No Ghoti repo access from that environment
3. API key approved for that environment only
4. No real accounts, no external services
5. Separate audited milestone reviewed by human operator
6. Dual-gate green + human approval recorded in milestone doc
