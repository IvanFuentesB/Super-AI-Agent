# Local Model / Gemma Setup Guide

Ghoti uses Ollama and Gemma as a local, cheap worker lane for small summaries,
classification, and context compression. This lane is local-first and supervised:
it does not call live providers, download models automatically, post content, or
take account actions.

## Current Truth

- Ollama is available in the current local baseline: `ollama version is 0.24.0`.
- Gemma is installed only when `ollama list` proves a Gemma model is present.
- N+6.0A ran the human-approved `ollama pull gemma3:4b` on this local machine;
  verify current truth with `ollama list`.
- When Gemma is missing, weak, or not appropriate for a task, Ghoti uses
  `local_demo fallback`.
- `local_demo fallback` is deterministic local code, not a fake model claim.

## Check Status

```powershell
python 03_scripts/local_model_worker_lane.py --status --json
python 03_scripts/local_model_worker_lane.py --doctor --json
python 03_scripts/ghoti_product_launcher.py --local-worker-status --json
python 03_scripts/ghoti_product_launcher.py --gemma-status --json
python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
python 03_scripts/gemma_model_readiness.py --recommend --json
```

The status reports Ollama availability, visible models, Gemma status, active
mode, readiness percentage, and safety flags.

N+5.9A also writes Gemma readiness files:

```powershell
python 03_scripts/gemma_model_readiness.py --write-readiness --json
```

N+6.0A writes human-approved install/evaluation records:

```powershell
python 03_scripts/gemma_model_readiness.py --preflight --json
python 03_scripts/gemma_model_readiness.py --write-evaluation --json
```

Output folder:

```text
14_context/local_model_readiness/generated/
```

## Manual Gemma Commands

Ghoti may show these commands for Ivan to run later, but it will not run them
automatically:

```powershell
ollama list
ollama pull gemma3:4b
ollama pull gemma3:1b
ollama pull gemma3:270m
```

Do not pull large models from an automated milestone unless Ivan explicitly
approves it.

For N+6.0A only, Ivan explicitly approved one local model command:

```powershell
ollama pull gemma3:4b
```

That approval does not allow multiple pulls, provider setup, Telegram setup,
browser automation, or production routing.

`gemma3:4b` is the preferred first serious local worker candidate. It is listed
at about 3.3GB on Ollama's Gemma 3 page. `gemma3:1b` and `gemma3:270m` are
lighter manual alternatives for fast setup checks or constrained hardware.

## What Gemma Unlocks

With a Gemma model installed, later audited milestones can route small local
summaries and classifications through Ollama. Until then, the easy worker lane
keeps using deterministic local_demo output.

Run the quality plan before trusting the model:

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
```

Production routing remains disabled until a later human-approved milestone.

## Safety Boundaries

- No live APIs.
- No auto-downloads.
- No provider tokens.
- No Telegram setup.
- No posting or account actions.
- No money, trading, or legal actions.
- No bot/captcha/cloak bypass.

## Troubleshooting

### Ollama missing

Run `ollama --version` manually. If it is unavailable, install or start Ollama
outside Ghoti, then rerun `--doctor`.

### Ollama not running

Run `ollama list` manually. If it fails, start the local Ollama service and rerun
the Ghoti status command.

### Gemma missing

This is expected in the current baseline. Ghoti should report `local_demo
fallback active` instead of claiming a real Gemma worker is available.

### Model too slow or timeout

Keep using local_demo fallback for daily workflow. Real model routing belongs in
a later audited milestone after performance is known.

### Output missing

Run:

```powershell
python 03_scripts/local_model_worker_lane.py --write-demo-output --json
```

Then refresh the dashboard Local Model / Easy Worker Lane card.

## Roadmap

- model routing between local_demo and installed Ollama models
- context pack summarization through a real local Gemma model
- small local coding-assistant tasks
- local report summarizer
- Graphify repo knowledge map
- Hermes provider support later, only after verification
