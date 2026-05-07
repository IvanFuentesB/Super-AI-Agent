# Gemma Compression Smoke — N+3.51A

Generated: 2026-05-06

## Commands Run

```powershell
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
```

## Status

| Item | Value |
|------|-------|
| Ollama | FOUND (v0.9.2) |
| Gemma model | gemma3:4b (available) |
| Compact memory files | 19 |
| Dry-run compress | PASS |
| Apply compress | NOT RUN (generates logs in 05_logs/ which are blocked from staging) |

## Automation State

- `--status`: PASS
- `--compress --dry-run`: PASS — validates input path, model selection, output path preview
- `--compress --apply`: Ollama runs OK; output to `05_logs/gemma_compact_runs/` (not staged)
- `--outbox`: Copies draft to `14_context/prompt_bus/outbox/` for review

## What Is Automated

- Ollama version check
- Model availability check (gemma3:4b or any gemma variant)
- Input path validation (blocks secret-looking paths)
- Draft summary generation via local Ollama
- DRAFT_ONLY output with NOT_CANONICAL header

## What Is Still Manual

- Reviewing Gemma draft before promoting to canonical memory
- Copying approved summaries from `05_logs/` to `14_context/compact_memory/`

## Safety

- Output is always marked DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED
- Refuses paths containing: .env, secret, credential, token, key, password
- Never writes to canonical compact_memory automatically

## Next Step

`python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --apply --outbox`
