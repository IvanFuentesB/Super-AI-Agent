# Ghoti Token-Saving And Agent Context Plan

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: token_saving_plan / legal_context_management_only / not_cap_bypass

## Purpose

Define legal, safe context-management patterns for Ghoti's multi-agent workflow. This plan is about spending fewer tokens by carrying less irrelevant context, not bypassing provider limits.

## Allowed Token-Saving Patterns

- Compact JSON shared memory with durable truths and short findings.
- Per-run checkpoints under `05_logs/multi_agent_runs/<run_id>/`.
- Fresh-session handoff files that cite paths instead of pasting giant blobs.
- Small per-agent tasks with one responsibility each.
- Per-agent artifacts that are short, visible, and file-backed.
- Codex skill progressive disclosure: read only the skill instructions needed for the current task.
- Claude/Codex subagent-style separation when the operator explicitly delegates separate repo tasks.
- Local Gemma/Ollama diagnostics for summarization only after a model is explicitly approved and available.
- Pruning stale context from prompts while preserving file references and commit hashes.

## Forbidden Patterns

- Provider quota, cap, subscription, or usage-limit bypass.
- Fake accounts, account sharing abuse, or identity rotation.
- Deleting, modifying, or hiding provider limit storage.
- Hidden usage evasion.
- Prompting local models to bypass law, platform rules, or provider policies.
- Autonomous external action justified as "token saving."
- Removing safety context from handoffs to make prompts shorter.

## How Many-Agent Workflow Saves Tokens

- Each agent gets a compact task instead of the entire repo history.
- Each agent reads only the files relevant to its role.
- The supervisor receives summaries and artifact paths, not full copied documents.
- Shared memory stores compact current truths, not full transcripts.
- Later runs can resume from `run_manifest.json`, `supervisor_summary.md`, and `multi_agent_shared_memory.json`.

## Shared Memory Rules

- Keep memory JSON compact.
- Store facts, decisions, blockers, candidate-tool statuses, and short findings.
- Prefer paths over pasted content.
- Keep timestamps and source agent IDs.
- Cap list lengths so memory does not become another giant transcript.
- Never store secrets, credentials, private account data, or personal CV contents.

## Run Artifact Retention

- Keep small milestone demonstration runs that prove behavior.
- Archive or summarize older runs before they become noisy.
- Do not commit massive logs, screenshots, videos, model caches, or generated third-party artifacts.
- Future cleanup should be explicit and operator-confirmed.

## ChatGPT / Claude / Codex Division

- ChatGPT: architecture brain, planning, memory synthesis, prompt creation.
- Codex app: repo-local execution, precise edits, validation, commits, pushes when approved.
- Claude chat: reasoning, critique, prompt sharpening.
- Claude Code: execute one prepared repo-local prompt when credits/auth are available.
- User: approval gate for risky actions and final operator judgment.

## Legal Claude/Codex Credit-Saving Workflow (added N+3.1)

This section defines the approved workflow for reducing token/credit consumption
legally, without bypassing any provider limits, quotas, or subscriptions.

### Allowed Patterns

- Compact CLAUDE.md: keep project instructions short and file-referenced, not duplicated.
- Smaller subagent prompts: each Claude Code invocation gets one narrow repo task.
- Checkpoint files: each milestone writes a finish-line log and compact memory update.
- Prompt libraries: reusable skill files under `.claude/skills/` reduce repeated prompt text.
- Summarized run artifacts: agents write short markdown summaries, not full transcripts.
- Local Gemma diagnostics: after a model is approved and available, run only for offline summarization.
- File references instead of pasting: long docs are referenced by path, not pasted into prompts.
- Agent separation: ChatGPT/planning vs Claude/Codex execution reduces re-explaining context.

### Forbidden Patterns

- Quota, cap, subscription, or usage-limit bypass.
- Fake accounts, account sharing abuse, or identity rotation.
- Deleting, modifying, or hiding provider usage-limit storage.
- Hidden usage evasion.
- Removing safety context from handoffs to shorten prompts.

### Practical Workflow (N+3.1 confirmed)

1. ChatGPT creates architecture and full prompts (ghoti_current_prompt.md).
2. Claude Code executes narrow repo tasks from the prepared prompt.
3. Each milestone updates ghoti_finish_line_log.md and compact memory.
4. Long docs are referenced by path, not pasted.
5. Agents get one job each (see multi_agent_mvp.py pattern).
6. Handoff files carry only the current run context, not full history.

### Current Status

- Plan status: `token_saving_plan / legal_context_management_only / not_cap_bypass`
- Runtime wired: partially as local MVP memory/artifact pattern (N+3.0 + N+3.1).
- Cap bypass implemented: NO.
- Provider-limit evasion implemented: NO.

## Current Status

- Plan status: `token_saving_plan / legal_context_management_only / not_cap_bypass`
- Runtime wired: partially as local MVP memory/artifact pattern only.
- Cap bypass implemented: NO.
- Provider-limit evasion implemented: NO.
