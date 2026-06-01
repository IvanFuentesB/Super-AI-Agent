# Ghoti N+6.14A — Confined Local Browser Sandbox Action Runner

## What this milestone adds

N+6.14A makes Ghoti's computer-use capability one careful step more real than
N+6.13A, while staying inside a hard local sandbox.

- **N+6.13A** planned an action and, with an explicit flag, ran an *in-memory
  simulation* of the click against a Python model of the page. No browser was
  ever started; nothing left the process.
- **N+6.14A** performs a *real DOM-level action* inside a *real, fully confined,
  local browser*. It launches a headless Chromium-family browser (Chrome or Edge)
  with a throwaway temporary profile, points it at a local `file://` sandbox page,
  and drives it over a 127.0.0.1-only DevTools channel using a small,
  standard-library WebSocket client. The action sets the note field, clicks the
  button through the page's own DOM, and reads back the result.

This is real automation of a *local, offline page we ship ourselves* — and
nothing more.

## Exactly what it does

When `--allow-local-browser-sandbox` is passed and every confinement check holds,
the runner performs one scripted action in
`14_context/computer_use/sandbox/sandbox_target.html`:

1. set `#note-input` value to `GHOTI_OK`,
2. click `#status-button` via DOM `click()`,
3. read back `#status-output` and confirm it became `GHOTI_OK`.

`goal_satisfied` is true only when both the note and the status read back as
`GHOTI_OK`. The default mode is dry-run, which launches no browser and performs
no action.

## How it stays safe

- **Not live web automation.** `http://` and `https://` targets, and anything
  with a `://` scheme, are rejected before any browser starts. The runner never
  navigates to a website.
- **Not account control.** No login, no credentials, no account context, no
  outbound API. The page is a local file we author.
- **No OS-level input.** The note is set and the button clicked through the DOM
  inside the browser. The runner never moves the mouse, never presses a key, and
  never uses any operating-system keyboard or mouse interface.
- **Local sandbox file only.** The target must resolve to a file under
  `14_context/computer_use/sandbox/`. Paths outside that root are rejected. The
  HTML is scanned for external/network resource references and refused if any are
  found, so the action only ever runs against a fully offline page.
- **Throwaway profile only.** The browser uses a fresh temporary user-data
  directory created with `tempfile.mkdtemp(...)` and deleted in a `finally`
  block. The runner never uses a normal user browser profile and never attaches
  to an already-running browser session.
- **Loopback DevTools only.** All control traffic is to `127.0.0.1`; a
  non-loopback DevTools host is refused. No network is used beyond that loopback
  channel.
- **Standard library only.** No third-party packages, and specifically no
  Selenium, Playwright, pyautogui, or browser-use. The DevTools WebSocket client
  is a minimal in-repo standard-library implementation.
- **Explicit opt-in, safe degradation.** Dry-run is the default. The browser is
  launched only with the explicit flag and only when confinement holds. If no
  browser or DevTools endpoint is reachable, the runner performs no action and
  returns a safe `blocked_or_unavailable_reason`; it never falls back to anything
  less safe.

## Feature flags and kill switch

The dedicated policy file
`14_context/computer_use/sandbox/feature_flags_confined_browser_sandbox.json`
keeps every risky flag `false`
(`confined_browser_sandbox_enabled`, `confined_browser_cdp_enabled`,
`confined_browser_dom_action_enabled`, `live_browser_navigation_enabled`,
`os_level_input_enabled`) with `global_kill_switch_engaged` and
`strict_confinement_required` `true`. The shared example template
`23_configs/ghoti_feature_flags.example.json` carries the same flags, all
`false`, as the disabled-by-default public default. The flags are policy/posture;
the action itself additionally requires the explicit CLI opt-in and full
confinement.

## Relationship to statically inspected patterns

This runner is original code. It only *adapts patterns* observed during the
N+6.12A static inspection of public repositories; no third-party code was copied
or vendored:

- **TryCUA / CUA Driver (MIT)** — capability/policy separation and sandbox
  isolation as a first-class concept.
- **Browser Harness (MIT)** — a thin observe-then-act loop over a single page.
- **Vercel agent-browser (Apache-2.0)** — discrete, explicit commands issued over
  a DevTools channel.
- **Ruflo / claude-flow (MIT)** — coordinator/worker hand-off backed by local
  memory.

## What remains disabled

Live website navigation; any `http(s)://` target; account login automation;
CAPTCHA solving and bot-detection bypass; stealth/proxy automation; OS-level
mouse/keyboard input; arbitrary window control; arbitrary shell execution;
third-party repository code being run; dependency installation; use of a normal
user browser profile; Docker runtime; and outbound APIs all stay blocked. Every
risky feature flag defaults to `false`, and the global kill switch overrides
everything.

## Next step

`N+6.14B / N+6.15`: harden the confined DevTools utility (or a local Gemma-worker
driver, depending on the audit outcome) under separate review before any
non-sandbox target is ever considered. Until then the harness stays
local-sandbox-only.
