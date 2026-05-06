# Codex N+3.56 - Ruflo Install Gate Audit

## Verdict

CONDITIONAL PASS for safety. FAIL for actual Ruflo install readiness in a clean checkout.

The install gate is conservative and does not wire or launch Ruflo runtime. However, the clean merged state does not contain the Ruflo repo package metadata, and the audit shell did not find `npm`, so Ruflo cannot be installed or used from the branch as-is.

## Commands Run

- `python 03_scripts/ruflo_install_gate.py --help`
- `python 03_scripts/ruflo_install_gate.py --status`
- `python 03_scripts/ruflo_install_gate.py --install --dry-run`
- `python 03_scripts/ruflo_install_gate.py --smoke`
- `python 03_scripts/ruflo_install_gate.py --report --dry-run`
- `python 03_scripts/ruflo_install_gate.py --catalog --dry-run`

## Observed Truth

- Ruflo directory: missing in clean audit worktree.
- `package.json`: missing.
- `package-lock.json`: missing.
- `node_modules`: not installed.
- `npm`: not found.
- Node: found, `v22.16.0`.
- Runtime wiring: reported as NO.
- Swarm launch: not run.
- MCP launch: not run.
- `npx`: not run.
- Global install: not run.

## Install Gate Safety

Source inspection shows:

- Install command is `npm ci --ignore-scripts`.
- Lifecycle script detection exists for install-related lifecycle hooks.
- Package-lock is required before `npm ci`.
- Apply path checks for `npm` before install.
- Report and catalog modes are dry-run capable.
- Safety flags report no global install, no runtime wiring, no swarm launch, no MCP launch, and ignore-scripts enabled.

## Capability Gap

The branch cannot honestly claim Ruflo is installed or usable. It can only claim a safety gate exists and correctly blocks when the local Ruflo package is unavailable.

## Direct Answer

Is Ruflo installed/usable yet? No.

Is it safe to install now? Not from this clean checkout. Required prerequisites are missing:

- Ruflo repo/package files under `21_repos/third_party/evals/ruflo`
- `package-lock.json`
- `npm` in PATH
- explicit operator approval

## Safe Future Command After Prerequisites Exist

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

Do not run this until `ruflo_install_gate.py --status` and `--install --dry-run` pass in the real main checkout and the operator explicitly approves.
