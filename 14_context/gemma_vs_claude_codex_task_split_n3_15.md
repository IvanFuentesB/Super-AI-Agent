# Gemma vs Claude Code vs Codex — Task Split — N+3.15

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.15
Status: reference / routing_guide / no_autonomous_execution

---

## Decision Matrix

| Task | Gemma (local) | Codex (copy-paste) | Claude Code (paid) | ChatGPT (human) |
|---|---|---|---|---|
| Compress context / summarize .md file | YES — primary | no | no | no |
| Draft validation checklist | YES | no | no | no |
| Classify task risk level | YES | no | no | no |
| Suggest worker card fields | YES | no | no | no |
| Independent audit / doc analysis | no | YES — primary | secondary | no |
| Standalone analysis doc (no runtime) | no | YES | no | no |
| Hard multi-file implementation | NO | NO | YES — required | no |
| Runtime wiring / module extension | NO | NO | YES — required | no |
| Commit + push + validation | NO | NO | YES — required | no |
| Architecture / planning decisions | no | no | no | YES — required |
| New milestone prompt design | no | no | no | YES — required |
| Strategy / roadmap decisions | no | no | no | YES — required |

---

## Gemma Boundaries (Strict)

### Allowed
- Read a local repo file (path validated, inside repo root, allowed extension)
- Summarize or compress its content
- List blockers, next actions, decisions worth preserving
- Cite file paths mentioned in text
- Draft checklists for task validation
- Classify a task description as easy / medium / hard / risky

### Not Allowed
- Read files outside repo root
- Access secrets, `.env`, credential stores, CV files
- Edit any repo file (output is artifact-only)
- Execute shell commands or generated code
- Make decisions about external accounts, payments, legal matters
- Call any external API or cloud service
- Auto-commit or auto-push anything

---

## When NOT to Use Gemma

- When the task requires multi-step reasoning across 5+ files simultaneously
- When the output needs to be trusted for a safety-critical decision
- When a second opinion is needed (use Codex instead)
- When the task involves any external action or live account

---

## Claude Code Boundaries

Claude Code handles tasks that require:
- Writing or modifying multiple files in one atomic operation
- Running shell commands with side effects (install, build, test)
- Validation across AST parse, JSON lint, node --check
- Staging, committing, and pushing to git remote
- Any decision that modifies repo state permanently

Claude Code must not be used for:
- Routine text summarization (Gemma can do this)
- Read-only analysis of a single doc (Codex can do this)
- Strategic planning (ChatGPT does this)

---

## Codex Boundaries

Codex handles:
- Independent audits — no access to runtime files, fresh eyes only
- Standalone analysis docs in `14_context/` (e.g., `codex_*.md`)
- Limited, clearly-scoped implementation with human review step

Delivery: copy-paste prompt only. No file system access. No git operations.

---

## Routing Example: Context Compression Before a New Milestone

1. Gemma compresses `14_context/current_state.md` → saves output to `05_logs/local_brain_runs/<id>/response.txt`
2. Human reads Gemma output, copies key bullets to Obsidian vault note
3. New Claude Code session prompt references vault note path instead of full file
4. Result: Claude Code session starts with 3,000–6,000 fewer input tokens

---

## Routing Example: New Feature Request

1. ChatGPT (human-operated): produce a milestone prompt with goal, phases, and safety rules
2. Claude Code: execute the milestone — implementation, validation, commit, push
3. Gemma: after delivery, compress the new state doc for the next session handoff

---

## Paperclip / OpenClaw / n8n

All remain **planning_only**. Not installed. Not runtime-wired.
Routing decisions involving these candidates are deferred until explicit operator approval.
