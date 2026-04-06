# Provider Adapter Roadmap

## Why Adapters Are Needed

Adapters keep provider-specific API details out of the core control logic. They make routing, approval checks, logging, and fallback behavior inspectable instead of hard-coded into one prompt or one vendor path.

## Planning Vs Live Integration

- planning-only scaffolding: provider profiles, routing notes, task fit, and council plans
- live integration: authenticated API calls, tool wiring, retries, quotas, logging, and approval-aware external execution

## Provider Groups

- OpenAI: Responses API, tool use, and computer-use style execution paths
- Claude: Claude Code or Agent SDK style integration for coding and review workflows
- Gemini: function calling, multimodal analysis, and video-related planning paths
- Gemma local: Ollama or another local runtime for privacy-sensitive drafts and fallback work
- Optional later research adapter: search-oriented providers such as Perplexity or similar

## Routing Philosophy

- do not hard-code that one provider is always best
- use provider profiles, evals, approval requirements, and task fit
- keep local fallback explicit instead of magical

## Recommended Near-Term Order

1. OpenAI
2. Gemma local
3. Gemini
4. Claude
5. optional research adapters later

## Still Unimplemented

- no live provider adapters
- no shared provider interface
- no auth/token handling layer
- no real model eval loop feeding routing decisions yet
