# Local Model / Easy Worker Lane Status

Local worker readiness: 75%. Ollama is installed (ollama version is 0.24.0), Gemma is installed, so real local evaluation is possible. Production routing remains gated. No live APIs, no auto-downloads.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Local worker status: `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json`
- Local worker demo: `python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json`
- Active mode: `ollama_gemma`
- Ollama available: `True`
- Ollama version: `ollama version is 0.24.0`
- Gemma installed: `True`
- Gemma model: `gemma3:4b`
- Manual check command: `ollama list`
- Manual install command: `ollama pull gemma3:4b`

## Visible Local Models

- `gemma3:4b`

Safety: no live APIs, no auto-downloads, no posting, no account actions.
