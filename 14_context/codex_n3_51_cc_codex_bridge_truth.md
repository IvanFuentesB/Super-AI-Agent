# Codex N+3.51 - Claude Code / Codex Bridge Truth

Milestone: N+3.51

Date: 2026-05-06

## Direct Answer

Claude Code and Codex are not automatically linked yet.

What exists is a local coordination scaffold:

- `14_context/agent_lanes/` for lane locks, lane status, merge rules, and role boundaries.
- `03_scripts/agent_lane_status.py` for validating and appending lane lock/status JSONL.
- `14_context/prompt_bus/` for prompt handoff directories.
- `03_scripts/prompt_bus.py` for prompt status and dry-run/apply prompt writes.
- `03_scripts/ghoti_local_orchestrator.py` for local read-only status checks and next prompt previews.
- `03_scripts/local_worker_router.py` for routing recommendations across Claude, Codex, ChatGPT, Python, Gemma, Ruflo, Obsidian, and course/certificate lanes.
- `14_context/compact_memory/` and `14_context/obsidian_vault/` for durable local memory.

This is enough for a v1 bridge by file handoff and human-operated prompts.

It is not an automatic bridge.

## What Works Today

The current bridge can:

- Show the current branch and base HEAD.
- Show prompt bus outbox/inbox counts.
- Show active lane locks and latest statuses.
- Validate lane JSONL and registry files.
- Generate dry-run prompt previews for next Claude/Codex work.
- Write prompt artifacts only when `--apply` is passed.
- Recommend worker routes based on task text.
- Keep safety gates explicit and local.

## What Is Still Manual

Still manual:

- Human chooses which prompt to paste.
- Human sends the prompt into Claude Code, Codex, or ChatGPT.
- Human chooses when a branch is ready to merge.
- Human updates state docs unless a future script is explicitly given ownership.
- Human reviews Gemma or local worker drafts before canonical use.
- Human approves all public/live/money/account actions.

The system is more organized now, but it is still a bridge made of local files, commands, and operator discipline.

## What Is Not Yet Automated

Not yet automated:

- No automatic Claude Code invocation.
- No automatic Codex invocation.
- No ChatGPT connector/send path.
- No automatic clipboard bridge.
- No real prompt context pack generator from state + lane + goal.
- No dashboard card for local bridge status.
- No automatic lane heartbeat/status beacons.
- No merge assistant that audits branch, locks, changed files, validation, and merge order.
- No Gemma compression worker that writes prompt summaries.
- No Ruflo orchestration layer.

## Is Prompt Bus + Agent Lanes + Local Orchestrator Enough As V1?

Yes, as a safe v1 coordination substrate.

No, as an operator system that feels "linked."

The v1 bridge is useful because it creates:

- stable files,
- explicit branch/lane ownership,
- validation commands,
- dry-run/apply discipline,
- durable prompts,
- human review gates.

The missing piece is an operator-facing layer that turns these into a workflow:

1. Read current goal.
2. Read lane locks/status.
3. Read current state and compact memory.
4. Generate Claude/Codex/ChatGPT prompts.
5. Write outbox artifacts.
6. Show them on dashboard.
7. Update lane status when work starts/finishes.
8. Check merge readiness.

## Should Ruflo Become The Orchestrator Layer?

Potentially later, but not yet.

Ruflo/claude-flow is interesting because its README claims multi-agent orchestration for Claude Code, swarms, hooks, MCP, agents, memory, and routing. That is directly aligned with the user's goal.

But Ghoti cannot hand control to Ruflo yet because:

- dependencies are not installed,
- package behavior has not been locally smoked,
- swarm commands have not been audited,
- external/provider behavior is not bounded,
- it may try to integrate with Claude Code hooks/MCP in ways that bypass Ghoti lane locks,
- it is not yet known whether it respects local-only/no-live-action constraints.

Recommended v1 meaning of "use Ruflo":

1. isolated install only,
2. read-only help/version command only,
3. local-only plan generation only if help/version passes,
4. no swarm execution without explicit future approval,
5. no global install,
6. no secrets,
7. no live accounts or browser automation,
8. no repo writes outside declared lane,
9. no hidden background processes.

## Exact Next Bridge Functions Needed

The next Claude run should build:

- `03_scripts/ghoti_dashboard.py`
  - read-only bridge/dashboard status summary,
  - JSON and markdown output,
  - no server mutation by itself.

- `03_scripts/gemma_compact_memory_worker.py`
  - reads a markdown file,
  - dry-run default,
  - optionally calls local Ollama/Gemma only when available and approved,
  - writes draft summary to `14_context/prompt_bus/outbox/` or `05_logs/gemma_compact_memory_drafts/`,
  - never overwrites compact memory automatically.

- `03_scripts/ruflo_install_gate.py`
  - `--check`,
  - `--install-dry-run`,
  - `--install-apply`,
  - runs `npm ci --ignore-scripts` only inside Ruflo folder,
  - never runs swarms/MCP/global install.

- `03_scripts/prompt_bus.py` improvements:
  - generate Claude Code prompt,
  - generate Codex prompt,
  - generate ChatGPT handoff,
  - generate status JSON,
  - all dry-run first.

- Dashboard read card in `01_projects/dashboard_mvp/`:
  - displays local orchestrator state,
  - prompt bus outbox,
  - lane locks/status,
  - Ruflo/Gemma/Obsidian readiness,
  - no mutation buttons.

## Safety Gate

The bridge may reduce copy-paste, but it must not reduce human approval.

Forbidden for this layer:

- automatic posting,
- automatic sending,
- automatic selling,
- automatic payments,
- account creation,
- credential use,
- scraping,
- job applications,
- giveaway entries,
- swarm launch,
- model output execution,
- hidden browser/desktop control.
