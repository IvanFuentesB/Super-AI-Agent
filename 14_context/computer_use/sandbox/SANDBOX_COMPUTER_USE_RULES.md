# Sandbox Computer-Use Rules (N+6.13A)

These rules govern the first local **sandbox computer-use action harness**. The
harness is **sandbox only**. It plans and dry-runs actions against a local,
offline HTML target. It does **not** drive a live browser, does **not** control
the desktop, and does **not** perform real clicks or typing this milestone.

## What this harness is

- A local sandbox target: `sandbox_target.html` (offline, no external resources).
- A local observation fixture: `sandbox_observation_fixture.json` (`local_only: true`).
- A planner that turns the observation into a JSON action plan.
- A runner that, by default, **dry-runs** the plan (reports what it would do and
  performs nothing). An optional `--allow-sandbox-action` mode runs the plan as an
  in-memory **simulation** against a model of the local target only.

## What is allowed now

- Read the local fixture and the local sandbox HTML.
- Produce a dry-run action plan that requires human approval.
- Simulate the plan against an in-memory model of the local sandbox target.

## What is NOT enabled (blocked actions)

- Live browser or live website control. Live computer-use against real sites.
- Account login automation, cart, purchase, payment, money, or trading.
- CAPTCHA, bot, cookie, or cloak bypass. Stealth or proxy automation.
- Arbitrary desktop or window control. Real click, real typing, or hotkeys.
- Arbitrary shell execution. Installing dependencies. Running third-party repo code.
- Docker/QEMU/KASM runtime. External APIs, accounts, or telemetry.

Real click and real typing stay disabled. No real OS action is performed.

## Strict confinement and why real action stays simulated

With the Python standard library alone, real mouse/keyboard input cannot be
**strictly confined** to the generated local sandbox target: OS-level input would
reach whatever window is focused. Because strict confinement cannot be guaranteed,
`--allow-sandbox-action` keeps the action **simulated** and reports
`sandbox_action_not_performed_reason: strict confinement not yet guaranteed`.

## Feature flags and kill switch

All risky capabilities are gated by `feature_flags_sandbox_computer_use.json`.
Every risky flag defaults to `false`; `sandbox_computer_use_dry_run_enabled`
defaults to `true`. `global_kill_switch_engaged` is `true` and overrides
everything. Human approval is required before any future real action.

## Attribution (design inspiration only; no code copied)

Patterns adapted as design inspiration only, from repos statically inspected in
N+6.12A — no third-party code is copied:

- **TryCUA / CUA Driver** (MIT) - capability/policy separation; sandbox isolation.
- **Browser Harness** (MIT) - thin observe-then-act loop.
- **Vercel agent-browser** (Apache-2.0) - discrete, explicit action commands.
- **Ruflo / claude-flow** (MIT) - coordinator/worker hand-off with local memory.

## Next step (N+6.13B)

A future, separately approved and Codex-audited milestone (N+6.13B) may introduce
a strictly confined sandbox executor (for example, a local headless renderer the
harness fully owns) so that a real sandbox-only action can be performed without
risk of touching any other window. Until then, the harness stays dry-run and
simulation only.
