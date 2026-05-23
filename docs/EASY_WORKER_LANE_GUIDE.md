# Easy Worker Lane Guide

The Easy Worker Lane is Ghoti's first practical local worker surface. It gives
Ivan safe, repeatable offline tasks without spending provider credits and without
pretending that full autonomy exists.

## Commands

```powershell
python 03_scripts/local_model_worker_lane.py --status --json
python 03_scripts/local_model_worker_lane.py --doctor --json
python 03_scripts/local_model_worker_lane.py --demo-task summarize-latest-report --json
python 03_scripts/local_model_worker_lane.py --demo-task status-paragraph --json
python 03_scripts/local_model_worker_lane.py --demo-task classify-next-task --json
python 03_scripts/local_model_worker_lane.py --demo-task codex-next-prompt --json
python 03_scripts/local_model_worker_lane.py --write-demo-output --json
```

Launcher shortcuts:

```powershell
python 03_scripts/ghoti_product_launcher.py --local-worker-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json
```

## Safe Demo Tasks

- summarize latest Ghoti report
- compress latest status into one paragraph
- classify next task as coding, docs, audit, content, or research
- generate a short Codex next prompt from the context pack

These tasks are deterministic in `local_demo fallback` mode. They do not call
live APIs or download models.

## Generated Outputs

```text
14_context/local_worker/generated/
```

- `local_worker_status.json`
- `local_worker_status.md`
- `latest_report_summary.md`
- `status_paragraph.md`
- `codex_next_prompt_from_context.md`

## Dashboard

Open:

```text
http://127.0.0.1:3210
```

Read the **Local Model / Easy Worker Lane** card. It shows Ollama status, Gemma
status, active mode, readiness percentage, safe demo tasks, generated output
paths, and the manual Gemma command. It also states no live APIs and no
auto-downloads.

## What Still Requires Premium Models

Codex, ChatGPT, Claude, or a later configured provider is still needed for deep
coding work, nuanced product reasoning, large refactors, and high-stakes review.
The Easy Worker Lane is for small local/offline summaries and status handling.

## Troubleshooting

### local_demo fallback appears

This is correct when Gemma is missing. Ghoti remains useful for context packs,
status paragraphs, and deterministic report summaries.

### status says Ollama missing

Run `ollama --version` and `ollama list` manually. Start Ollama outside Ghoti,
then rerun `python 03_scripts/local_model_worker_lane.py --doctor --json`.

### generated files are stale

Run `python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json` and
refresh the dashboard.

### dashboard is stale

Run launcher smoke, refresh the dashboard, and stop only the recorded launcher
PID if you need to restart:

```powershell
python 03_scripts/ghoti_product_launcher.py --smoke --json
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
```

## Next Roadmap

- Graphify repo knowledge map
- better context retrieval
- real Gemma model routing after manual install
- local report summarizer using an installed model
- Hermes provider later, only after support is proven
