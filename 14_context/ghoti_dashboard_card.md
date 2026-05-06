# Ghoti Dashboard Card — N+3.51A

Generated: 2026-05-06 19:59 UTC
Branch: `feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening` | HEAD: `56cf614` | Dirty: 41 dirty files

## Bridge Status
- CC/Codex automatic: NO
- No Ruflo runtime wiring: CONFIRMED
- No automatic CC/Codex control: CONFIRMED
- Bridge type: local/manual copy-paste (stronger than N+3.50A)
- Less manual now: context packs, lane locks, dashboard, Ruflo deps installable
- Still manual: handing prompts between Claude/Codex/ChatGPT

## Prompt Bus
- Outbox files: 1
- Latest: codex_context_pack_20260506T195827Z_n3-51-codex.md

## Agent Lanes
- Active locks: 5
- Status records: 8
- Latest agent: claude_code_n3_51a
- Latest state: implementation_in_progress

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
- Install blocked: False
- Runtime wiring: NO

## Gemma / Ollama
- Ollama: FOUND
- Gemma model: FOUND

## Course/Certificate Helper
- course_certificate_assistant.py: EXISTS

## Obsidian
- Vault exists: YES
- Executable: FOUND — C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe

## Safety Flags
- Read-only card: YES
- No live actions: YES
- No Ruflo runtime wiring: YES
- No automatic CC/Codex control: YES
- Human approval required: YES

## Next Recommended Commands
```bash
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-51 --include-status --include-memory --include-next-actions --dry-run
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```
