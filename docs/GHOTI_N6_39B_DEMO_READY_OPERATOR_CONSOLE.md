# GHOTI N+6.39B -- Demo-Ready Operator Console

**Milestone:** N+6.39B
**Branch:** `feat/ghoti-agent-claude-n6-39b-demo-ready-operator-console`
**Status:** Implemented (feature branch; not merged)

---

## What was addressed

This milestone turns the N+6.39A capability console into a demo-ready operator
console: clear hero section, interactive guided flow, honest investor demo mode,
roadmap, and improved approvals/GitHub pages.

---

## Changes

### Fix A: Badge / card overflow

- `body { overflow-x: hidden }` prevents horizontal scrollbars.
- `.cap-badge { white-space: normal; word-break: break-word; overflow-wrap: break-word }`
  -- badges wrap instead of overflowing their card.
- `.cap-cardlet-top { flex-wrap: wrap; min-width: 0 }` -- top row wraps on narrow screens.
- `.cap-cardlet-top > strong { min-width: 0; flex: 1 1 0 }` -- title shrinks before the badge.

### Fix B: Overlay default-collapsed

- The bottom-right `#ghoti-state-indicator` now starts collapsed on the first visit
  (no stored localStorage preference), so a new user sees a calm topline, not a
  "degraded" body.
- If the user has previously set a preference, that preference wins.
- Logic: `stored === null ? true : stored === "1"`.

### Fix C: "What is Ghoti?" hero section

- New `#cap-hero` section at the top of the Home / Capabilities view.
- Three plain-language bullets: Local only, Supervised, Honest about limits.
- Four status chips: Local-only, Supervised, Dry-run-first, No live account actions.

### Fix D: "Real Use Today" guided flow

- Replaced the static "Real use today" list with an interactive five-card demo grid.
- Cards: Run Safe Check, Show Repo Map, Run Fixture Replay, Prepare Handoff Packet,
  Check Local Model Lane.
- Each card has a button that calls the existing safe capability endpoint.
- The `[data-cap-action]` selector in `initCapabilityConsole` now wires up all
  demo cards, not just those inside `#cap-button-panel`.

### Fix E: Investor Demo Mode panel

- Collapsible `<details>` element with id `cap-investor-demo-panel`.
- Sections: 30-second pitch, 90-second demo flow, What is real today,
  What is not live yet, Why it matters.
- Collapsed by default; expands on click.

### Fix F: "Why blocked is good" explanation

- New `#cap-why-blocked-section` section in the capabilities panel.
- Explains that "blocked safely" is a feature: you see what Ghoti declined and why.
- Blue left-border callout block.

### Fix G: Roadmap

- New `#cap-roadmap` section with five ordered items:
  1. Obsidian Memory Bridge
  2. Telegram notification bridge
  3. Live agent with approval gate
  4. Real computer-use lane
  5. Hermes Codex provider integration

### Fix H: Approvals page improvement

- Added `#approvals-static-card` before `#approvals-slot`.
- Plain-language explanation: inbox is empty when nothing is running; error means
  unavailable, not broken.
- Collapsed debug block.
- No private paths in the static card.

### Fix I: GitHub page improvement

- Added `#github-static-card` before `#github-slot`.
- Plain language: "does not push, merge, or modify anything".
- Read-only note for each field.
- Collapsed debug block.

### Fix J: "Show me what command to run" copyable area

- New `#cap-show-command` section with a visible code block showing the next
  safe command and a "Copy command" button.
- `capShowCmdCopy()` in app.js handles the clipboard write with a graceful
  fallback when clipboard is unavailable.

---

## Tests

25 tests in `01_projects/runtime_mvp/tests/test_n6_39b_demo_ready_operator_console.py`.

Covers:
- Body overflow hidden, badge word-break.
- Overlay default-collapsed logic.
- Hero section: "What is Ghoti?", 3 bullets, 4 status chips.
- Demo flow: 5 cards present.
- Investor demo panel: all 5 sub-sections present.
- Why blocked is good.
- Roadmap: 5 items present.
- Approvals static card: present, no private paths, friendly message.
- GitHub static card: present, read-only note.
- Show command area: elements and handler present.
- No AI attribution. No provider keys. Context snapshot and docs files exist.

---

## What stayed disabled

No live computer-use, no live agent launch, no account actions, no browser
automation (beyond opening localhost when asked), no MCP, no Telegram, no
Obsidian, no provider/API keys, no auto-submit, no secrets. No third-party code
committed. No AI attribution.

## Next milestones

1. **N+6.39B Codex audit** (audit of this console).
2. **Obsidian Memory Bridge** (N+6.40A).
