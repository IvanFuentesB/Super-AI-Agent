# Ghoti Safety Gates (Compact)

**Updated:** 2026-04-27 — Milestone N+3.7
**Source:** `14_context/computer_use_strategy_note.md`, `01_projects/runtime_mvp/src/super_ai_agent/action_intent.py`, `01_projects/runtime_mvp/runtime_data/wait_resume_items.json`

---

## Active Wait/Resume Gates (pending)

| Gate | Risk | Resume Command |
|------|------|---------------|
| Push pending commits | medium | `git push origin feat/ghoti-visible-operator-stack` |
| Gemma model pull | medium | `ollama pull gemma3:4b` (operator approval) |
| AutoBrowser evaluation | high | manual review |
| External adapter execution | high | dashboard approval inbox |
| TryCUA / CUA Driver evaluation | high | sandbox VM + allowlist required |
| OpenFang repo identification + Rust install | medium | manual search + operator approval |
| Screenpipe capture start | medium | operator approval required; status route exists (N+3.7) |
| Obsidian vault token-saving workflow | low | use vault notes in prompts — active |
| Tool intake evaluation | medium | per-candidate review |
| Docker Desktop install approval (N+3.6/N+3.7) | high | type: APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX |
| CUA Docker/Ubuntu smoke after Docker install | high | only after Docker verified + sandbox profile approved |
| Screenpipe dashboard route + Obsidian sync | low | done in N+3.7 (PATH B) |

## Absolute Rules (CLAUDE.md + prompt)

- No writes outside repo root
- No CUA/Screenpipe wired without explicit approval
- No screen capture without operator start
- No credentials / 2FA / banking capture ever
- No autonomous external outreach / posting / purchases
- No bypassing provider usage limits
- No live account actions without approval
- Push only after validation passes
- Docker Desktop install only on explicit APPROVE phrase

## ActionIntent Gate

Every external or risky action must:
1. Create an ActionIntent (approval inbox entry)
2. Pass `approval_required=True` if risk is medium or high
3. Be consumed only once (no replay)
4. Write an audit JSONL entry at `05_logs/action_audit.jsonl`

---

> Full gate list: `01_projects/runtime_mvp/runtime_data/wait_resume_items.json`  
> ActionIntent contract: `01_projects/runtime_mvp/src/super_ai_agent/action_intent.py`
