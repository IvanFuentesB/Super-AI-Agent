# Active Worker Cards — N+3.14

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.14

---

## LOCAL-GEMMA-EASY-001

| Field | Value |
|---|---|
| Worker ID | LOCAL-GEMMA-EASY-001 |
| Tool / Model | gemma3:4b via Ollama 0.9.2 |
| Role | Local easy-task brain — summaries, checklists, context compression |
| Task | summarize_local_markdown, classify_task_risk, draft_checklist, compress_context, suggest_worker_card |
| Allowed Files | 05_logs/local_brain_runs/** (write), 14_context/*.md (read only) |
| Forbidden Files | secrets, .env, CV_*, output/**, third_party/**, live account config |
| Risk Level | low |
| Approval Gates | None for preview runs; human approval required before any repo edit or external action |
| Expected Output | 05_logs/local_brain_runs/<run_id>/request.json, response.txt, summary.md |
| Validation Commands | python local_brain_router.py --preview |
| Commit Rules | Only artifact files under 05_logs/local_brain_runs/; no model-generated code staged without review |
| Handoff File | 14_context/local_gemma_router_preview_n3_14.md |
| Status | active (preview_only) |
| Last Update | 2026-04-28 |
| Next Action | Route one context-compression task and compare output quality |

---

## CODEX-AUDIT-001

| Field | Value |
|---|---|
| Worker ID | CODEX-AUDIT-001 |
| Tool / Model | OpenAI Codex (copy-paste prompt delivery) |
| Role | Independent repo/doc auditor and limited implementation assistant |
| Task | Audit docs, generate analysis files, limited code edits with approval |
| Allowed Files | 14_context/*.md (write), 04_docs/*.md (write), 23_configs/*.example.json (read) |
| Forbidden Files | secrets, .env, CV_*, output/**, third_party/**, live account config |
| Risk Level | low–medium |
| Approval Gates | Human must approve any code change; docs-only by default |
| Expected Output | 14_context/codex_*.md analysis and audit files |
| Validation Commands | git diff --name-status (review before staging) |
| Commit Rules | Stage only named analysis docs; commit message must include codex lane label |
| Handoff File | 14_context/codex_n3_14_next_claude_implementation_prompt_review.md (if exists) |
| Status | active |
| Last Update | 2026-04-28 |
| Next Action | Provide copy-paste prompt for next audit task |

---

## CLAUDECODE-IMPLEMENT-001

| Field | Value |
|---|---|
| Worker ID | CLAUDECODE-IMPLEMENT-001 |
| Tool / Model | Claude Code (claude-sonnet-4-6) |
| Role | Hard multi-file implementation, runtime wiring, guarded by allowed file lists and validation |
| Task | Complex implementation tasks, runtime extensions, policy enforcement, commit/push |
| Allowed Files | As specified in ghoti_current_prompt.md ALLOWED EDITS section |
| Forbidden Files | ghoti_current_prompt files, third_party/**, .claude/**, CV_*, output/**, secrets |
| Risk Level | medium–high |
| Approval Gates | Push requires user confirmation; risky shell commands require confirmation; external actions blocked |
| Expected Output | Implementation files, validation output, commit hash, push status |
| Validation Commands | AST parse, JSON lint, node --check, git diff --check |
| Commit Rules | Stage only N+milestone files; focused commit message per milestone |
| Handoff File | 14_context/ghoti_finish_line_log.md |
| Status | active |
| Last Update | 2026-04-28 |
| Next Action | Continue executing ghoti_current_prompt.md milestones |

---

## PAPERCLIP-CONTROL-PLANE-CANDIDATE

| Field | Value |
|---|---|
| Worker ID | PAPERCLIP-CONTROL-PLANE-CANDIDATE |
| Tool / Model | Paperclip (open-source orchestration framework — not installed) |
| Role | Future multi-agent orchestration control plane candidate |
| Task | Routing tasks across workers, managing agent lifecycle, aggregating results |
| Allowed Files | N/A — audit/planning only |
| Forbidden Files | All — not installed, not runtime-wired |
| Risk Level | high |
| Approval Gates | Full operator approval required before install or run |
| Expected Output | Architecture plan docs only |
| Validation Commands | N/A |
| Commit Rules | Docs only until install approved |
| Handoff File | 14_context/codex_n3_14_paperclip_vs_openclaw_verdict.md (if exists) |
| Status | planning_only — not installed |
| Last Update | 2026-04-28 |
| Next Action | Source audit before any install decision |

---

## OPENCLAW-WORKER-CANDIDATE

| Field | Value |
|---|---|
| Worker ID | OPENCLAW-WORKER-CANDIDATE |
| Tool / Model | OpenClaw (open-source channel/worker agent — cloned read-only) |
| Role | Future worker and channel agent candidate for browser-assist and managed-operator tasks |
| Task | Browser-assisted execution, channel routing, operator surface extension |
| Allowed Files | N/A — read-only reference only |
| Forbidden Files | All — not runtime-wired |
| Risk Level | high |
| Approval Gates | Full operator approval required before any wiring or install |
| Expected Output | Reference patterns and integration notes only |
| Validation Commands | N/A |
| Commit Rules | Reference docs only |
| Handoff File | 21_repos/third_party/evals/ (read-only reference clone location) |
| Status | planning_only — reference-only |
| Last Update | 2026-04-28 |
| Next Action | Identify specific patterns worth adopting before any runtime integration |

---

## N8N-WORKFLOW-CANDIDATE

| Field | Value |
|---|---|
| Worker ID | N8N-WORKFLOW-CANDIDATE |
| Tool / Model | n8n (workflow automation platform — not installed) |
| Role | Future deterministic workflow rails for structured, repeatable multi-step tasks |
| Task | Structured multi-step workflows, conditional branching, integration glue |
| Allowed Files | N/A — planning only |
| Forbidden Files | All — not installed, not runtime-wired |
| Risk Level | medium |
| Approval Gates | Full operator approval required before install or run |
| Expected Output | Architecture plan docs only |
| Validation Commands | N/A |
| Commit Rules | Docs only |
| Handoff File | 14_context/codex_n3_14_n8n_openclaw_paperclip_architecture_plan.md (if exists) |
| Status | planning_only — not installed |
| Last Update | 2026-04-28 |
| Next Action | Evaluate vs OpenClaw for deterministic workflow role; decide after Gemma routing proves stable |
