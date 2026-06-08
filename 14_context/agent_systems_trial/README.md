# Agent Systems Trial Context (N+6.35A)

## What this directory contains

| File | Purpose |
|------|---------|
| `agent_systems_inventory_n6_35a.json` | Static inspection inventory for 7 plug-and-play agent repos |
| `README.md` | This file |

## What is real

- 7 repos cloned into `21_repos/third_party_runtime_sandbox/` (gitignored).
- Static inspection of each repo's LICENSE, README, entrypoints, install surface.
- `ghoti_agent_systems_trial.py` reads the inventory and plans — but **never runs** third-party code.

## What is NOT live

- No third-party agent, swarm, or automation has been launched.
- No hooks are installed or enabled.
- No Docker, MCP server, VM, or remote desktop is running.
- No network calls to external APIs. No secrets committed.
- No CUA file from N+6.34A has been edited.

## Repo verdicts

| Repo | Verdict | Reason |
|------|---------|--------|
| `claude_swarm` | MOST_READY | Pure Python, claude-agent-sdk, no Docker/MCP/hooks |
| `am_will_swarms` | SECOND_READY | Skills only; no install; no license confirmed |
| `clawteam` | CLI_ONLY | Ships MCP server — use CLI only |
| `ruflo` | ADAPT_LATER | MCP + hooks daemon; install-script review required |
| `ecc` | GOVERNANCE_PATTERNS_ONLY | Ships hooks.json + install.sh; never install |
| `paperclip` | ADAPT_LATER | Docker required |
| `hermes_paperclip_adapter` | ADAPT_LATER | Needs Hermes + Paperclip reviewed first |

## Why these repos, why this order

CUA was trialled first (N+6.34A — isolated computer-use engine).
N+6.35A adds the remaining agent/swarm systems. Trial order follows the real_repo_trial_plan_n6_33a.md:
claude_swarm and am_will_swarms are Python-native and lowest-risk; ruflo/ecc/paperclip
require more install-script review or blocked capabilities (hooks, docker, MCP).

## Next step

A separate audited milestone for each promotion toward a live engine trial.
Every live trial requires its own audited milestone, human approval, and dual-gate green.
