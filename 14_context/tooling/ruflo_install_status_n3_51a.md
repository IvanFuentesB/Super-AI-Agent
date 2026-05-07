# Ruflo Install Status — N+3.51A

Generated: 2026-05-06

## Commands Run

```powershell
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/ruflo_install_gate.py --smoke
python 03_scripts/ruflo_install_gate.py --report --dry-run
python 03_scripts/ruflo_install_gate.py --catalog --dry-run
```

## Status

| Item | Value |
|------|-------|
| Ruflo dir | `21_repos/third_party/evals/ruflo` |
| Package | claude-flow v3.5.80 |
| package.json | EXISTS |
| package-lock.json | EXISTS |
| node_modules | NOT INSTALLED |
| Lifecycle scripts | NONE (safe for `npm ci --ignore-scripts`) |
| npm | NOT FOUND on this machine |
| node | v22.16.0 |
| Install blocked | NO (no lifecycle scripts) |

## Automation State

- `--status`: PASS (read-only, no install)
- `--install --dry-run`: PASS (validates install path, no execution)
- `--install --apply`: BLOCKED by missing npm. Install safe if npm installed.
- `--smoke`: PASS (read-only package inspection)
- `--report --dry-run`: PASS
- `--catalog --dry-run`: PASS (reads README, CLAUDE.md, CHANGELOG.md)

## What Is Automated

- Lifecycle script detection (preinstall, postinstall, prepare, etc.)
- package-lock.json presence check
- npm ci --ignore-scripts gate (ready to run when npm available)
- Catalog metadata read (README/CLAUDE/CHANGELOG)

## What Is Still Manual

- npm installation on the machine
- Human decision to run `--install --apply`
- Staging of node_modules (must NOT be staged)

## Blocker

`npm` not found. Install via winget: `winget install --id OpenJS.NodeJS.LTS`
Or install Node.js which includes npm.

## Runtime Wiring

NO — Ruflo is NOT wired to any Ghoti runtime, MCP, or swarm controller.

## Next Step

Install npm, then run: `python 03_scripts/ruflo_install_gate.py --install --apply`
