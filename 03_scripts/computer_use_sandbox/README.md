# Sandbox Computer-Use Action Harness (N+6.13A)

Local, sandbox-only computer-use harness: a planner, a runner, and a check. It
plans and dry-runs actions against a local offline HTML target. It does **not**
drive a live browser, control the desktop, or perform real clicks/typing this
milestone. See `14_context/computer_use/sandbox/SANDBOX_COMPUTER_USE_RULES.md`.

## Files

- `sandbox_action_planner.py` - reads a local observation fixture and emits a JSON
  action plan (`target: sandbox_only`, `requires_human_approval: true`).
- `sandbox_action_runner.py` - dry-runs the plan by default (performs nothing).
  `--allow-sandbox-action` runs an in-memory **simulation** against a model of the
  local sandbox target only; it does not control the real OS.
- `check_sandbox_computer_use.ps1` - emits a JSON status of files and flags.

## Run (read-only / dry-run)

```bash
python 03_scripts/computer_use_sandbox/sandbox_action_planner.py \
  --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json

python 03_scripts/computer_use_sandbox/sandbox_action_runner.py \
  --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json

python 03_scripts/computer_use_sandbox/sandbox_action_runner.py \
  --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json \
  --allow-sandbox-action --json

powershell -ExecutionPolicy Bypass -File \
  03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1
```

## Why real action stays simulated

With only the Python standard library, real mouse/keyboard input cannot be
strictly confined to the generated local sandbox target. So `--allow-sandbox-action`
keeps the action simulated and reports
`sandbox_action_not_performed_reason: strict confinement not yet guaranteed`, with
a clear next step for N+6.13B. `action_performed` is always `false`.

## Disabled and blocked

Live browser/website control, account login, CAPTCHA/bot bypass, stealth/proxy,
arbitrary desktop or window control, real click/typing/hotkeys, arbitrary shell
execution, dependency installs, third-party repo code execution, Docker runtime,
and external APIs are all blocked. Every risky feature flag defaults `false` and
the global kill switch overrides everything.

## Attribution

Design inspiration only; no third-party code copied. Patterns adapted from repos
statically inspected in N+6.12A: TryCUA/CUA (MIT), Browser Harness (MIT), Vercel
agent-browser (Apache-2.0), and Ruflo/claude-flow (MIT).

## N+6.14A confined local browser sandbox runner

`confined_browser_sandbox_runner.py` goes one safe step past the N+6.13A
simulation. Where N+6.13A only modelled the click in memory, N+6.14A performs a
**real DOM action inside a real, fully confined local browser**: a headless
Chromium-family browser launched with a throwaway temporary profile, pointed at a
local `file://` sandbox page, and driven over a 127.0.0.1-only DevTools channel
using a standard-library WebSocket client. It is still not live web automation,
account control, or any OS-level input. See
`14_context/computer_use/sandbox/CONFINED_BROWSER_SANDBOX_RULES.md`.

```bash
# Dry-run (default): no browser, no DOM action.
python 03_scripts/computer_use_sandbox/confined_browser_sandbox_runner.py \
  --target 14_context/computer_use/sandbox/sandbox_target.html --json

# Confined action: launches a headless browser with a temporary profile and
# performs the local sandbox DOM action only.
python 03_scripts/computer_use_sandbox/confined_browser_sandbox_runner.py \
  --target 14_context/computer_use/sandbox/sandbox_target.html \
  --allow-local-browser-sandbox --json

powershell -ExecutionPolicy Bypass -File \
  03_scripts/computer_use_sandbox/check_confined_browser_sandbox.ps1
```

The confined action sets `#note-input` to `GHOTI_OK`, clicks `#status-button`
via DOM `click()`, and verifies `#status-output` reads back `GHOTI_OK`. If no
local browser or DevTools endpoint is reachable, the runner performs no action
and returns a safe `blocked_or_unavailable_reason`. Targets that are URLs, sit
outside the sandbox root, are missing, or reference external/network resources
are rejected before any browser starts. All risky flags default `false`; the
global kill switch overrides everything. Next step: `N+6.14B / N+6.15` hardens
the confined DevTools utility under separate audit before any non-sandbox target
is considered.
