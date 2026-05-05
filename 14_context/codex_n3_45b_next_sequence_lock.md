# N+3.45B Next Sequence Lock

Status: Codex lane recommendation.
Date: 2026-05-05

## Current Lane Verdict

Codex N+3.45B should remain docs/source-check only and file-separated from Claude N+3.45A.

## Exact Next Steps

1. Wait for Claude N+3.45A result.
2. Audit Claude branch for path ownership, validation, prompt-bus safety, and no live actions.
3. Merge Claude branch only if safe.
4. Merge Codex branch only if it remains docs-only and non-overlapping.
5. Run N+3.46 retrospective.
6. Decide whether to proceed with Ruflo isolated runtime test, OpenClaw comparison, or prompt bus dashboard.

## Recommended Next Claude

```text
N+3.45A - Tooling Prompt Bus / Local Worker Implementation
```

Must remain local-only, with no external tool connections.

## Recommended Next Codex

```text
N+3.46 - Parallel Pilot Retrospective And Claude Branch Audit
```

Audit:

- branch separation
- file ownership
- validation
- prompt-bus safety
- local-worker boundaries
- no external action

## Recommended ChatGPT Action

Prepare merge/audit prompts after Claude reports:

- one prompt for Codex N+3.46 audit
- one prompt for Claude recovery if validation fails
- one human merge checklist

## Future Milestone Options

Only after N+3.46:

- Ruflo isolated clone/intake
- OpenClaw/Paperclip/n8n comparison deep dive
- prompt bus dashboard read card
- local Gemma compact memory dry-run
- connector/account inventory spec

## Hard Stop Conditions

- Claude branch touched Codex docs.
- Codex branch touched Claude implementation paths.
- Either branch touched live accounts, connectors, scraping tools, or external MCPs.
- Either branch staged unrelated dirty files.
- State docs diverged or were edited by both lanes.

## Sequence Verdict

Do not start Ruflo/OpenClaw/Paperclip/n8n/browser tooling until the controlled parallel pilot is audited and the prompt bus/local-worker layer is stable.
