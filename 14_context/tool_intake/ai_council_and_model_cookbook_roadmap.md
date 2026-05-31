# AI Council, Model Cookbook, Deep Research & Document Editor Roadmap (candidate-only)

Status: **candidate_only**, planning only. These are the workspace-side ideas
extracted from Odysseus. Nothing is installed, downloaded, or wired into the
runtime; each remains a documented candidate evaluated through the N+6.7A intake
pipeline.

## AI Council / Model Compare

- **Value:** blind, council-style comparison of multiple model answers so the human
  picks the best one. Fits Ghoti's existing local routing (llama3.1:8b coordinator,
  gemma3:4b worker).
- **Local-first path:** compare local Ollama models on loopback only
  (`http://127.0.0.1:11434`); answers shown unlabeled; the human chooses.
- **External path (gated):** API models may be added later, approval-only, with keys
  supplied at run time and never stored.
- **First safe test:** a blind-compare spec that reads two model outputs from local
  fixtures and presents them unlabeled; no live API; no key storage.
- **Forbidden now:** storing API keys, calling paid APIs without approval, auto-acting
  on the winning answer.

## Model Cookbook / Hardware Fit

- **Value:** a cookbook mapping models to hardware fit (VRAM/RAM/CPU) so Ghoti only
  picks models that actually run on the local machine.
- **Local-first path:** a static table of the approved local models and their resource
  needs; read-only reference.
- **First safe test:** write the static cookbook table for the currently approved local
  models; no downloads, no installs.
- **Forbidden now:** auto-downloading model weights, install actions, pulling
  unapproved models.

## Deep Research Visual Reports

- **Value:** structured research reports (sections + visuals) from a query, using local
  search plus local summarization, output as a Markdown draft.
- **Local-first path:** an approved local search (SearXNG-style) plus a local
  summarizer; the report is a draft the human reviews.
- **External path (gated):** external search APIs are approval-only; keys are never
  stored; reports are never auto-published.
- **First safe test:** spec a report template and run a dry summarization over a local
  fixture corpus; no live web calls.
- **Forbidden now:** live web scraping without approval, storing search API keys,
  auto-publishing a report.

## Document Editor for Project Documentation

- **Value:** an AI-assisted editor for Ghoti's own docs/memory - draft, revise, and
  summarize Markdown, always proposing a diff for human approval.
- **Local-first path:** operate only on repo Markdown under approved folders; a
  local-model assist proposes a diff; the human applies it; the tool never auto-writes.
- **First safe test:** propose a Markdown diff for a doc under `14_context/`; the human
  applies it; nothing is auto-written or auto-committed.
- **Forbidden now:** auto-writing or auto-committing, editing outside the repo root,
  touching `.env`/secrets.

## Phasing

- **Phase 1 (local-first specs):** AI council compare harness, model cookbook table.
- **Phase 2 (local drafts):** deep research draft, document-editor diff proposals.
- **Integration** only after each has tests proving safe behavior and a Codex audit
  passes. "Documented + statically reviewed" is the default resting state.

## Not enabled by this roadmap

No MCP, no browser-use, no computer-use, no Telegram. No model downloads, no installs,
no live API calls without approval, no stored keys. `main` is untouched.
