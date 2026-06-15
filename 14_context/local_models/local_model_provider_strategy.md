# Local Model Provider Strategy

Goal: route cheap drafting/summary work to local or low-cost models through the
existing Agent OS approval queue and run records - never as a hidden side
channel.

## Providers

- **Ollama (local, present)** - default for cheap drafts/summaries. No keys, no
  network beyond localhost.
- **OpenRouter (optional fallback)** - only if a draft needs a stronger model;
  `OPENROUTER_API_KEY` set locally, never committed. Real calls are audited
  separately before enabling.
- **Deterministic local fallback** - when no model is available, the existing
  deterministic fallback worker produces a bounded draft. This stays the safe
  default.

## Routing rules

1. All model output is a *draft/suggestion*, written to repo-local artifacts via
   the bounded executor; it is never executed as a command.
2. Routing decisions and outputs are recorded in run records / evidence, like
   any other approved worker step.
3. Any real (non-local) model invocation is gated by a separate approval and
   audit; it is off by default.
4. No provider keys live in the repo. No external writes. No account actions.

## Next step

Wire an approved "local model draft" worker that proposes which provider to use
and produces a bounded draft, behind the approval queue + Rust guard - same
pattern as the existing local-model-summary-classification-worker.
