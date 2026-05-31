# N+6.9 — Multi-Agent Orchestration Policy + Obsidian Memory Contract (SPEC ONLY)

Status: PLAN / SPEC ONLY. No router, classifier, or automation is built or
enabled by this document. It defines the routing policy and the Obsidian memory
contract a future N+6.9A milestone enforces (still supervised, still dry-run for
launches). Writing this spec takes no live action.

Author lane: systems architect (planning lane)
Date: 2026-05-31

## 1. Routing decision table (which task goes where)

ChatGPT is the main brain (planning, architecture, prompt design, safety).
Hermes is the local coordinator that routes a classified task to the right
executor and records the handoff. Routing never bypasses a human gate for risky
work.

| Task type | Routed to | Mode | Notes |
|-----------|-----------|------|-------|
| Summarize / compress text or logs | Gemma (gemma3:4b) | local | cheap local summarizer, loopback only |
| Coordinator chat / triage / draft handoff | Llama (llama3.1:8b) via Hermes | local | Hermes' local brain; drafts, does not implement |
| Implement a defined task | Claude Code | supervised | one task, one branch, one worktree |
| Audit a branch / merge-gate | Codex | supervised | verdict only; human merges |
| Web research with citations | Perplexity / ChatGPT / manual | manual | bring back cited sources; no silent scraping |
| Large PDF / doc → Markdown | MarkItDown (later) | gated intake | only after N+6.7 intake; sandbox convert |
| Repo graph / code map | Understand-Anything / Graphify (later) | gated intake | read-only output; after intake |
| Architecture / strategy / prompt design | ChatGPT | planning | the main brain; writes the plans |
| Final approval / merge | Human | gate | last authority, always |

## 2. Input task classification schema

Every incoming task is classified before routing. Proposed shape of a task
record (written into the vault, not auto-executed):

```json
{
  "task_id": "N6.6A",
  "title": "Hermes router wrapper system",
  "type": "implement | audit | summarize | research | intake | plan",
  "risk": "low | medium | high | blocked",
  "assigned_to": "claude | codex | gemma | llama | human | unassigned",
  "status": "idle",
  "requires_human_gate": true,
  "allowed_files": ["..."],
  "forbidden": ["secrets", "telegram", "browser/computer-use", "live api"]
}
```

## 3. Risk classification + approval gates

| Risk | Definition | Gate |
|------|------------|------|
| low | Local, read-only or note-writing, repo/vault-bounded, reversible. | No special gate; standard review. |
| medium | Local writes to code/tests, dry-run launch design, sandboxed intake. | Human reviews before merge. |
| high | Anything touching launch-for-real, network beyond loopback, or new tool wiring. | Explicit human approval **before** the step. |
| blocked | Live account/API, posting, money, browser/desktop control, unknown binary, Telegram. | Not done without a dedicated, separately-approved milestone. |

Approval gates are never weakened by routing. A task classified `high` or
`blocked` stops and waits for a human; the coordinator may prepare notes but takes
no live action.

## 4. Status lifecycle

A task moves through a fixed lifecycle. The coordinator updates the status note;
it never skips the human-decision state for a merge.

```
idle -> planned -> assigned -> running -> output_ready -> audit_ready
     -> (blocked | pass) -> human_decision -> done
```

- `blocked` can be entered from any state; it records a reason and stops.
- `human_decision` is mandatory before a merge to main.

## 5. Handoff file lifecycle

The handoff is a manual, file-based relay through the vault — copy/paste, not auto
cross-agent execution:

1. Coordinator writes `02_Agent_Handoffs/CURRENT_TASK.md` (classified task).
2. `prepare_claude_prompt` produces `CLAUDE_PROMPT.md`; a human starts Claude.
3. Claude writes `04_Logs/CLAUDE_LAST_RUN.md` and pushes its branch.
4. `prepare_codex_audit` produces `CODEX_AUDIT_PROMPT.md`; a human starts Codex.
5. Codex writes `04_Logs/CODEX_LAST_AUDIT.md` with a verdict
   (`CLEAN PASS` / `CONDITIONAL PASS` / `BLOCKED_VALIDATION`).
6. `collect_agent_outputs` writes `04_Logs/HERMES_COORDINATOR_SUMMARY.md`.
7. Human reads the summary and decides merge / fix / block.

---

## 6. Obsidian memory contract

The vault is the shared memory. It is the single board everyone reads. It is not a
secret store and not a raw-log dump.

### Vault structure (target contract)

| Folder | Purpose | State today |
|--------|---------|-------------|
| `00_Inbox/` | New, unsorted notes; `START_HERE.md` entry point. | exists |
| `01_Projects/` | Per-project durable context. | target (create when first used) |
| `02_Agent_Handoffs/` | Current task + agent prompts. | exists |
| `03_Decisions/` | Decision records (intake, architecture, merges). | target (create when first used) |
| `04_Logs/` | Last run, last audit, coordinator summary, wrapper runs. | exists |
| `05_Backlog/` | Documented directions not yet built. | exists |
| `99_Attachments/` | Small supporting assets. | target (create when first used) |

Folders marked "target" are **not** created by this plan (no empty directories);
they are the contract a later milestone fills when it first needs them.

### Required files (target set)

`AGENT_RULES.md`, `02_Agent_Handoffs/CURRENT_TASK.md`,
`02_Agent_Handoffs/CLAUDE_PROMPT.md`, `02_Agent_Handoffs/CODEX_AUDIT_PROMPT.md`,
`04_Logs/CLAUDE_LAST_RUN.md`, `04_Logs/CODEX_LAST_AUDIT.md`,
`04_Logs/HERMES_COORDINATOR_SUMMARY.md` (target),
`02_Agent_Handoffs/NEXT_CLAUDE_TASK.md`,
`02_Agent_Handoffs/NEXT_CODEX_AUDIT_PROMPT.md`.

### What belongs in the vault

- Stable truth (current roles, current Hermes setup).
- The current task and its classification.
- Decisions and their reasons.
- Audit summaries and verdicts.
- Blocked reasons.
- The next action / next prompt.

### What does NOT belong in the vault

- **no secrets**: tokens, API keys, passwords, cookies, `.env`, auth files.
- Raw, huge logs — compress with Gemma first, store the summary.
- Browser cookies or session data.
- Personal credentials or PII.
- Unverified claims stated as fact (mark drafts as drafts).

## 7. Audit checklist for N+6.9A (what Codex verifies)

1. Routing matches the table; ChatGPT is the main brain, Hermes is the coordinator
   that routes but does not implement or audit.
2. Risk gates hold: `high`/`blocked` tasks stop for a human; no gate weakened.
3. The status lifecycle includes a mandatory `human_decision` before any merge.
4. The vault contract holds: required files present, **no secrets**, no raw-log
   dumps, no PII; "target" folders are not created empty.
5. No live action: **no Telegram**, **no browser/computer-use**, **no MCP installed**,
   no live API, no autonomous launch.
6. Reversible: policy + enforcement notes/tests only.
