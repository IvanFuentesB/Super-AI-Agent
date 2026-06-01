# Ghoti N+6.13A Sandbox Computer-Use Action Harness

## Purpose

N+6.13A is the first milestone where Ghoti moves beyond observation-only toward a
**local sandbox computer-use action harness** - without becoming unsafe. It adds a
local sandbox target, an action planner, a dry-run runner, and an optional
in-memory sandbox simulation. It is **sandbox only**. There is **no live browser**
and **no live computer-use** against real websites, no account control, no
arbitrary desktop control, and no full autonomy this milestone.

This milestone builds on the N+6.12A Ruflo + computer-use repo intake: it reuses
those **statically inspected** patterns and the disabled adapter contracts as
design inspiration, with attribution and no third-party code copied.

## Dependency on N+6.12A

This branch is built on the N+6.12A feature branch
(`feat/ghoti-agent-claude-n6-12a-ruflo-computer-use-repo-intake`,
commit `4e81610`), which was not yet merged to `main` at the time of writing.
N+6.13A therefore depends on N+6.12A landing first. The N+6.12A static intake,
the `computer_use_adapter_contract.py` disabled flags, and the per-repo reports are
the source material reused here.

## Scope

- A local sandbox target: `14_context/computer_use/sandbox/sandbox_target.html`
  (offline; no external scripts, styles, network, login, or resources).
- A local observation fixture: `sandbox_observation_fixture.json` (`local_only: true`,
  `live_website: false`, `account_context: false`).
- A planner: `03_scripts/computer_use_sandbox/sandbox_action_planner.py` (stdlib
  only) that emits a JSON action plan (`target: sandbox_only`,
  `requires_human_approval: true`, `dry_run_default: true`).
- A runner: `03_scripts/computer_use_sandbox/sandbox_action_runner.py` (stdlib
  only) that dry-runs by default and performs nothing.
- A check: `03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1` that
  emits JSON status.
- Rules + feature flags under `14_context/computer_use/sandbox/`.

## What is NOT enabled (blocked actions)

- Live browser / live website control. Live computer-use against real sites.
- Account login automation, cart, purchase, payment, money, or trading.
- CAPTCHA / bot / cookie / cloak bypass. Stealth or proxy automation.
- Arbitrary desktop or window control. Real click, real typing, or hotkeys.
- Arbitrary shell execution. Installing dependencies. Running third-party repo code.
- Docker / QEMU / KASM runtime. External APIs, accounts, or telemetry.

Real click stays disabled. Real typing stays disabled. No real OS action is
performed. No desktop was controlled.

## The action loop (observe -> plan -> dry-run -> simulate)

1. **Observe**: read the local fixture (mocked observation of the local target).
2. **Plan**: the planner emits ordered actions - type `GHOTI_OK` into `note-input`,
   then click `status-button` - each marked `requires_human_approval: true`.
3. **Dry-run**: the runner reports what it would do and performs nothing
   (`action_performed: false`).
4. **Simulate** (optional, `--allow-sandbox-action`): the runner applies the plan
   to an in-memory model parsed from the local sandbox HTML and confirms the goal
   is satisfied locally. It still performs no real action.

## Why real action stays simulated (and the N+6.13B next step)

With the Python standard library alone, real mouse/keyboard input cannot be
**strictly confined** to the generated local sandbox target: OS-level input would
reach whatever window is focused. Because strict confinement cannot be guaranteed,
`--allow-sandbox-action` keeps the action simulated and reports
`sandbox_action_not_performed_reason: strict confinement not yet guaranteed`.

The clear next step is **N+6.13B**: a separately approved and Codex-audited
milestone that introduces a strictly confined sandbox executor (for example, a
local renderer the harness fully owns) so a real sandbox-only action can be
performed without risk of touching any other window.

## Feature flags and kill switch

Risky capabilities are gated by
`14_context/computer_use/sandbox/feature_flags_sandbox_computer_use.json`, where
every risky flag defaults `false` and `sandbox_computer_use_dry_run_enabled`
defaults `true`. The same sandbox flag keys also appear in
`23_configs/ghoti_feature_flags.example.json` in that file's safe all-off baseline
(every sandbox flag `false`, matching its "disabled by default" convention, which
keeps `dry_run` `false` there). `global_kill_switch_engaged` is `true` and
overrides everything. Human approval is required before any future real action.

## Reuse with attribution (no code copied)

Design inspiration only, adapted from repos **statically inspected** in N+6.12A -
no third-party code is copied or vendored:

- **TryCUA / CUA Driver** (MIT) - capability/policy separation; sandbox isolation.
- **Browser Harness** (MIT) - thin observe-then-act loop.
- **Vercel agent-browser** (Apache-2.0) - discrete, explicit action commands.
- **Ruflo / claude-flow** (MIT) - coordinator/worker hand-off with local memory.

## Safety summary

The harness is local-only and fixture-only. It does not install anything, does not
execute external repo code, does not start a UI-TARS or any third-party runtime,
does not control the desktop, does not click or type or press hotkeys for real,
and does not call live APIs or accounts. Approval gates are intact and unchanged.
The work is on a feature branch only; `main` is not pushed.
