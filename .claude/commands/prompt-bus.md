---
description: Show prompt bus status — canonical Claude prompt path, outbox files, and copy-paste instructions.
allowed-tools: Bash, Read
---

Run:
```bash
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --list-outbox
```

Then explain:
- Where `14_context/ghoti_current_prompt.md` is (the canonical Claude Code prompt)
- How to write a new Claude prompt: `python 03_scripts/prompt_bus.py --write-claude --title "..." --body "..." --apply`
- How to stage a Codex prompt: `python 03_scripts/prompt_bus.py --write-codex --title "..." --body "..." --apply`
- What files are in the outbox
- Template locations:
  - `14_context/prompt_bus/templates/claude_code_prompt_template.md`
  - `14_context/prompt_bus/templates/codex_prompt_template.md`
  - `14_context/prompt_bus/templates/chatgpt_handoff_template.md`

Remind: no clipboard write by default, no live sends, no external APIs.
