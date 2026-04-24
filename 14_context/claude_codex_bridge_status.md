# Claude ↔ Codex Bridge Status

Milestone: N+1.5
Date: 2026-04-24

---

## Verified Status

**`manual_handoff_only`**

No runtime plugin, no automated bridge, no codex-plugin package found locally.

---

## Evidence Found

Search ran against:
- `14_context/` — all `.md` files
- `.claude/` — all files
- `01_projects/dashboard_mvp/` — server.js, app.js
- `01_projects/runtime_mvp/` — README, runtime_data

Matches on `codex`, `handoff`, `claude.*codex`, `codex.*claude`:
- Multiple hits on `handoff` — all refer to Ghoti's internal `handoff_snapshot.md` and `operator_handoff_summary.md` workflows, not a Claude/Codex bridge
- No match on `codex-plugin`, `openai/codex-plugin`, or `codex:setup`
- No npm package `@openai/codex`, `codex-plugin`, or similar found in any `package.json`

`where codex` result: **not found** (INFORMACI... error on Windows = no file matching codex)

`where claude` result: `C:\Users\ai_sandbox\AppData\Roaming\npm\claude` — Claude Code CLI is installed

---

## What Exists Now

| Component | Exists |
|-----------|--------|
| Claude Code CLI (`claude`) | YES — at npm global |
| Codex CLI (`codex`) | NO |
| Runtime bridge plugin | NO |
| codex-plugin npm package | NO |
| Claude ↔ Codex shared config | NO |
| Automated handoff script | NO |

---

## What Is Not Installed

- OpenAI Codex CLI
- Any npm package bridging Claude Code and Codex
- Any config file wiring the two systems together
- Any automated prompt-routing between Claude and Codex

---

## Safe Next Implementation Path

If a Claude ↔ Codex bridge is desired in the future:

1. **Verify Codex CLI exists:** `npx @openai/codex --version` or official install from OpenAI
2. **Read the official docs** for both Claude Code and Codex CLI before assuming compatibility
3. **Manual handoff first:** Copy-paste Ghoti prompt files between sessions — already working
4. **Do not claim integration exists** until verified with actual tool invocations
5. **Human approval required** before any automated cross-system dispatch

---

## What Not to Claim

- Do not say "Claude and Codex are bridged" — they are not
- Do not say "the bridge is installed" — it is not
- Do not say "handoff is automated" — it is manual copy-paste only
- Do not present Ghoti's internal `handoff_snapshot.md` as a Claude/Codex runtime bridge

---

## Manual Fallback Workflow (What Currently Works)

1. Operator opens `14_context/ghoti_current_prompt.md` — this is the single source of truth for the current milestone
2. Operator pastes into Claude Code (or Codex) session
3. Claude Code executes the prompt end-to-end
4. Results committed and pushed to `feat/ghoti-visible-operator-stack`
5. Next milestone prompt created as a new file (do not create extra prompt files unless explicitly asked)

This workflow is:
- Fully manual
- Zero automation
- Fully traceable
- Safe from cross-system prompt injection

There is no daemon, no scheduler, no webhook. The operator decides when to hand off.
