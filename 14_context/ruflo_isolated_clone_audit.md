# RUFLO Isolated Clone Audit

Status label: `isolated_clone_audit / no_install / no_runtime_wiring`
Date: 2026-04-26
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+2.9
Auditor: Claude Code (Sonnet 4.6)

---

## Clone Truth

- Clone path: `21_repos/third_party/evals/ruflo`
- Source URL: https://github.com/ruvnet/ruflo
- Clone command: `git clone --depth 1 https://github.com/ruvnet/ruflo.git`
- Commit hash cloned: `01070ed` — "fix: Tier A blockers #1596, #1567, #1556 (v3.5.80) (#1598)"
- Package version: `3.5.80` (package.json `claude-flow`)
- npm install run: NO
- scripts run: NO
- daemons started: NO
- MCP servers started: NO
- ANTHROPIC_API_KEY configured: NO
- Staged in git: NO (third-party eval area; intentionally excluded)

---

## License

- License: MIT
- Copyright: 2024–2026 ruvnet
- Commercial-use: permitted under MIT
- AGPL implications: none
- Attribution required: yes (copyright notice)

---

## Package Scripts Summary

Scripts found in `package.json`:

| Script | Command summary |
|---|---|
| `dev` | `tsx watch src/index.ts` — TypeScript dev server |
| `build` | `tsc` — TypeScript compile |
| `build:ts` | `cd v3/@claude-flow/cli && npm run build || true` |
| `test` | `vitest` |
| `test:security` | `vitest run v3/__tests__/security/` |
| `security:audit` | `npm audit --audit-level high` |
| `v3:security` | `npm run security:audit && npm run security:test` |

**preinstall / postinstall / prepare scripts:** NONE FOUND in v3.5.80.

This is a significant improvement from the previously reported malicious preinstall scripts in v3.1.0-alpha.55 through v3.5.2. Those scripts have been removed. The absence of install hooks in v3.5.80 reduces but does not eliminate install risk, as npm deps may carry their own hooks.

---

## Repo Size

- File count on clone: ~9,999 files (progress output reached 100% at 9,999)
- Case-sensitive filename collisions detected during checkout (Windows):
  - `.agents/skills/worker-benchmarks/SKILL.md` vs `skill.md`
  - `.agents/skills/worker-integration/SKILL.md` vs `skill.md`
  - Only one version of each lands on Windows filesystem — low risk for our read-only audit, but indicates the repo was developed on Linux/Mac

---

## Install / Preinstall Script Risk

- Preinstall hooks: NONE in top-level package.json (v3.5.80)
- Postinstall hooks: NONE in top-level package.json
- Risk assessment: medium — no hooks at top level, but `npm install` would pull all optional and dev dependencies which may have their own lifecycle scripts. Full dependency tree not audited (requires install).
- Prior history: v3.1.0-alpha.55 through v3.5.2 contained obfuscated preinstall that silently deleted directories. Remediated by removal, with no maintainer explanation. Trust remains conditional.

---

## MCP / Tool-Description Injection Risk

- MCP tools declared: 314 (per CLAUDE.md documentation in the repo)
- Injection risk: HIGH — prior confirmed incident (Issue #1375): prompt injection via MCP tool descriptions directed Claude to add repo owner as contributor without user consent. Remediation claimed but not independently audited.
- CLAUDE.md in the cloned repo aggressively configures Claude Code behavior (swarm orchestration, auto-spawn agents, run npm commands). This CLAUDE.md was loaded into our session via system-reminder — the instructions were received but evaluated and not followed, as they are from a third-party repo and outside our repo root task scope.

---

## API Key / Account Requirements

- ANTHROPIC_API_KEY: REQUIRED — explicitly listed in CLAUDE.md and docker env config
- OPENAI_API_KEY: OPTIONAL — listed for dual-mode Codex collaboration
- Paid: YES — every agent call consumes metered Anthropic API credits; RUFLO wraps Claude Code
- Local-only feasibility: NO — requires active Anthropic API key for agent execution
- PINATA credentials (IPFS plugin registry): OPTIONAL — only for plugin publishing

---

## Windows Compatibility Concerns

- Known issue: PowerShell/nvm integration fails (GitHub Issue #615)
- Case-sensitive file collisions on checkout (Windows NTFS is case-insensitive)
- Docker not required for core (Node.js based), but some sub-features may need it
- Node.js 20+, npm 9+ required
- Local Node/npm availability: confirmed (Node v22.16.0, npm 10.9.2)
- Assessment: partially compatible — core CLI likely works, but nvm/PowerShell integration and file-collision edge cases remain

---

## Dependency Risk Summary (package.json only, no install)

Production dependencies (minimal):
- `semver: ^7.6.0` — well-known, low risk
- `zod: ^3.22.4` — schema validation, low risk

Optional dependencies (not installed):
- `@claude-flow/codex`, `@ruvector/*`, `agentdb`, `agentic-flow` — ruvnet ecosystem; trust unverified independently
- `@claude-flow/plugin-gastown-bridge` — unknown third-party bridge plugin

Dev dependencies (not installed):
- `@openai/codex: ^0.98.0` — OpenAI toolchain
- `tsx`, `typescript`, `eslint`, `vitest` — standard toolchain, low risk

npm audit run: NO — not run; lockfile audit requires install or separate offline analysis.

---

## Verdict

**isolated install candidate** — pending explicit operator approval for a narrow install milestone.

Security history (obfuscated preinstall in prior versions, prompt injection via MCP) means trust has not yet been independently restored by us. The v3.5.80 snapshot appears cleaner, but:
- 314 MCP tools = very large attack surface
- CLAUDE.md in the cloned repo attempts to configure Claude Code behavior aggressively
- Full dependency tree (npm audit) not yet verified
- Windows compatibility partially unverified

---

## Exact Next Safe Step

If operator explicitly approves in terminal:
```
npm install --no-scripts --ignore-scripts
npm audit
```

Then inspect MCP tool descriptors for any remaining injection patterns before running any agent or MCP server.

Do NOT run `npx claude-flow@v3alpha init` or `npx claude-flow@v3alpha daemon start` until full source + MCP descriptor audit is complete and operator approves.
