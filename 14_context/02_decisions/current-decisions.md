# Current Decisions

Last updated: 2026-04-05

## Workspace

- `AI_Managed_Only` is the only permanent workspace root.
- `AI_Workspace` is temporary only.
- `claw-code` stays in the temporary root for now.

## Tooling

- No major installs until approved.
- First repair/install batch is:
  - Python
  - PowerShell 7
  - `uv`
  - `gh`
  - `pnpm`
- PATH cleanup is explicitly deferred.

## Repo stance

- Claw Code is reference/later-experiment only, not the foundation.
- OpenHarness is a later candidate, not a current base.

## Planning stance

- local-first docs and memory first
- GitHub later for versionable infra
- Notion later for curated summaries and dashboards

## Language stance

- Rust is planned as a later learning/build path
- C++ is planned as a later availability path
- neither gets installed in this phase
