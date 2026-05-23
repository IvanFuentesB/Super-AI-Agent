# Token-Efficient Computer-Use Roadmap

## Token Efficiency

- Evaluate Graphify for knowledge graph compression and source memory.
- Use the N+5.7A local repo knowledge map now for selected file maps, latest
  report indexes, subsystem indexes, and task bundles.
- Create local compact memory snapshots before sending context to premium models.
- Use Gemma/Ollama for cheap summarization and classification.
- Avoid sending the whole repo to premium models.
- Route easy tasks to local workers when possible.
- Route implementation to Claude Code when available.
- Route audits and verification to Codex.
- Route planning/product reasoning to ChatGPT/Claude when manually invoked.
- Cache source intelligence packets.
- Compress context into Obsidian/compact memory.
- Show token-saving truth in the dashboard through Local Memory, Local Worker,
  Repo Knowledge / Graphify Lane, and Hermes Agent / Manual Bridge cards.

## Repo Knowledge / Graphify Lane

- Current implementation: local JSON/Markdown files under
  `14_context/repo_knowledge/generated/`.
- Current commands:
  `python 03_scripts/ghoti_repo_knowledge_map.py --write --json` and
  `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`.
- Current bundles: audit-main, dashboard, local-memory, local-model-worker,
  hermes, content-workflow, safety, and next-milestone.
- Graphify runtime status: roadmap only/not wired.
- External repo runtime: not wired.
- Network: not used.
- Later Graphify work should add richer graph retrieval only after a separate
  audit gate.

## Hermes Manual Bridge

- Current implementation: safe readiness files under
  `14_context/hermes_workflow/generated/`.
- Current commands:
  `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
  and `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`.
- This saves tokens by producing a small skills index, manual setup checklist,
  and operator bridge packet.
- Hermes provider setup, Telegram, tokens, live APIs, and browser automation
  remain manual later.

## Computer Use

- UI-TARS remains observation-only.
- Future click/type controls require a separate audited milestone.
- Browser automation should be compliant QA, not bypass or abuse.
- Browser actions need human approval for real effects.
