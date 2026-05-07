# Ruflo Catalog — 20260506T200137Z

- **Ruflo dir**: 21_repos\third_party\evals\ruflo
- **Runtime launch**: NO — catalog is read-only metadata only

## Package
- **Name**: claude-flow
- **Version**: 3.5.80
- **Description**: Ruflo - Enterprise AI agent orchestration for Claude Code. Deploy 60+ specialized agents in coordinated swarms with self-learning, fault-tolerant consensus, vector memory, and MCP integration
- **Scripts**: ['dev', 'build', 'build:ts', 'test', 'test:ui', 'test:security', 'lint', 'security:audit', 'security:fix', 'security:test', 'v3:domains', 'v3:swarm', 'v3:security']
- **Dependencies**: ['semver', 'zod']

## README.md
```
# 🌊 RuFlo v3.5: Enterprise AI Orchestration Platform

<div align="center">

![Ruflo Banner](ruflo/assets/ruflo-small.jpeg)



[![GitHub Project of the Day](https://img.shields.io/badge/GitHub-Project%20of%20the%20Day-ff6600?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ruvnet/claude-flow)

[![Star on GitHub](https://img.shields.io/github/stars/ruvnet/claude-flow?style=for-the-badge&logo=github&color=gold)](https://github.com/ruvnet/claude-flow)
[![Monthly Downloads](https://img.shields.io/npm/dm/claude-flow?style=for-the-badge&logo=npm&color=blue&label=Monthly%20Downloads)](https://www.npmjs.com/package/claude-flow)
[![Total Downloads](https://img.shields.io/npm/dt/claude-flow?style=for-the-badge&logo=npm&color=cyan&label=Total%20Downloads)](https://www.npmjs.com/package/claude-flow)
[![ruv.io](https://img.shields.io/badge/ruv.io-AI%20Platform-green?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9
```

## CLAUDE.md
```
# Claude Code Configuration - Ruflo v3.5

> **Ruflo v3.5** (2026-04-07) — Stable release with verified capabilities.
> 6,000+ commits, 314 MCP tools, 16 agent roles + custom types, 19 AgentDB controllers.
> Packages: `@claude-flow/cli@3.5.65`, `claude-flow@3.5.65`, `ruflo@3.5.65`

## Behavioral Rules (Always Enforced)

- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested
- NEVER save working files, text/mds, or tests to the root folder
- Never continuously check status after spawning a swarm — wait for results
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files

## File Organization

- NEVER save to root folder — use the directories below
- Use `/src` for source code files
- Use `/tests` for test files
- Use `/
```

## CHANGELOG.md
```
# Changelog

All notable changes to the Ruflo project (formerly Claude Flow) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.0] - 2026-02-27

### Ruflo v3.5 — First Major Stable Release

This release marks the official rebranding from **Claude Flow** to **Ruflo** and represents the first major stable release after 5,800+ commits, 55 alpha iterations, and 10 months of development.

### Highlights

- **Rebranding**: Claude Flow → Ruflo across all packages (`@claude-flow/cli`, `claude-flow`, `ruflo`)
- **agentic-flow v3.0.0-alpha.1 Integration**: Full deep integration with 10 subpath exports (ReasoningBank, Router, Orchestration, Agent Booster, SDK, Security, QUIC transport)
- **AgentDB v3.0.0-alpha.9**: 8 new controllers (HierarchicalMemory, MemoryConsolidation, SemanticRouter, GNNService, RVFOptimizer, MutationGuard, AttestationLog, Guar
```
