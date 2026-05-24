# Local Worker Next Steps

1. Run `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`.
2. Review `14_context/local_model_readiness/generated/gemma_install_decision.md`.
3. If Ivan approves a model download later, run `ollama pull gemma3:4b` manually.
4. Rerun `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`.
5. Rerun `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`.
6. Keep production routing disabled until a later audited milestone.

Current mode: `ollama_gemma`.
Recommendation: gemma3:4b is installed. Run the local quality plan next, but keep production routing disabled until a later human-approved milestone.
