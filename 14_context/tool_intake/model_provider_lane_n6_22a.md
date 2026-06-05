# Model / provider routing lane (N+6.22A)

Static, planning-only research lane for **cheap, long-context model routing**. No API
keys, no live calls, no secrets committed.

## Candidates / research

- **DeepSeek** (newest / V4-like, cheap long-context provider) - org page
  `github.com/deepseek-ai` (`needs_verification` for the specific model/routing repo).
  Interesting as a low-cost long-context option for bulk/cheap work.
- **Kimi (Moonshot) + Claude swarms** - research combining a cheap long-context
  provider (Kimi) for breadth with Claude for high-quality steps, as **simulated**
  swarms first (via the N+6.21A Agent Arena) before any live multi-provider run.
- **Composio / provider abstraction** - integration layer; keys deferred.

## Routing idea (research only)

- Cheap/long-context provider for wide, low-stakes passes (summarize, scan, draft).
- Premium provider (Claude) for the careful steps (implement, audit, merge-gate).
- A local router would pick the provider per task by cost/quality - **planned, not
  built**, and never with committed keys.

## Hard rules

- No API keys or secrets in the repo - all provider research stays abstract until a
  secret-management milestone.
- No live calls during this lane; this is a written routing plan only.
- Local-first: prefer local models (Ollama/Gemma) where possible; remote providers stay
  optional and key-gated.
