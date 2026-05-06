# Claude N+3.51A — Ruflo/Gemma/Bridge Hardening

Branch: `feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening`
Base: `56cf614` (N+3.50A)
Date: 2026-05-06

## Deliverables

| File | Status | Notes |
|------|--------|-------|
| `03_scripts/ruflo_install_gate.py` | UPDATED | Added `--catalog` mode |
| `03_scripts/gemma_compact_memory_worker.py` | UPDATED | Safe write, --outbox, hardened |
| `03_scripts/cc_codex_bridge.py` | NEW | Local file bridge, no API, no clipboard |
| `03_scripts/course_certificate_assistant.py` | NEW | Study plans/trackers/cert logs only |
| `03_scripts/prompt_bus.py` | UPDATED | `--allow-canonical-overwrite` protection |
| `03_scripts/ghoti_dashboard.py` | UPDATED | Course helper + Obsidian exe status |
| `03_scripts/local_worker_router.py` | EXISTS | Course + Ruflo + prompt bus routes |
| `03_scripts/open_obsidian_vault.ps1` | EXISTS | Check + Open modes |
| `01_projects/dashboard_mvp/server.js` | EXISTS | Route: GET /api/ghoti/local-orchestrator/status |
| `23_configs/cc_codex_bridge.example.json` | NEW | Bridge config example |
| `23_configs/course_certificate_assistant.example.json` | NEW | Course config example |
| `14_context/tooling/ruflo_install_status_n3_51a.md` | NEW | Ruflo smoke docs |
| `14_context/tooling/gemma_compression_smoke_n3_51a.md` | NEW | Gemma smoke docs |
| `14_context/tooling/cc_codex_bridge_n3_51a.md` | NEW | Bridge docs |
| `14_context/tooling/course_certificate_assistant_n3_51a.md` | NEW | Course docs |
| `14_context/tooling/obsidian_open_helper_n3_51a.md` | NEW | Obsidian docs |
| `14_context/ghoti_dashboard_card.md` | UPDATED | N+3.51A truth card |

## Validation Results

| Check | Result |
|-------|--------|
| AST parse all scripts | PASS |
| ruflo --status | PASS |
| ruflo --install --dry-run | PASS (npm not installed → blocked on apply) |
| ruflo --smoke | PASS |
| ruflo --catalog --dry-run | PASS (reads README/CLAUDE.md/CHANGELOG) |
| gemma --status | PASS (Ollama v0.9.2, gemma3:4b found) |
| gemma --compress --dry-run | PASS |
| cc_codex_bridge --status | PASS |
| cc_codex_bridge --write-pair --dry-run | PASS |
| cc_codex_bridge --write-pair --apply | PASS |
| cc_codex_bridge --next --dry-run | PASS |
| cc_codex_bridge --verify | PASS |
| course_certificate_assistant --policy | PASS |
| course_certificate_assistant --plan --dry-run | PASS |
| course_certificate_assistant --plan --apply | PASS |
| course_certificate_assistant --tracker --apply | PASS |
| course_certificate_assistant --certificate-log --apply | PASS |
| course_certificate_assistant --status | PASS |
| prompt_bus --status-json | PASS |
| prompt_bus --write-context-pack --dry-run | PASS |
| prompt_bus --allow-canonical-overwrite protection | PASS (refuses without flag) |
| prompt_bus --allow-canonical-overwrite approved | PASS (overwrites with flag) |
| ghoti_dashboard --status | PASS |
| ghoti_dashboard --json | PASS |
| ghoti_dashboard --card --apply | PASS |
| local_worker_router --recommend (5 routes) | PASS |
| CONFIG JSON OK (5 configs) | PASS |
| node --check server.js | PASS |
| node --check app.js | PASS |
| agent_lane_status --check | PASS (5 locks, 8 statuses) |
| obsidian -Check | PASS (vault OK, Obsidian 1.12.7 found) |

## Ruflo Status

- Deps installed: NO (npm not found on machine)
- node_modules: NOT INSTALLED
- Lifecycle scripts: NONE (safe when npm available)
- Runtime wired: NO
- Blocker: npm not found. Install via winget: `winget install --id OpenJS.NodeJS.LTS`

## Gemma Status

- Ollama: FOUND (v0.9.2)
- Model: gemma3:4b (available)
- Compression dry-run: PASS
- Apply smoke: Available (logs to 05_logs/ — not staged)

## CC/Codex Bridge

- Automatic: NO
- Files generated: YES (smoke handoffs in 14_context/bridge/outbox/)
- What remains manual: Paste files into target AI tool

## Course Helper

- Script: EXISTS
- Policy: Clear (no fake certs, no cheating, no assessment submission)
- Output dirs: CREATED (plans/, trackers/, certificate_log/)

## Obsidian

- Vault: EXISTS (12 .md files)
- App: FOUND via winget (1.12.7)
- Exe: `C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe`

## Dashboard Route

- `GET /api/ghoti/local-orchestrator/status`: EXISTS in server.js (node --check PASS)

## Project Percentage

- Before N+3.51A: ~80%
- After N+3.51A branch (this commit): ~88-91%
  - Bridge hardening: complete
  - New scripts: complete
  - Ruflo: gate ready, blocked on npm
  - Gemma: operational
  - Obsidian: found and working
- After Codex PASS + merge: target 90-94%

## Next Codex Audit Recommendation

```
Branch: feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
Verify: new cc_codex_bridge.py (bridge type, no-api, no-clipboard)
Verify: new course_certificate_assistant.py (no fake certs, no cheating)
Verify: prompt_bus.py --allow-canonical-overwrite protection
Verify: ruflo_install_gate.py --catalog mode
Verify: ghoti_dashboard.py course_helper + obsidian_exe fields
Check: all configs valid JSON
Check: AST all scripts clean
```

## Safety

- No live actions
- No external API calls
- No Ruflo runtime wiring
- No clipboard
- No fake certificates
- Human approval required for all publish/commit/deploy actions
