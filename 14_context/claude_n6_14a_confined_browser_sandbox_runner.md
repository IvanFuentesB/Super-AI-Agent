# Ghoti N+6.14A — Confined Local Browser Sandbox Action Runner (Report)

## Final verdict

**IMPLEMENTED_AND_PUSHED.** A confined, real DOM action now runs inside a real
local browser, fully contained to a local offline sandbox page, with no live web,
no account, and no OS-level input.

## Branch / worktree / base

- **Branch:** `feat/ghoti-agent-claude-n6-14a-confined-browser-sandbox-runner`
- **Worktree:** `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_14a_confined_browser_sandbox_runner`
- **Base main:** `0b6255c5f79596e63368d01518c50f2519f09d45`
  (`docs(ghoti): record n6.13b sandbox computer-use merge gate`)
- **Commit message:** `feat(ghoti): add confined browser sandbox runner`

## Dependency on N+6.13A

N+6.13A is already merged into `main`
(`e775efb` feat → `43ee009` merge → `0b6255c` gate). This branch was created
cleanly from `origin/main`; it does **not** depend on the unmerged N+6.13A
feature branch. The dirty primary worktree was inspected read-only only.

## What changed since N+6.13A

- **N+6.13A** dry-ran a plan and, with an explicit flag, ran an *in-memory
  simulation* of the click against a Python model of the page. No browser was
  launched (`action_performed` always `false`, reason "strict confinement not yet
  guaranteed").
- **N+6.14A** performs a *real DOM action* inside a *real but fully confined
  local browser*: a headless Chromium-family browser launched with a throwaway
  temporary profile, pointed at a local `file://` sandbox page, driven over a
  `127.0.0.1`-only DevTools channel using a small standard-library WebSocket
  client. It is more real, and still safe.

## Files changed

New:

- `03_scripts/computer_use_sandbox/confined_browser_sandbox_runner.py`
- `03_scripts/computer_use_sandbox/check_confined_browser_sandbox.ps1`
- `14_context/computer_use/sandbox/feature_flags_confined_browser_sandbox.json`
- `14_context/computer_use/sandbox/confined_browser_expected_result.json`
- `14_context/computer_use/sandbox/CONFINED_BROWSER_SANDBOX_RULES.md`
- `docs/GHOTI_N6_14A_CONFINED_BROWSER_SANDBOX_RUNNER.md`
- `01_projects/runtime_mvp/tests/test_n6_14a_confined_browser_sandbox_runner.py`
- `14_context/claude_n6_14a_confined_browser_sandbox_runner.md` (this report)

Updated:

- `03_scripts/computer_use_sandbox/README.md` — appended an N+6.14A section.
- `23_configs/ghoti_feature_flags.example.json` — added six confined-browser
  flags, all `false`, preserving the single-true-flag invariant.

## Was the browser action performed or safely unavailable?

**Performed (real, confined).** On this host a Chromium-family browser is
available, so the `--allow-local-browser-sandbox` run launched a confined
headless browser and completed the DOM action.

### Dry-run result (default, no browser)

```
mode               = dry_run
ok                 = true
browser_launched   = false
dom_action_performed = false
os_input_used      = false
live_website       = false
account_context    = false
target_is_local    = true
target_under_sandbox_root = true
requires_human_approval   = true
```

### Allow-local result (confined real action)

```
mode               = local_browser_sandbox
ok                 = true
browser_launched   = true
dom_action_performed = true
note_value         = GHOTI_OK
status_output      = GHOTI_OK
goal_satisfied     = true
temporary_profile_used    = true
temporary_profile_cleaned = true
os_input_used      = false
live_website       = false
account_context    = false
cdp_browser        = Chrome/148.0.7778.179
```

When no local browser or DevTools endpoint is reachable, the same mode returns a
safe result with `dom_action_performed: false` and a `blocked_or_unavailable_reason`
(the test suite accepts either outcome and never requires a browser to exist).

## Result field verification table

| Field | Required | Observed |
|-------|----------|----------|
| `mode` (allow-local) | `local_browser_sandbox` | `local_browser_sandbox` |
| `target_is_local` | `true` | `true` |
| `target_under_sandbox_root` | `true` | `true` |
| `live_website` | `false` | `false` |
| `account_context` | `false` | `false` |
| `os_input_used` | `false` | `false` |
| `browser_launched` | `true` | `true` |
| `dom_action_performed` | `true` | `true` |
| `note_value` | `GHOTI_OK` | `GHOTI_OK` |
| `status_output` | `GHOTI_OK` | `GHOTI_OK` |
| `goal_satisfied` | `true` | `true` |
| `temporary_profile_used` | `true` | `true` |
| `temporary_profile_cleaned` | `true` | `true` |

## Validation

- `git diff --check` — clean. `git show --check --stat HEAD` — clean.
- `node --check` not applicable (no dashboard JS touched this milestone).
- Runner dry-run and allow-local both emit valid JSON (above).
- PowerShell check `check_confined_browser_sandbox.ps1` emits JSON with `ok: true`,
  `dry_run_works: true`, and every risky flag `false`.
- Full N+6 unittest suite: **201 tests, 0 failures** (20 new in N+6.14A; 181
  pre-existing all still passing).
- `public_repo_security_audit.py --run --json` — `safe_to_make_public: true`,
  no blocking findings.
- `ghoti_product_launcher.py --status --json` — `ok: true`.

## Safety summary

- **Standard library only.** No third-party packages; specifically no Selenium,
  Playwright, pyautogui, pynput, or browser-use. The DevTools WebSocket client is
  a minimal in-repo standard-library implementation.
- **Local sandbox only.** URL targets, paths outside the sandbox root, missing
  files, and files referencing external/network resources are all rejected before
  any browser starts.
- **No OS-level input.** The note is set and the button clicked through the page
  DOM. No mouse move, no key press, no OS keyboard/mouse interface.
- **Throwaway profile only.** A fresh `tempfile.mkdtemp(...)` user-data directory,
  deleted in a `finally` block. Never a normal user profile; never an existing
  browser session.
- **Loopback DevTools only.** All control traffic is to `127.0.0.1`; non-loopback
  DevTools hosts are refused; no other network is used.
- **Explicit opt-in, safe degradation.** Dry-run is the default; the browser
  launches only with the explicit flag and only when confinement holds; otherwise
  the runner performs no action and returns a safe result.
- Every risky feature flag defaults `false`; the global kill switch is engaged.

## Direct answers

- **Does the runner now perform a real action (not just simulate)?** Yes — a
  confined DOM action inside a real headless local browser.
- **Was the action confined to the local sandbox page?** Yes — a local
  `file://` page under `14_context/computer_use/sandbox/`.
- **Did it navigate any live website?** No.
- **Did it touch any account / login / credentials?** No.
- **Did it use OS-level mouse/keyboard input?** No.
- **Did it use a normal browser profile?** No — a temporary profile, cleaned up.
- **Did it install anything or use third-party packages?** No — standard library
  only.
- **Did it run third-party repository code?** No.
- **Are approval gates intact?** Yes — the action requires an explicit flag plus
  full confinement, and every risky flag stays `false` by default.

## What remains disabled

Live website navigation; any `http(s)://` target; account login automation;
CAPTCHA solving and bot-detection bypass; stealth/proxy automation; OS-level
mouse/keyboard input; arbitrary window control; arbitrary shell execution;
third-party repository code being run; dependency installation; use of a normal
user browser profile; Docker runtime; and outbound APIs.

## Next step and Codex audit target

- **Next step:** `N+6.14B / N+6.15` — harden the confined DevTools utility (or a
  local Gemma-worker driver, depending on the audit outcome) under separate
  review before any non-sandbox target is considered.
- **Codex audit target branch:**
  `audit/ghoti-agent-codex-n6-14a-confined-browser-sandbox-runner`
