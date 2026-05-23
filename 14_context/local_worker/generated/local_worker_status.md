# Local Model / Easy Worker Lane Status

Local worker readiness: 45%. Ollama is installed (ollama version is 0.24.0), Gemma is missing, so Ghoti is using local_demo fallback. Context packs and deterministic summaries work now; run the documented manual Gemma command later to unlock real local worker tasks. No live APIs, no auto-downloads.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Local worker status: `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- Local worker demo: `python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json`
- Active mode: `local_demo`
- Ollama available: `True`
- Ollama version: `ollama version is 0.24.0`
- Gemma installed: `False`
- Gemma model: `missing`
- Manual check command: `ollama list`
- Manual install command: `ollama pull gemma3:4b`

## Visible Local Models

- none visible

Safety: no live APIs, no auto-downloads, no posting, no account actions.
