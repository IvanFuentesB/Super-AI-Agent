# GitHub Plan

Last updated: 2026-04-05

## Current verified state

- Git is installed.
- No GitHub CLI auth is configured yet.
- No private repo structure exists under the base workspace yet.

## Proposed repo structure later

### Private repo: `sandbox-infra`

Purpose:

- scripts
- setup docs
- sanitized configs
- prompts
- workspace conventions
- automation definitions
- evaluation harnesses

Version:

- yes

### Private repo: `assistant-stack`

Purpose:

- agent configs
- local model configs
- benchmark prompts
- eval results metadata
- orchestration code
- custom tools and wrappers

Version:

- yes

### Optional private repo: `project-docs` or project-specific repos

Purpose:

- actual builds and app work under `01_projects`

Version:

- yes when the project is real

## Keep local only

- model files and large quantized blobs
- raw benchmark outputs that are too large or noisy
- secrets and tokens
- browser/session exports
- app caches
- raw system snapshots that may include sensitive machine detail

## Version by default

- markdown docs
- install scripts
- maintenance scripts
- prompt files
- agent definitions
- benchmark prompts
- benchmark summaries
- sanitized config templates
- repo evaluation docs

## Do not version by default

- `.env` secrets
- auth tokens
- `.ssh`
- browser profiles
- raw Notion app databases
- model caches
- temp exports
- giant binary installers

## Branching and commit rules later

- keep infra changes small and reversible
- separate config changes from app/project changes
- do not auto-commit machine-wide changes without review
- commit docs and rationale with setup changes
- use PRs for anything that changes shared workflow or automation behavior

## GitHub usage pattern later

1. local work and docs first
2. stage sanitized outputs into the right repo
3. commit with clear rollback notes
4. open PRs for infrastructure and automation changes
