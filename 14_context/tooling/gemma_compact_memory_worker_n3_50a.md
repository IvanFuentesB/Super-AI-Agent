# Gemma Compact Memory Worker — N+3.50A Tooling Doc

Script: `03_scripts/gemma_compact_memory_worker.py`
Status: IMPLEMENTED — stdlib only, local Ollama only, DRAFT output

## Purpose
Use local Ollama/Gemma3 to produce draft compression summaries of compact memory files.
Never modifies `14_context/compact_memory/` automatically.
All output is DRAFT_ONLY and requires human review before promotion.

## Commands
| Command | Effect |
|---|---|
| `--status` | Check Ollama version, list models, confirm Gemma availability |
| `--compress --input PATH --dry-run` | Preview what would be compressed |
| `--compress --input PATH --apply` | Run Gemma compression, write draft to 05_logs/gemma_compact_runs/ |
| `--max-chars N` | Truncate input to N chars (default 12000) |
| `--output-dir PATH` | Custom output directory |

## Safety Rules
- Only reads files inside repo root
- Refuses secret-like paths (`.env`, `secret`, `credential`, `token`, `key`, `password`)
- Output marked `DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED`
- Never updates canonical compact memory files
- Local Ollama only — no cloud API calls
- Output write to 05_logs/ blocked by Windows/ai_sandbox restriction; use Node.js or git hash fallback to persist if needed

## N+3.50A Status
- Ollama: FOUND (v0.9.2)
- gemma3:4b: FOUND
- Dry-run: PASS
- Apply smoke: Ollama ran OK; output write blocked by ai_sandbox restriction (known)
