---
description: Deep planning mode — produce an implementation plan, risks, validations, and file ownership for the current Ghoti milestone.
allowed-tools: Bash, Read, Glob, Grep
---

You are in deep planning mode for the Ghoti operator system.

Steps:
1. Read the current prompt file: `14_context/ghoti_current_prompt.md`
2. Read: `14_context/agent_lanes/active_locks.jsonl` and `14_context/agent_lanes/lane_status.jsonl`
3. Run: `git status --short` and `git log --oneline -8`
4. Run: `python 03_scripts/prompt_bus.py --status`

Then produce:
- Milestone summary: what needs to be done
- Implementation plan: ordered steps with file paths
- File ownership: which files this lane may touch
- Risk list: what could go wrong and how to detect it
- Validation plan: exact commands to verify completion
- Safety gates: what requires human approval
- What is NOT in scope this lane

Rules:
- Ask clarifying questions only if they would block the plan
- Do not implement — only plan
- No live actions
- No cap bypass
- Respect active lane locks
