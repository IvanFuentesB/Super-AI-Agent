# Ghoti Dashboard Card — N+3.50A

Generated: 2026-05-06 14:24 UTC
Branch: `audit/ghoti-agent-codex-n3-51-post-n3-49-bridge-audit` | HEAD: `3b12ff2`

## Prompt Bus
- Outbox files: 0
- Latest: (none)

## Agent Lanes
- Active locks: 3
- Status records: 5
- Latest agent: claude_code_n3_50a
- Latest state: implementation_started

## Obsidian Vault
- Exists: YES
- Markdown files: 12

## Compact Memory
- Exists: YES
- Markdown files: 19

## Ruflo
- Path exists: YES
- Package: claude-flow v3.5.80
- node_modules: NOT INSTALLED
- Lifecycle scripts: NONE (safe)
- Install blocked: false

## Gemma / Ollama
- Ollama: FOUND
- Gemma model: FOUND

## Safety Flags
- Read-only card: YES
- No live actions: YES
- Human approval required: YES

## Next Recommended Commands
```bash
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-50 --dry-run
```
