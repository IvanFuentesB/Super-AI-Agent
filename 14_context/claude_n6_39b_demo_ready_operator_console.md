# Context Snapshot -- N+6.39B Demo-Ready Operator Console

**Milestone:** N+6.39B
**Date:** 2026-06-09
**Branch:** `feat/ghoti-agent-claude-n6-39b-demo-ready-operator-console`
**Starting branch:** `feat/ghoti-agent-claude-n6-39a-ghoti-usability-rescue`
**Status:** IMPLEMENTED_AND_PUSHED (feature branch; not merged)

---

## Goal

Turn the N+6.39A capability console into a demo-ready operator console:
fix badge overflow, make overlay non-alarming, add "What is Ghoti?" hero,
"Real Use Today" guided flow, "Investor Demo Mode" panel, "Why blocked is good"
explanation, roadmap, and improve Approvals/GitHub pages.

## Files changed

| File | Change |
|------|--------|
| `01_projects/dashboard_mvp/public/styles.css` | Fix A (overflow), hero/demo/roadmap/cmd styles |
| `01_projects/dashboard_mvp/public/index.html` | Hero, demo flow, investor panel, roadmap, blocked explanation, command area, approvals card, github card |
| `01_projects/dashboard_mvp/public/app.js` | Overlay default-collapsed; capShowCmdCopy; [data-cap-action] wiring extended |
| `01_projects/runtime_mvp/tests/test_n6_39b_demo_ready_operator_console.py` | 25 tests |
| `docs/GHOTI_N6_39B_DEMO_READY_OPERATOR_CONSOLE.md` | Full docs |
| `14_context/claude_n6_39b_demo_ready_operator_console.md` | This snapshot |

## Fix A: Badge overflow

`body { overflow-x: hidden }`, `.cap-badge { word-break: break-word }`,
`.cap-cardlet-top { flex-wrap: wrap; min-width: 0 }`.

## Fix B: Overlay

Overlay now starts collapsed on first visit (no stored pref).
Logic: `stored === null ? true : stored === "1"`.

## Fix C: Hero

`#cap-hero` section with "What is Ghoti?", 3 bullets, 4 status chips
(Local-only, Supervised, Dry-run-first, No live account actions).

## Fix D: Real Use Today

Replaced static list with 5-card interactive demo grid.
Cards: Run Safe Check, Show Repo Map, Run Fixture Replay, Prepare Handoff Packet,
Check Local Model Lane. `[data-cap-action]` selector extended to all instances.

## Fix E: Investor Demo Mode

Collapsible `<details id="cap-investor-demo-panel">` with 5 sub-sections:
30-second pitch, 90-second demo flow, What is real today,
What is not live yet, Why it matters.

## Fix F: Why blocked is good

`#cap-why-blocked-section` in capabilities panel. Blue left-border callout.

## Fix G: Roadmap

`#cap-roadmap` section. 5 items: Obsidian Memory Bridge, Telegram notification
bridge, Live agent with approval gate, Real computer-use lane,
Hermes Codex provider integration.

## Fix H: Approvals

`#approvals-static-card` before `#approvals-slot`. Plain language, no private
paths, collapsed debug, "No action needed if you are not running any agents".

## Fix I: GitHub

`#github-static-card` before `#github-slot`. "does not push, merge, or modify
anything". Read-only note. Collapsed debug.

## Fix J: Show command

`#cap-show-command` section with `#cap-show-cmd-text` code block and
`#cap-show-cmd-copy` button. `capShowCmdCopy()` handles clipboard with fallback.

## Tests

25 tests pass. Cover all 10 fixes + no-unsafe rules.

## What stayed disabled

No live computer-use, live agents, account actions, browser automation (beyond
localhost), MCP, Telegram, Obsidian, provider/API keys, auto-submit, secrets.
No third-party code committed. No AI attribution.

## Codex audit target

`audit/ghoti-agent-codex-n6-39b-demo-ready-operator-console`

## Next milestone

N+6.40A (Obsidian Memory Bridge), after N+6.39B Codex audit.
