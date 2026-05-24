# Gemma / Local Model Readiness Status

Local model readiness: 45%. Ollama is installed (ollama version is 0.24.0). Gemma is missing, active mode is local_demo fallback, and no auto-downloads are enabled.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Gemma status command: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Gemma doctor command: `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`
- Gemma quality plan command: `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`
- Ollama installed: `True`
- Ollama version: `ollama version is 0.24.0`
- Ollama reachable: `True`
- Installed model count: `0`
- Gemma installed: `False`
- Preferred model: `gemma3:4b`
- Preferred model installed: `False`
- Fallback models installed: `none`
- Active worker mode: `local_demo`
- Gemma readiness percentage: `45%`
- Local worker readiness percentage: `45%`
- Production routing enabled: `false`
- Manual approval required: `true`

## Visible Models

- none visible

## Recommendation

Gemma is missing. Keep local_demo fallback active, or manually approve `ollama pull gemma3:4b` later.

Safety: No live APIs, no auto-downloads, no `ollama pull` performed, no provider tokens, production routing remains disabled.
