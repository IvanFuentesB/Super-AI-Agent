# Claude N+3.63A — OpenFang MoneyPrinter Content Runway

**Branch:** feat/ghoti-agent-claude-n3-63-openfang-moneyprinter-content-runway
**Base:** origin/feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness (d807c5a)
**Date:** 2026-05-07

## Mission

Build a clean, auditable N+3.63A branch that advances Ghoti toward a 100% locally-supervised MVP by:

1. Adding external repo intake cards for OpenFang (two candidates) and MoneyPrinter (V1 + V2).
2. Creating a local-first, approval-gated Content Money Workflow scaffold.
3. Routing and dashboard integration for both new scaffolds.
4. No clone, no install, no run, no live posting, no secrets, no external API calls.

## Deliverables

| File | Purpose |
|------|---------|
| `03_scripts/external_repo_intake.py` | Stdlib-only catalog/intake tool for external repo candidates |
| `03_scripts/content_money_workflow.py` | Local-first content planning scaffold |
| `03_scripts/local_worker_router.py` | Updated with 2 new routes |
| `03_scripts/ghoti_dashboard.py` | Updated with 2 new sections, milestone=N+3.63A |
| `23_configs/external_repo_intake.example.json` | Config with all actions disabled |
| `23_configs/content_money_workflow.example.json` | Config with publishing disabled |
| `23_configs/local_worker_routing.example.json` | Updated with 2 new workers |
| `14_context/tooling/external_repo_intake_catalog_n3_63.md` | Catalog doc |
| `14_context/tooling/external_repo_risk_report_n3_63.md` | Risk report doc |
| `14_context/tooling/openfang_intake_n3_63.md` | OpenFang intake notes |
| `14_context/tooling/moneyprinter_intake_n3_63.md` | MoneyPrinter intake notes |
| `14_context/tooling/content_money_workflow_n3_63.md` | Workflow doc |
| `14_context/tooling/ghoti_100_percent_runway_n3_63.md` | 100% runway doc |

## Safety Statements

- OpenFang intake only — no clone, no install, no run.
- MoneyPrinter intake only — no clone, no install, no run.
- Content workflow planning only — no upload, no post, no live actions.
- No secrets stored or read.
- No external API calls by default.
- Human review required before any real integration.
- "100%" means local-supervised MVP, not autonomous money machine.

## OpenFang Ambiguity

Two separate projects use the name "OpenFang":

- **aidiss/openfang** (Python gateway) — lightweight Python AI agent gateway, FastAPI/HTMX, ~5K LOC. Tracked as `openfang_python_gateway`.
- **RightNow-AI/openfang** (Rust Agent OS) — 14 crates, Hands (Clip/Lead/Collector), security/audit architecture. Tracked as `openfang_rust_agent_os`.

Do NOT conflate these two projects.

## MoneyPrinter Note

- **MoneyPrinter by DevBySami** = FujiwaraChoki/MoneyPrinter (V1). YouTube Shorts pipeline, Ollama-first, DB queue.
- **MoneyPrinterV2** = FujiwaraChoki/MoneyPrinterV2 (V2). Higher-risk: social bots, affiliate, outreach. Tracked separately.

## Remaining Path to 100% Supervised MVP

1. Codex audit N+3.61A (done? check audit branch)
2. Merge N+3.58-FIX/N+3.61A chain or merge final branch
3. Audit N+3.63A
4. Build one end-to-end local content workflow artifact from idea to manual publish checklist
5. Add Obsidian memory snapshot
6. Add dashboard "100% MVP readiness" card
7. Only after approval, evaluate installing external repos
