# Browser Executor Research

## Playwright CLI Skill In Codex

- why it matters: best fit for explicit, operator-visible browser work from the current Codex environment
- likely fit: strong near-term path for approval-gated browser research and step-by-step flow testing
- complexity and risk: lower than building a new browser runtime, but still requires clear boundaries
- when to use it: when a human wants a concrete browser task executed and inspected now

## browser-use

- why it matters: useful reference for agentic browser flows and observation loops
- likely fit: medium-term reference for a higher-level browser executor
- complexity and risk: more agentic behavior means more safety and approval design work
- when to use it: after explicit browser-control boundaries are defined and a controlled wrapper is needed

## Stagehand

- why it matters: useful reference for structured browser action primitives
- likely fit: good candidate if the project needs a more programmable browser-control layer later
- complexity and risk: moderate; still depends on a real browser-control integration path
- when to use it: when the project wants clearer action building blocks instead of a more autonomous browser agent

## OpenHands Runtime Concepts

- why it matters: useful reference for confirmation modes, headless runs, and terminal agent UX
- likely fit: good runtime-pattern reference, not the first browser executor
- complexity and risk: broad agent runtime surface and more operational weight than needed now
- when to use it: when refining approval UX, execution modes, or terminal control patterns

## Recommendation

The next browser-control step should be the Playwright CLI skill in Codex for explicit, approval-gated research and smoke flows. Keep `browser-use`, `stagehand`, and `OpenHands-CLI` as comparison material until the browser executor boundary is clearer.
