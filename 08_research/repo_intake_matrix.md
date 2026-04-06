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
