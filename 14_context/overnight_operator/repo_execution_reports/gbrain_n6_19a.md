# GBrain N+6.19A Static Inspection Report

Source: `https://github.com/garrytan/gbrain`

Clone path: `21_repos/third_party_runtime_sandbox/gbrain`

Observed HEAD: `9a0bae8d62cdd1e0dd6655e24e082fe6c69c5dac`

Latest commit summary: `9a0bae8 v0.42.25.0 fix(pricing): unify chat-model pricing into one canonical source; add Opus 4.8 (#1819) (#1827)`

License detected: MIT

## Result

GBrain cloned successfully into the ignored runtime sandbox. Only read-only metadata and static scans were performed.

## Components Observed

- `gbrain.yml`
- `docs/architecture`
- `docs/mcp`
- `docs/integrations`
- `docs/tutorials`
- `examples/skillpack-reference`
- `recipes/agent-voice`
- `skills/brain-ops`
- `skills/brain-pdf`
- `skills/brain-taxonomist`
- `skills/capture`
- `AGENTS.md`, `CLAUDE.md`, `INSTALL_FOR_AGENTS.md`

## Safety Scan

Static scan verdict: blocked for runtime execution.

The scanner found high-review and review patterns typical of a large agent system: remote shell examples, container examples, dynamic execution references, and install material. Ghoti must not run or install GBrain in this milestone.

## Extraction Value

GBrain is useful for:

- brain repo format
- skills-as-memory/workflow layout
- MCP documentation structure
- capture and briefing skills
- eval/recipe examples
- evidence trail and compiled truth concepts

No GBrain code was executed. No GBrain service was started. No Telegram, MCP, provider, or account setup was performed.
