# Super-AI-Agent

Execution-first AI operating framework for legitimate business workflows, documentation, GitHub and project operations, internship and job-search ops, owned-account workflows, and later browser or app control plus multi-model orchestration.

## Current Summary

This repo is the core workspace for building a controllable AI system that produces reviewable outputs, keeps risky actions explicit, and grows from a small checked runtime instead of a vague pile of prompts and notes.

## Live Capabilities

- approval-aware runtime with file-backed task state
- durable context and handoff snapshots from `14_context`
- GitHub read-only inspection plus approval-gated draft and write-action commands
- environment and capability detection for `python`, `git`, and `gh`
- repeatable runtime checker
- internship, CV, LinkedIn, outreach, showcase, and portfolio scaffold generation
- local deterministic browser control playground with Playwright smoke checks

## Scaffold-Only Or Research State

- mail and Notion adapters are planning-only
- full browser and app execution are still not implemented
- multi-model routing remains planning and policy scaffolding
- remote GitHub smoke tests are explicit and available, but the default checker remains non-mutating

## Reference Intake Role

`21_repos/third_party` is an intake lane for external repos used as comparison and extraction material only. Those repos help evaluate patterns from tools like career-ops, official Claude Code, OpenClaw, Playwright, Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, Browser Use, Stagehand, OpenHands, and related ecosystems without merging vendor code into this core repo.

## Internship And Showcase Relevance

This repo already demonstrates a few concrete recruiter-friendly angles:

- GitHub workflow control with explicit approvals
- internship application pack generation
- structured personal-ops and career-ops scaffolding
- durable context and checker-driven runtime discipline

## Repo Structure

- `13_prompts`: reusable prompts, including handoff prompts
- `14_context`: durable project state, decisions, open questions, and handoff files
- `01_projects/runtime_mvp`: small checked runtime and CLI
- `20_agents`: agent templates, shared patterns, and future agent-specific memory
- `21_repos`: reference intake and later external evaluations
- `23_configs`: local configuration files and setup state

## Working Method

- Use summarized context files instead of relying on long chats
- Keep changes small and reversible
- Require approval for risky actions

## Next Milestones

- Test the browser playground manually
- Decide between Playwright-first and browser-use-first for the next executor layer
- Prepare one internship-facing live demo
- Evaluate Windows-Use, Windows-MCP, official Claude Code, and OpenClaw for selective extraction value
- Plan live Notion groundwork later
- Keep outbound and remote actions approval-gated
