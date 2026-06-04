# ECC N+6.19A Static Inspection Report

Source: `https://github.com/affaan-m/ecc`

Clone path: `21_repos/third_party_runtime_sandbox/ecc`

Observed HEAD: `0f84c0e2796703fbda87d577b2636351418c7442`

Latest commit summary: `0f84c0e feat: add ECC2 local control pane (#2131)`

License detected: MIT

## Result

ECC cloned successfully into the ignored runtime sandbox. Only read-only metadata and static scans were performed.

## Components Detected

- `.agents`, `agents/`, `agent.yaml`, `AGENTS.md`
- `skills/`, `.claude/skills`, `.cursor/skills`, `.agents/skills`
- `rules/`, `RULES.md`
- `commands/`, `COMMANDS-QUICK-REF.md`
- `hooks/`, hook docs, hook tests
- `.mcp.json`, `mcp-configs/`
- `SECURITY.md`, `the-security-guide.md`, security/audit commands
- prompt and policy material under docs, rules, and prompt-related skills

## Safety Scan

Static scan verdict: blocked for runtime execution.

The scanner found high-review patterns such as remote script-to-shell examples, install hooks, privilege/container examples, dynamic execution patterns, and package install references. This is expected for a large coding setup repo, but it means Ghoti must not install or run ECC blindly.

## Extraction Value

ECC is immediately useful as a design reference for:

- agent profile layout
- skill layout and placement policy
- command templates
- hook lifecycle concepts
- MCP/client config documentation
- security/audit command patterns
- repo hygiene and prompt rules

No ECC code was executed. No ECC code was copied into runtime. Any future reuse must keep attribution and pass a separate license/code review.
