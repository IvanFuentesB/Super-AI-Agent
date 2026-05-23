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

Current main hash: `23ace6dedb7acdfd19b148988be35e121f140070`
Latest clean milestone: N+5.5B - Local Memory Context Pack landed on main
Current context pack milestone: N+5.6A - Local Model / Gemma Setup Truth + Easy Worker Lane
Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
Dashboard: `http://127.0.0.1:3210`

Status truth:
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0.
- Hermes browser/Playwright degraded/not claimed.
- Codex provider in Hermes pending/not proven.
- Telegram manual later/no token; No VPS.
- Gemma model missing unless a new local check proves otherwise; local_demo fallback active.
- Obsidian/local memory present.
- UI-TARS observation-only.
- Adapter runner approval-gated/local-only.
- External sandbox static inspection/planning-only.

Next safe milestone after this pack:
N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval

Ask Codex to create a feature branch, add focused tests first, implement only the
Graphify/repo knowledge map and context retrieval changes, validate, push feature,
then create a separate audit branch. Do not start live providers or tokens.
