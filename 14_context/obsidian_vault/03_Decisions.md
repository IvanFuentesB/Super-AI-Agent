# Ghoti Decisions (Compact)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** Codex planning docs in `14_context/`, `14_context/obsidian_vault/06_Safety_Gates.md`

---

## Purpose

Durable decision log with rationale and source links.
Covers architectural, safety, model-routing, and money-workflow boundaries.

## Source of Truth

- Codex planning docs in `14_context/codex_n3_*.md`
- `14_context/obsidian_vault/06_Safety_Gates.md`

## Update Rules

- Add entries when a decision changes future behavior.
- Include rationale and source link for every entry.
- Do not remove old decisions without operator approval.
- Mark reviewed entries with reviewer and date.

---

## Key Decisions (through N+3.34)

### Architecture

| Decision | Rationale | Source |
|----------|-----------|--------|
| Python stdlib-only helper scripts | No installs, no external deps, reproducible | CLAUDE.md |
| All money workflow files are artifact/template only | No live posting, selling, or outreach | `14_context/codex_n3_34_memory_safety_gate_review.md` |
| Compact memory is a pointer layer, not source of truth | Prevents context loss if compact files are stale | `14_context/codex_n3_34_compact_memory_contract.md` |
| Obsidian vault is navigation/summary, not source of truth | Durable records in milestone docs, not vault | `14_context/codex_n3_34_obsidian_vault_structure_spec.md` |
| No task deletion | History preserved via filter/archive, not delete | CLAUDE.md |

### Safety

| Decision | Rationale | Source |
|----------|-----------|--------|
| No live actions without explicit approval phrase | Approval gates prevent accidental execution | CLAUDE.md + ActionIntent contract |
| Forbidden: JobSpy, email/social automation, giveaways, fake accounts | ToS risk, legal risk, data risk | `14_context/codex_n3_34_memory_safety_gate_review.md` |
| N+3.18 dirty files (local_brain_router.py etc.) unstaged by default | Prevents dirty commit poisoning | Codex N+3.33 audit |
| No secrets in vault or compact memory | Memory files are repo-tracked, not secret stores | `14_context/codex_n3_34_memory_safety_gate_review.md` |

### Model Routing

| Decision | Rationale | Source |
|----------|-----------|--------|
| Gemma/Ollama = default local brain | API cost saving, local-first | `14_context/codex_n3_34_gemma_compression_workflow_spec.md` |
| Claude Code = hard implementation + commits | Correctness required | `14_context/agent_registry/agent_routing_policy_n3_14.md` |
| Codex = audit + spec + source verification | Accuracy for planning docs | CLAUDE.md prompt |
| ChatGPT = strategy + prompts + architecture | Breadth + reasoning | CLAUDE.md prompt |

### Memory

| Decision | Rationale | Source |
|----------|-----------|--------|
| Obsidian vault = 10-file human-readable navigation layer | Reduces prompt token load without losing durable context | `14_context/codex_n3_34_obsidian_vault_structure_spec.md` |
| Compact memory = 6-file compressed pointer set | Smaller prompt packs for Claude/Codex/ChatGPT/Gemma | `14_context/codex_n3_34_compact_memory_contract.md` |
| Gemma drafts compact memory, human/Claude promotes | Prevents hallucinated facts becoming canonical | `14_context/codex_n3_34_memory_safety_gate_review.md` |

---

## Review Status

**status:** draft
**review_required:** yes — before canonical use, verify entries against source docs
**unknown:** decisions.md may not exist yet; source is Codex planning docs

## Related Files

- `14_context/obsidian_vault/06_Safety_Gates.md`
- `14_context/obsidian_vault/07_Agent_Routing.md`
- `14_context/codex_n3_34_memory_safety_gate_review.md`
