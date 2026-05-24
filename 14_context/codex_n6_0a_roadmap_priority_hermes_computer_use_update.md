# Codex N+6.0A Roadmap Priority Update - Hermes And Safe Computer-Use

Date: 2026-05-24

## Verdict

ROADMAP UPDATED / N+6.1A GUARD FIRST, THEN HERMES AND SAFE COMPUTER-USE.

This update does not start N+6.1A, N+6.2A, or N+6.3A. It updates the N+6.0A
feature branch docs, context pack generator, repo knowledge generator, and
generated roadmap files so the next sequence matches Ivan's priority: reduce
paid credit usage and prepare long, boring supervised task automation without
unsafe autonomy.

## Current Branch State

- Main baseline after N+5.9B: `20e1dce1e89f15a337054864560b95b82233877c`
- N+6.0A feature branch: `feat/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- Previous N+6.0A feature commit before this update: `8b5a6302cbe23601343f01d6ab10efa6d777afb8`
- Previous N+6.0A audit branch: `audit/ghoti-agent-codex-n6-0a-human-approved-gemma-install-first-local-evaluation`
- Previous N+6.0A audit commit: `7773aa5a1e11aa90c98992309b7742094f74888c`

## Updated Roadmap Order

1. N+6.1A - Constrained Gemma Worker Routing + Repo-Bundle Hallucination Guard.
2. N+6.2A - Hermes Agent Workflow / Manual Bridge Verification for faster supervised task execution.
3. N+6.3A - Safe Computer-Use Preparation with Gemma + Hermes + UI-TARS observation + Browser Harness/Vercel agent-browser roadmap.

N+6.2A and N+6.3A must not start until N+6.1A passes a clean audit gate.

## N+6.1A Gate

Allowed local tasks only:

- summarize latest report
- status paragraph
- Codex next prompt
- safety classification
- context bundle summary
- next milestone outline
- report-to-bullets

Required guard behavior:

- use known repo-map bundle IDs only
- reject invented bundle/file claims
- require source metadata
- fall back to `local_demo` when the guard fails
- never execute commands from model output
- never edit files from model output
- never use live APIs
- keep every action offline/local

## Hermes Priority

N+6.2A should verify Hermes as a manual bridge and faster supervised task
surface. It must remain safe-probe-only:

- Hermes WSL path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0`
- Hermes readiness: 58%
- Codex provider: pending/not proven
- Telegram: manual/no token
- Browser/Playwright: degraded/not claimed
- No VPS
- No provider setup, tokens, live APIs, Telegram setup, or browser automation.

## Safe Computer-Use Priority

N+6.3A should prepare, not enable, computer-use:

- Gemma + Hermes + UI-TARS observation + Browser Harness/Vercel agent-browser roadmap
- observation first
- human approval for every future click/type/live-account action
- no bot/captcha/cloak bypass
- no fake engagement or spam
- no autonomous account action
- no uncontrolled browser automation

## Files Updated

- `README.md`
- `docs/DAILY_OPERATOR_GUIDE.md`
- `docs/CODEX_ONLY_WORKFLOW.md`
- `docs/EASY_WORKER_LANE_GUIDE.md`
- `docs/HUMAN_APPROVED_GEMMA_INSTALL_LOG.md`
- `docs/LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md`
- `docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md`
- `docs/COMPUTER_USE_ROADMAP.md`
- `docs/HERMES_AGENT_WORKFLOW_GUIDE.md`
- `03_scripts/ghoti_context_pack_builder.py`
- `03_scripts/ghoti_repo_knowledge_map.py`
- `03_scripts/gemma_model_readiness.py`
- generated context pack files under `14_context/compact_memory/generated/`
- generated repo knowledge files under `14_context/repo_knowledge/generated/`
- generated Gemma readiness status under `14_context/local_model_readiness/generated/`

## Current Capability Truth

- `gemma3:4b` is installed locally in Ollama.
- First real local model eval score: 86%, 6 of 7 tasks passed.
- Local demo comparison score: 55%.
- Production routing remains disabled.
- N+6.1A was not started because the repo-bundle hallucination guard is the next required milestone.
- Hermes remains manual bridge only.
- UI-TARS remains observation-only.
- Adapter runner remains approval-gated/local-only.
- External sandbox remains static inspection only.

## Cleanup

No dashboard process was started for this roadmap update. No broad process kills
were used. No model pulls were run. No live APIs or provider setup were used.
