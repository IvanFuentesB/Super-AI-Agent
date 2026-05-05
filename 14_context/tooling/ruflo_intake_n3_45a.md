# Ruflo Isolated Intake — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## Clone Path

```
21_repos/third_party/evals/ruflo
```

Already present from a prior intake. No re-clone needed.

## Commit Hash Inspected

```
01070ede81fa6fbae93d01c347bec1af5d6c17f0
```

Latest commit message: `fix: Tier A blockers #1596, #1567, #1556 (v3.5.80) (#1598)`

## Package Manager Detected

**npm** — `package-lock.json` present. No `pnpm-lock.yaml` or `yarn.lock`.

`packageManager` field in `package.json` is empty.

## Package Identity

```json
{
  "name": "claude-flow",
  "version": "3.5.80",
  "description": "Ruflo - Enterprise AI agent orchestration for Claude Code. Deploy 60+ specialized agents in coordinated swarms with self-learning, fault-tolerant consensus, vector memory, and MCP integration"
}
```

Note: The npm package is `claude-flow` even though the project is now branded as "Ruflo". The CLI binary is likely still `claude-flow` or `ruflo` depending on install.

## Scripts Detected

From `package.json`:
```
dev, build, build:ts, test, test:ui, test:security, lint, security:audit,
security:fix, security:test, v3:domains, v3:swarm
```

## Postinstall Script

**None** — no `postinstall` key in scripts. Safe to `npm install --ignore-scripts` without risk of automatic execution.

## Architecture Summary

Ruflo is a multi-agent orchestration framework that wraps Claude Code:
- Routes tasks to 60+ specialized agents in configurable swarms
- Uses topologies: mesh, hierarchical, ring, star
- Consensus mechanisms: Raft, BFT, Gossip
- Self-learning Q-Learning router
- MCP server integration
- WASM/Rust-powered policy engine and embeddings layer
- MIT License

## Risk Review

| Risk | Level | Notes |
|------|-------|-------|
| Postinstall script | None | No postinstall in package.json |
| Live account wiring | Medium | Framework is designed to wrap Claude Code — requires API keys to run |
| MCP server launch | Medium | Starts an MCP server when run; do not run server in this intake |
| External API calls | Medium | Requires Claude API key env var to operate |
| Credential in repo | Low | No env examples with real secrets found |
| Dependency footprint | Medium | Node.js project, large dependency tree — install only in eval area |

## Install Readiness

**Dependency install: SKIPPED this milestone.**

Reason: Ruflo requires a Claude API key and live network calls to operate. Installing dependencies without running the server is safe, but the resulting `node_modules/` would be large (~100MB+) and should not be staged in the main repo. A separate explicit approval step is required before running `npm install --ignore-scripts`.

When approved, the safe install command is:
```bash
cd 21_repos/third_party/evals/ruflo
npm install --ignore-scripts
```

Do NOT run:
```bash
npm run dev
npm run build
npm start
```

## No Runtime Wiring

- Ruflo is NOT connected to Claude Code, Codex, GitHub, MCP, or any live accounts.
- No API keys added.
- No MCP server launched.
- No orchestration flows configured.
- This intake is source-review only.

## Next Safe Step

1. Get explicit approval: "APPROVE Ruflo npm install --ignore-scripts in eval area"
2. Run: `cd 21_repos/third_party/evals/ruflo && npm install --ignore-scripts`
3. Inspect built artifacts.
4. Create a Ghoti-isolated config (no real API keys) to understand config schema.
5. Only after a full Codex audit of the integration surface, consider wiring Ruflo as an orchestrator.

## Why Ruflo Is a Candidate But Not Yet Trusted Controller

Ruflo/claude-flow is a powerful orchestration layer that coordinates multiple Claude Code sessions and MCP tools. It is a **candidate** because:
- It understands the Claude Code tool model natively
- It supports swarm topologies that map to Ghoti's multi-agent goals
- It has a documented MCP integration path

It is **not yet a trusted controller** because:
- It has never been audited for Ghoti's specific safety boundaries
- It requires live Claude API access — any misconfiguration could trigger unintended model calls
- Its Q-Learning router and self-learning capabilities may make decisions that bypass Ghoti's approval gates
- The MCP server it launches could expose local tools to unintended callers
- A full Codex source-check audit is required before any live wiring

Status: `planning_only — not wired — awaiting Codex audit and explicit user approval`
