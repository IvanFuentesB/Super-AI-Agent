# Graphify Repo Knowledge Roadmap

## Current State

N+5.7A implements a lightweight local repo knowledge map. It is JSON/Markdown
only and lives under `14_context/repo_knowledge/generated/`.

Current status:

- Repo knowledge readiness: 55%.
- Local file map: available.
- Latest report index: available.
- Task bundles: available.
- Graphify runtime: roadmap only/not wired.
- External repo runtime: not wired.
- Network: not used.

## Why Graphify Matters

Graphify is the future direction for richer repo knowledge retrieval: turning
files, reports, docs, tests, and milestones into a navigable graph so Ghoti can
retrieve the right context without large prompts.

The current local map is deliberately simpler. It gives Ghoti useful context
retrieval now while avoiding external runtime risk.

## Later Capabilities

Future milestones can explore:

- file-to-subsystem graph edges
- report-to-commit and report-to-test links
- function/class symbol maps
- changed-file-to-test recommendations
- context bundle scoring
- Obsidian backlink export
- local model summaries of selected nodes when Gemma is installed
- optional Graphify runtime integration after audit

## Not Wired Yet

- No Graphify service.
- No graph database.
- No external repo clone/install/run.
- No network calls.
- No live provider calls.
- No automatic browser/computer-use control.

## Safety Gate For Real Graphify

A later Graphify runtime milestone should require:

- a clean feature branch and audit branch
- static review of the external tool
- no secrets or credentials in generated data
- explicit allowlist for scanned directories
- bounded file sizes
- no live APIs by default
- dashboard truth labels for runtime state
- public/security audit pass
- N+4/N+5 tests green

## Recommended Next Step

Use the local repo knowledge map through:

```powershell
python 03_scripts/ghoti_product_launcher.py --repo-map --json
python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
```

Then proceed to N+5.8A: Hermes Agent Workflow / Provider Setup Plan + Manual
Bridge Readiness.
