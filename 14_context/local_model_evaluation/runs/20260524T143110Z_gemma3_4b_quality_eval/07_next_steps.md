# Local Model Evaluation Next Steps

Review the score, then build N+6.1A routing only if the audit stays clean.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Local eval: `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`
- Gemma doctor: `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json`

Keep no live APIs, no provider setup, no Telegram setup, no browser automation, and no production routing.
