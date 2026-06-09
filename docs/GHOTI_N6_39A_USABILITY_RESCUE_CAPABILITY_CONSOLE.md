# GHOTI N+6.39A -- Usability Rescue: Operator Capability Console

**Milestone:** N+6.39A
**Branch:** `feat/ghoti-agent-claude-n6-39a-ghoti-usability-rescue`
**Status:** Implemented (feature branch; not merged)

---

## What was confusing before

- `ghoti_product_launcher.py --start-dashboard --open-dashboard` could crash with
  `KeyError: launcher_version` in the human printer.
- `--start-dashboard --json` returned `ok=false`, `port_in_use=true` and
  "port 3210 is already in use by another process" even when the Ghoti dashboard
  was already running and answering HTTP 200.
- `node server.js` crashed with a raw `EADDRINUSE` stack trace when the dashboard
  was already up.
- The dashboard opened on a dense page with no plain-language answer to
  "what can I actually do?".
- The bottom-right floating box ("Ghoti degraded" / "No visible target") was
  always on screen and could not be hidden or collapsed.
- The Approvals page could show a raw access-denied error as a big ugly block.

## What was fixed

1. **Launcher human printer is crash-proof.** Every field is read with `.get()`
   and a default, and there is a generic fallback for unknown action shapes.
   A missing `launcher_version` can no longer raise `KeyError`.
2. **Already-running dashboard is detected truthfully.** When the port is busy,
   the launcher now probes `GET /api/product-control/status`. If the Ghoti
   dashboard answers, it returns `ok=true`, `already_running=true`,
   `detected_via="health_probe"` and (with `--open-dashboard`) opens the browser.
3. **Unknown port occupant gives a clear, non-destructive warning.** If the port
   is held by something that is not the Ghoti dashboard, the launcher returns a
   clear error plus a safe *inspect* command. It never auto-kills anything.
4. **`node server.js` handles `EADDRINUSE` gracefully** with a friendly message
   that tells you the dashboard is probably already running, and how to inspect
   the listener safely.
5. **New Operator Capability Console** (default landing page) shows, in plain
   language: what Ghoti can do now, what is safe to run, what is dry-run only,
   what is blocked, and what is not built yet.
6. **The bottom-right overlay can be collapsed and hidden** (per-session, stored
   in `localStorage`), with a small restore chip to bring it back.
7. **The Approvals page now shows a friendly card** ("Approval inbox unavailable -
   no action needed unless you expected approvals") with the raw error tucked
   into a collapsed "Debug details" block.

---

## How to open the dashboard

```bash
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
# then open:
http://127.0.0.1:3210
```

The Home / Capabilities page is the default landing view.

## Why "port in use" can mean "already running"

Port 3210 being busy is usually just the Ghoti dashboard already running. The
launcher now confirms this by reading `GET /api/product-control/status`. If that
returns the Ghoti product JSON, the launcher treats it as *already running*
(`ok=true`) instead of an error. Only a non-Ghoti occupant produces a warning.

---

## What Ghoti can do today (safe, local)

- Check repo safety with the public security audit (warnings, no blockers).
- Generate a repo map / context pack for handoff.
- Run local model / Ollama worker status (exact truth, nothing faked).
- Run a safe claude-swarm fixture replay (5 tasks / 3 groups / 0 overlaps,
  no provider, no API key, no external CLI).
- Produce Claude / Codex handoff packets.
- Inspect external tools safely (read-only static scan).

## What Ghoti cannot do yet

- Live agents
- Telegram commands (planned later; notification-only first)
- Obsidian bridge (not implemented yet)
- Real computer-use
- Account actions
- Auto-merge

---

## What buttons are safe

Every button in the "What can I click?" panel calls only an existing safe local
endpoint or script: Refresh status, Run Safe Check, Run Public Audit, Run Repo
Map, Run Local Worker Status, Run Fixture Replay Check, Show Hermes Packet
Status, Copy next safe command. None of them launch agents, touch accounts, use
MCP or Telegram, automate a browser, or call a provider/API.

## What the bottom-right overlay does now

- A collapse button (minimize the body) and a hide button ("hide for this
  session"). When hidden, a small "Ghoti status" chip lets you bring it back.
- The collapsed/hidden choice persists in `localStorage`.
- Idle is treated as normal and calm, not as an error.

## How to run safe checks

- Click **Run Safe Check** (fast mode) for a quick live read, or use the
  buttons in the "What can I click?" panel.
- Backend endpoints:
  - `GET /api/product-control/capabilities` -- static capability cards (instant).
  - `POST /api/product-control/run-capability-check` -- runs safe checks
    (`{"mode":"fast"}` default, `{"mode":"full"}` optional). Writes the latest
    result to repo-local `runtime_data/` (gitignored).
  - `GET /api/product-control/latest-capability-check` -- the cached last run.

If `--context-pack` is slow on your machine, that does not fail this milestone;
it is surfaced as a warning. Future hardening can cache it.

---

## Capability status labels (plain language)

| Backend term | Shown as |
|--------------|----------|
| static_scan_only | Inspected only, not executed |
| dry_run_available | Safe demo/check available |
| roadmap_only_not_wired | Planned, not connected |
| manual_bridge_ready | Manual setup guide exists, no live automation |
| blocked safely | Ghoti refused to run something unsafe |
| idle | Waiting for you; nothing is running |

---

## What stayed disabled

No live computer-use, no live agent launch, no account actions, no browser
automation (beyond opening localhost when asked), no MCP, no Telegram, no
Obsidian, no provider/API keys, no auto-submit, no secrets. No third-party code
committed. No AI attribution.

## Next milestones

1. **Obsidian Memory Bridge** (after this capability console).
2. **Telegram notification bridge** (after Obsidian; notification-only first).

---

## Codex audit target

`audit/ghoti-agent-codex-n6-39a-ghoti-usability-rescue`
