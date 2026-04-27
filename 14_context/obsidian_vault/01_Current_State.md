# Ghoti Current State (Compact)

**Updated:** 2026-04-27 — Milestone N+3.3
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/current_state.md`

---

## What Exists and Works

- Operator console dashboard (Node/Express) with live state, approvals, tasks, artifacts
- Desktop bridge: focus, clipboard, hotkey, wait, mouse, one-line type — all allowlisted
- ActionIntent + CapabilityAdapter contracts — approval-gated, audit-traced
- Wait/resume supervisor — 9 pending gates, local-only, no external execution
- Multi-agent MVP — 5 deterministic local agents, repo-bound
- Brain foundation (Gemma/Ollama wired, but no models installed)
- Specialist-agent registry (scaffolding only)
- Compact memory at `14_context/compact_memory/`
- MCP server launch helper at `03_scripts/run_mcp_server.ps1`

## What Does NOT Exist Yet

- No live Ollama model (ollama list is empty)
- No Browser Use install
- No live external adapters (AutoBrowser, RUFLO, Obscura, CUA) wired into runtime
- No live mail/LinkedIn/Notion writes
- No screen capture started
- No CUA/Screenpipe runtime wiring

## N+3.3 Additions

- CUA Driver readiness plan — evaluation_plan / sandbox_first / not_runtime_wired
- OpenFang Rust candidate plan — exact_repo_unknown / rust_not_installed
- Screenpipe 3-day retention plan + cleanup script + policy JSON
- Obsidian vault token-saving plan + this vault

## Active Risk

- Session context fills quickly → use vault notes + file paths
- Rust not installed → OpenFang evaluation blocked
- No CUA sandbox defined → CUA evaluation blocked

---

> Full detail: `14_context/current_state.md`
