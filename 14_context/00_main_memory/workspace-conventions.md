# Workspace Conventions

## Root rule

Use `C:\Users\ai_sandbox\Documents\AI_Managed_Only` as the only permanent workspace root.

## Organization rule

- stable docs go in `04_docs`
- logs go in `05_logs`
- setup and migration planning go in `12_setup`
- shared sandbox memory goes in `14_context`
- repo checkouts belong in `21_repos` once they are moved or cloned there

## Editing rule

- prefer local markdown and scripts first
- keep files versionable and readable
- avoid dumping random notes into the workspace root

## Security rule

Never commit or mirror:

- secrets
- tokens
- browser data
- auth exports
- raw Notion caches
- machine-specific noisy dumps unless sanitized

## Sync rule

- local markdown is the source of truth first
- GitHub later stores versionable infra, scripts, prompts, configs, and docs
- Notion later stores curated summaries, decisions, trackers, and dashboards
