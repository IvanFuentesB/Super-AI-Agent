# Claude Agents Parallel Workflow Plan

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: future_agent_plan / not_runtime_wired / manual_handoff_only

## Purpose

Define future Claude Code / Claude chat / Codex-style parallel agent roles without claiming they are wired into Ghoti runtime.

This is a planning document only. The N+3.0 native multi-agent MVP is a deterministic local Python runner, not a Claude Code subagent bridge.

## Future Agent Roles

| Agent | Single responsibility | Allowed tools | Forbidden tools/actions | Memory file | Expected output |
|---|---|---|---|---|---|
| `repo-cartographer` | Map relevant files, modules, and ownership for a milestone | read repo files, `rg`, `git status`, `git log` | edits, commits, installs, external services | `14_context/multi_agent_shared_memory.json` | 5-10 bullets plus file paths |
| `safety-gatekeeper` | Check approval gates, blocked files, and unsafe workflow drift | read docs, inspect diffs, git status | hiding errors, weakening gates, approving risky actions | `14_context/multi_agent_shared_memory.json` | concise risk list and pass/fail |
| `implementation-planner` | Turn a milestone into one coherent coding slice | read docs, propose files, outline validation | broad refactors, external tool wiring without approval | `14_context/multi_agent_shared_memory.json` | 1 implementation plan |
| `test-runner` | Run syntax checks, smoke tests, and route checks | shell validation commands, read outputs | destructive commands, installs unless approved | `05_logs/multi_agent_runs/<run_id>/` | exact commands + results |
| `doc-finisher` | Update finish-line logs and handoff docs | read/write approved docs only | rewriting history, staging runtime junk | `14_context/ghoti_finish_line_log.md` | final log entry |
| `external-repo-auditor` | Evaluate public/external repo docs and licenses | read public docs, fill evaluation template | clone/install/build without approval | `14_context/external_repo_evaluation_template.md` | verdict + risk table |
| `token-budget-keeper` | Keep prompts and memory compact | read summaries, propose pruning | cap bypass, deleting safety context | `14_context/multi_agent_shared_memory.json` | short context budget note |

## Operating Rules

- Each agent gets exactly one small job.
- Agents cite file paths rather than paste large blobs.
- Agents write compact artifacts.
- The supervisor summarizes artifacts, not raw full context.
- Any risky action still requires explicit operator approval.
- No agent can authorize another agent to perform external actions.

## Manual Handoff Truth

- Claude Code <-> Codex automatic bridge remains `manual_handoff_only`.
- Codex skills/plugins are operator/session capabilities, not Ghoti runtime integrations unless proven.
- Future Claude subagent use depends on explicit Claude Code capability and operator approval.

## Current Status

- Plan status: `future_agent_plan / not_runtime_wired / manual_handoff_only`
- Runtime wired: NO.
- External services connected: NO.
- Approval gates weakened: NO.
