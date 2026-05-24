# Local Model Quality Evaluation Guide

N+5.9A prepares local task quality evaluation without pretending Gemma is
installed. N+6.0A adds the first human-approved local model evaluation packet.
If `gemma3:4b` is installed, the evaluation can call the local Ollama service on
localhost. If Gemma is missing, the result stays a controlled `local_demo`
fallback. Production routing remains disabled either way.

## Commands

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/ghoti_product_launcher.py --local-model-eval --json
python 03_scripts/gemma_model_readiness.py --quality-plan --json
python 03_scripts/gemma_model_readiness.py --local-model-eval --json
python 03_scripts/gemma_model_readiness.py --write-evaluation --json
python 03_scripts/gemma_model_readiness.py --write-readiness --json
```

Generated files live under:

```text
14_context/local_model_readiness/generated/
14_context/local_model_evaluation/runs/
```

Important files:

- `gemma_readiness_status.md`
- `gemma_install_decision.md`
- `gemma_manual_commands.md`
- `local_task_quality_plan.md`
- `local_task_quality_rubric.json`
- `local_demo_quality_eval.json`

N+6.0A evaluation run files:

- `00_manifest.json`
- `01_model_status_before_after.json`
- `02_eval_tasks.json`
- `03_gemma_outputs.md`
- `04_local_demo_baseline.md`
- `05_quality_scores.json`
- `06_quality_review.md`
- `07_next_steps.md`
- `08_dashboard_summary.md`

## Evaluation Tasks

Future real Gemma testing should cover:

- summarize latest Ghoti report
- produce one-paragraph human status
- classify next task
- generate a concise Codex prompt from context pack
- identify relevant repo bundle
- detect unsafe automation request
- compress a long report to 10 bullets

## Scoring

Score each task on:

- JSON validity
- instruction following
- safety gate correctness
- usefulness
- hallucination risk
- latency/runtime

## Routing Rule

Do not route production work to Gemma by default; production routing remains disabled.
N+6.0A proved Gemma can help, but one repo-bundle task hallucinated a
nonexistent external bundle. N+6.1A must therefore build constrained routing
with a repo-bundle hallucination guard before any real worker task integration.

Allowed N+6.1A tasks are deliberately boring and local: summarize latest report,
status paragraph, Codex next prompt, safety classification, context bundle
summary, next milestone outline, and report-to-bullets. The router must use
known repo-map bundle IDs only, reject invented bundle or file claims, require
source metadata, fall back to `local_demo` if the guard fails, and never execute
commands or edit files from model output.

Local Gemma should start with easy, low-risk work only: summaries,
classifications, tracker rows, compact memory, simple drafts, and status
extraction. Codex, Claude, and ChatGPT remain for hard coding, audits, browser
work, and complex reasoning until local quality is proven.

After N+6.1A is clean, the roadmap priority moves to N+6.2A Hermes Agent
Workflow / Manual Bridge Verification, then N+6.3A Safe Computer-Use
Preparation with Gemma, Hermes, UI-TARS observation, Browser Harness, and Vercel
agent-browser roadmap. Those milestones still exclude provider setup, Telegram,
live APIs, uncontrolled click/type, and autonomous account actions.

## Safety Notes

- No live APIs.
- No provider setup.
- No Telegram setup.
- No browser automation.
- No production routing.
- `ollama pull` is allowed only when the current human prompt explicitly
  approves the exact model command.
