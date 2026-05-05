# N+3.44b Controlled Parallel Verdict

Status: Codex gate verdict.
Date: 2026-05-05

```text
CONTROLLED_PARALLEL_ALLOWED = YES
```

This is a narrow yes. It does not permit uncontrolled parallel agents, live actions, external integrations, account actions, or broad simultaneous editing. It permits the first tiny controlled pilot only.

## Required Rules

- Every agent needs a lane id.
- Every implementation or audit lane must declare a branch.
- Every shared file edit requires a lock before writing.
- No two agents may edit the same locked file.
- No live actions.
- No external tools unless separately approved.
- No installs, clones, new MCP connections, scraping, emails, posts, payments, job applications, giveaway entries, account creation, or live account use.
- Merge one branch at a time.
- State docs are updated by one designated owner only.
- `active_locks.jsonl` and `lane_status.jsonl` must be checked before merge.
- The user must approve before any public, money-facing, account, connector, browser, or external side-effect action.
- Gemma/local model output stays draft-only unless human-reviewed and promoted.
- Python automation workers stay repo-local, deterministic, and stdlib-only unless explicitly approved otherwise.

## Why The Gate Passes

- Required lane files exist.
- Helper script compiles.
- Helper uses Python stdlib only.
- `--check` passes.
- Empty lock/status JSONL files parse.
- Dry-run lock/status commands print records and do not write.
- JSONL writes require `--apply`.
- Shared-file lock policy exists and covers core state/memory files.
- Registry defines all required active and future lanes.
- Course/certificate and Python automation safety boundaries are explicit.

## Known Limits

- The first pilot must be small because the helper is still a coordination aid, not a full concurrency controller.
- The helper does not prevent humans from editing files without locks; discipline and merge review are still required.
- Lock release is status-based rather than a dedicated helper command.
- `allowed_paths` and `forbidden_paths` should be validated more strictly in a later hardening pass.

## Approval Scope

Approved after this audit commit is pushed:

- two-lane controlled pilot with separate branches
- no overlapping write paths
- no shared state-doc edits by both agents
- one branch merged at a time

Not approved:

- uncontrolled parallel execution
- external tool integrations
- live account actions
- public/money-facing side effects
- autonomous agent execution without locks and human merge review
