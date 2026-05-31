# HERMES_ROUTER_POLICY.md — How Hermes Routes Work

Status: routing contract. Hermes classifies a task, then routes it per this table.
Routing never bypasses a human gate for risky work.

## 1. Routing table (which work goes where)

| Work type | Routed to | Mode |
|-----------|-----------|------|
| Planning / architecture / prompt design / safety | **ChatGPT** (main brain) | planning |
| Handoff / memory / status / classification | **Hermes / Llama** (`llama3.1:8b`) | local |
| Summary / compression of logs or docs | **Gemma** (`gemma3:4b`) | local, loopback |
| Implementation of a defined task | **Claude Code** | supervised |
| Audit / merge gate | **Codex** | supervised |
| Current web research (with citations) | **ChatGPT / Perplexity / manual** | manual |
| Large docs → Markdown | **NotebookLM / MarkItDown** (later, after intake) | gated |
| Repo graph / code map | **Understand-Anything / Graphify** (later, after intake) | gated |
| Final approval / merge | **Human** | gate |

Hermes drafts and routes; it does not implement, audit, or merge.

## 2. Risk levels and gates

| Risk | Examples | Gate |
|------|----------|------|
| **low** | read files, summarize, prepare prompts | standard; no special gate |
| **medium** | write handoff notes, generate prompt files | human reviews before use |
| **high** | run tests, create branches, launch tools | explicit human approval **before** |
| **blocked** | browser control, account login, posting, money, secrets, destructive commands | not done without a dedicated, separately-approved milestone |

A task classified `high` or `blocked` **stops and waits for a human**. Hermes may
prepare notes but takes no live action. Approval gates are never weakened by routing.

## 3. Status lifecycle

A task moves through a fixed lifecycle; Hermes updates the status note and never
skips the `human_decision` state before a merge:

```
idle -> planned -> assigned -> running -> output_ready -> audit_ready
     -> (blocked | pass) -> human_decision
```

- `blocked` can be entered from any state; it records a reason and stops.
- `human_decision` is mandatory before any merge to `main`.

## 4. How routing is executed (this milestone)

Routing is executed only through the **approved wrappers** in
`03_scripts/hermes_router/`. Those wrappers are **dry-run / read-only by default**,
are bounded to the repo root and the vault, and **never run arbitrary commands**.
Hermes has no other way to act.
