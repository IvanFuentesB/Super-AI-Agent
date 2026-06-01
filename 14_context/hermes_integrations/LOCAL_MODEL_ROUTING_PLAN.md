# Local Model Routing Plan (local-first)

Status: **planning / documented truth**. Routing stays **local-first** and on loopback.
This note mirrors `local_worker_status.ps1` and the existing local routing.

## Routing truth

- **Coordinator:** Hermes = `llama3.1:8b` (local). Plans, classifies, summarizes.
- **Cheap worker:** `gemma3:4b` (local). Summaries and routine work.
- **Endpoint:** Ollama / custom endpoint on loopback only (e.g. `127.0.0.1:11434`),
  documented; the planning scripts never contact it.

## Routing rules

- Prefer the **cheapest local model** that can do the task; escalate only when needed.
- Cloud/API models are **optional, approval-gated, not extra spend**, and never required.
- No network call is made by the foundation scripts; `local_only: true`.

## Not enabled now

No live 24/7 worker, no queue, no scheduled jobs. `twenty_four_seven_mode_enabled: false`.
The llama coordinator is the documented Hermes model, not a running 24/7 process.
