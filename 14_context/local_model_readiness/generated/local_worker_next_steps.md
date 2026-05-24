# Local Worker Next Steps

1. Run `python 03_scripts/ghoti_product_launcher.py --gemma-status --json`.
2. Review `14_context/local_model_readiness/generated/gemma_install_decision.md`.
3. If Ivan approves a model download later, run `ollama pull gemma3:4b` manually.
4. Rerun `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`.
5. Rerun `python 03_scripts/ghoti_product_launcher.py --gemma-quality-plan --json`.
6. Keep production routing disabled until a later audited milestone.

Current mode: `local_demo`.
Recommendation: Gemma is missing. Keep local_demo fallback active, or manually approve `ollama pull gemma3:4b` later.
