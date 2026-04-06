# Local vs Sync Boundaries

## Keep local only

- secrets
- tokens
- `.ssh`
- browser profiles
- raw session databases
- raw Notion application data
- large model blobs
- temporary scratch logs
- machine-specific noisy dumps unless sanitized

## Good GitHub candidates later

- scripts
- prompts
- sanitized configs
- markdown docs
- repo evaluations
- benchmark prompts
- benchmark summaries
- automation definitions
- agent templates

## Good Notion candidates later

- setup summaries
- decision summaries
- repo verdicts
- install tracker
- automation ideas
- project dashboards
- experiment summaries

## Rule of thumb

If a file is sensitive, noisy, machine-specific, or hard to review in diffs, keep it local.

If a file is structured, reusable, and useful in review, it is a GitHub candidate.

If a file is summary-level and useful for planning or dashboards, it is a Notion candidate later.
