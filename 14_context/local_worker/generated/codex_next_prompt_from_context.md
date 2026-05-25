        Continue Ghoti / Super-AI-Agent from the current clean local-first supervised baseline.

        Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary worktree read-only except inspection.
        Refresh context first with `python 03_scripts/ghoti_product_launcher.py --context-pack --json` and inspect latest reports under `14_context/`.

        Local worker truth:
        - Run `python 03_scripts/ghoti_product_launcher.py --local-worker-status --json` to check Ollama/Gemma/local_demo mode.
        - Run `python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json` to refresh compact deterministic demo outputs.
        - Do not run `ollama pull`, live APIs, providers, Telegram, posting, or account actions unless the human explicitly approves later.

        Context prompt excerpt:

        Continue Ghoti / Super-AI-Agent from the current local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary
worktree read-only except inspection. No force-push, no history rewrite, no
secrets, no live account/API/posting/money/trading/legal actions, no bot/captcha/
cloak bypass, no fake autonomy claims, no shell-true command execution, and no live providers/tokens.

Current main hash: `1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6`
Latest clean milestone: N+6.0B - Human-Approved Gemma Install + First Local Evaluation landed on main
Current context pack milestone: N+6.1A - Constrained Local Model Routing + Repo-Bundle Hallucination Guard
Previous repo knowledge milestone: N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval
Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
Dashboard: `http://127.0.0.1:3210`

Status truth:
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0.
- Hermes Agent / Manual Bridge exposes safe status, skills index, manual checklist, and bridge packet.
- Hermes browser/Playwright degraded/not claimed.
- Codex provider in Hermes pending/not proven.
- Telegram manual later/no token; No VPS.
- Gemma `gemma3:4b` is installed if local `ollama list` still proves it; local_demo fallback remains available.
- Gemma / Local Model Quality files live under `14_context/local_model_readiness/generated/`; local model eval runs live under `14_context/local_model_evaluation/runs/`.
- N+6.1A local routing must require source metadata, known repo bundle IDs, known files, and fallback when guard checks fail.
- N+6.2A should verify Hermes manual bridge workflow readiness without setup/tokens/live APIs.

[excerpt truncated; run the context-pack command for the full prompt.]
