# Ghoti Dashboard Card — N+3.56-FIX

Generated: 2026-05-06 20:57 UTC
Branch: `feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass` | HEAD: `1a2c6fd` | Dirty: 24 dirty files

## Bridge Status
- CC/Codex automatic: NO
- Bridge type: local manual file handoff
- Clipboard: NO
- API calls: NO
- Auto-send: NO
- Human copy-paste required: YES
- Bridge helper (cc_codex_bridge.py): EXISTS
- Init mode available: YES (--init --dry-run/--apply)
- No Ruflo runtime wiring: CONFIRMED
- No automatic CC/Codex control: CONFIRMED

## Prompt Bus
- Outbox files: 0
- Latest: (none)

## Agent Lanes
- Active locks: 6
- Status records: 10
- Latest agent: claude_code_n3_56_fix
- Latest state: implementation_started

## Obsidian Vault
- Exists: YES
- Markdown files: 12
- Required files pass: YES

## Compact Memory
- Exists: YES
- Markdown files: 19

## Ruflo
- Source status: SOURCE_MISSING_BOOTSTRAPPABLE
- Path exists: NO
- Package: unknown vunknown
- node_modules: NOT INSTALLED
- Lifecycle scripts: NONE (safe)
- Install blocked: False
- Runtime wiring: NO

## Gemma / Ollama
- Ollama: FOUND — ollama version is 0.9.2
- Gemma model: FOUND

## Course/Certificate Helper
- course_certificate_assistant.py: EXISTS
- --goal supported: YES

## Obsidian App
- obsidian_probe.py: EXISTS
- Executable: FOUND — C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe
- Winget installed: NOT DETECTED

## Safety Flags
- Read-only card: YES
- No live actions: YES
- No Ruflo runtime wiring: YES
- No automatic CC/Codex control: YES
- Human approval required: YES

## Next Recommended Commands
```bash
python 03_scripts/obsidian_probe.py --status
python 03_scripts/ruflo_install_gate.py --source-status
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/cc_codex_bridge.py --init --dry-run
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-56-fix --include-status --include-memory --include-next-actions --dry-run
```
