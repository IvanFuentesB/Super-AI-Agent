# N+3.41 Ultraplan, Codex Goal, And Routines Backlog

Status: Codex backlog/spec only.
Date: 2026-05-05

The operator wants stronger planning and routine execution: one-shot or as-close-as-possible builds, question gathering before large work, AI routines, agent routines, scheduled agents, execute routines later, and long-running goal workflows. This is useful, but it needs lane locks and approval gates before execution.

## Source-Checked Planning Features

| Feature | Source-check status | Usefulness | Safety note |
| --- | --- | --- | --- |
| Claude Code `/ultraplan` | official Claude Code docs found | high for complex multi-step planning | cloud/web infrastructure; review before execution |
| Claude Code `/ultrareview` | official Claude Code docs found | high for bug review after implementation | cloud review, may cost money, needs account auth |
| Codex cloud/background/parallel tasks | official OpenAI Codex docs found | high for isolated background coding tasks | use only with branch/lane locks |
| Codex Goal exact feature | partially verified via community discussion; exact official named feature not confirmed | research | treat as concept until official source is found |
| AI routines/scheduled agents | concept verified, exact Ghoti implementation not present | later | safe only for local tasks first |

## Planning Workflow Pattern

For big builds:

1. Question-gathering phase.
2. Assumption list.
3. Risk list.
4. File ownership plan.
5. Validation plan.
6. Approval gates.
7. Implementation plan.
8. Human review.
9. Execute only after approval.

This keeps "one-shot" ambition grounded. The goal is fewer wasted runs, not unsafe autonomy.

## When To Use Each Lane

| Lane | Use for | Do not use for |
| --- | --- | --- |
| `/ultraplan` | complex multi-step planning, architecture, risk review | bypassing human approval or spending money |
| Claude Code local | implementation, tests, commits | source-check-only tasks or live account actions |
| Codex | audits, specs, source-checks, independent review | runtime implementation unless explicitly assigned |
| Gemma/Ollama | cheap local summaries, compression, first drafts | executing output or editing canonical memory automatically |
| ChatGPT | strategy, prompts, decision framing | claiming repo truth without local evidence |

## Agent Routines

Future routine types:

- weekly Money OS review
- daily next-action summary
- local memory compression draft
- queue triage draft
- content batch draft
- internship tracker review
- stale-task audit
- budget/subscription review

Routine statuses:

- proposed
- questions_needed
- ready_for_local_draft
- local_draft_created
- needs_human_approval
- approved_for_local_execution
- completed
- blocked
- rejected

## Ask-First Routine Rule

Routines that could affect money, accounts, public content, email, jobs, scraping, or external systems must ask questions first and stop before execution.

Minimum questions:

- What account or platform would be affected?
- What exact output should be produced?
- Is any public, money-facing, or account action involved?
- What files may be read?
- What files may be written?
- What validation proves success?
- What is the stop condition?

## Local Plan Files

Recommended future folder:

```text
14_context/agent_lanes/
```

Potential files:

- `routine_registry.md`
- `routine_template.md`
- `<agent_id>_active_lock.md`
- `<agent_id>_status.md`
- `<routine_id>_plan.md`
- `<routine_id>_approval_checklist.md`

## Approval Gates Before Execution

Approval required before:

- email sending
- job applications
- social posting
- account creation
- connector installation
- MCP server connection
- scraping
- payments/subscriptions
- public product listing
- app-store actions
- browser automation against logged-in accounts

## Long-Running Work Rules

Codex or Claude long-running/background work can be useful only if:

- branch is isolated
- write scope is explicit
- origin comparison is recorded
- lock file exists
- heartbeat/status artifact exists
- validation plan exists
- stop condition exists
- no live-account actions are included

## Current Recommendation

Use `/ultraplan` for complex planning and `/ultrareview` for high-stakes code review after implementation, but do not use either as an approval bypass. Treat Codex Goal/long-running workflows as future lane-locked background work, not free-roaming autonomy.

This also preserves the broad "all the things we have been talking about" backlog as a future routines and lane-lock system rather than a single unsafe automation jump.
