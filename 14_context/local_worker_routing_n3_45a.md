# Local Worker Routing — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## What Was Built

A local worker routing scaffold that helps decide when to use Python, Gemma/Ollama, Claude, Codex, or ChatGPT — saving tokens and reducing cost for deterministic tasks.

### Files Created

| File | Purpose |
|------|---------|
| `03_scripts/local_worker_router.py` | CLI routing recommender — stdlib only |
| `14_context/local_workers/README.md` | Worker tier guide |
| `14_context/local_workers/local_worker_policy_n3_45a.md` | Routing rules |
| `23_configs/local_worker_routing.example.json` | Config schema example |

---

## How to Use

### Recommend a route

```bash
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
# → gemma_local_worker

python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
# → python_automation_worker

python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
# → claude_code_impl

python 03_scripts/local_worker_router.py --recommend --task "plan next milestone"
# → chatgpt_strategy
```

### Generate templates

```bash
python 03_scripts/local_worker_router.py --study-template --dry-run
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
```

---

## Routing Rules Summary

| Task Class | Route |
|-----------|-------|
| JSON/JSONL, file parsing, report gen, validation | `python_automation_worker` |
| Compress, summarize, score, draft | `gemma_local_worker` (fallback: Claude) |
| Implement, build, test, commit | `claude_code_impl` |
| Audit, source-check, safety gate | `codex_audit` |
| Strategy, architecture, planning | `chatgpt_strategy` |
| Live/account/money/public | `human_approval_required` — STOP |

---

## Validation

```bash
python -c "import ast, pathlib; ast.parse(pathlib.Path('03_scripts/local_worker_router.py').read_text(encoding='utf-8')); print('AST OK')"
python 03_scripts/local_worker_router.py --help
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
python 03_scripts/local_worker_router.py --study-template --dry-run
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
```

---

## Safety Gates

- No external APIs
- No live account actions
- Python workers: stdlib only
- Gemma: `enabled: false` in config until explicitly enabled
- `human_approval_required` route never runs automation

---

## What Is Not Wired Yet

- Ollama status check disabled by default
- Gemma routing disabled in config
- No automatic task dispatch — router only recommends
- Study/cert templates are scaffolds — all coursework human-only

---

## Next Steps

- Enable Gemma routing when Ollama confirmed running
- Add JSONL-based task queue for Python automation workers
- Wire prompt bus `--write-codex` to automatically create Codex prompts for audit tasks
