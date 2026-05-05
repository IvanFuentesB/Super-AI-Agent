# Prompt Bus — N+3.45A

**Milestone:** N+3.45A
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
**Date:** 2026-05-05

---

## Purpose

The prompt bus is a local file-based manager that reduces copy-paste friction when coordinating work between Claude Code, Codex, ChatGPT, and future agents.

It does NOT:
- Send anything automatically
- Call any external API
- Write clipboard without opt-in
- Operate live accounts

It DOES:
- Maintain the canonical Claude Code prompt file
- Stage Codex/ChatGPT prompt files in a structured outbox
- Print copy-paste instructions
- Track current prompt status

---

## Directory Structure

```
14_context/prompt_bus/
  README.md              — this file
  current_status.md      — human-readable status snapshot
  inbox/                 — incoming notes/requests (manual drop)
  outbox/                — staged prompt files for other agents
  archive/               — rotated old prompts
  templates/
    claude_code_prompt_template.md
    codex_prompt_template.md
    chatgpt_handoff_template.md
```

---

## Canonical Claude Prompt Path

```
14_context/ghoti_current_prompt.md
```

This file is the entry point for every Claude Code session. The prompt bus can overwrite it (with `--apply`) or dry-run before writing.

---

## CLI

```bash
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --init
python 03_scripts/prompt_bus.py --write-claude --title "N+3.46" --body "..." --dry-run
python 03_scripts/prompt_bus.py --write-claude --title "N+3.46" --body "..." --apply
python 03_scripts/prompt_bus.py --write-codex --title "audit" --body "..." --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "audit" --body "..." --apply
python 03_scripts/prompt_bus.py --list-outbox
```

---

## Safety Gates

- `--write-claude` never overwrites without `--apply`
- `--write-codex` never writes without `--apply`
- No clipboard access by default
- No external network calls
- No account actions
- Python stdlib only
