# GBrain Memory Extraction Plan For Ghoti

Attribution: inspired by static inspection of `https://github.com/garrytan/gbrain` at commit `9a0bae8d62cdd1e0dd6655e24e082fe6c69c5dac`.

## Patterns To Adapt

1. Brain repo format: give Ghoti memory folders explicit purpose and schema.
2. Evidence trail: every status claim should point to report, command, or generated artifact.
3. Compiled truth: maintain a short canonical truth document distinct from long reports.
4. Skillpack model: represent repeatable workflows as local skills with source, status, and safety gates.
5. Capture skills: turn inbox/outbox and Obsidian handoffs into structured capture lanes.
6. MCP/Telegram path: document as manual future bridge, not enabled runtime.

## Proposed N+6.20/N+6.21 Changes

- Add a `compiled_truth.md` generated from status brain and repo reports.
- Add a `brain_index.json` for Obsidian/handoff vault lookup.
- Add evidence links to context packs.
- Add a capture queue for pasted outputs and external repo scan summaries.
- Keep Telegram and MCP manual until separately approved.
