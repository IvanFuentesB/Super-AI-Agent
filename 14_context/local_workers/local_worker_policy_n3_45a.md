# Local Worker Routing Policy — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Status:** active

---

## Routing Decision Table

| Task Class | Route | Rationale |
|-----------|-------|-----------|
| JSON/JSONL validate, parse, report, file gen | `python_automation_worker` | Deterministic — no tokens needed |
| CSV, markdown gen, queue processing | `python_automation_worker` | Deterministic — no tokens needed |
| Compression, summary, scoring, draft | `gemma_local_worker` | Cheap local inference if Ollama available |
| Implementation, tests, commits | `claude_code_impl` | Requires reasoning; use Claude tokens |
| Audit, source-check, safety gate | `codex_audit` | Requires audit discipline; use Codex |
| Strategy, architecture, planning | `chatgpt_strategy` | Requires broad context; use ChatGPT |
| Live/account/public/money action | `human_approval_required` | STOP — never automate without explicit approval |

---

## Python Automation Worker Rules

- Python >= 3.11, stdlib only
- No external packages unless explicitly approved and installed
- No external APIs or HTTP calls
- No credential reads
- No writes outside repo root
- Dry-run by default; `--apply` required for writes

## Gemma Local Worker Rules

- Ollama + Gemma3:4b (installed N+3.13, smoke-passed)
- Output is always `draft` status
- Never use Gemma output as canonical truth without human review
- Never commit Gemma output directly without promotion review
- Disabled by default in routing config; enable explicitly

## Fallback Chain

If `gemma_local_worker` is unavailable (Ollama not running):
→ Route to `claude_code_impl` for small tasks or `chatgpt_strategy` for drafts

## What Is Not Routed

- Anything requiring live accounts: always `human_approval_required`
- Anything requiring external HTTP: always requires explicit approval
- Course/exam submissions: always human-only
- Credential operations: always human-only

---

## Config File

See `23_configs/local_worker_routing.example.json` for the routing config schema.

## Script

`03_scripts/local_worker_router.py` implements routing recommendations.
