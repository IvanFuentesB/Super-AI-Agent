# Ghoti Skills and Agent Workflow

Milestone: N+6.4A
Date: 2026-05-31

This document describes how Ghoti's agents divide work, how "skills" are treated,
and how a task moves from idea to merged change. It documents the current,
supervised workflow. It does not enable any new automation.

## Agents and their single responsibilities

- ChatGPT — strategy, architecture, and prompt design. Produces the plan.
- Hermes (local, WSL) — coordinator and memory writer. Turns the plan into
  handoff notes, tracks state in the Obsidian vault, and routes the next step.
- Claude Code — implementation specialist. Implements exactly one assigned task
  on a feature branch with minimal, surgical changes.
- Codex — audit and verification specialist. Reviews the implementation against
  `main` and records a verdict.
- Gemma (gemma3:4b) — cheap local summaries, compression, and classification.
- Llama (llama3.1:8b) — Hermes' local coordinator brain.
- Git — the source of truth, history, and rollback.
- Human — final approval for risky actions and all merges.

## Handoff flow

1. ChatGPT designs the plan.
2. Hermes writes `CURRENT_TASK.md` in the Obsidian handoff vault.
3. Claude Code reads the task and implements minimal changes on a feature
   branch, then writes `CLAUDE_LAST_RUN.md`.
4. Codex audits against `main` and writes `CODEX_LAST_AUDIT.md`.
5. Hermes summarizes and recommends merge or fix.
6. Human approves the merge.

Handoffs are manual: notes are copy/pasted between tools through the vault and
the prompt bus. No agent launches another agent automatically.

## What a "skill" means in Ghoti

A skill is a named, reusable playbook or capability description. In Ghoti today
skills are treated as **documentation and policy**, not as auto-running code:

- Local repo skills (for example `goal`, `ultraplan`, `ghoti-status`,
  `prompt-bus`) are Ghoti-owned prompts/playbooks.
- External skills (for example Anthropic-provided guideline skills) are
  **inspected first** and adopted as guidance. They are not wired into a runtime
  loop and do not execute external code on their own.
- The registry of known skills and their enablement status lives in
  `14_context/skills/ghoti_skill_registry.md`.

## Guardrails carried into every task

- One task per agent; never let two agents edit the same files at once.
- Branches/worktrees for isolation.
- No secrets in prompts, repos, or notes.
- No live account/API/posting/money actions without human approval.
- Minimal, surgical changes (see `14_context/skills/karpathy_guidelines_intake.md`).

## Not enabled by this workflow

- No Telegram, browser, or computer-use automation.
- No automatic cross-agent execution.
- No autonomous merges. Ghoti stays supervised.
