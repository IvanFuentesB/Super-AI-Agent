# Codex N+3.53 - Ruflo Install Gate Audit

## Clean Branch Truth

N+3.50A adds `03_scripts/ruflo_install_gate.py`, but a clean checkout of the pushed branch does not include `21_repos/third_party/evals/ruflo`. Therefore the gate cannot find `package.json` or `package-lock.json` in the validated clean branch.

## Local Machine Truth

The main worktree has an untracked local Ruflo clone at `21_repos/third_party/evals/ruflo`. Its `package.json` reports:

- Package name: `claude-flow`
- Version: `3.5.80`
- Bin: `claude-flow`
- Repository: `https://github.com/ruvnet/claude-flow.git`
- Description includes enterprise agent orchestration, swarms, vector memory, and MCP integration.
- Scripts include `v3:swarm`, `v3:security`, `security:audit`, `security:fix`, tests, lint, and build commands.
- Top-level lifecycle scripts were not present in the inspected package snippet.

This local clone is not tracked by Git and is not available in a clean checkout.

## Gate Behavior

`ruflo_install_gate.py` does the right high-level things:

- Detects lifecycle script names such as `preinstall`, `install`, `postinstall`, `prepare`, `prepack`, and related hooks.
- Blocks install when lifecycle scripts are detected.
- Uses `npm ci --ignore-scripts` as the install command.
- Reports `node_modules` and `package-lock.json` status.
- Keeps smoke/report checks read-only unless `--apply` is used for local report writing.
- Does not run `npx`, MCP, swarm, or Ruflo runtime commands.

## Critical Gaps

1. In a clean branch checkout, Ruflo is missing. That makes the install gate a shell around an absent dependency.
2. `--install --apply` is too easy to trigger. It should require a second explicit confirmation flag before npm runs.
3. NPM was not found in the isolated validation environment.
4. `node_modules` is absent and must remain unstaged if an install later occurs.
5. The repo must decide whether Ruflo is intentionally untracked local eval material or whether a manifest/bootstrap step is required to fetch it later. Do not silently assume clean clones have it.

## Safe Install Command

Only after explicit approval and only when the local Ruflo directory exists:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

The stronger gate should require a command like:

```powershell
python 03_scripts/ruflo_install_gate.py --install --apply --confirm-local-ruflo-install
```

## Runtime Wiring Status

- Ruflo runtime: not wired.
- Ruflo swarm: not launched.
- Ruflo MCP: not launched.
- Ruflo live account actions: none.
- Ruflo usable as Ghoti orchestrator: no.

## Verdict

`FAIL FOR USABILITY / CONDITIONAL FOR SAFETY`

The script is safety-aligned, but Ruflo is not installed or clean-checkout available. It is not usable yet.
