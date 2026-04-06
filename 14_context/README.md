# Context System

This directory is the local-first memory and context layer for the sandbox.

Rules:

- `C:\Users\ai_sandbox\Documents\AI_Managed_Only` is the only permanent workspace root.
- `C:\Users\ai_sandbox\AI_Workspace` is temporary only.
- Main sandbox memory lives under `14_context`.
- Specialized automations and agents get their own memory and task areas under `20_agents`.
- Keep operational truth local first, then mirror selected summaries to GitHub or Notion later.

Start here:

- `00_main_memory/README.md`
- `02_decisions/current-decisions.md`
- `04_learning_paths/rust-and-cpp-on-windows.md`
- `../20_agents/agent-memory-guide.md`
