# Local Model Routing Guide

N+6.1A adds constrained local model routing for small, boring, offline tasks. It uses `gemma3:4b` when available, then validates output with the repo-bundle hallucination guard before trusting it. If the guard rejects the model output, Ghoti falls back to deterministic `local_demo` output.

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-route-task status-paragraph --json
python 03_scripts/ghoti_product_launcher.py --local-worker-routing-demo --json
```

Allowed routed tasks:

- `summarize-latest-report`
- `status-paragraph`
- `codex-next-prompt`
- `safety-classification`
- `context-bundle-summary`
- `next-milestone-outline`
- `report-to-bullets`

Blocked tasks include code editing, shell commands, browser actions, API actions, posting, money/trading/legal decisions, credential/session handling, unsupported file claims, and live account operations.

Safety boundaries: no live APIs, no provider setup, no Telegram setup, no browser automation, no commands executed from model output, and no file edits from model output.
