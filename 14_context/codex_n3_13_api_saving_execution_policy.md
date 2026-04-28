# Codex N+3.13 API-Saving Execution Policy

Status: codex_parallel_audit / policy_only / legal_context_management_only / not_cap_bypass

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## 1. Principle

Use expensive models only where they produce a clear advantage. API saving means legal context compaction, local summaries, model routing, small task specs, and avoiding repeated giant prompts. It must never mean provider cap bypass, fake accounts, quota evasion, hidden limit manipulation, or abuse of paid services.

## 2. Default Model Routing

| Model/tool | Best use |
| --- | --- |
| Gemma/Ollama | Cheap local low-risk text tasks after model smoke |
| Codex | Parallel audits, repo inspection, code review, plan verification, small safe edits |
| Claude Code | Main implementation lane, multi-file edits, repo execution with validation |
| ChatGPT | High-level planning, coordination, milestone prompts, memory synthesis |

## 3. Decision Table

| Task type | Default model/tool | Approval required? | Notes |
| --- | --- | --- | --- |
| Summarize docs | Gemma after smoke | No, if local/read-only | Use file paths and compact outputs |
| Compress memory | Gemma after smoke | No, if local/read-only | Keep summaries short |
| Classify queue | Gemma after smoke | No, if preview-only | No automatic dispatch |
| Generate checklist | Gemma after smoke | No, if internal draft | Human reviews before execution |
| Write code plan | Codex or Claude | Sometimes | Gemma can draft only |
| Edit one file | Codex or Claude Code | Yes if behavior/risk changes | Validate before commit |
| Edit multiple files | Claude Code or Codex | Usually yes | Avoid local-brain-only edits |
| Debug failing tests | Claude Code/Codex | Depends on scope | Preserve logs and exact commands |
| Run Docker/CUA | Claude Code main lane | Yes, explicit | Digest/payload/action gates required |
| Browser action | Future adapter only | Yes | No live accounts until approved |
| Live account action | Human-controlled only | Yes, always | No autonomous sending/posting |
| Git commit | Codex/Claude | Yes by milestone prompt | Stage explicit files only |
| Git push | Codex/Claude | Yes by milestone prompt | Report denial honestly |
| Install package | Claude/Codex only | Yes, explicit | Record risks and rollback |
| Pull model/image | Claude/Codex only | Yes, exact approval | No pull in audit lane |

## 4. Escalation Rules

- If Gemma fails twice or produces uncertain output, escalate to Claude/Codex.
- If a task touches secrets, auth, payments, live accounts, reputation, private data, legal/tax/financial decisions, or external actions, require human approval plus a stronger model review.
- If a task needs a new tool, package install, Docker image pull, model pull, or third-party clone, require an approval gate.
- If the source, license, repo identity, or risk profile is uncertain, run a Codex audit first.
- If a task is destructive, irreversible, or could change external state, human approval is mandatory.

## 5. Token-Saving Rules

- Cite file paths instead of pasting huge docs.
- Use `14_context/obsidian_vault/` notes as compact context.
- Update compact memory and task summaries rather than repeating old logs.
- Prefer artifact summaries with links to run output paths.
- Keep per-agent task specs small and explicit.
- Avoid re-pasting historical finish-line logs unless a specific milestone needs them.
- Use fresh-session handoffs that mention only current truth, blockers, approvals, and file paths.

## 6. Future Implementation

Start with preview-only fields and commands:

- Read-only CLI: `python 01_projects/runtime_mvp/src/super_ai_agent/brain_route_preview.py`
- Config: `23_configs/brain_routing_policy.example.json`
- Dashboard field: `recommended_brain`
- Queue field: `estimated_difficulty`
- Output fields: `approval_required`, `risk_level`, `reason`, `confidence`

No autonomous dispatch should be enabled until the preview outputs are validated over multiple milestones.

## 7. Verdict

Implement preview-only routing first. Gemma should reduce API usage for low-risk local text work only after model smoke succeeds. Claude Code and Codex should remain the execution and review lanes for hard repo tasks. Human approval remains the gate for installs, pulls, external actions, Docker/CUA, browser control, git pushes, and anything risky.
