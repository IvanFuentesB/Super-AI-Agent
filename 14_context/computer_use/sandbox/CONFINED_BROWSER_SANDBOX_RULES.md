# Confined Local Browser Sandbox Rules (N+6.14A)

These rules govern `03_scripts/computer_use_sandbox/confined_browser_sandbox_runner.py`.
They are stricter than, and build on, the N+6.13A sandbox computer-use rules in
`SANDBOX_COMPUTER_USE_RULES.md`.

## What changed since N+6.13A

- **N+6.13A** dry-ran a plan and, with an explicit flag, ran an *in-memory
  simulation* of the click against a Python model of the page. No browser was
  ever launched.
- **N+6.14A** performs a *real DOM-level action* inside a *real, but fully
  confined, local browser*: a headless Chromium-family browser launched with a
  throwaway profile, pointed at a local `file://` sandbox page, driven only over
  a loopback DevTools channel. It is more real, and still safe.

## Hard confinement rules

1. **Local file only.** The target must resolve to a file under
   `14_context/computer_use/sandbox/`. Anything with a `://` scheme, or any path
   that resolves outside the sandbox root, is rejected before any browser starts.
2. **No live web.** `http://` and `https://` targets are rejected. The runner
   never navigates to a website and never touches an account.
3. **Offline target only.** The sandbox HTML is scanned for external/network
   resource references (`<script src>`, `<link href>`, `<img src>`, `<iframe
   src>`, protocol-relative `src`, `@import`, any `http(s)://`). If any are
   found, the action is refused.
4. **Throwaway profile only.** The browser runs against a fresh
   `tempfile.mkdtemp(...)` user-data directory that is deleted in a `finally`
   block. The runner never uses a normal user browser profile and never attaches
   to an already-running browser session.
5. **Loopback DevTools only.** The runner talks to `http://127.0.0.1:<port>`
   and a `ws://127.0.0.1:<port>` DevTools socket. A non-loopback DevTools host is
   refused. No network is used beyond that loopback channel.
6. **No OS-level input.** The note is set and the button is clicked through the
   page's own DOM (`element.value`, `element.click()`) inside the browser. The
   runner never moves the mouse, never presses keys, and never uses any OS
   keyboard/mouse API.
7. **Standard library only.** No third-party packages. No Selenium, Playwright,
   pyautogui, or browser-use. The DevTools WebSocket client is a minimal,
   in-repo, standard-library implementation.
8. **Explicit opt-in.** Dry-run is the default. A browser is launched only when
   `--allow-local-browser-sandbox` is passed *and* every confinement check above
   holds. If confinement cannot be guaranteed, the runner performs no action and
   returns a safe blocked/unavailable result.
9. **Graceful, safe degradation.** If no local browser is found, or the local
   DevTools endpoint never becomes reachable, the runner returns
   `dom_action_performed: false` with a `blocked_or_unavailable_reason`. It never
   falls back to anything less safe.

## The one confined action

When enabled and confined, the runner performs exactly one scripted action in
the local sandbox page:

1. set `#note-input` value to `GHOTI_OK`,
2. click `#status-button` via DOM `click()`,
3. read back `#status-output` and confirm it became `GHOTI_OK`.

`goal_satisfied` is true only when both the note and the status read back as
`GHOTI_OK`.

## Permanently blocked this milestone

Live website navigation; any `http(s)://` target; account login automation;
CAPTCHA solving or bot-detection bypass; stealth/proxy automation; OS-level
mouse/keyboard input; arbitrary window control; arbitrary shell execution;
third-party repository code being run; dependency installation; use of a normal
user browser profile; Docker runtime; outbound APIs. Every risky feature flag
defaults to `false`, and the global kill switch overrides everything.

## Feature flags

The dedicated policy file is
`14_context/computer_use/sandbox/feature_flags_confined_browser_sandbox.json`.
Risky flags default to `false`; `global_kill_switch_engaged` and
`strict_confinement_required` default to `true`. The shared example config
`23_configs/ghoti_feature_flags.example.json` carries the same flags, all
`false`, as the disabled-by-default public template.

## Next step

`N+6.14B / N+6.15`: harden the confined DevTools utility (or a local
Gemma-worker driver) under separate audit before any non-sandbox target is ever
considered. Until then the harness stays local-sandbox-only.
