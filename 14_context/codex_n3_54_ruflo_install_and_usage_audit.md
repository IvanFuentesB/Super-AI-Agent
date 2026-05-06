# Codex N+3.54 - Ruflo Install And Usage Audit

## Verdict

AUDIT STATUS: PENDING TARGET BRANCH

The N+3.51 Ruflo install/use hardening cannot be audited because the real Claude N+3.51 implementation branch is not pushed.

## Known Prior Truth

- N+3.49A added a local orchestrator and Ruflo smoke/intake checks.
- N+3.50A branch exists at `56cf614` and added a Ruflo install gate script.
- Ruflo was previously reported as present in the primary workspace under `21_repos/third_party/evals/ruflo`, but that path was not proven as a tracked dependency on clean main.
- Prior package truth observed from the local candidate: package name `claude-flow`, version `3.5.80`.
- Ruflo node dependencies were not installed in the clean audited branch.
- Ruflo runtime, swarm, and MCP were not wired into Ghoti.

## Required N+3.51 Audit Questions

When the N+3.51 branch is pushed, Codex must verify:

- Does `21_repos/third_party/evals/ruflo/package.json` exist in the clean branch or is Ruflo still local-only/untracked?
- Does `package-lock.json` exist?
- Does the install gate require `npm ci --ignore-scripts`?
- Does the install gate refuse global installs?
- Does the install gate refuse `npx` and hidden runtime launch paths?
- Does the install gate inspect lifecycle scripts before install?
- Does it refuse install if unsafe lifecycle scripts exist?
- Is `node_modules/` unstaged and excluded from merge?
- Did Claude avoid launching Ruflo swarm, MCP, browser control, or autonomous runtime?
- Does the report prove local deps are usable, or only document blockers?

## Safe Next Ruflo Command If The Gate Passes

Only after Codex confirms the install gate is safe, the next Claude/operator step may be:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

This command must remain isolated to the Ruflo directory. No global install, `npx`, swarm launch, MCP launch, browser automation, credentials, account actions, or Ghoti runtime wiring should happen in the same milestone.

## Required Hard Gates Before Real Ruflo Use

- No global install.
- No credentials or `.env` reads.
- No external account actions.
- No browser or desktop automation.
- No MCP or swarm launch without explicit future approval.
- No repo writes outside declared lane paths.
- No hidden background processes.
- All commands must be logged.
- First use must be local help/version/read-only only.

## Current Ruflo Verdict

Ruflo remains an important candidate, but it is not proven usable from N+3.51 because the real implementation branch is missing. Treat it as gated and not yet merged.
