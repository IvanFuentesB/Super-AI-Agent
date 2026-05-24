# Gemma / Local Model Readiness Status

Local model readiness: 74%. Ollama is installed (ollama version is 0.24.0). Gemma model available: gemma3:4b. Active mode is ollama_gemma. Production routing remains disabled.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Gemma status command: `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`
- Gemma doctor command: `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`
- Gemma quality plan command: `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`
- Local model eval command: `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`
- Ollama installed: `True`
- Ollama version: `ollama version is 0.24.0`
- Ollama reachable: `True`
- Installed model count: `1`
- Gemma installed: `True`
- Preferred model: `gemma3:4b`
- Preferred model installed: `True`
- Fallback models installed: `none`
- Active worker mode: `ollama_gemma`
- Gemma readiness percentage: `74%`
- Local worker readiness percentage: `75%`
- Production routing enabled: `false`
- Manual approval required: `true`
- Real local evaluation status: `real_gemma_eval_complete`
- Latest eval score: `86`
- Latest eval run path: `14_context/local_model_evaluation/runs/20260524T143110Z_gemma3_4b_quality_eval`

## Visible Models

- `gemma3:4b`

## Recommendation

gemma3:4b is installed. Run the local quality plan next, but keep production routing disabled until a later human-approved milestone.

Safety: No live APIs, no auto-downloads, no `ollama pull` performed, no provider tokens, production routing remains disabled.
