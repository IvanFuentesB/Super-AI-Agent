# Ghoti Safety Gates (N+3.34 Canonical)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** CLAUDE.md, `14_context/codex_n3_34_memory_safety_gate_review.md`, `14_context/obsidian_vault/05_Safety_Gates.md`

---

## Purpose

Canonical compact safety boundaries for all Ghoti work.
Predecessor: `05_Safety_Gates.md` (N+3.7) — intact and valid.

## Source of Truth

- `CLAUDE.md` (project root — always authoritative)
- `14_context/codex_n3_34_memory_safety_gate_review.md`
- `14_context/obsidian_vault/05_Safety_Gates.md` (N+3.7 predecessor)
- `01_projects/runtime_mvp/src/super_ai_agent/action_intent.py`

## Update Rules

- Never weaken approval gates.
- Update only when safety policy explicitly changes.
- Human review required always.
- Do not add new action surfaces without operator approval.

---

## Absolute No-Go Rules

1. No writes outside repo root (`C:\Users\ai_sandbox\Documents\AI_Managed_Only`)
2. No reads of `.env`, secrets, credentials, OS env vars without same-turn approval
3. No live account actions (post, pay, send, sell, scrape) without explicit approval phrase
4. No model output execution without human review
5. No fake proof, testimonials, or engagement
6. No secrets in vault or compact memory files
7. No bypassing provider usage limits
8. No destructive git operations without operator confirmation

## Forbidden Workflows (explicitly blocked)

- JobSpy / email harvesting / social automation
- Giveaway / raffle / fake account farming
- Mass posting or scraping
- Connector/account wiring without approval
- External MCP integration in runtime without approval
- Free-Claude/unlocked-Claude/Mythos/leaked repos used in runtime
- Automate giveaways, fake accounts, spam, account farming

## Approval Gates

- Medium/High risk actions → ActionIntent → approval inbox → approved before execute
- Any git push → validation passes → user confirmation unless pre-authorized
- Any install → explicit `APPROVE <tool>` phrase required
- Money-facing distribution → operator review + approval required per action

## Local Safe Tasks (no extra approval needed)

- Read files in repo root
- Write local artifact files in `05_logs/`, `14_context/`, `output/`
- Create/update local markdown memory files (vault, compact memory)
- Run local stdlib-only Python scripts (dry-run mode)
- Run `git status`, `git log`, `git diff`, `git fetch`
- Run `python -m py_compile` or AST parse

## ActionIntent Gate

1. Create ActionIntent (approval inbox entry)
2. `approval_required=True` for medium/high risk
3. Consume only once (no replay)
4. Write JSONL audit entry at `05_logs/action_audit.jsonl`

---

## Review Status

**status:** reviewed (Claude N+3.34)
**human_review_required:** always before canonical promotion

## Related Files

- `14_context/obsidian_vault/05_Safety_Gates.md` — N+3.7 predecessor (intact)
- `14_context/codex_n3_34_memory_safety_gate_review.md`
- `14_context/compact_memory/safety_rules.md`
- `01_projects/runtime_mvp/runtime_data/wait_resume_items.json`
