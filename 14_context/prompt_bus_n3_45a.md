# Prompt Bus — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## What Was Built

A local file-based prompt manager (`03_scripts/prompt_bus.py`) that coordinates copy-paste between Claude Code, Codex, ChatGPT, and future agents.

### Files Created

| File | Purpose |
|------|---------|
| `03_scripts/prompt_bus.py` | CLI script — stdlib only |
| `14_context/prompt_bus/README.md` | Usage guide |
| `14_context/prompt_bus/current_status.md` | Status snapshot |
| `14_context/prompt_bus/inbox/` | Manual inbox for incoming notes |
| `14_context/prompt_bus/outbox/` | Staged Codex/ChatGPT prompt files |
| `14_context/prompt_bus/archive/` | Rotated old prompts |
| `14_context/prompt_bus/templates/claude_code_prompt_template.md` | Claude prompt template |
| `14_context/prompt_bus/templates/codex_prompt_template.md` | Codex audit prompt template |
| `14_context/prompt_bus/templates/chatgpt_handoff_template.md` | ChatGPT handoff template |

---

## How to Use

### Check status

```bash
python 03_scripts/prompt_bus.py --status
```

### Write a Claude prompt

```bash
python 03_scripts/prompt_bus.py --write-claude --title "N+3.46" --body "Your prompt here" --dry-run
python 03_scripts/prompt_bus.py --write-claude --title "N+3.46" --body "Your prompt here" --apply
```

This writes to `14_context/ghoti_current_prompt.md` — the canonical Claude Code entry point.

### Stage a Codex prompt

```bash
python 03_scripts/prompt_bus.py --write-codex --title "N+3.45B audit" --body "Your prompt" --apply
```

Creates: `14_context/prompt_bus/outbox/codex_{{timestamp}}_{{slug}}.md`

### List outbox

```bash
python 03_scripts/prompt_bus.py --list-outbox
```

---

## Commands

```
--init          Create directories/templates if missing
--status        Print branch, prompt path, outbox count
--write-claude  Write canonical Claude prompt (--apply to write)
--write-codex   Write Codex prompt to outbox (--apply to write)
--list-outbox   List outbox files
```

---

## Validation

```bash
python -c "import ast, pathlib; ast.parse(pathlib.Path('03_scripts/prompt_bus.py').read_text(encoding='utf-8')); print('AST OK')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --init --dry-run
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --list-outbox
```

---

## Safety Gates

- `--write-*` never writes without `--apply`
- No clipboard access
- No external network calls
- No account actions
- Python stdlib only

---

## What Is Not Wired Yet

- Clipboard support: disabled (opt-in not implemented)
- No automatic prompt staging from git hooks
- No Obsidian vault write automation

---

## Next Steps

- Use `--write-claude` when preparing the next milestone prompt
- Use `--write-codex` to stage Codex audit prompts
- Extend templates as new agent types are added
