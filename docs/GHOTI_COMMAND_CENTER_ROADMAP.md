# Ghoti Command-Center Roadmap (N+6.6 → N+6.9)

Status: PLAN / SPEC ONLY. Nothing in this document is implemented, wired, or
enabled. It defines the target architecture and the order in which later,
separately-approved milestones may build it. No live action is taken by writing
this roadmap.

Author lane: systems architect (planning lane)
Date: 2026-05-31
Base main at plan time: origin/main contains N+6.4A and N+6.4B
(`14_context/ghoti_current_truth.md`, `14_context/agent_handoff_vault/`,
`14_context/codex_n6_4b_main_merge_gate.md`).

This roadmap is the index. The detailed contracts live in the companion specs:

- `docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md` — Hermes router wrapper system.
- `docs/GHOTI_N6_7_TOOL_REPO_INTAKE_SPEC.md` — tool / repo intake pipeline.
- `docs/GHOTI_N6_8_COMMAND_CENTER_ANALYTICS_SPEC.md` — fast dashboard + local analytics.
- `docs/GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md` — routing + Obsidian memory contract.
- `14_context/skills/hermes_router_wrapper_policy.md` — condensed wrapper policy (guidance-only).
- `14_context/agent_handoff_vault/05_Backlog/n6_6_7_8_9_command_center_backlog.md` — phased backlog.

---

## 1. Big picture — who does what (target end state)

The command center is a supervised relay, not an autonomous swarm. Each agent has
one job and stays in its lane. The chain reads left to right; the human owns the
last gate.

> ChatGPT thinks → Hermes coordinates → Obsidian remembers → Claude implements →
> Codex audits → Gemma summarizes → Human approves.

| Agent | Role in the command center | Explicitly NOT its job |
|-------|----------------------------|------------------------|
| ChatGPT | Primary reasoning, architecture, prompt design, and safety framing. The main brain that writes the plans and the agent prompts. | Not the local executor; does not touch the repo directly. |
| Hermes | Local coordinator / switchboard. Runs approved wrappers, writes handoffs, moves notes between agents. Hermes is the local coordinator, not the main brain. | Never runs arbitrary commands; does not design strategy; does not audit or merge. |
| Obsidian | Durable shared memory and handoff board. The single source of "what is the current task / last run / last audit". | Not a secret store; not a raw-log dump. |
| Claude Code | Implementation specialist. Implements one assigned task on a branch in a worktree. | Does not self-assign; does not audit its own work; does not merge to main. |
| Codex | Audit / review / merge-gate. Verifies a branch against main and returns a verdict. | Does not implement features; does not merge without a human. |
| Gemma (gemma3:4b) | Cheap local summarizer / compressor / classifier. Shrinks logs and notes for memory. | Not a reasoning brain; not an implementer or auditor. |
| Llama (llama3.1:8b) | Hermes' local coordinator brain (drafting/triage only). | Not the architect; not an implementer. |
| Git | Truth, history, rollback. Every change is a commit on a branch. | Not bypassed; no history rewrite without explicit human approval. |
| Human | Final authority. Approves risky actions and every merge to main. | — |

Routing detail (which task goes to which agent), the task-classification schema,
risk levels, status lifecycle, and the Obsidian memory contract are specified in
`docs/GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md`.

---

## 2. Phase sequence (N+6.6 → N+6.9)

Each phase is its own milestone with its own branch, audit, and human merge. A
later phase does not start until the earlier one is merged. No phase below is
built by this roadmap.

| Phase | Milestone | What it adds | Risk posture |
|-------|-----------|--------------|--------------|
| N+6.6A | Hermes Router Wrapper System | Read-only / note-writing wrappers (`.ps1`), dry-run first, plus tests. No agent launch. | Low. Repo- and vault-bounded; no live action. |
| N+6.6B | Dry-run launch wrappers | `launch_claude_task.ps1` / `launch_codex_audit.ps1` in **print-only dry-run** (emit the command they *would* run; never execute it). | Medium. Still no real launch. |
| N+6.7A | First tool/repo intake | Run the 10-step intake on two safe, high-value candidates (MarkItDown, Understand-Anything) as documentation + static inspection only. | Low–medium. Static inspection; no runtime wiring. |
| N+6.8A | Command-center dashboard scaffold | Fast local dashboard view + local-first analytics scaffold (JSONL), local-only by default. | Low. Local-only; no external telemetry. |
| N+6.9A | Router policy enforcement | Wire the orchestration policy into the wrappers (classification, risk gate, status lifecycle) — still supervised, still dry-run for launches. | Medium. Policy enforcement only; no autonomy. |

The recommended **next** implementation milestone is **N+6.6A** (wrappers + tests,
dry-run only). Its ready-to-run Claude prompt and Codex audit prompt are in:

- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_CLAUDE_TASK.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_CODEX_AUDIT_PROMPT.md`

---

## 3. MCP plan (do NOT install yet)

No MCP server is installed, configured, or enabled. "no MCP installed" is the
current truth and the test asserts it. MCP is a future option introduced one
server at a time, each behind its own audited milestone:

1. Filesystem MCP — **read-only**, scoped to `14_context/agent_handoff_vault/`
   and `docs/` only. (First candidate; read-only.)
2. GitHub MCP — **read-only** (status, PR/issue read). No write, no merge.
3. A small custom "repo-status" MCP — read-only repo facts (branch, ahead/behind,
   last audit verdict).
4. Write-capable MCP — only after a dedicated audit and human approval.

Forbidden now (and until separately approved): browser MCP, any account/action
MCP, social-posting MCP, and any uncontrolled filesystem-write MCP.

---

## 4. Computer-use clarification (important)

The N+6.5A observation harness (if/when it lands) is an **observation-only**
adapter. It is NOT real computer-use. To be unambiguous:

- Real desktop/browser computer-use is a separate, later track. Its safe ramp is:
  local fixture tests → screenshot observation (no click/type) → approval gate →
  limited click/type **dry-run** → live only with a human present.
- GUI computer-use is for *browser/desktop* tasks (filling a form, clicking a UI).
  It is **not** the way to launch Claude or Codex. Launching agents is done with
  the Hermes **wrappers** (text in, text out) — wrappers are safer, testable, and
  leave an audit log. "no browser/computer-use" is the current command-center
  default.

---

## 5. Standing safety guarantees for the whole roadmap

These hold across every phase. Any phase that needs to change one of these must
do so in its own milestone, with its own audit and explicit human approval.

- Hermes runs **approved wrappers only** and will **never run arbitrary commands**.
- Repo-root bounded: no writes outside `C:\Users\ai_sandbox\Documents\AI_Managed_Only`.
- **no secrets** are read or written by wrappers (no `.env`, tokens, cookies, auth files).
- **no Telegram**, **no browser/computer-use**, no live account/API/posting/money actions.
- **no MCP installed**; no autonomous agent launch; agent launches are dry-run first.
- Tool/repo intake does **no blind installs** — static inspection before any code runs.
- Analytics is **local-first**, local-only by default, no external telemetry, no PII.
- One agent per task; no overlapping edits; Git is the rollback path; human merges.
