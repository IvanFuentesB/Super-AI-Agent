# Prioritized Next Actions

Last updated: 2026-04-05

## Low-risk next steps

1. Keep documenting the sandbox inside this workspace as changes happen.
2. Keep `AI_Managed_Only` as the only permanent root and treat `AI_Workspace` as temporary until an approved cleanup phase.
3. Approve a small foundation toolchain repair batch later:
   - fix Python
   - install PowerShell 7
   - install `uv`
   - install `gh`
4. After that, approve a local-model starter batch later:
   - install Ollama
   - test Gemma 4 E2B or E4B

## Medium-risk next steps

1. Clean stale `Navif` user paths out of machine PATH.
2. Re-home or re-clone `claw-code` under `AI_Managed_Only\21_repos\core` only in a later approved cleanup phase.
3. Add a minimal editor extension set.
4. Connect GitHub auth.

## High-risk or later-only steps

1. Source-profile access into `C:\Users\Navif`
2. Browser migration
3. OneDrive behavior changes
4. Registry changes
5. WSL2 and Docker
6. Large harness installs

## First clean build path

1. Fix the sandbox basics
2. Add GitHub hygiene
3. Add one local model runtime
4. Add one editor integration
5. Add scripts and logs
6. Only then evaluate heavier harness layers

## Things to keep manual

- destructive system changes
- browser/account imports
- Git credential changes
- anything that touches the other Windows account

## Safe future automations

- environment snapshots
- repo state reports
- docs sync queue preparation
- benchmark result collection
