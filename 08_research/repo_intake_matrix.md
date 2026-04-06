# Repo Intake Matrix

## browser-use/browser-use

- local clone path: `21_repos/third_party/browser-use`
- category: browser automation framework
- why it matters: useful reference for owned-account browser workflows and observation loops
- likely role: candidate browser executor or wrapper reference
- risk/cost notes: browser dependency overhead and approval-boundary design matter
- next action: inspect Windows fit and approval-gated execution patterns

## browser-use/web-ui

- local clone path: `21_repos/third_party/browser-use-web-ui`
- category: browser automation UI layer
- why it matters: useful reference for a local dashboard or review surface
- likely role: optional control-plane reference, not core runtime
- risk/cost notes: web UI stack adds surface area fast
- next action: inspect only for operator workflow ideas, not direct adoption

## browserbase/stagehand

- local clone path: `21_repos/third_party/stagehand`
- category: browser control primitives
- why it matters: useful for later browser/app executor research
- likely role: structured browser action reference
- risk/cost notes: may assume cloud/browser tooling outside current scope
- next action: inspect the action model and observation loop fit

## OpenHands/OpenHands

- local clone path: `21_repos/third_party/openhands`
- category: agent harness
- why it matters: good reference for execution loops and agent shell patterns
- likely role: comparison material, not immediate core
- risk/cost notes: large surface area and heavier operational model
- next action: inspect architecture only, do not pull it into core

## aider-ai/aider

- local clone path: `21_repos/third_party/aider`
- category: coding assistant CLI
- why it matters: strong reference for Git-aware coding workflow patterns
- likely role: compare commit, prompt, and coding loop ergonomics
- risk/cost notes: provider assumptions and interactive CLI style may not match this control plane
- next action: inspect workflow patterns and safe Git conventions

## n8n-io/n8n

- local clone path: `21_repos/third_party/n8n`
- category: workflow orchestration platform
- why it matters: useful reference for workflow modeling and future integration bridges
- likely role: optional orchestration reference later
- risk/cost notes: large Node platform, not a small core fit
- next action: inspect how much is reusable conceptually versus too heavy

## logto-io/logto

- local clone path: `21_repos/third_party/logto`
- category: auth and identity platform
- why it matters: useful reference for approved-user auth later
- likely role: auth-model reference, not a near-term dependency
- risk/cost notes: significant infra weight for a system that is still only-me-first
- next action: inspect role separation and audit concepts only

## modelcontextprotocol/servers

- local clone path: `21_repos/third_party/mcp-servers`
- category: integration and tool servers
- why it matters: useful reference set for future GitHub, Notion, browser, and data adapters
- likely role: adapter intake library and comparison set
- risk/cost notes: breadth is high, quality and fit vary by server
- next action: inspect server patterns selectively instead of treating the repo as one unit

## santifer/career-ops

- local clone path: `21_repos/third_party/career-ops`
- category: career and internship ops system
- why it matters: strong reference for fit scoring, tailored CV generation, tracking, and human-in-the-loop career workflows
- likely role: reference for internship and job-search operating patterns, not core runtime code
- risk/cost notes: Claude-specific assumptions, Playwright-heavy flows, and direct application patterns should not be copied blindly
- next action: extract scoring, tracker, and review ideas without inheriting the whole stack

## santifer/cv-santiago

- local clone path: `21_repos/third_party/cv-santiago`
- category: portfolio and case-study site
- why it matters: useful reference for portfolio packaging, case-study structure, and proof-oriented career assets
- likely role: reference for later portfolio and case-study output design
- risk/cost notes: production web stack and live AI surface are much heavier than the current runtime MVP
- next action: inspect case-study structure and portfolio asset presentation only

## browser-use/browser-use-examples

- local clone path: `21_repos/third_party/browser-use-examples`
- category: browser automation examples
- why it matters: shows concrete Browser Use patterns beyond the core framework repo
- likely role: example library for future browser executor experiments
- risk/cost notes: examples vary in scope and may assume external services or cloud flows
- next action: inspect the simplest agent and scraper examples first

## OpenHands/OpenHands-CLI

- local clone path: `21_repos/third_party/openhands-cli`
- category: agent runtime CLI
- why it matters: useful reference for confirmation modes, headless runs, and terminal agent UX
- likely role: runtime-pattern reference for execution modes and approval UX
- risk/cost notes: larger agent runtime assumptions and Python tooling overhead are outside the current core scope
- next action: inspect CLI confirmation and headless workflow design only

## anthropics/claude-code

- local clone path: `21_repos/third_party/claude-code-official`
- category: official coding-agent CLI
- why it matters: cleaner reference for terminal UX, plugin layout, install paths, and supported documentation than dubious claw snapshots
- likely role: official reference for command, plugin, and operator-surface ideas
- risk/cost notes: vendor-specific workflow assumptions and provider coupling should not leak into core design
- next action: inspect plugin and operator patterns only, not vendor-specific execution assumptions

## openclaw/openclaw

- local clone path: `21_repos/third_party/openclaw`
- category: broad personal assistant control plane
- why it matters: useful comparison point for gateway, browser, channel, and permission concepts
- likely role: reference for later control-plane and browser-executor thinking, not a near-term dependency
- risk/cost notes: much broader scope than this repo, WSL2-oriented Windows setup, and a heavy multi-channel surface
- next action: extract only a few control-boundary and onboarding ideas, keep the rest as reference-only

## hesreallyhim/awesome-claude-code

- local clone path: `21_repos/third_party/awesome-claude-code`
- category: curated resource index
- why it matters: useful discovery map for skills, hooks, slash commands, tooling, and official docs
- likely role: curated reference list for selective future intake
- risk/cost notes: list quality varies and the repo license limits modified redistribution, so it should stay a pointer source only
- next action: use it to discover patterns and official references, not as a core dependency
