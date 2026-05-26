# Token-Efficient Computer-Use Roadmap

## Token Efficiency

- Evaluate Graphify for knowledge graph compression and source memory.
- Use the N+5.7A local repo knowledge map now for selected file maps, latest
  report indexes, subsystem indexes, and task bundles.
- Create local compact memory snapshots before sending context to premium models.
- Use Gemma/Ollama for cheap summarization and classification only after local
  availability and quality are proven.
- Avoid sending the whole repo to premium models.
- Route easy tasks to local workers when possible.
- Route implementation to Claude Code when available.
- Route audits and verification to Codex.
- Route planning/product reasoning to ChatGPT/Claude when manually invoked.
- Cache source intelligence packets.
- Compress context into Obsidian/compact memory.
- Show token-saving truth in the dashboard through Local Memory, Local Worker,
  Gemma / Local Model Quality, Repo Knowledge / Graphify Lane, and Hermes Agent
  / Manual Bridge cards.

## Current Priority Sequence

Ghoti's near-term roadmap now prioritizes local models, Hermes workflows, and
safe computer-use preparation because the operator needs to automate long,
boring task sequences without burning paid credits.

1. N+6.1B - constrained Gemma worker routing with a repo-bundle hallucination
   guard is the current main baseline.
2. N+6.2A - Hermes Agent Workflow / Manual Bridge Verification. Verify WSL path
   mapping, skills, safe commands, blocked commands, and manual bridge guide
   files only; no tokens, provider setup, Telegram setup, live APIs, browser
   automation, or computer-use click/type.
3. N+6.3A - Safe Computer-Use Preparation with Gemma, Hermes, UI-TARS
   observation, Browser Harness, and Vercel agent-browser roadmap. Observation
   comes first, and every click/type/live-account action stays behind explicit
   human approval.

N+6.2A must never run Hermes setup, provider config, Telegram setup, live APIs,
browser automation, or computer-use click/type. It verifies the manual bridge
only.

## Gemma / Local Model Quality

- Current implementation: local readiness and quality-plan files under
  `14_context/local_model_readiness/generated/`, plus N+6.0A evaluation runs
  under `14_context/local_model_evaluation/runs/`.
- Current commands:
  `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`,
  `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`,
  `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`,
  and `python 03_scripts/ghoti_product_launcher.py --gemma-write-readiness --json`.
- Current truth: N+6.0A installed `gemma3:4b` after explicit human approval;
  future truth must still be verified with `ollama list`.
- First real local quality eval: 86%, 6 of 7 tasks passed. The failed
  repo-bundle task hallucinated an external bundle, so N+6.1A routes only
  allowlisted offline tasks through a source guard and fallback.
- Manual command candidates are documented, but Codex must not run additional
  `ollama pull` commands automatically.
- Broad production routing to Gemma remains disabled; N+6.1A is a constrained
  safe-task lane with no command/file/browser/account execution from model
  output.

## Repo Knowledge / Graphify Lane

- Current implementation: local JSON/Markdown files under
  `14_context/repo_knowledge/generated/`.
- Current commands:
  `python 03_scripts/ghoti_repo_knowledge_map.py --write --json` and
  `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`.
- Current bundles: audit-main, dashboard, local-memory, local-model-worker,
  local-model-routing, hermes, content-workflow, safety, and next-milestone.
- Graphify runtime status: roadmap only/not wired.
- External repo runtime: not wired.
- Network: not used.
- Later Graphify work should add richer graph retrieval only after a separate
  audit gate.

## Hermes Manual Bridge

- Current implementation: safe readiness files under
  `14_context/hermes_workflow/generated/` and WSL/manual guide files under
  `14_context/hermes_manual_bridge/generated/`.
- Current commands:
  `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
  `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`,
  `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json`,
  and `python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json`.
- This saves tokens by producing a small skills index, manual setup checklist,
  and operator bridge packet.
- Hermes provider setup, Telegram, tokens, live APIs, browser automation, and
  computer-use click/type remain manual later.

## Computer Use

- UI-TARS remains observation-only.
- Hermes remains manual-bridge only until N+6.2A verifies safe local workflow
  surfaces without setup/tokens/live APIs.
- Future click/type controls require a separate audited milestone.
- Browser automation should be compliant QA, not bypass or abuse.
- Browser actions need human approval for real effects.
