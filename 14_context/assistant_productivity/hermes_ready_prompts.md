# Hermes Ready Prompts

Hermes is the cheap local status, memory, and handoff summarizer. It does not
execute commands, configure providers, touch accounts, or control browsers.

## Daily Ghoti control-room summary

> Read the latest committed status, Agent OS evidence, compact memory, open
> handoffs, and branch reports. Return current main SHA, active lanes, completed
> capabilities, blockers, top five next actions, and uncertainty. Do not run
> anything.

## Summarize Claude Code report

> Compress `<Claude report path>` into scope, branch/commit, files changed,
> validation, safety boundaries, unfinished work, and the exact Codex audit
> target. Link every claim to the source path.

## Summarize Codex audit

> Compress `<Codex audit path>` into verdict, blockers, checks reproduced,
> branch/commit truth, push/merge status, and exact next action. Preserve failed
> checks and uncertainty.

## Summarize MCP status

> Read MCP templates and strategy configs. Report which connectors are
> documented, disabled, credentialed, read-only candidates, blocked, or
> source-needed. Do not configure or authenticate anything.

## Summarize tool-stack status

> Read the acceleration stack status, tool registry, skills registry, and
> install queue. Return available tools, missing tools, P0/P1 priorities,
> inspect-first items, and blocked items.

## Summarize Ruflo status

> Read the Ruflo intake/productivity records. Report inspected path, version,
> binary name, safe productivity uses, uncertain syntax, and blocked live swarm
> actions. Do not launch Ruflo.

## Top five next actions

> From committed repo truth only, rank five narrow next actions by impact,
> dependency readiness, risk, and verification cost. Each action must name an
> owner, branch suggestion, files, and done signal.

## Create handoff and detect conflicts

> Create a compact handoff for `<Claude Code or Codex>` containing branch,
> commit, task, files touched, commands/checks reported, blockers, and next
> action. Compare all cited SHAs and branches; flag conflicts or stale claims.
> Do not invent missing values.
