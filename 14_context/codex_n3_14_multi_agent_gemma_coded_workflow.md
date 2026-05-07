# Codex N+3.14 Multi-Agent Gemma/Codex/Claude Workflow

Status: codex_parallel_audit / workflow_policy_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Goal

Route easy work to local Gemma/Ollama, reserve Codex and Claude Code for harder repo work, and prepare many specialized agents without losing safety, visibility, or approval discipline.

## Task Classes

### 1. Local Easy / API-Free

Default: Gemma/Ollama.

Examples:

- summarizing local docs
- creating checklists
- classifying tasks
- cheap brainstorming
- drafting small reports
- compacting memory notes
- extracting TODOs from local logs

Rules:

- Text-only.
- Local files only.
- Reversible.
- No live accounts.
- No external actions.
- No commits or pushes.

### 2. Medium Coding / Repo Docs

Default: Codex.

Examples:

- docs audits
- limited file edits
- tests/checks
- source inspection
- GitHub repo triage
- skeptical review lane while Claude implements

Rules:

- Stage explicit files only.
- Do not touch dirty unrelated files.
- Keep output artifacts visible.
- Escalate if scope becomes multi-file runtime surgery.

### 3. Hard Coding / Operator Stack

Default: Claude Code or Codex depending task shape.

Examples:

- multi-file runtime changes
- dashboard work
- CUA adapter work
- approval gates
- state migration
- complex test repair

Rules:

- Use clear allowed/forbidden file lists.
- Require validation commands.
- Preserve approval gates.
- Avoid broad refactors unless explicitly approved.

### 4. Strategic Reasoning / Architecture

Default: ChatGPT first when possible, then delegate to Claude/Codex.

Examples:

- milestone design
- safety tradeoffs
- multi-agent architecture
- provider/tool choice
- business strategy

Rules:

- Keep handoffs compact.
- Reference docs by path.
- Turn strategy into executable prompts or small worker cards.

### 5. Deterministic Automation

Default later: n8n or Ghoti automation layer.

Examples:

- scheduled health checks
- local webhook intake
- status notifications
- daily summaries
- file watcher trigger

Rules:

- Stable workflow first.
- Approval-gated before external effects.
- No credentials until separate review.

### 6. Personal Assistant / Channel Agent

Default later: OpenClaw-style worker.

Examples:

- chat/mobile interface
- channel notifications
- personal assistant workflows

Rules:

- Sandboxed/local first.
- No broad credentials.
- No public exposure.
- Human approval for every external action.

## Local Brain Route Pseudocode

```text
function recommend_brain(task):
  if task.requests_install_or_pull_or_external_action:
    return human_approval + claude_or_codex

  if task.touches_live_account_or_money_or_legal_or_posting:
    return blocked_until_explicit_approval

  if task.is_text_only and task.is_local and task.is_reversible and task.risk == low:
    return gemma_local

  if task.is_one_file_code_or_doc_change and risk <= medium:
    return codex_or_claude_reviewed

  if task.is_multi_file_runtime_or_dashboard_or_adapter_change:
    return claude_code_or_codex

  if task.is_strategy_or_architecture:
    return chatgpt_then_delegate

  return human_review
```

## Approval Gates

Approval is required for:

- Docker pull/run/build.
- Ollama pull.
- installs.
- Git push.
- CUA/browser execution.
- live account access.
- posting/email/outreach.
- money movement.
- legal/tax/permit filing.
- deletes and destructive cleanup.
- third-party runtime wiring.

## When Not To Use Gemma

Do not use Gemma alone for:

- secrets/auth/payment/live-account work
- multi-file runtime edits
- CUA or browser execution
- code that weakens approval gates
- deciding whether to install/run external tools
- legal/financial/medical/business advice as final output
- anything that must be highly reliable without review

## Avoiding API Waste Without Cap Bypass

Allowed:

- compact memory
- Obsidian-style vault notes
- local Gemma summaries
- worker cards
- short task specs
- file references instead of pasted logs
- Codex parallel audits instead of repeated large Claude sessions

Forbidden:

- fake accounts
- provider quota evasion
- subscription/cap bypass
- hidden manipulation of provider state
- using local models to avoid safety/legal boundaries

## Parallel Agent Count

Safe near-term default:

- 1 main implementation worker
- 1 parallel Codex audit worker
- 1 local Gemma summary/classification task
- 1 human approval gate

Upper bound before Paperclip/control-plane proof:

- 3 to 5 active workers total
- every worker must have a worker card
- only one worker may touch runtime files at a time
- only one worker may stage/commit at a time

## Worker Card Format

```yaml
worker_id: ghoti-n3-14-router-docs
tool_model: codex
task: "Draft local brain routing policy"
allowed_files:
  - "14_context/codex_n3_14_*.md"
forbidden_files:
  - "01_projects/runtime_mvp/src/**"
  - "01_projects/dashboard_mvp/**"
  - "14_context/ghoti_current_prompt*.md"
expected_output:
  - "policy doc"
  - "validation summary"
status: "running | blocked | done | failed"
handoff_file: "14_context/codex_n3_14_next_claude_implementation_prompt_review.md"
commit_hash: "filled after commit"
```

## Verdict

The next Ghoti-native implementation should be a preview-only brain router and worker-card registry. This gives the user immediate API-saving structure without installing Paperclip, OpenClaw, or n8n yet.
