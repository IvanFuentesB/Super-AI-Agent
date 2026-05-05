# N+3.45B Prompt Bus And Copy-Paste Manager Spec

Status: local spec only.
Date: 2026-05-05

## Purpose

The prompt bus is a local file-based handoff layer that tells the operator what to paste where. It reduces prompt sprawl and supports controlled Claude/Codex/Gemma/ChatGPT lanes without auto-sending or live account actions.

## Core Files

Canonical Claude prompt:

```text
14_context/ghoti_current_prompt.md
```

Future prompt bus outbox:

```text
14_context/prompt_bus/outbox/
```

Suggested future structure:

```text
14_context/prompt_bus/
  README.md
  outbox/
    claude/
    codex/
    chatgpt/
    gemma/
  templates/
    claude_implementation_prompt.md
    codex_audit_prompt.md
    chatgpt_strategy_prompt.md
    gemma_compression_prompt.md
  status/
    prompt_bus_status.jsonl
```

Do not create these files in this Codex lane; Claude N+3.45A may own implementation if explicitly scoped.

## Prompt Record Shape

Future JSON/markdown metadata:

- prompt_id
- created_at
- target_agent
- target_branch
- task_slug
- paste_destination
- allowed_paths
- forbidden_paths
- required_validation
- approval_required_before_send
- status
- source_files
- prompt_body

## What To Paste Where

Each prompt artifact should include:

- exact agent/tool
- exact branch
- exact allowed paths
- exact forbidden paths
- whether it is a plan/audit/implementation prompt
- whether the user should paste into Claude Code, Codex, ChatGPT, or Gemma
- expected final report fields

## Safety Rules

- Never auto-send by default.
- Clipboard write is optional and requires explicit approval.
- No keyboard automation into live tools until separately approved.
- No account creation, posting, sending, paying, scraping, applying to jobs, or giveaway entry.
- No prompt that asks an agent to bypass usage caps, auth, captchas, TOS, academic integrity, or safety gates.
- Prompt bus cannot convert model output into approval.
- Prompt bus cannot mutate `active_locks.jsonl` or `lane_status.jsonl` unless a future helper is explicitly approved.

## ChatGPT Handoff Templates

ChatGPT should receive:

- current branch/origin state
- target lane split
- exact prompt objective
- sources to cite
- safety no-go list
- merge sequence

ChatGPT should output:

- Claude prompt
- Codex prompt
- optional Gemma prompt
- human merge checklist

## Status Summaries

Prompt bus should show:

- prompt ready
- prompt pasted manually
- waiting for agent
- result received
- needs audit
- merged
- superseded

All status writes should be local and append-only.

## Future Dashboard Card

Read-only card:

```text
Ghoti Prompt Bus
```

Displays:

- latest prompt artifacts
- target agent
- branch
- status
- copy-only prompt path
- validation requirements
- warnings for approval-required actions

Allowed interactions:

- refresh
- copy file path
- copy prompt text only after explicit user action

Forbidden interactions:

- send
- submit
- login
- post
- pay
- apply
- connect account

## Verdict

Prompt bus is a high-priority local coordination layer. It should be implemented before Ruflo/OpenClaw/Paperclip/n8n runtime wiring because it gives Ghoti explicit, auditable human-in-the-loop routing.
