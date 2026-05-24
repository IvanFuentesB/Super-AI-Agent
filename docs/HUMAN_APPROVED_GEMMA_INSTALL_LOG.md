# Human-Approved Gemma Install Log

N+6.0A is the first milestone allowed to install exactly one local Ollama model,
and only because Ivan explicitly approved `ollama pull gemma3:4b` in the
milestone prompt.

## Scope

- Approved model: `gemma3:4b`
- Approved command: `ollama pull gemma3:4b`
- Do not pull multiple models.
- Do not pull `gemma3:1b` or `gemma3:270m` unless a later human prompt approves
  that fallback after documenting why `gemma3:4b` is unsafe or impossible.
- Do not call live provider APIs.
- Do not configure Hermes providers, Telegram, browser automation, or cloud
  providers.
- Do not enable production routing automatically after install.

## Preflight And Evaluation Files

Preflight files are written under:

```text
14_context/local_model_evaluation/runs/<timestamp>_gemma_preflight/
```

Evaluation files are written under:

```text
14_context/local_model_evaluation/runs/<timestamp>_gemma3_4b_quality_eval/
```

If the model is unavailable, Ghoti writes a controlled fallback run ending in:

```text
<timestamp>_gemma_missing_quality_eval/
```

## Commands

Check readiness:

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
python 03_scripts/gemma_model_readiness.py --preflight --json
```

Run the first local evaluation summary:

```powershell
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
python 03_scripts/gemma_model_readiness.py --write-evaluation --json
```

The install command is manual and approval-bound:

```powershell
ollama pull gemma3:4b
```

## Current Truth

This document is the policy log. The generated run files are the source of truth
for whether `gemma3:4b` was actually installed and evaluated in this workspace.
If install fails, `local_demo` fallback remains active and Ghoti must not claim a
real Gemma worker is available.

## N+6.0A Result

- Preflight directory:
  `14_context/local_model_evaluation/runs/20260524T140851Z_gemma_preflight/`
- Install command run once:
  `ollama pull gemma3:4b`
- Install result:
  `ollama list` reports `gemma3:4b` installed at 3.3 GB.
- Final evaluation directory:
  `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval/`
- Final local quality score:
  `86%` (`6 / 7` tasks passed).
- Important limitation:
  the repo-bundle identification task hallucinated a nonexistent external bundle,
  so production routing remains disabled and N+6.1A should not route repo
  knowledge selection to Gemma without a tighter task wrapper and another audit.
