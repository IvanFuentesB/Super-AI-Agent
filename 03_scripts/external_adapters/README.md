# External Adapter Contracts (N+6.12A)

Inert, **non-runtime** contract stubs that capture *patterns* learned from a
read-only static inspection of external repositories. Nothing in this directory
runs, installs, imports, or controls anything. These files exist so that a future,
separately-approved milestone has a clean, disabled-by-default starting point with
attribution and security context already recorded.

## What "contract" means here

- **No live computer-use yet.** No browser is driven, no desktop is controlled, no
  pointer/key is pressed, no network call is made. Every capability flag defaults
  to `False` and is additionally overridden by a global kill switch.
- **Static-inspected, not blindly run.** The upstream repos were cloned into
  `21_repos/third_party_static/` for read-only inspection only (git-ignored, never
  installed, never executed). See the manifest under
  `14_context/tool_intake/repo_intake_manifests/` and the per-repo reports under
  `14_context/tool_intake/repo_intake_reports/`.
- **Reuse with attribution and license awareness.** Where a pattern was reused, the
  source project, its URL, and its license are named in the file, and we record
  whether any code was copied (it was not - patterns are re-expressed from scratch).
- **Feature flags and kill switches.** Each contract exposes explicit disabled
  flags and a global kill switch so the disabled posture is auditable.

## Files

| File | Source inspiration | License | Code copied? | State |
|------|--------------------|---------|--------------|-------|
| `ruflo_adapter_contract.py` | Ruflo / claude-flow (`ruvnet/ruflo`) | MIT | No - re-expressed | Disabled (`RUFLO_SWARM_ENABLED = False`) |
| `computer_use_adapter_contract.py` | UI-TARS, Browser Harness, Vercel agent-browser, TryCUA/CUA, Browser-use | MIT / Apache-2.0 | No - patterns only | Disabled (`COMPUTER_USE_ENABLED = False`) |

### `ruflo_adapter_contract.py`

Re-expresses one safe, non-runtime pattern from Ruflo: role-labeled single-purpose
agents, explicit coordinator/worker separation, shared *local* memory hand-offs,
and declared (not implicit) skills. **No Ruflo code is vendored.** Ruflo is MIT
(reuse would be permitted) but has a documented supply-chain history - an obfuscated
malicious npm pre-install script, an MCP prompt-injection issue (#1375), and a
remediated SQL-injection history - so Ghoti re-expresses only the architecture idea
and never installs, imports, or runs Ruflo.

```
python 03_scripts/external_adapters/ruflo_adapter_contract.py --status --json
python 03_scripts/external_adapters/ruflo_adapter_contract.py --describe --json
```

### `computer_use_adapter_contract.py`

Documents the observe -> plan -> action loop shared by the inspected computer-use
stacks, as disabled capability flags. Field names match the repo's existing
observation-adapter convention (`click_enabled` / `type_enabled` / `hotkeys_enabled`,
all `False`). Stealth / captcha-bypass / proxy-rotation are **permanently refused**
under Ghoti's no-bypass policy. Apache-2.0 (agent-browser) would require preserving
`NOTICE`/attribution if any of its code were reused; none is reused, so no `NOTICE`
applies.

```
python 03_scripts/external_adapters/computer_use_adapter_contract.py --status --json
python 03_scripts/external_adapters/computer_use_adapter_contract.py --describe --json
```

## Hard boundaries (this milestone)

No execution of third-party code. No installs (`npm` / `pip` / `pnpm` / `uv`). No
imports of cloned repo modules. No live browser or desktop control. No network or
model-provider calls. No credential/token/cookie reads. No MCP server enablement.
Turning any capability on belongs to a future approved milestone with its own Codex
audit gate.
