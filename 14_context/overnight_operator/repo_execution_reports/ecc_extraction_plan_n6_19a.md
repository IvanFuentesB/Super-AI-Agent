# ECC Extraction Plan For Ghoti

Attribution: inspired by static inspection of `https://github.com/affaan-m/ecc` at commit `0f84c0e2796703fbda87d577b2636351418c7442`.

## Adapt First

1. Agent profiles: define Ghoti roles for implementation, audit, Hermes coordination, local memory, and local model summaries.
2. Skill registry: map skills into `14_context/skills/` with install status, source, license, and safety gate.
3. Command templates: convert command surfaces into dry-run prompt packet templates.
4. Hooks: adapt as validators and status reporters only, not automatic code execution.
5. Security scanner: fold rule ideas into Codex audit gates and public repo audit checks.
6. MCP surfaces: keep as manual bridge docs until a separate setup milestone.

## Do Not Adapt Yet

- live hook execution
- automatic skill install
- MCP setup
- dashboard control pane runtime
- package installation
- global command shims

## N+6.20A Use

Use ECC-style agent profiles and command templates to build the approved-window copy/paste harness. The harness should prepare packets and require a human-approved paste; it must not auto-submit.
