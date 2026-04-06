# Agent Memory Guide

## Main memory vs agent memory

### Put it in main memory (`14_context`) when:

- it describes the whole sandbox
- it is a stable decision
- it affects multiple future agents
- it describes workspace conventions
- it summarizes repo classifications or stack direction

### Put it in agent memory (`20_agents/<agent>/memory`) when:

- it is specific to one automation or specialized agent
- it is task-scoped
- it contains operating assumptions for that one agent
- it tracks retries, recent outcomes, or working context for that agent

## Recommended per-agent structure

Each specialized agent should have:

- `memory/`
- `prompts/`
- `configs/`
- `logs/`
- `docs/`
- `tasks/`

## What future automations should store

In `memory/`:

- stable task context
- known constraints
- preferred tools
- approved boundaries

In `tasks/`:

- current queue
- backlog
- open blockers

In `logs/`:

- execution summaries
- errors worth keeping
- last successful run summaries

In `docs/`:

- what the agent is for
- inputs and outputs
- failure modes
- rollback notes

## What should never go to GitHub

- secrets
- tokens
- raw account data
- browser/session material
- private exports that are not sanitized
- unreviewed noisy logs

## What can later mirror into Notion

- decision summaries
- install status
- experiment summaries
- repo evaluations
- automation trackers
- curated agent overviews

## How to keep this from becoming a junk drawer

- keep shared truth in one place
- keep each agent scoped to one real job
- archive stale notes instead of letting folders sprawl
- prefer short structured markdown over giant transcript dumps
- review and prune regularly
