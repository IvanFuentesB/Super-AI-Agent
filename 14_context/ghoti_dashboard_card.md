# Ghoti Dashboard Card — N+3.65

Generated: 2026-05-07 09:13 UTC
Branch: `feat/ghoti-agent-claude-n3-65-supervised-content-mvp-100` | HEAD: `30009cd` | Dirty: 18 dirty files

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
- Active locks: 11
- Status records: 20
- Latest agent: claude_code_n3_65_supervised_mvp_100
- Latest state: implementation_started

## Obsidian Vault
- Exists: YES
- Markdown files: 13
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

## LLM Council (N+3.61A)
- LLM Council: scaffold EXISTS
- Config: EXISTS
- Default mode: local_demo
- External providers: DISABLED by default
- Local demo available: YES
- Runtime wiring: NO autonomous actions
- Human review: REQUIRED

## External Repo Intake (N+3.63A)
- external_repo_intake.py: EXISTS
- OpenFang candidates tracked: YES (openfang_python_gateway, openfang_rust_agent_os)
- MoneyPrinter candidates tracked: YES (moneyprinter_shorts, moneyprinter_v2)
- Clone/install/runtime wiring: NO
- Catalog config: EXISTS
- Catalog doc: EXISTS
- Risk report: EXISTS

## Content Money Workflow (N+3.63A)
- content_money_workflow.py: EXISTS
- Config: EXISTS
- Planning only: YES
- Live posting: NO
- Human review gate: REQUIRED
- Goal: one safe local artifact-to-manual-publish workflow
- Output dir (14_context/content_workflows/): EXISTS
- Saved plans: 0
- Saved shot lists: 0

## Supervised Content MVP (N+3.65)
- supervised_content_mvp_runner.py: EXISTS
- ghoti_readiness_check.py: EXISTS
- external_repo_implementation_map.py: EXISTS
- Proof packet exists: YES — 20260507T091135Z_ai_tools_for_students_and_crea
- Packet files: 13/12
- supervised_mvp_slice_score: 100
- production_public_release_ready: NO
- Live posting: NO
- Upload: NO
- External API: NO
- Clone/install/run external repos: NO
- Human approval required: YES

## 100% Local Slice Readiness (N+3.65)
- Score applies to: supervised local MVP slice only
- See: 14_context/tooling/ghoti_100_percent_readiness_n3_65.md
- Production/autonomous release: NOT APPLICABLE
- production_public_release_ready: false

## External Repo Implementation Map (N+3.65)
- OpenFang implemented as Ghoti-native: YES (not just intake)
- MoneyPrinter implemented as Ghoti-native: YES (not just intake)
- Clone/install/run: NO
- See: 14_context/tooling/external_repo_implementation_map_n3_65.md

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
