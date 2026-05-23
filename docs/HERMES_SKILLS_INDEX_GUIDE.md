# Hermes Skills Index Guide

The Hermes skills index is a local snapshot of visible Hermes skills. It helps Ivan see what might be useful later without claiming those skills are configured providers.

## Generate

```powershell
python 03_scripts/hermes_agent_workflow_bridge.py --skills-index --json
python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json
```

## Important Skills To Track

- `codex`: useful later only if provider support is verified.
- `claude-code`: implementation lane planning.
- `hermes-agent`: Hermes core workflow layer.
- `mcp`: future tool bridge planning.
- `memory` / `obsidian`: local memory workflow planning.
- `github`: repository workflow planning.
- `plan` and `test-driven-development`: engineering workflow support.
- browser/computer-use skills: not enabled for control.
- content skills: planning only, no posting.

## Truth

Skill presence is not provider support. The bridge reports detected skills, safety status, and future use separately.
