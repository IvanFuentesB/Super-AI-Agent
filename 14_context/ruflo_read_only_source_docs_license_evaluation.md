# RUFLO Read-Only Source / Docs / License Evaluation

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: source_docs_license_evaluated / research_only / not_runtime_wired

## Basic Identity

- Repo/tool name: RUFLO / RuFlo
- Source URL: https://github.com/ruvnet/ruflo
- Raw README checked: https://raw.githubusercontent.com/ruvnet/ruflo/main/README.md
- Raw package checked: https://raw.githubusercontent.com/ruvnet/ruflo/main/package.json
- Raw license checked: https://raw.githubusercontent.com/ruvnet/ruflo/main/LICENSE
- Raw security policy checked: https://raw.githubusercontent.com/ruvnet/ruflo/main/SECURITY.md
- Raw agent guide checked: https://raw.githubusercontent.com/ruvnet/ruflo/main/AGENTS.md
- Public security concern issue checked: https://github.com/ruvnet/ruflo/issues/1375
- Public remediation issue checked: https://github.com/ruvnet/ruflo/issues/1384
- Public Windows compatibility issue checked: https://github.com/ruvnet/ruflo/issues/615
- Vendor / owner: `ruvnet`
- Category: multi-agent orchestration / Claude Code and Codex-adjacent tooling
- Evaluation method: read-only web/source/docs/license review; no clone, install, run, account connection, or runtime wiring

## Claimed Purpose

RUFLO presents itself as an enterprise AI orchestration platform for Claude Code and multi-agent systems. Its README describes a CLI/MCP-driven orchestration layer with swarms, agent roles, memory, learning/routing, provider support, hooks, background workers, and Claude Code/Codex integration claims.

The GitHub repo page describes it as an agent orchestration platform for Claude with multi-agent swarms, distributed swarm intelligence, RAG integration, and Claude Code / Codex integration.

## Real Purpose After Inspection

RUFLO appears to be a large Node/TypeScript-first orchestration package published under the package name `claude-flow`, with RUFLO branding layered over or alongside Claude Flow naming.

Important observed details:

- Main package name in `package.json`: `claude-flow`.
- Current package version observed: `3.5.80`.
- Node engine requirement: `>=20.0.0`.
- Primary binary: `claude-flow`.
- License field: `MIT`.
- Optional dependencies include Codex, plugin bridge, vector/router components, AgentDB, and agentic-flow packages.
- Dev dependencies include `@openai/codex`.
- The install script supports global, npx, MCP setup, doctor, and init modes.
- The install script can attempt to install Claude Code CLI if missing, which is too invasive for Ghoti without explicit approval.

## License / Ownership

- License: MIT according to GitHub repository page, raw `LICENSE`, and `package.json`.
- Commercial-use clarity: MIT generally permits use, modification, distribution, sublicensing, and selling copies, subject to retaining copyright/license notice.
- Copyleft/AGPL implications: none found in the checked top-level license.
- Unknowns: optional dependencies and downstream plugins may have their own licenses and must be checked separately before install or integration.

## Security / Operational Risk

RUFLO has a large operational surface for Ghoti:

- MCP server capability.
- CLI commands.
- Swarms/agents/tasks.
- Memory storage and retrieval.
- Hooks and background workers.
- Provider routing claims.
- GitHub/repo automation claims.
- Installer that can modify local tooling and Claude MCP config.
- Potential interaction with Claude Code, Codex, and API/provider credentials.

Top risks:

- Broad filesystem access if run inside the repo without sandboxing.
- Hidden or semi-hidden background hooks/workers if installed in full mode.
- Account/API-key exposure if provider integrations are enabled.
- Overclaiming autonomy or treating orchestration records as actual safe execution.
- Usage-limit/cap-bypass framing in public docs must not be adopted by Ghoti.
- MCP/tool registration could expand the action surface before approval gates are designed.
- Public GitHub issue #1375 reports serious concerns around MCP prompt injection, an obfuscated preinstall script in older versions, persistence/uninstall problems, and unresolved security items. These claims should be treated as risk signals requiring source-level audit before any install.
- Public GitHub issue #1384 is a remediation overview for v3.5.40, so there is evidence the project responded to at least some security concerns, but remediation claims were not verified locally.
- Public GitHub issue #615 indicates Windows PowerShell / Node environment compatibility may need specific testing.

## Runtime Requirements

- Node/npm: required; Node >=20 is declared.
- Python: not confirmed as a hard requirement from the checked package root, though repo language mix includes Python.
- Rust: README claims WASM/Rust-powered components, and optional dependencies include RuVector packages. Direct Rust install requirement was not proven from the checked package root.
- Docker: not proven from checked root docs.
- Browser: not proven as required for base install.
- Background services: full setup can involve MCP and daemon/worker-style components according to docs.
- Windows compatibility: not proven. Installer is bash-based and curl-pipe oriented; Windows use likely needs npx/npm/PowerShell-specific review before any install.
- Windows risk note: a public issue exists for Windows PowerShell compatibility, so Ghoti should not assume smooth Windows operation until an isolated smoke test proves it.

## Account / Auth / Secrets

Potentially relevant:

- Claude Code CLI / Claude account.
- Codex CLI / Codex app.
- LLM provider keys for Anthropic/OpenAI/Google/etc. if provider routing is used.
- GitHub credentials if GitHub automation features are enabled.
- Local memory/database files.

No accounts or secrets were used in this evaluation.

## Local-Only Feasibility

Potentially feasible only after a carefully isolated follow-up:

- Read-only docs/license review: already done.
- Isolated clone without install: possible later with explicit approval.
- Dependency audit before install: required.
- Local npx smoke test: possible later, but still installs/caches packages and must be approved.
- Full MCP/daemon/init setup: not safe yet for Ghoti.

## Approval Gates Needed Before Any Future RUFLO Use

- Explicit clone approval.
- Explicit dependency/install approval.
- Explicit approval before `curl | bash`, `npm install -g`, `npx ruflo`, `npx claude-flow`, MCP registration, doctor, init, daemon, or hooks.
- Explicit approval before connecting Claude, Codex, GitHub, Ollama, OpenAI, Anthropic, Google, or any account/API key.
- Explicit approval before any filesystem writes outside an isolated evaluation folder.
- Explicit approval before any browser, shell, GitHub, PR, issue, or external network automation.

## Test Plan For A Future Isolated Milestone

1. Read current README, package, license, and security docs again.
2. Fill a fresh evaluation template with exact version/date.
3. If approved, clone to a clearly named isolated evaluation folder.
4. Inspect package manifests and install scripts before running anything.
5. Run dependency/license audit without executing project scripts if possible.
6. Test Windows compatibility in no-runtime or dry-run mode.
7. Do not run `init`, `doctor --fix`, MCP setup, daemon, hooks, or provider configuration in the first clone milestone.
8. Record generated files and ensure none are staged unless explicitly intended.

## Decision

- Clone/install decision: `not_decided`
- Integration decision: `research_only / not_runtime_wired`
- Final verdict: `research only` now; `use soon` only after isolated clone/dependency audit proves it is manageable.
- Required next milestone: isolated read-only clone/dependency audit only if the operator explicitly approves.

## Ghoti Fit

RUFLO remains strategically interesting for Ghoti because it overlaps with the desired future shape: many single-purpose agents, shared local memory, role-scoped coordination, and manual handoff discipline.

However, the surface area is large enough that it should not be wired directly into Ghoti yet. The safest near-term value is to mine architecture patterns, not run it as an operator.

## Current Status

- Source/docs/license evaluated: YES.
- Cloned: NO.
- Installed: NO.
- Run locally: NO.
- Runtime wired: NO.
- Approval gates changed: NO.
- External services connected: NO.

## Sources Used

- https://github.com/ruvnet/ruflo
- https://raw.githubusercontent.com/ruvnet/ruflo/main/README.md
- https://raw.githubusercontent.com/ruvnet/ruflo/main/package.json
- https://raw.githubusercontent.com/ruvnet/ruflo/main/LICENSE
- https://raw.githubusercontent.com/ruvnet/ruflo/main/SECURITY.md
- https://raw.githubusercontent.com/ruvnet/ruflo/main/AGENTS.md
- https://raw.githubusercontent.com/ruvnet/ruflo/main/scripts/install.sh
- https://github.com/ruvnet/ruflo/issues/1375
- https://github.com/ruvnet/ruflo/issues/1384
- https://github.com/ruvnet/ruflo/issues/615
