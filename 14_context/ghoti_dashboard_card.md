# Ghoti Dashboard Card — N+3.58A

Generated: 2026-05-06 21:18 UTC
Branch: `feat/ghoti-agent-claude-n3-58-language-truth-rust-readiness-merge-assistant` | HEAD: `874aefd` | Dirty: 16 dirty files

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
- Active locks: 7
- Status records: 12
- Latest agent: claude_code_n3_58a
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

## Language Truth (N+3.58A)
- Tracked Java: NONE
- Tracked Rust: NONE
- Rust toolchain (rustc): NOT FOUND
- Rust toolchain (cargo): NOT FOUND
- Rust toolchain (rustup): NOT FOUND
- Runtime language truth: Python + Node/JS + PowerShell currently; Rust later when stable core is justified
- repo_language_inventory.py: EXISTS
- merge_assistant.py: EXISTS
- rust_readiness_probe.py: EXISTS
- Rewrite to Rust now: NO
- Java planned: NO

## Safety Flags
- Read-only card: YES
- No live actions: YES
- No Ruflo runtime wiring: YES
- No automatic CC/Codex control: YES
- Human approval required: YES

## Next Recommended Commands
```bash
python 03_scripts/repo_language_inventory.py --status
python 03_scripts/rust_readiness_probe.py --status
python 03_scripts/ghoti_merge_assistant.py --status
python 03_scripts/obsidian_probe.py --status
python 03_scripts/ruflo_install_gate.py --source-status
python 03_scripts/cc_codex_bridge.py --init --dry-run
```
