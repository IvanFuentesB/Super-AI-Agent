# Prompt Bus — N+3.50A Context Packs

Script: `03_scripts/prompt_bus.py`
New command: `--write-context-pack`

## Purpose
Generate rich handoff/context packs for Claude, Codex, and ChatGPT from current repo state.

## New Commands
```bash
python 03_scripts/prompt_bus.py --write-context-pack \
  --target {claude,codex,chatgpt,all} \
  --title "TITLE" \
  --include-status \
  --include-memory \
  --include-next-actions \
  --dry-run
  # --apply to actually write
```

## Behavior by Target
| Target | Output |
|---|---|
| `claude` | Overwrites `14_context/ghoti_current_prompt.md` (with --apply) |
| `codex` | Writes timestamped `14_context/prompt_bus/outbox/codex_context_pack_*.md` |
| `chatgpt` | Writes timestamped `14_context/prompt_bus/outbox/chatgpt_context_pack_*.md` |
| `all` | All three above |

## Content Included (flags)
- `--include-status`: branch, head, prompt bus counts, lane lock counts, latest agent/state
- `--include-memory`: compact memory file pointers
- `--include-next-actions`: recommended next commands
- Always includes: safety rules section

## Safety
- Dry-run must not write (default)
- Codex/ChatGPT targets always write timestamped outbox files, never overwrite canonical Claude prompt
- Outbox files are generated and not staged unless explicitly part of milestone docs
