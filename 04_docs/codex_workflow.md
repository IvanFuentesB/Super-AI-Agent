# Codex Workflow

## Role of Codex

- Codex is the execution layer for this repo
- Codex may handle file edits, branch work, commits, pushes, and future PR preparation
- Continue is the local control and context-reading layer
- `14_context` is the durable handoff source of truth

## Standard Task Pattern

1. Read relevant context files first
2. State plan
3. Show exact target paths
4. Make scoped changes only
5. Validate results
6. Commit
7. Push
8. Update status or memory if needed

## Branch Rules

- `main` = tiny safe foundation, docs, or config cleanup
- `feat/*` = new capability
- `fix/*` = repairs
- `docs/*` = documentation-only work
- `exp/*` = uncertain experiments

## Git Rules

- Commit after a reviewed checkpoint
- Push after meaningful checkpoints
- Include commit and push inside Codex task prompts by default
- Do not merge automatically unless explicitly asked

## Verification Rules

- After each batch, update or review the status board
- Run the checker script or report verification findings
- The working tree should be clean unless intentionally left dirty
