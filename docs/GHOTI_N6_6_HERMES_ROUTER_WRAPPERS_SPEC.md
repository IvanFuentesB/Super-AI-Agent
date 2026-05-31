# N+6.6 — Hermes Router Wrapper System (SPEC ONLY)

Status: PLAN / SPEC ONLY. No wrapper below exists yet, none is wired, none is
enabled. This document is the contract a future N+6.6A milestone implements and a
future Codex audit verifies. Writing this spec takes no live action.

Author lane: systems architect (planning lane)
Date: 2026-05-31

## Why wrappers

Hermes is the local coordinator, not the main brain. To keep coordination safe,
Hermes runs **approved wrappers only** and will **never run arbitrary commands**.
A wrapper is a small, named PowerShell script with a fixed contract: known
inputs, known outputs, an allow-list of file paths it may touch, and an explicit
forbidden list. If a task is not expressible as one of these wrappers, it does
not run through Hermes — it goes to a human.

Proposed (not created here) locations:

- Wrapper scripts: `03_scripts/hermes_wrappers/*.ps1` (repo-bounded).
- Wrapper run log: `14_context/agent_handoff_vault/04_Logs/wrapper_runs/<date>.jsonl`
  (vault-bounded, append-only, one JSON object per run).
- Handoff notes the wrappers read/write: the existing vault folders
  `00_Inbox/`, `02_Agent_Handoffs/`, `04_Logs/`, `05_Backlog/`.

## Global wrapper rules (apply to every wrapper)

- **Repo-root bounded.** No path outside
  `C:\Users\ai_sandbox\Documents\AI_Managed_Only`. Reject `..` traversal and
  absolute paths outside the root.
- **Vault-bounded where possible.** Note read/write stays inside
  `14_context/agent_handoff_vault/`.
- **no secrets.** Never read or write `.env`, tokens, API keys, cookies, auth
  files, or OS environment secrets. If a target file path matches a secret
  pattern, abort.
- **no Telegram**, **no browser/computer-use**, no live account/API/posting/money.
- **no MCP installed** and none invoked.
- No destructive commands (no delete/reset/force), no broad process kills, no
  calling external/unknown scripts.
- **One agent per task; no overlapping edits.** A wrapper that assigns work must
  refuse if the target task is already `running` for another agent.
- All output lands in the Obsidian vault or the wrapper run log — never on a
  remote, never in a secret store.
- Every run appends one structured record to the wrapper run log (see schema).
- **Dry-run is the default for anything that would launch an agent.** Launch
  wrappers print the command they *would* run and exit; they do not execute it.

## Wrapper run log record (schema)

Each run appends one line to `04_Logs/wrapper_runs/<date>.jsonl`:

```json
{
  "ts": "2026-05-31T00:00:00Z",
  "wrapper": "read_current_task",
  "mode": "run | dry-run",
  "inputs": { "task_id": "N6.6A" },
  "ok": true,
  "wrote": ["02_Agent_Handoffs/CLAUDE_PROMPT.md"],
  "read": ["02_Agent_Handoffs/CURRENT_TASK.md"],
  "local_only": true,
  "live_action": false,
  "notes": "string"
}
```

`local_only` and `live_action: false` are required on every record. A wrapper
that cannot honor them must abort before doing anything.

## Common contract fields (used in each wrapper below)

Purpose · Inputs · Outputs · Allowed paths · Forbidden actions · Log · Dry-run ·
Failure · Approval · Tests · Security concerns.

---

## Phase-1 wrappers (read-only / note-writing — N+6.6A)

### 2.1 `read_current_task.ps1`

- **Purpose.** Read the active task from the vault and return it as text/JSON for
  a coordinator or human. Pure read.
- **Inputs.** none (optional `-Json` switch).
- **Outputs.** stdout: the contents of `02_Agent_Handoffs/CURRENT_TASK.md` (and a
  small JSON summary if `-Json`).
- **Allowed paths.** read `02_Agent_Handoffs/CURRENT_TASK.md`,
  `00_Inbox/START_HERE.md`, `AGENT_RULES.md`. No writes (except the run log).
- **Forbidden actions.** any write to task/prompt files; any network; any secret read.
- **Log.** one record, `mode:"run"`, `read:[...]`, `wrote:[]`.
- **Dry-run.** identical to run (it is already read-only).
- **Failure.** if the file is missing, exit non-zero with a clear message; write a
  failed record; change nothing.
- **Approval.** none required (read-only).
- **Tests.** returns file content; refuses a path outside the vault; emits a log
  record with `live_action:false`.
- **Security concerns.** path traversal on the optional path arg → enforce the
  allow-list.

### 2.2 `write_handoff_note.ps1`

- **Purpose.** Write or update a single named handoff note in the vault (e.g.
  `CLAUDE_LAST_RUN.md`, `HERMES_COORDINATOR_SUMMARY.md`).
- **Inputs.** `-Target <allowed-note-name>`, `-BodyFile <path-in-repo>` (the text
  to write, read from a repo file so no large blob is passed on the command line).
- **Outputs.** the named note is created/overwritten with the provided body.
- **Allowed paths.** write only to a fixed allow-list inside
  `02_Agent_Handoffs/` and `04_Logs/`. Read `-BodyFile` from inside the repo root.
- **Forbidden actions.** writing outside the allow-list; writing secrets; deleting
  notes; appending raw un-summarized logs (see Gemma wrapper to compress first).
- **Log.** one record with `wrote:[target]`.
- **Dry-run.** print the target path and a diff-preview; write nothing.
- **Failure.** if `-Target` not on the allow-list → abort, no write, failed record.
- **Approval.** none for the allow-listed notes; anything else is refused.
- **Tests.** writes an allowed note; rejects a non-allowed target; dry-run writes
  nothing; refuses a secret-looking body.
- **Security concerns.** allow-list must be exact; never accept an arbitrary
  destination path.

### 2.3 `run_gemma_summary.ps1`

- **Purpose.** Use the **local** Gemma model (gemma3:4b via the local endpoint
  `http://127.0.0.1:11434/v1`) to summarize/compress a repo text file into a short
  note. Local only.
- **Inputs.** `-InputFile <path-in-repo>`, `-MaxWords <int>`,
  `-OutTarget <allowed-note-name>`.
- **Outputs.** a compressed summary written through `write_handoff_note` rules.
- **Allowed paths.** read `-InputFile` inside the repo; write the summary to the
  vault allow-list. Network: **loopback only** (`127.0.0.1:11434`); any non-loopback
  host is refused.
- **Forbidden actions.** calling any non-local endpoint; sending secrets to the
  model; writing outside the vault.
- **Log.** one record, `notes:"gemma local summary"`, `local_only:true`.
- **Dry-run.** print the prompt and the destination; do not call the model.
- **Failure.** if the local endpoint is down → abort with a clear message; no
  partial write.
- **Approval.** none (local model, local files) — but the loopback check is hard.
- **Tests.** refuses a non-loopback endpoint; dry-run makes no call; refuses
  secret-looking input; output respects `-MaxWords`.
- **Security concerns.** must not exfiltrate file contents anywhere but the local
  model; enforce loopback.

### 2.4 `prepare_claude_prompt.ps1`

- **Purpose.** Assemble a ready-to-paste Claude implementation prompt from the
  current task + rules, and write it to `02_Agent_Handoffs/CLAUDE_PROMPT.md`.
- **Inputs.** `-TaskFile` (default `CURRENT_TASK.md`).
- **Outputs.** `CLAUDE_PROMPT.md` containing scope, allowed files, safety rules,
  validation, and the required final-response format — text only.
- **Allowed paths.** read `CURRENT_TASK.md`, `AGENT_RULES.md`; write `CLAUDE_PROMPT.md`.
- **Forbidden actions.** launching Claude; embedding secrets; writing outside the
  allow-list.
- **Log.** one record, `wrote:["02_Agent_Handoffs/CLAUDE_PROMPT.md"]`.
- **Dry-run.** print the assembled prompt; write nothing.
- **Failure.** missing task file → abort.
- **Approval.** none (note assembly only).
- **Tests.** produced prompt contains the safety block and the allowed-files list;
  contains no secret; dry-run writes nothing.
- **Security concerns.** prompt must never include credentials or absolute secret
  paths.

### 2.5 `prepare_codex_audit.ps1`

- **Purpose.** Assemble a ready-to-paste Codex audit prompt (branch under audit,
  base main, scope, checklist, verdict set) into
  `02_Agent_Handoffs/CODEX_AUDIT_PROMPT.md`.
- **Inputs.** `-Branch <feature-branch>`, `-BaseMain <ref>`.
- **Outputs.** `CODEX_AUDIT_PROMPT.md` with the audit checklist and the verdict
  vocabulary (`CLEAN PASS` / `CONDITIONAL PASS` / `BLOCKED_VALIDATION`).
- **Allowed paths.** read `CURRENT_TASK.md`, `AGENT_RULES.md`; write `CODEX_AUDIT_PROMPT.md`.
- **Forbidden actions.** launching Codex; merging; embedding secrets.
- **Log.** one record, `wrote:["02_Agent_Handoffs/CODEX_AUDIT_PROMPT.md"]`.
- **Dry-run.** print the assembled audit prompt; write nothing.
- **Failure.** missing inputs → abort.
- **Approval.** none (note assembly only).
- **Tests.** prompt names the branch + base main and lists the three verdicts;
  contains no secret.
- **Security concerns.** branch names only; never an access token.

### 2.6 `collect_agent_outputs.ps1`

- **Purpose.** Gather the latest run/audit notes into a single coordinator summary
  (`04_Logs/HERMES_COORDINATOR_SUMMARY.md`) so a human sees one board.
- **Inputs.** none (reads the known notes).
- **Outputs.** a concise summary referencing `CLAUDE_LAST_RUN.md` and
  `CODEX_LAST_AUDIT.md` with their headline status.
- **Allowed paths.** read `04_Logs/CLAUDE_LAST_RUN.md`, `04_Logs/CODEX_LAST_AUDIT.md`,
  `02_Agent_Handoffs/CURRENT_TASK.md`; write `04_Logs/HERMES_COORDINATOR_SUMMARY.md`.
- **Forbidden actions.** writing outside the allow-list; inventing status not in
  the source notes.
- **Log.** one record, `wrote:["04_Logs/HERMES_COORDINATOR_SUMMARY.md"]`.
- **Dry-run.** print the summary; write nothing.
- **Failure.** if a source note is missing, summarize what exists and mark the
  rest "missing"; never fabricate.
- **Approval.** none (read + summarize).
- **Tests.** summary cites only facts present in source notes; dry-run writes
  nothing.
- **Security concerns.** must not copy secrets from any note into the summary.

---

## Phase-2 wrappers (dry-run launch — N+6.6B, still no real launch)

These exist to design the launch contract **without launching anything**. In
N+6.6B they are **print-only**: they emit the exact command a human would run and
exit. Real execution is a later, separately-approved milestone with a human
present.

### 2.7 `launch_claude_task.ps1` (DRY-RUN ONLY)

- **Purpose.** Show the command/prompt that would start a Claude implementation
  run for the current task. Does not start anything.
- **Inputs.** `-TaskFile`, `-DryRun` (forced true in N+6.6B).
- **Outputs.** prints the would-be invocation + the prompt path; exits 0.
- **Allowed paths.** read `CLAUDE_PROMPT.md`; write nothing but the run log.
- **Forbidden actions.** actually spawning Claude; any live API; any process start.
- **Log.** one record, `mode:"dry-run"`, `live_action:false`.
- **Dry-run.** the only mode. A non-dry-run path is not implemented in N+6.6B.
- **Failure.** missing prompt → abort.
- **Approval.** real (non-dry-run) launch requires a separate milestone + human.
- **Tests.** asserts it never starts a process and always logs `live_action:false`.
- **Security concerns.** must be impossible to flip to live without a code change
  that an audit would catch.

### 2.8 `launch_codex_audit.ps1` (DRY-RUN ONLY)

- **Purpose.** Show the command/prompt that would start a Codex audit. Does not
  start anything.
- **Inputs.** `-Branch`, `-DryRun` (forced true in N+6.6B).
- **Outputs.** prints the would-be invocation + the audit-prompt path; exits 0.
- **Allowed paths.** read `CODEX_AUDIT_PROMPT.md`; write nothing but the run log.
- **Forbidden actions.** spawning Codex; merging; any live API.
- **Log.** one record, `mode:"dry-run"`, `live_action:false`.
- **Dry-run.** the only mode in N+6.6B.
- **Failure.** missing audit prompt → abort.
- **Approval.** real launch is a separate milestone + human.
- **Tests.** never starts a process; logs `live_action:false`.
- **Security concerns.** same as 2.7 — no silent path to live.

---

## Audit checklist for N+6.6A (what Codex verifies)

1. Only the Phase-1 wrappers exist; each matches its contract above.
2. Every wrapper enforces the repo-root + vault allow-list and rejects traversal.
3. No wrapper reads/writes secrets; **no secrets** appear in any output.
4. **never run arbitrary commands** — there is no pass-through/`Invoke-Expression`
   of caller-supplied strings.
5. Launch wrappers, if present, are dry-run only and cannot execute.
6. Tests cover: happy path, path-traversal rejection, secret rejection, dry-run
   writes-nothing, and the run-log `local_only:true` / `live_action:false` fields.
7. **no Telegram**, **no browser/computer-use**, **no MCP installed**, no live API.
8. Reversible: scripts + tests + log folder only; trivially revertable.
