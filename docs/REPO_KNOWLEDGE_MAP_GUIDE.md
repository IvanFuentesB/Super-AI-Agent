# Repo Knowledge Map Guide

## Purpose

The repo knowledge map gives Ghoti a compact local index of the files, reports,
scripts, and docs that matter most right now. It helps Ivan ask Codex, ChatGPT,
or Claude for focused work without pasting the whole repo history.

This is not an autonomy layer. It does not call live providers, clone external
repos, run Graphify, or use network.

## Commands

```powershell
python 03_scripts/ghoti_repo_knowledge_map.py --status --json
python 03_scripts/ghoti_repo_knowledge_map.py --scan --json
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
python 03_scripts/ghoti_repo_knowledge_map.py --bundle next-milestone --json
python 03_scripts/ghoti_product_launcher.py --repo-map --json
python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
python 03_scripts/ghoti_product_launcher.py --repo-bundle hermes --json
```

## Generated Files

Output directory:

```text
14_context/repo_knowledge/generated/
```

Files:

- `repo_knowledge_map.json`
- `repo_knowledge_map.md`
- `latest_reports_index.md`
- `subsystem_index.md`
- `task_bundle_audit_main.md`
- `task_bundle_dashboard.md`
- `task_bundle_local_memory.md`
- `task_bundle_local_model_worker.md`
- `task_bundle_hermes.md`
- `task_bundle_content_workflow.md`
- `task_bundle_safety.md`
- `task_bundle_next_milestone.md`
- `codex_next_prompt_graph_context.md`
- `chatgpt_repo_context_summary.md`

## Task Bundles

Use task bundles to reduce token load:

- `audit-main` for current-main verification.
- `dashboard` for Product Control Center work.
- `local-memory` for context pack and Obsidian work.
- `local-model-worker` for Ollama/Gemma/local_demo work.
- `hermes` for the next Hermes manual bridge milestone.
- `content-workflow` for supervised content demo work.
- `safety` for public/security and unsafe automation checks.
- `next-milestone` for the next recommended milestone prompt.

Each bundle includes purpose, files to inspect first, current truth, safety
boundaries, useful commands, validation commands, known limitations, and a next
prompt.

The `hermes` bundle now points to the Hermes Agent / Manual Bridge files:

- `03_scripts/hermes_agent_workflow_bridge.py`
- `docs/HERMES_AGENT_WORKFLOW_GUIDE.md`
- `docs/HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md`
- `14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md`

## Safety

- Local-only.
- No live APIs.
- No network.
- No external repo runtime.
- No provider setup.
- No posting or account actions.
- No money, trading, or legal actions.
- UI-TARS remains observation-only.
- Hermes setup, provider config, Telegram, and token flows remain manual later.

## Dashboard

The dashboard card is **Repo Knowledge / Graphify Lane**. It shows repo
knowledge readiness, map path, latest report index, task bundles, the
recommended prompt path, and the truth that Graphify is roadmap only/not wired.

## Troubleshooting

If files are missing, run:

```powershell
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
```

If a bundle looks stale, regenerate the map after the newest merge/audit report
is committed.

If a file is missing from the index, add it to the selected safe catalog in
`03_scripts/ghoti_repo_knowledge_map.py` with a subsystem and a short reason.
