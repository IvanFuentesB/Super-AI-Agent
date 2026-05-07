# Agent Routing Policy — N+3.14

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.14
Status: routing_policy / preview_only / no_autonomous_execution

---

## Routing Hierarchy

### 1. Local Gemma / Ollama (LOCAL-GEMMA-EASY-001)

Handles: easy, local, low-risk tasks.

**Route here when:**
- Summarizing a local markdown file
- Classifying a task as easy/medium/hard/risky
- Drafting a checklist for validation
- Compressing context for handoff
- Suggesting worker card fields

**Never route here when:**
- Secrets, live account data, or credentials are involved
- The task requires editing the repo (Gemma output must not be auto-committed)
- Any external action is involved (email, browser, login, payment, legal)
- The task requires reasoning across multiple files with high complexity

**Current status:** preview_only — enabled=false; preview runs via `--preview` flag only.

---

### 2. Codex (CODEX-AUDIT-001)

Handles: independent audits, documentation, limited focused implementation.

**Route here when:**
- An independent second opinion on docs or code is needed
- A standalone analysis doc is needed without touching complex runtime code
- Limited, clearly scoped implementation is needed with human review

**Delivery method:** copy-paste prompt only (no file access).

---

### 3. Claude Code (CLAUDECODE-IMPLEMENT-001)

Handles: hard multi-file implementation, runtime wiring, milestone execution.

**Route here when:**
- Complex changes spanning multiple files are needed
- Runtime modules need to be created or extended
- Validation, staging, committing, and push coordination are required
- A complete milestone must be delivered end-to-end

**Guardrails:** Allowed file lists per milestone; push requires user approval; external actions blocked.

---

### 4. ChatGPT (external, human-operated)

Handles: planning, architecture decisions, prompt generation, strategic choices.

**Route here when:**
- High-level architecture or design decisions are needed
- A fresh external perspective on the roadmap is valuable
- Prompt engineering for a new milestone is needed

**Delivery method:** human operator pastes context and returns a decision or plan.

---

### 5. Paperclip (PAPERCLIP-CONTROL-PLANE-CANDIDATE) — PLANNING ONLY

May become: the orchestration control plane coordinating workers.

**Current status:** not installed. Audit only. No install/run until explicit operator approval.

---

### 6. OpenClaw (OPENCLAW-WORKER-CANDIDATE) — PLANNING ONLY

May become: a worker and channel agent for browser-assisted and managed-operator tasks.

**Current status:** read-only reference clone at 21_repos/third_party/. Not runtime-wired. No install/run until explicit operator approval.

---

### 7. n8n (N8N-WORKFLOW-CANDIDATE) — PLANNING ONLY

May become: deterministic workflow rails for structured multi-step tasks.

**Current status:** not installed. Planning only. No install/run until explicit operator approval.

---

## Safety Rules

- No live actions (browser click, email, posting, login, payment, legal) without operator approval.
- Gemma output must never be auto-committed or auto-executed.
- All external adapter installs (Paperclip, OpenClaw, n8n) require explicit operator approval before proceeding.
- Push to remote always requires operator approval.
- Approval gates are preserved and must not be weakened.

---

## API Credit Saving Strategy

1. Route easy local tasks (checklists, summaries, context compression) to Gemma/Ollama first.
2. Route audits and limited docs to Codex.
3. Reserve Claude Code for hard implementation and milestone delivery.
4. Reserve ChatGPT for strategy and architecture.
5. This is an API cost reduction strategy — not a cap bypass or quota evasion path.
