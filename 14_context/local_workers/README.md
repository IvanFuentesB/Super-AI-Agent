# Local Workers — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05

---

## Purpose

The local worker layer routes tasks to the cheapest appropriate executor, saving Claude/ChatGPT/Codex tokens for work that truly requires them.

## Worker Tiers

| Worker | Tasks | Cost |
|--------|-------|------|
| `python_automation_worker` | JSON/JSONL, file parsing, validation, report gen | Free (local Python) |
| `gemma_local_worker` | Summaries, compression, drafts, scoring | Near-free (local Ollama) |
| `claude_code_impl` | Implementation, commits, reasoning, tests | Medium (Claude tokens) |
| `codex_audit` | Audit, source-check, safety gate, spec writing | Medium (Codex tokens) |
| `chatgpt_strategy` | Strategy, architecture, next-milestone planning | Medium (ChatGPT tokens) |
| `human_approval_required` | Live/account/money/public actions | N/A — must stop and ask |

## Routing CLI

```bash
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
python 03_scripts/local_worker_router.py --study-template --dry-run
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
```

## Policy

See `14_context/local_workers/local_worker_policy_n3_45a.md` for routing rules.

## Safety

- No external APIs
- No live account actions
- Python workers: stdlib only
- Gemma output: draft only — never canonical without human review
- Live/public/money actions always route to `human_approval_required`
