# Machine Capability Summary

Last updated: 2026-04-05

## Verified hardware

- CPU: AMD Ryzen 9 8945HS
- Cores / threads: 8 / 16
- RAM: 32 GB
- GPU 1: NVIDIA GeForce RTX 4060 Laptop GPU
- VRAM reported by `nvidia-smi`: 8188 MiB
- GPU 2: AMD Radeon 780M Graphics
- Storage free on `C:`: about 315 GB
- OS: Windows 11 Home Single Language, 64-bit

## What this machine is good at

- serious software development
- local automation and scripting
- local indexing, retrieval, and prompt/eval workflows
- small to medium local models
- quantized local models via Ollama or llama.cpp
- browser automation and desktop orchestration later

## What is realistic for local models later

Low-risk local path:

- Gemma 4 E2B
- Gemma 4 E4B
- similar small or mid-size quantized coding/chat models

Balanced path:

- one local daily-driver model
- one cloud fallback model
- local reranking, embeddings, and eval tools

Possible but not ideal as a daily default:

- Gemma 4 26B quantized experiments
- larger coding agents with heavy context and tool use

Not realistic as a clean daily local-first default on this hardware:

- running multiple large models concurrently
- using 31B-class models as the main always-on local assistant without major tradeoffs
- pretending 8 GB VRAM is enough for a comfortable high-end local stack with no compromises

## Practical recommendation

Use this machine as a strong hybrid workstation:

- local first for day-to-day agent work, scripts, search, editing, and smaller models
- cloud fallback for harder reasoning and long-context tasks
- keep the stack modular so local and cloud backends can swap without changing the workflow

## Verified Gemma notes

Official Google docs for Gemma + Ollama currently list Gemma 4 sizes as:

- `gemma4:e2b`
- `gemma4:e4b`
- `gemma4:26b`
- `gemma4:31b`

Official source used:

- https://ai.google.dev/gemma/docs/integrations/ollama

Practical interpretation for this machine:

- E2B and E4B are the realistic local starting points
- 26B and 31B are later experiments, not the first daily-driver plan
