# Ghoti N+3.50A — Dashboard, Ruflo Install Gate, Gemma Compact Worker

Generated: 2026-05-06
Branch: feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma

---

## What Was Built

### A — `03_scripts/ruflo_install_gate.py`
Stdlib-only script managing Ruflo isolated install and smoke.
- `--status`: prints Ruflo dir, package.json info, lifecycle scripts, npm version
- `--install --dry-run`: prints exact `npm ci --ignore-scripts` command, does not run
- `--install --apply`: runs `npm ci --ignore-scripts` in Ruflo dir only (no global)
- `--smoke`: read-only checks — package existence, node_modules, package-lock, npm version
- `--report --dry-run/--apply`: generates JSON + markdown report under `05_logs/ruflo_smoke/`
- Detects lifecycle scripts: `preinstall`, `postinstall`, `prepare`, etc. — blocks install if present
- Ruflo (claude-flow v3.5.80): NO lifecycle scripts detected — safe for `npm ci --ignore-scripts`

### B — `03_scripts/gemma_compact_memory_worker.py`
Stdlib-only Ollama/Gemma draft compression worker.
- `--status`: checks Ollama version, lists models, picks `gemma3:4b` if present
- `--compress --dry-run`: shows what would be compressed and where
- `--compress --apply`: runs `ollama run gemma3:4b` with compact summarization prompt
- Output marked `DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED`
- Never modifies `14_context/compact_memory/` automatically
- Rejects paths outside repo root and secret-like filenames
- Gemma3:4b confirmed present. Ollama apply smoke: Ollama ran OK; output write to 05_logs/ blocked by Windows/ai_sandbox restriction (known issue — use Node.js or git hash fallback)

### C — `03_scripts/ghoti_dashboard.py`
Stdlib-only local dashboard-card generator.
- `--status`: compact status summary
- `--json`: machine-readable JSON status object to stdout
- `--card --dry-run/--apply`: generates markdown card at `14_context/ghoti_dashboard_card.md`
- Reads: agent_lanes JSONL, prompt bus outbox, obsidian vault, compact memory, Ruflo, Ollama

### D — Dashboard UI Local Orchestrator Card
- New route: `GET /api/ghoti/local-orchestrator/status`
- New section `#section-local-orchestrator` in index.html
- New sidebar link "Local Orchestrator"
- `renderLocalOrchestratorCard(payload)` and `refreshLocalOrchestrator()` in app.js
- Shows: Prompt Bus, Agent Lanes, Obsidian/Compact Memory, Ruflo, Gemma/Ollama, Safety flags
- No approve/execute/install/post/pay buttons

### E — `03_scripts/prompt_bus.py` — Context Packs
Added commands:
- `--write-context-pack --target {claude,codex,chatgpt,all}`
- `--include-status`, `--include-memory`, `--include-next-actions`
- `--title TITLE`, `--dry-run`, `--apply`
- Claude target can overwrite canonical prompt (--apply); Codex/ChatGPT write timestamped outbox files
- Includes: branch/head, lane status, compact memory pointers, next commands, safety rules

### F — `03_scripts/open_obsidian_vault.ps1`
Patched with:
- Always prints vault path and existence
- `-Check`: lists required files, runs `winget list --id Obsidian.Obsidian`, checks common exe paths, prints Obsidian URI and exact launch command
- `-Open`: opens vault via `obsidian://open?path=...` URI

## What Was Deliberately NOT Wired Yet

- Ruflo runtime wiring to Ghoti execution: NOT done
- Ruflo npm dependencies: NOT installed (operator must approve and run `--install --apply`)
- Gemma output promotion to canonical memory: NOT done (DRAFT only)
- Gemma compression output write via Python: blocked by ai_sandbox restriction; use Node.js or git hash fallback
- No autonomous browser, no live accounts, no payments, no posting

## Project Percentage After N+3.50A

- Before N+3.50A: ~65%
- After N+3.50A: ~73%

## Next Milestones

### N+3.51 — Controlled Ruflo/Gemma/Local-Worker Pilot
- Sandboxed local task using Ruflo/Gemma without repo impact
- Expected after: ~78%

### N+3.52 — Dashboard Action-Intent Generation
- Dashboard generates command blocks for local-only tasks
- Expected after: ~83%

### N+3.53 — Merge Assistant
- Writes command blocks, opens Obsidian/context packs
- Expected after: ~88%

## Safety Gates
- All live/public/money actions require explicit human approval
- Ruflo not wired to Ghoti execution
- Gemma output is DRAFT only
- No global npm install
- No secrets or .env reads
