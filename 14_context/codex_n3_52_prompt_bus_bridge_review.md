# Codex N+3.52 - Prompt Bus Bridge Review

## Current Bridge Pieces

Ghoti now has a real v1 bridge foundation:

- `14_context/agent_lanes/` for locks and status beacons
- `14_context/prompt_bus/` for local handoff files
- `03_scripts/prompt_bus.py` for local prompt/status generation
- `03_scripts/local_worker_router.py` for routing recommendations
- `03_scripts/ghoti_local_orchestrator.py` for local status checks
- N+3.50A dashboard local orchestrator card

This is not automatic control of Claude Code, Codex, ChatGPT, Gemma, or Ruflo.

## Validated Prompt Bus Behavior

- `python 03_scripts/prompt_bus.py --status-json` worked.
- `python 03_scripts/prompt_bus.py --write-context-pack --target all --dry-run` previewed Claude, Codex, and ChatGPT handoff content.
- Dry-run did not write.
- Apply can write outbox files.
- Apply can overwrite the canonical Claude prompt, which needs stronger review and confirmation.

## What Remains Manual

- The user still chooses what to paste into Claude Code, Codex, and ChatGPT.
- Prompt bus does not control live sessions.
- There is no automatic merge assistant.
- Gemma does not yet automatically compress context in a successful workflow.
- Ruflo does not orchestrate lanes.
- Dashboard status does not execute anything.

## Safety Gaps

Next implementation should add:

- Outbox-first context pack behavior.
- Explicit confirmation before overwriting `14_context/ghoti_current_prompt.md`.
- `--review` or `--plan` mode listing exactly what would change.
- Active-lock conflict checks before prompt writes.
- Clear labels: `DRAFT`, `COPY_ONLY`, `NOT_SENT`, `HUMAN_REVIEW_REQUIRED`.

## Router Gap

Observed router issue:

- Input: `create prompt bus context pack for claude and codex`
- Observed route: `codex_audit`
- Desired route: prompt bus/local orchestration lane

The router needs prompt-bus/context-pack keywords with higher priority than broad Codex audit routing.

## Verdict

`PARTIALLY AUTOMATED, STILL MANUAL`

The bridge is meaningful but not autonomous. It reduces prompt assembly chaos, not human approval or copy-paste responsibility.
