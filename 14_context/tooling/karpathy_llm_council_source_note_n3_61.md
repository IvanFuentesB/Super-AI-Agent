# Karpathy LLM Council — Source Note — N+3.61A

## Source Concept

Concept: karpathy/llm-council (GitHub: github.com/karpathy/llm-council)

The original project implements a multi-model council system using OpenRouter as the
API gateway, with a frontend/backend stack and full provider integration.

## What We Did and Did Not Do

We did NOT:
- Clone or vendor the karpathy/llm-council repository
- Copy any code from the original project
- Install its dependencies (Node, npm packages, Python packages, OpenRouter SDK)
- Wire its frontend or backend into Ghoti
- Make any external API calls in our implementation

We DID:
- Implement a Ghoti-local scaffold inspired by the 3-stage architectural concept:
  Stage 1: individual first opinions, Stage 2: anonymous peer review, Stage 3: chairman synthesis
- Write this as a single stdlib-only Python script (03_scripts/llm_council_runner.py)
- Disable all external providers by default
- Add local_demo mode (no model required) and optional ollama_local mode
- Store sessions locally in 05_logs/llm_council_runs/ (not staged to git)
- Add safety flags in all session output: LOCAL_ONLY_BY_DEFAULT, NO_AUTONOMOUS_ACTIONS,
  HUMAN_REVIEW_REQUIRED, EXTERNAL_CALLS_DISABLED_BY_DEFAULT

## If We Later Clone the Reference App

If we decide to vendor the original source for reference or evaluation:
- Put it under `21_repos/third_party/evals/llm-council`
- Keep it intake-only: read-only, no install, no runtime wiring
- Do not run `npm install` or `pip install` in the intake copy
- Audit before any integration with Ghoti runtime

## Architectural Differences

| Aspect | karpathy/llm-council | Ghoti Council Scaffold |
|--------|---------------------|------------------------|
| Backend | Node.js / Python | Pure Python stdlib |
| Provider | OpenRouter (live API) | local_demo (default), ollama_local (optional) |
| External calls | Yes (required) | No (disabled by default) |
| Frontend | Web UI | CLI only |
| Auth | API key required | No key required (local_demo) |
| Deployment | Cloud / web | Local only |
| Autonomous actions | Not applicable | Explicitly disabled |

## Why Local-First First

Ghoti's safety model requires:
1. Human approval gates before any external action
2. No secrets stored in the repo
3. No autonomous posting, emailing, paying, or trading
4. No package installs without operator approval

The local_demo mode satisfies all of these while proving the 3-stage architecture.
External providers can be added later under explicit operator authorization.
