# Local Model Quality Evaluation Guide

N+5.9A prepares local task quality evaluation without pretending Gemma is
installed. The current fallback result is a deterministic `local_demo` plumbing
check, not real model quality. production routing remains disabled.

## Commands

```powershell
python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json
python 03_scripts/gemma_model_readiness.py --quality-plan --json
python 03_scripts/gemma_model_readiness.py --write-readiness --json
```

Generated files live under:

```text
14_context/local_model_readiness/generated/
```

Important files:

- `gemma_readiness_status.md`
- `gemma_install_decision.md`
- `gemma_manual_commands.md`
- `local_task_quality_plan.md`
- `local_task_quality_rubric.json`
- `local_demo_quality_eval.json`

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

Do not route production work to Gemma by default. A later human-approved
milestone should install a model, run the quality plan, inspect outputs, and
only then decide whether any low-risk tasks can use the local model.

Local Gemma should start with easy, low-risk work only: summaries,
classifications, tracker rows, compact memory, simple drafts, and status
extraction. Codex, Claude, and ChatGPT remain for hard coding, audits, browser
work, and complex reasoning until local quality is proven.
