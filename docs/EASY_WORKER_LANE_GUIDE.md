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
python 03_scripts/ghoti_product_launcher.py --gemma-status --json
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
```

## Safe Demo Tasks

- summarize latest Ghoti report
- compress latest status into one paragraph
- classify next task as coding, docs, audit, content, or research
- generate a short Codex next prompt from the context pack
- classify safety risk for a local-only request
- summarize a known context bundle
- outline the next milestone from repo-local context
- compress a report to bullets

These tasks are deterministic in `local_demo fallback` mode. They do not call
live APIs or download models.

N+5.9A adds the **Gemma / Local Model Quality** lane. Use it to decide whether
to stay on `local_demo`, manually pull `gemma3:4b`, or try a lighter manual
fallback (`gemma3:1b` or `gemma3:270m`). The lane writes a quality plan but does
not route production work to Gemma.

N+6.0A adds the first human-approved local evaluation packet. When `gemma3:4b`
is installed, the eval command can compare real local Gemma output to
`local_demo`. If the model is missing, the eval reports a controlled fallback
instead of pretending quality was measured.

Current N+6.0A result: `gemma3:4b` installed locally and the first eval scored
86%, with 6 of 7 tasks passing. The failed task hallucinated a repo bundle, so
real routing remains a later audited decision rather than an automatic switch.

N+6.1A should build only constrained routing for these boring local tasks. It
must use known repo-map bundle IDs only, reject invented bundle/file claims,
require source metadata, fall back to `local_demo` if the guard fails, and never
execute commands or edit files from model output.

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

Read the **Gemma / Local Model Quality** card for real model availability,
manual approval status, the recommended manual command, quality evaluation
status, and generated readiness files.

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

- N+6.1A constrained Gemma worker routing plus repo-bundle hallucination guard
- N+6.2A Hermes Agent Workflow / Manual Bridge Verification, safe probes only
- N+6.3A Safe Computer-Use Preparation with Gemma, Hermes, UI-TARS observation,
  Browser Harness, and Vercel agent-browser roadmap
- Graphify-grade context retrieval later
- Hermes provider later, only after support is proven and explicitly approved
