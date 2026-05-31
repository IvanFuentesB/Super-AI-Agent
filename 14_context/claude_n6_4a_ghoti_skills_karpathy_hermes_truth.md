# N+6.4A — Ghoti Skills System + Karpathy Guidelines + Current Hermes Truth

Milestone: N+6.4A
Date: 2026-05-31
Author lane: implementation specialist

## Branch and worktree

- Branch: `feat/ghoti-agent-claude-n6-4a-ghoti-skills-karpathy-hermes-truth-clean`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_4a_clean_replacement_claude`
- Base main: `8613508674deb9abb44dc1b9e5a54dfee3261ee6` (origin/main at branch time)
- Commit message: `feat(ghoti): register Hermes truth and agent skill workflow`
  (clean replacement; commit hash recorded in final response after commit).

## What this milestone does

Registers the current, verified truth about Ghoti's multi-agent system and its
local Hermes setup, documents the agent skill/handoff workflow, adopts the
Karpathy guidelines as guidance-only, and records a backlog-only product
direction for dashboard speed and future local-first analytics.

This is a documentation + tests milestone. No runtime is wired, no automation is
enabled, no live actions are taken, and no feature code is added.

## Files changed

### Imported from backup (vault subtree, staged)

Imported `14_context/agent_handoff_vault` from `backup/n6-4a-handoff-vault-local`
(the vault did not exist on origin/main). Files:

- `14_context/agent_handoff_vault/.obsidian/app.json`
- `14_context/agent_handoff_vault/00_Inbox/START_HERE.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/CLAUDE_PROMPT.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/CODEX_AUDIT_PROMPT.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/CURRENT_TASK.md`
- `14_context/agent_handoff_vault/04_Logs/CLAUDE_LAST_RUN.md`
- `14_context/agent_handoff_vault/04_Logs/CODEX_LAST_AUDIT.md`
- `14_context/agent_handoff_vault/AGENT_RULES.md`

### Created — truth and docs

- `14_context/ghoti_current_truth.md` — master truth registry (agent roles,
  Hermes setup, Obsidian, explicit "what is NOT enabled").
- `docs/HERMES_LOCAL_SETUP_CURRENT_TRUTH.md` — factual Hermes record.
- `docs/GHOTI_SKILLS_AND_AGENT_WORKFLOW.md` — agents, handoff flow, skill meaning.
- `docs/CLAUDE_CODE_SKILLS_POLICY.md` — how Claude Code uses skills safely.
- `docs/CODEX_AUDIT_WORKFLOW.md` — Codex audit/verdict process.

### Created — skills registry

- `14_context/skills/ghoti_skill_registry.md`
- `14_context/skills/karpathy_guidelines_intake.md`
- `14_context/skills/claude_code_skill_install_log.md`
- `14_context/skills/codex_working_rules.md`

### Created — backlog note

- `14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md`

### Created — tests

- `01_projects/runtime_mvp/tests/test_n6_4a_ghoti_skills_karpathy_hermes_truth.py`

## Current truth registered (summary)

- ChatGPT — main strategy / architecture / prompt brain.
- Hermes — local coordinator / switchboard / memory writer (WSL Ubuntu,
  `ai_sandbox`, v0.14.0, model llama3.1:8b, custom local endpoint
  `http://127.0.0.1:11434/v1`).
- Obsidian — durable shared memory / handoff board (installed; vault under
  `14_context/agent_handoff_vault`).
- Claude Code — implementation specialist.
- Codex — audit / review / verification specialist.
- Gemma (gemma3:4b) — cheap summaries / compression / classification.
- Llama (llama3.1:8b) — Hermes coordinator brain.
- Git — truth / history / rollback. Human — final approval.
- Local Ollama models: llama3.1:8b and gemma3:4b. qwen was removed.

## Validation results (real output)

| Check | Command | Result |
|-------|---------|--------|
| Whitespace | `git diff --check` | clean (exit 0) |
| n6 tests | `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v` | Ran 30 tests — OK (n6_0a 5, n6_1a 9, n6_2a 4, n6_4a 12) |
| Launcher status | `ghoti_product_launcher.py --status --json` | ok=True |
| Context pack | `ghoti_product_launcher.py --context-pack --json` | ok=True |
| Repo map | `ghoti_product_launcher.py --repo-map --json` | ok=True |
| Security audit | `public_repo_security_audit.py --run --json` | ok=True; 150 checks, 143 passed, 0 failed, 7 warnings, safe_to_make_public=True |

Note: `--context-pack` and `--repo-map` regenerate tracked artifacts under
`14_context/compact_memory/generated/` and `14_context/repo_knowledge/generated/`
as a side effect. Those regenerations are out of scope for this milestone and
were reverted (`git checkout --`) so the committed diff stays surgical. Only the
files listed above are committed.

## Safety summary

- No secrets, API keys, tokens, `.env`, cookies, or browser sessions were read or
  written.
- No Telegram setup. No browser/computer-use enablement. No desktop control, no
  click/type/hotkey.
- No external repo installs, no external repo code execution, no live APIs.
- No autonomous agent launch; handoffs remain manual.
- No approval gate weakened. No main push. No force push. The dirty primary
  worktree was treated read-only.
- Stage was explicit (no `git add -A`).

### Direct answers

- Does the truth doc register ChatGPT/Hermes/Obsidian/Claude/Codex/Gemma/Llama
  roles? — Yes.
- Is Hermes' local setup (WSL, v0.14.0, llama3.1:8b, loopback endpoint, gemma3:4b,
  qwen removed) recorded? — Yes.
- Is Telegram claimed as enabled? — No; recorded as NOT configured.
- Is browser/computer-use claimed as enabled? — No; recorded as NOT approved/enabled.
- Are Claude Code/Codex claimed as auto-wired into Hermes? — No; manual handoffs.
- Is Ghoti claimed as fully autonomous? — No; supervised.
- Are production analytics / external telemetry claimed as live? — No; backlog only.
- Did Ghoti run a browser, install anything, or execute external repo code? — No.
- Are approval gates intact? — Yes.

## Dashboard performance / local analytics note

- Path: `14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md`
- Status: backlog only — direction documented, not built. Future analytics must be
  local-first, no external tracking by default, no user secrets, no invasive
  telemetry, nothing leaving the machine without explicit human approval.

## What Codex should audit next

1. Scope: confirm every committed file is one of the listed milestone files and
   that no generated artifact or unrelated file slipped into the commit.
2. Truthfulness: re-read the truth/docs/skills files and confirm no overclaim
   (Telegram, browser/computer-use, autonomy, auto-wired agents, live analytics).
3. Tests: re-run the `test_n6_*.py` discover and confirm 30 pass, including the
   pre-existing n6_0a/n6_1a/n6_2a modules.
4. Safety: confirm no secrets, no installs, no live actions, approval gates intact,
   and that the security audit reports 0 failed checks.
5. Reversibility: confirm the change is docs/tests only and trivially revertable.

## Final verdict

IMPLEMENTED_AND_PUSHED (clean replacement branch; main not pushed).
