# Context Snapshot -- N+6.39A Ghoti Usability Rescue (Operator Capability Console)

**Milestone:** N+6.39A
**Date:** 2026-06-09
**Branch:** `feat/ghoti-agent-claude-n6-39a-ghoti-usability-rescue`
**Starting main:** `70755c89de926d4cf6a9083858287351757673ba` (after N+6.38B)
**Status:** IMPLEMENTED_AND_PUSHED (feature branch; not merged - Codex out of messages)

---

## Goal

Turn the existing safe backend into a clear local operator console: make the
dashboard explain what Ghoti can do now, what is dry-run only, what is blocked,
and what is not built yet - and fix the launcher/overlay/approvals annoyances.

## Files changed

| File | Change |
|------|--------|
| `03_scripts/ghoti_product_launcher.py` | Crash-proof human printer (.get + fallback); `_probe_ghoti_dashboard`; already-running detection; safe non-Ghoti port warning |
| `01_projects/dashboard_mvp/server.js` | 3 capability endpoints + EADDRINUSE graceful handler |
| `01_projects/dashboard_mvp/public/index.html` | Capabilities console view (default landing); overlay collapse/hide controls + restore chip |
| `01_projects/dashboard_mvp/public/app.js` | Capability console logic; overlay hide/collapse (localStorage); friendly approval-unavailable card |
| `01_projects/dashboard_mvp/public/styles.css` | Capability console + overlay control styles |
| `01_projects/runtime_mvp/tests/test_n6_39a_ghoti_usability_rescue.py` | 26 tests |
| `docs/GHOTI_N6_39A_USABILITY_RESCUE_CAPABILITY_CONSOLE.md` | Full docs |
| `14_context/claude_n6_39a_ghoti_usability_rescue.md` | This snapshot |

## Launcher fix

- `_print_human` uses `.get()` defaults everywhere + generic fallback -> no more
  `KeyError: launcher_version`.
- `cmd_start_dashboard` probes `GET /api/product-control/status` on a busy port:
  Ghoti answering -> `ok=true`, `already_running=true`, `detected_via=health_probe`,
  opens browser if asked. Unknown occupant -> `ok=false`,
  `port_occupied_by_non_ghoti=true` + safe inspect command (never auto-kill).

## Dashboard changes

- New default "Home / Capabilities" view: What can Ghoti do now, Safe things to
  run, What is blocked / not implemented, Next recommended action, System health,
  Warnings, capability cards, "What can I click?" buttons, Real use today, Not
  real yet, Next recommended build, Why am I seeing warnings.
- Buttons call only safe local endpoints; raw JSON tucked into collapsed debug.

## Overlay fix

- Bottom-right `#ghoti-state-indicator` and `#ghoti-target-marker` gained collapse
  + hide controls; per-session persistence via `localStorage`; restore chip.
  Idle is calm, not scary.

## New endpoints

- `GET /api/product-control/capabilities`
- `POST /api/product-control/run-capability-check` (fast default / full optional)
- `GET /api/product-control/latest-capability-check`

Latest check is written to repo-local `runtime_data/capability_check_latest.json`
(gitignored; not committed).

## Capabilities exposed (safe)

Repo safety audit, repo map / context pack, local model/worker status, claude-swarm
fixture replay (5 tasks / 3 groups / 0 overlaps), Claude/Codex handoff packets,
external-tool static inspection. claude-swarm dry-run shown as "blocked safely".

## Tests

26 tests pass. Cover: human-printer missing-key safety; already-running ok;
unknown-port safe warning; endpoint contract; required statuses; dry-run
blocked-safely; fixture 5/3/0; overlay hide/collapse + localStorage; collapsed
debug; no provider keys / MCP / Telegram exec / AI attribution; fixture PS1
ASCII; public audit no blocking findings.

## What stayed disabled

No live computer-use, live agents, account actions, browser automation (beyond
opening localhost), MCP, Telegram, Obsidian, provider/API keys, auto-submit,
secrets. No third-party code committed. No AI attribution.

## Obsidian touched?

No. Obsidian is shown as "not implemented yet" only. No vault read/write.

## Telegram touched?

No. Telegram is shown as "planned later (notification-only)" only. No bot, no
command execution.

## Codex audit target

`audit/ghoti-agent-codex-n6-39a-ghoti-usability-rescue`

## Next milestone

N+6.39B (Codex audit of this console), then Obsidian Memory Bridge.
