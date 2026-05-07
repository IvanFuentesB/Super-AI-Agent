# Ghoti Current State (Compact)

**Updated:** 2026-04-27 — Milestone N+3.7
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/current_state.md`

---

## What Exists and Works

- Operator console dashboard (Node/Express) with live state, approvals, tasks, artifacts
- Desktop bridge: focus, clipboard, hotkey, wait, mouse, one-line type — all allowlisted
- ActionIntent + CapabilityAdapter contracts — approval-gated, audit-traced
- Wait/resume supervisor — 20+ pending gates, local-only, no external execution
- Multi-agent MVP — 5 deterministic local agents, repo-bound
- Brain foundation (Gemma/Ollama wired, but no models installed)
- Specialist-agent registry (scaffolding only)
- Compact memory at `14_context/compact_memory/`
- MCP server launch helper at `03_scripts/run_mcp_server.ps1`
- CUA descriptor-only adapter in `action_intent.py` — no execution, no install
- Docker/CUA install gate documented at `14_context/docker_desktop_cua_install_gate_n3_6.md`
- CUA Docker/Ubuntu sandbox path documented at `14_context/cua_docker_ubuntu_sandbox_path_n3_6.md`
- Screenpipe status-only dashboard route: `GET /api/ghoti/screenpipe/status` (N+3.7)
- Obsidian vault token-saving workflow active at `14_context/obsidian_vault/`

## What Does NOT Exist Yet

- No live Ollama model (ollama list is empty)
- No Browser Use install
- No live external adapters (AutoBrowser, RUFLO, Obscura, CUA) wired into runtime
- No live mail/LinkedIn/Notion writes
- No screen capture started
- No Docker installed, no WSL installed — all local CUA execution paths blocked
- No CUA container run, no CUA install performed

## N+3.4–N+3.7 Additions

- N+3.4: CUA source confirmed (trycua/cua, macOS-only canonical), sandbox profile, CUA descriptor, computer-use/candidates route
- N+3.5: CUA exact source verified (ls-remote HEAD 46dbcb47), shallow clone at 21_repos/third_party/evals/cua
- N+3.6: Docker/CUA gate doc, CUA Docker/Ubuntu sandbox path, wait/resume updated to 20 seeds
- N+3.7 (PATH B): Screenpipe read-only dashboard status route, Obsidian vault sync, wait/resume updated

## Active Risk

- Docker not installed, WSL not installed — CUA blocked until Docker approved and installed
- Screenpipe capture requires operator-start and explicit approval
- Session context fills quickly → use vault notes + file paths

---

> Full detail: `14_context/current_state.md`

---

## N+3.34 Update (2026-05-05)

- **N+3.18 resolved:** video-to-money runner + scoring implemented (dirty N+3.18 files remain unstaged by design)
- **N+3.29–N+3.32:** weekly review, dashboard card, manual queue intake, manual queue read view — all implemented and pushed
- **N+3.34 (this milestone):** Obsidian vault 10-file scaffold + compact memory 6-file set created
- **Gemma3:4b:** installed and smoke-passed (N+3.13)
- **Docker:** installed (N+3.11); CUA smoke pending approval phrase
- **MCP:** ghoti-local MCP server connected read-only (N+3.36)
- **Next milestone:** N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding

**Review status:** draft — Codex audit required after N+3.34 push.
