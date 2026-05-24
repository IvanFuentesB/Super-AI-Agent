# Gemma Model Install Decision

N+5.9A is a decision and readiness milestone. It checks local Ollama/Gemma
truth, writes an install plan, and keeps `local_demo` fallback active. It does
not download models automatically.

## Current Truth

- Ollama is installed in the current baseline: `ollama version is 0.24.0`.
- Gemma is missing unless `ollama list` proves a Gemma model is present.
- Active mode remains `local_demo` fallback while Gemma is missing.
- Production routing remains disabled.
- No live APIs, provider tokens, Hermes setup, Telegram setup, or browser
  automation are part of this milestone.

## Check Before Deciding

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-status --json
python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
python 03_scripts/gemma_model_readiness.py --recommend --json
```

## Recommended First Manual Pull

```powershell
ollama pull gemma3:4b
```

Manual approval required before model download. Ghoti must not run this command
automatically.

Why 4B first: it is the first serious local worker candidate for compact
memory, summaries, classifications, tracker rows, and short drafts without
jumping to larger 12B/27B models. Ollama's Gemma 3 page lists `gemma3:4b` at
about 3.3GB with a 128K context window, and Gemma 3 requires Ollama 0.6 or
later. The local machine reports Ollama 0.24.0, but the actual model still must
be installed manually and verified locally.

## Lighter Manual Alternatives

```powershell
ollama pull gemma3:1b
ollama pull gemma3:270m
```

Use these if Ivan wants a faster low-risk smoke test or the machine struggles
with the 4B model. They may be useful for setup checks, but quality may be
weaker.

## When To Stay On local_demo

Stay on `local_demo` when:

- disk, RAM, VRAM, or time is constrained
- the model pull has not been explicitly approved
- quality has not been measured yet
- the task is a deterministic status, report, or prompt-pack generation

Codex, Claude, and ChatGPT remain the right tools for hard coding, audits,
complex reasoning, browser/computer-use work, and provider decisions until local
quality is proven.
