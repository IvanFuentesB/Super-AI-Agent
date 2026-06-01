# Computer-Use Stack - Static Intake Report (N+6.12A)

**Priority:** critical (explicit second priority for N+6.12A)
**Type:** umbrella grouping; members tracked separately
**Members:** UI-TARS, Browser Harness, Vercel agent-browser, TryCUA / CUA Driver, Browser-use

The "computer-use stack" is not one repo. It is a family of approaches for letting
an agent perceive a screen and (eventually, under approval) act on it. Each member
has its own report in this folder. None is runtime-wired; the
`computer_use_enabled` flag stays `false`.

## Members at a glance

| Member | License | Cloned | Commit | Report |
|--------|---------|--------|--------|--------|
| UI-TARS | unknown | no | - | `ui_tars_n6_12a.md` |
| Browser Harness | MIT | yes | `6d20866` | `browser_harness_n6_12a.md` |
| Vercel agent-browser | Apache-2.0 | yes | `b4f2f37` | `vercel_agent_browser_n6_12a.md` |
| TryCUA / CUA Driver | MIT | yes | `4c54f43` | `trycua_cua_driver_n6_12a.md` |
| Browser-use | MIT | no (deferred) | - | (deferred; see manifest) |

## Shared useful patterns

1. **Observation-first** screen parsing before any action (aligns with the N+5.0A /
   N+6.5A observation work already in the repo).
2. **Approval-gated action** with a sandboxed desktop/browser.
3. **Capability/policy separation** so control is declared and gated, not implicit.

## Shared risks (all kept disabled)

Live desktop control (click/type/hotkeys), live browser control over CDP, container
runtimes (Docker/QEMU/KASM), global native-binary installs, model-provider/network
calls, and - in the cloud variants - stealth/captcha/proxy features that conflict
with Ghoti's no-bypass policy.

## Extraction

A single inert contract, `03_scripts/external_adapters/computer_use_adapter_contract.py`,
documents the observe -> plan -> action loop as disabled capability flags
(`click_enabled` / `type_enabled` / `hotkeys_enabled` / `live_browser_enabled` /
`desktop_control_enabled` / ... all `false`), with stealth/captcha/proxy
**permanently refused**. No member's code is copied. Apache-2.0 (agent-browser)
would require a `NOTICE` only if its code were reused; none is.

## First safe next test

Treat each member separately under its own feature flag; keep computer-use disabled
behind the global kill switch. For any member, the next step is read-only doc/source
review (README, manifest, Dockerfile/Cargo.toml) - no build, no run, no control.
