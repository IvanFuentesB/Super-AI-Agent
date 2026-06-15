# Ruflo Productivity Prompts

Ruflo / `claude-flow` is an inspected productivity candidate at
`21_repos/third_party/evals/ruflo`. Its package metadata reports version
`3.5.80`, binary name `claude-flow`, and MIT license. The clone is gitignored
and not committed. Command syntax remains uncertain; do not launch an open-ended
swarm.

## Planning prompt

> Produce a dry-run task decomposition for `<goal>`. Return tasks, dependencies,
> file ownership, parallel groups, risks, and validation. Do not launch agents.

## Repo-analysis prompt

> Produce a read-only repo analysis plan for `<scope>`. Name the smallest source
> files and tests to inspect, expected patterns, and questions to resolve. Do
> not execute tools or modify files.

## Handoff prompt

> Convert this task result into a compact Claude Code implementation handoff and
> a separate Codex audit handoff. Preserve source paths, branch/commit truth,
> blockers, and test evidence.

## Safe-use boundary

Claude Code and Codex may use reviewed Ruflo output as a planning input. Ghoti
may later govern Ruflo through the approval queue and Rust guard. Live swarms,
hooks, MCP, account actions, and auto-submit remain blocked.
