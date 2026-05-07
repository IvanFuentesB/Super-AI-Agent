# Ruflo Install Gate — N+3.50A Tooling Doc

Script: `03_scripts/ruflo_install_gate.py`
Status: IMPLEMENTED — stdlib only, no external deps

## Purpose
Manages isolated Ruflo npm dependency install and smoke checks.
Blocks any install that would run lifecycle scripts (`preinstall`, `postinstall`, `prepare`, etc.).
Ruflo (claude-flow v3.5.80) has NONE of these — safe for `npm ci --ignore-scripts`.

## Commands
| Command | Effect |
|---|---|
| `--status` | Print Ruflo dir, package.json info, lifecycle check, npm version |
| `--install --dry-run` | Print exact `npm ci --ignore-scripts` command, no execution |
| `--install --apply` | Run `npm ci --ignore-scripts` inside Ruflo dir only |
| `--smoke` | Read-only checks — package, node_modules, package-lock, npm version |
| `--report --dry-run` | Preview JSON/markdown report |
| `--report --apply` | Write JSON + markdown to `05_logs/ruflo_smoke/<run_id>/` |

## Safety Rules
- No global npm install
- No `npx`, no MCP launch, no swarm launch, no runtime wiring
- Lifecycle scripts block install entirely until explicit override (not implemented)
- Reports go to 05_logs/ and are not staged unless explicitly part of milestone docs

## N+3.50A Status
- node_modules: NOT installed (run `--install --apply` with operator approval)
- Lifecycle scripts: NONE detected
- npm version: not found in PATH at validation time (node.js available via direct path)
