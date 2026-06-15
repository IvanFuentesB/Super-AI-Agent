# Claude Code Skills

Skills for the primary builder agent. `manual_required: true` means the canonical
source must be confirmed and the skill installed into a project-scoped location
before use (never overwrite global/user skill folders). Status of record:
`14_context/tool_stack/skills_registry.json`.

| Skill | Purpose | manual_required |
|-------|---------|-----------------|
| karpathy-guidelines | Anti-pitfall coding discipline; minimal, surgical changes | false |
| context-engineering | Structure context windows for reliable agent work | false |
| search-first/source-driven-development | Read sources before writing; ground changes in code | false |
| incremental-implementation | Build in small, reversible steps | false |
| verification-loop | Validate each change before claiming done | false |
| parallel-execution-optimizer | Plan independent work to run in parallel | true |
| frontend-design | Front-end/UI design discipline | true |
| code-review-security | Review changes for correctness and security | false |
| mcp-builder | Build well-designed MCP servers/tools | false |
| skill-creator | Create and improve skills | false |
| prompt-optimizer | Improve prompts for triggering and quality | true |
| hooks-mastery | Author Claude Code hooks/settings automation | true |
| ccstatusline | Status line customization tooling | true |
| claudekit | Claude Code helper toolkit | true |
| claude-code-action | CI/Action integration for Claude Code | true |
| claude-task-master | Task breakdown/management workflow | true |
| claude-loop | Recurring/interval execution helper | true |
| claude-squad | Multi-agent squad orchestration | true |
| claude-mem | Long-term memory bridge (must not duplicate memory) | true |
| superclaude | Agent framework to evaluate for patterns | true |
| bmad | Agent framework to evaluate for patterns | true |
| archon | Agent framework to evaluate for patterns | true |
| official-anthropic-skills-repo | Official skills bundle (intake-first, inspect before adopting) | true |

Notes:

- The discipline skills (karpathy, context-engineering, search-first,
  incremental, verification-loop, code-review-security, mcp-builder,
  skill-creator) are already part of this repo's workflow; use them directly.
- Framework skills (superclaude, bmad, archon) and memory bridges (claude-mem)
  are evaluate-first: extract patterns, do not import wholesale, and do not add a
  second memory system.
- `official-anthropic-skills-repo`: inspect via repo intake before adopting any
  part of it.
