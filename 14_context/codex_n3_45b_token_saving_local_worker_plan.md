# N+3.45B Token Saving Local Worker Plan

Status: Codex planning/source-check lane only.
Date: 2026-05-05

## Goal

Reduce expensive frontier-model context load without pretending to bypass usage caps. Ghoti should use cheap local tools for deterministic or low-risk work, then give Claude/Codex compact, focused prompts.

## Routing Model

| Worker | Best use | Output status | Safety boundary |
|---|---|---|---|
| Python automation worker | deterministic parsing, JSONL validation, markdown/report generation, file organization inside allowed repo folders, queue processing | source-trustable if code is reviewed and deterministic | stdlib-first, repo-local, no accounts, no scraping, no credentials |
| Gemma/Ollama local worker | cheap summaries, draft labels, scoring drafts, note compression, content angles | draft only until reviewed | no external API, no tool execution, no canonical overwrite |
| Obsidian/compact memory worker | durable markdown memory plus compressed pointer files | canonical only after human/Claude/Codex review | never delete source records; mark stale/unknown |
| Claude Code | implementation, tests, commits, runtime fixes | implementation source after validation | lane branch and locks; no live actions |
| Codex xhigh | audits, source-checks, long plans, risk registers | audit/spec source | docs-only unless explicitly asked |
| ChatGPT | strategy, prompts, merge orchestration | strategy/prompt source | no repo writes unless user asks |

## No Cap Bypass

- Do not use "free Claude", leaked Claude Code, unlocked Claude Code, Mythos, OBLITERATUS, or guardrail-removal tooling.
- Do not bypass subscriptions, rate limits, auth, captchas, or provider usage caps.
- Local Gemma is not a fake Claude replacement. It is a cheap local draft worker for easy tasks.
- Python scripts are not agents; they are deterministic helpers for repeatable work.

## Local Gemma Role

Use Gemma/Ollama for:

- context compression drafts
- weekly review summaries
- risk labels
- simple scoring explanations
- content/product idea drafts
- transcript/note summaries

Do not use Gemma for:

- executing model output
- canonical truth without review
- public claims
- sending/posting/selling
- account actions

## Python Automation Role

Use Python scripts for:

- JSONL line-by-line parsing
- malformed-line reports
- markdown artifact assembly
- summary route fixtures
- queue status rollups
- study trackers
- simple deterministic calculations
- validation checks

Do not use Python scripts for:

- account login
- real emails/posts/payments
- scraping without legal/TOS review
- credential reads
- bypassing approvals

## Compact Prompt Flow

1. Durable record lives in `14_context/`, `14_context/obsidian_vault/`, `14_context/money_workflows/`, or `05_logs/`.
2. Python extracts deterministic facts where possible.
3. Gemma drafts a short summary for cheap compression.
4. Human/Codex/Claude reviews before promotion.
5. Claude receives a focused prompt with file pointers, exact branch, allowed paths, forbidden paths, validation, and final report format.

## Near-Term Implementation Order

1. Prompt bus/local worker docs and scaffolding.
2. Python deterministic helper for prompt/current-task packaging.
3. Gemma draft compression into logs only.
4. Human-reviewed compact memory promotion.
5. Dashboard read view for prompts/worker status.

## Verdict

Proceed with local prompt bus + Python worker + Gemma draft worker before any external orchestrator. This saves tokens without unsafe autonomy and keeps Claude focused on implementation.
