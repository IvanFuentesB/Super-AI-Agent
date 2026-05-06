# Codex N+3.50 - Ruflo Install Gate

Milestone: N+3.50B - Audit Claude N+3.49A and prepare merge safety verdict

Date: 2026-05-06

## Practical Stance

The user wants Ruflo used, not ignored. The right next step is not runtime wiring. The right next step is an isolated dependency install gate inside the existing Ruflo eval directory, with no credentials, no global install, no MCP launch, no swarm execution, and no connection to Ghoti runtime.

## Current Ruflo Truth

Main workspace path:

```text
C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
```

Observed:

- Path exists in the main workspace.
- Package name: `claude-flow`
- Version: `3.5.80`
- `node_modules`: absent.
- Scripts listed include build/test/lint/security/v3 commands.
- No lifecycle scripts named `preinstall`, `postinstall`, or `prepare` were found by package metadata inspection.
- A direct nested `git rev-parse` hit a Git dubious-ownership warning under the current Windows user. Do not modify global Git safe-directory config without explicit approval.

The detached validation worktree did not contain the local Ruflo eval clone. That is expected because the eval clone is not tracked in the main repo.

## Approved Next Step

Ruflo isolated npm install is approved as the next Claude step only under this exact gate:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

This approval is narrow:

- local eval directory only
- no global install
- no Ruflo runtime
- no MCP server launch
- no Claude API key
- no account connectors
- no background processes
- no writes to Ghoti runtime
- no repo staging of `node_modules`

## Commands Allowed After Install

Only local help/version/read-only commands should be considered after install, and only after the install completes cleanly:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm --version
node --version
npm pkg get name version scripts
```

If a local binary exists after install, inspect help only:

```powershell
npx --no-install claude-flow --help
```

Do not run swarm, MCP, dev server, start, build, test, or any command that could spawn long-running processes until Codex audits the installed dependency surface.

## Hard Gates Before Any Agent Swarm Or Runtime Use

Before Ruflo can control anything:

- No global install.
- No credentials.
- No API keys.
- No external account actions.
- No autonomous desktop/browser control.
- No repo writes outside a declared agent lane.
- No live actions.
- No hidden background processes.
- Log every command.
- Confirm active lane lock before work starts.
- Confirm allowed paths and forbidden paths.
- Confirm no `.env` or secret reads.
- Confirm no MCP server exposed to unintended callers.
- Confirm no Claude/Codex/GitHub connector wiring.
- Confirm no npm scripts run without explicit approval.

## What Not To Do

Do not run:

```powershell
npm run dev
npm run build
npm start
npm run v3:swarm
npm run v3:domains
npm run security:fix
```

Do not connect Ruflo to:

- Claude API
- Claude Code
- Codex
- GitHub
- MCP tools
- live accounts
- browser/desktop control
- email/social/payment/job/giveaway workflows

## Next Claude Recommendation For Ruflo

Add a Ruflo install gate runner, not runtime wiring:

- script name suggestion: `03_scripts/ruflo_install_gate.py`
- default: `--dry-run`
- required write/install mode: `--apply`
- reads package metadata first
- refuses global paths
- refuses if lifecycle scripts exist
- refuses if `.env` or credentials are required
- runs only `npm ci --ignore-scripts` inside the approved eval directory
- writes a local report under `05_logs/ruflo_install_gate/<run_id>/`
- never stages `node_modules`

## Install Gate Verdict

Ruflo isolated npm install is conditionally approved for the next Claude step under the exact command and hard gates above. Ruflo runtime wiring is not approved.
