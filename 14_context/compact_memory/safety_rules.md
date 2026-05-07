---
memory_type: compact_pointer
status: reviewed
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - CLAUDE.md
  - 14_context/codex_n3_34_memory_safety_gate_review.md
  - 14_context/obsidian_vault/06_Safety_Gates.md
  - 01_projects/runtime_mvp/src/super_ai_agent/action_intent.py
generated_by: claude
reviewed_by: claude
review_required_before_canonical_use: true
---

# Compact: Safety Rules

> **WARNING:** Compressed pointer layer. CLAUDE.md always overrides this file.
> Human review required before canonical use.
> **Max target size:** 400–800 words

---

## Absolute No-Go Rules

1. No writes outside repo root (`C:\Users\ai_sandbox\Documents\AI_Managed_Only`)
2. No reads of `.env`, secrets, credentials, OS env vars without same-turn approval
3. No live account actions (post, pay, send, sell, scrape) without explicit approval phrase
4. No model output execution without human review
5. No fake proof, testimonials, or engagement
6. No secrets in vault or compact memory
7. No bypassing provider usage limits
8. No destructive git ops without operator confirmation

## Forbidden Workflows

- JobSpy / email harvesting / social automation
- Giveaway / raffle / fake account farming
- Mass posting or scraping
- Connector/account wiring without approval
- External MCP integration without approval
- Free-Claude/unlocked/Mythos/leaked repos in runtime
- Automate giveaways, fake accounts, spam, account farming

## Approval Gates

- Medium/High risk actions → ActionIntent → approval inbox → approved before execute
- Any git push → validation passes → user confirmation unless pre-authorized
- Any install → explicit `APPROVE <tool>` phrase required
- Money-facing distribution → operator review + approval per action

## Local Safe Tasks (no extra approval needed)

- Read files in repo root
- Write local artifact files in `05_logs/`, `14_context/`, `output/`
- Create/update local markdown memory files (vault, compact memory)
- Run local stdlib-only Python scripts (dry-run mode)
- Run `git status`, `git log`, `git diff`, `git fetch`
- Run `python -m py_compile` or AST parse

## ActionIntent Gate

1. Create ActionIntent (approval inbox entry)
2. `approval_required=True` if risk medium/high
3. Consume only once (no replay)
4. Write JSONL audit at `05_logs/action_audit.jsonl`

## Dirty-File Staging Warning

Never `git add -A`. Stage only intentional milestone files.
Always run `git diff --check` and `git status --short` before commit.

---

## Source Pointers

- Authoritative: CLAUDE.md
- Safety gate review: `14_context/codex_n3_34_memory_safety_gate_review.md`
- Vault note: `14_context/obsidian_vault/06_Safety_Gates.md`
- ActionIntent: `01_projects/runtime_mvp/src/super_ai_agent/action_intent.py`

## Next Update Instructions

Update only when safety policy explicitly changes.
Human review always required before canonical promotion.
