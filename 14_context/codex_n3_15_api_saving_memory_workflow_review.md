# Codex N+3.15 API-Saving Memory Workflow Review

Status: codex_parallel_audit / workflow_review_only / legal_context_management_only / not_cap_bypass

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.15 should turn local Gemma into a useful context-compression helper. The goal is to reduce paid API usage by moving easy local text work to local inference, while preserving human/Claude/Codex control for hard or risky work.

This is legitimate local compute and context management. It is not provider cap bypass, quota evasion, fake-account use, or hidden manipulation of model-provider limits.

## Model/Tool Responsibilities

| Work type | Default tool/model | Notes |
| --- | --- | --- |
| Easy local summaries | Gemma/Ollama | Local markdown and logs only |
| Context compression | Gemma/Ollama | Artifact-only output, no source edits |
| Checklist drafts | Gemma/Ollama | Low-risk internal drafts |
| Risk labels / task classification | Gemma/Ollama or Codex review | Gemma can draft; humans/Codex verify risky cases |
| Multi-file implementation | Claude Code | Main implementation lane |
| Hard architecture or safety design | ChatGPT + Claude/Codex | ChatGPT plans; Claude/Codex execute/review |
| Independent audit | Codex | Parallel reviewer lane |
| Git staging/commit/push | Claude/Codex only | Explicit files, validation, no `git add .` |
| CUA/browser/external actions | Claude/Codex + approval | Never Gemma alone |

## Gemma Handles Easy Local Work

Approved Gemma task classes:

- summarize local docs
- compress context
- draft compact checklists
- classify task difficulty and risk
- extract TODOs from local logs
- rewrite internal notes
- produce first-pass worker-card drafts

Gemma must stay local-only:

- no external API calls
- no web browsing
- no file edits from model output
- no live accounts
- no CUA/browser execution

## Claude Code Handles Hard Implementation

Claude Code remains best for:

- multi-file runtime changes
- dashboard route/UI implementation
- wait/resume updates
- CUA adapter work
- validation and smoke tests
- milestone commits that intentionally include runtime files

Claude should use Gemma outputs as drafts or artifacts, not as commands.

## Codex Handles Audits and Independent Review

Codex is strongest as:

- parallel audit lane
- skeptical reviewer
- route/spec checker
- source/repo evaluator
- limited doc/code edit worker when not conflicting with Claude

Codex should continue producing small decision-support docs while Claude Code owns implementation lanes.

## ChatGPT Handles High-Level Planning

ChatGPT should remain:

- architect
- prompt generator
- memory bridge
- strategy synthesizer
- milestone coordinator

This reduces repeated Claude/Codex context load and keeps the work pointed.

## Obsidian / Vault Memory

The Obsidian-style vault should remain plain markdown for now:

- no RAG/vector DB yet
- no plugin dependency
- no external sync
- no paid service
- compact notes by path

Gemma context compression can produce candidate summaries that a human or Claude/Codex later decides whether to copy into vault notes.

## Recommended Memory Flow

1. ChatGPT or Claude identifies a source file that is too large for repeated prompting.
2. Claude runs `compress_context` against a repo-local file.
3. Gemma writes artifacts under `05_logs/local_brain_runs/<run_id>/`.
4. Claude/Codex reviews the response artifact.
5. Only after review, a human/Claude/Codex may update a compact vault note or current-state doc.
6. Future prompts cite the compact note path instead of pasting the full source.

## What This Must Not Become

- not autonomous memory rewriting
- not a live RAG/vector database
- not hidden prompt injection execution
- not provider cap bypass
- not quota evasion
- not a way to avoid safety/legal constraints
- not a source of unreviewed repo edits

## Verdict

The right N+3.15 target is a safe, artifact-only `compress_context` route. It will save tokens immediately by producing compact local summaries, but it should not edit memory files automatically until output quality and prompt-injection handling are proven.
