# Gemma Compression — N+3.56-FIX

**Script**: `03_scripts/gemma_compact_memory_worker.py`

## What changed in N+3.56-FIX

- `--status` output now explicitly labeled: Ollama found YES/NO, Ollama version, Gemma model found YES/NO, selected model, safe write fallback.
- Output markers listed in status: `DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED`.

## --status output format
```
Ollama found    : YES/NO
Ollama version  : v0.9.2
Gemma model found: YES/NO
Selected model  : gemma3:4b
Safe write fallback: Node.js
Output markers  : DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED
```

## Validation commands
```bash
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
```

## What is NOT done automatically
- No canonical compact memory writes.
- All output is `DRAFT_ONLY`.
- Human review required before any promotion to `14_context/compact_memory/`.
- No cloud API.

## If Ollama is missing
```
Ollama found    : NO
Recommendation  : Install Ollama from https://ollama.com; then: ollama pull gemma3:4b
```
