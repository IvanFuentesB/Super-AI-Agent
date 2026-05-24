Continue Ghoti / Super-AI-Agent from the current local-first supervised baseline.

Use only repo-contained worktrees under `.claude/worktrees`. Keep the primary
worktree read-only except inspection. No force-push, no history rewrite, no
secrets, no live account/API/posting/money/trading/legal actions, no bot/captcha/
cloak bypass, no fake autonomy claims, no shell-true command execution, and no live providers/tokens.

Current main hash: `20e1dce1e89f15a337054864560b95b82233877c`
Latest clean milestone: N+5.9B - Gemma Readiness / Local Quality Plan landed on main
Current context pack milestone: N+6.0A - Human-Approved Gemma Install + First Real Local Model Evaluation
Previous repo knowledge milestone: N+5.7A - Graphify / Repo Knowledge Map + Better Context Retrieval
Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
Dashboard: `http://127.0.0.1:3210`

Status truth:
- Hermes WSL installed at `/home/ai_sandbox/.local/bin/hermes`, v0.14.0.
- Hermes Agent / Manual Bridge exposes safe status, skills index, manual checklist, and bridge packet.
- Hermes browser/Playwright degraded/not claimed.
- Codex provider in Hermes pending/not proven.
- Telegram manual later/no token; No VPS.
- Gemma model missing unless a new local check proves otherwise; local_demo fallback active.
- Gemma / Local Model Quality files live under `14_context/local_model_readiness/generated/`; local model eval runs live under `14_context/local_model_evaluation/runs/`.
- Obsidian/local memory present.
- UI-TARS observation-only.
- Adapter runner approval-gated/local-only.
- External sandbox static inspection/planning-only.
- Repo Knowledge / Graphify Lane available as local JSON/Markdown files.

Next safe milestone after this pack:
N+6.1A - Local Model Routing + Real Worker Task Integration

Ask Codex to create a feature branch, add focused tests first, implement only the
next local model routing changes, validate, push feature, then create a separate
audit branch. Do not run new `ollama pull` commands unless the human explicitly
approves them in that milestone.
