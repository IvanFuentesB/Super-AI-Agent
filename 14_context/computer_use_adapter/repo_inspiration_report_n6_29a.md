# N+6.29A Repo Inspiration Report — Computer-Use Repo-Backed Adapter

## Summary

Five computer-use repos were used as static design references for the N+6.29A adapter.
All were inspected in N+6.12A (no new clones performed here). No code was copied.
Attribution is recorded in `repo_inspiration_manifest_n6_29a.json`.

## Repos and Patterns Adapted

### 1. TryCUA / CUA Driver (MIT)

- **Inspected in:** N+6.12A at commit `4c54f43`
- **Patterns adapted:**
  - Structured action-intent payload with declared type, target, value
  - Sandbox isolation boundary (allowed-target validation before any execution)
  - Capability declaration → blocked capabilities cause plan rejection
  - Approval gate: human approval token required before real execution
  - Dry-run status payload with all `real_*_performed` fields false
- **Not used:** live desktop control, Docker/QEMU/KASM, 189 shell scripts, real OS input APIs

### 2. UI-TARS (Apache-2.0)

- **Inspected in:** N+6.12A (source-needed; patterns from N+5.0A context also consulted)
- **Patterns adapted:**
  - Observation-only mode: adapter can inspect/read state without performing real OS actions
  - Typed action contract (click / type / read as explicit record fields)
  - Blocked-action manifest: canonical list of refused action types in every result
  - Arena status block: `simulation: true` / `live_execution: false` for visualization
- **Not used:** real GUI automation, model inference

### 3. Browser Harness (MIT)

- **Inspected in:** N+6.12A at commit `6d20866`
- **Patterns adapted:**
  - Local fixture pattern: static JSON fixture as action target instead of live page
  - CDP isolation: actions confined to loopback (127.0.0.1)
  - Blocked-URL guard: `target_url` validated against allowed-prefix list before accepting plan
- **Not used:** CDP to real web pages, self-writing-code

### 4. Vercel agent-browser (Apache-2.0)

- **Inspected in:** N+6.12A at commit `b4f2f37`
- **Patterns adapted:**
  - Capability declaration contract: `capabilities_required` validated against blocked set
  - Approval gate shape: `approval_token` field in result; `null` until human approves
  - `refused_live_actions` list: canonical list surfaced in every result payload
- **Note:** Apache-2.0 NOTICE required only if code is copied; none is copied here.

### 5. Ruflo (MIT)

- **Inspected in:** N+6.12A at commit `f57b698`
- **Patterns adapted:**
  - Coordinator/worker + shared-local-memory hand-off: adapter as coordinator, Rust policy checker (N+6.28A) as downstream worker
  - Declared-skill pattern: adapter explicitly lists allowed and refused action types
  - Dry-run-first invariant: no real execution without explicit flag AND human approval
- **Not used:** install scripts, npm postinstall hooks, any vendored Ruflo code
- **Risk noted:** supply-chain history (malicious npm pre-install, MCP prompt-injection, SQL-injection); no Ruflo code is vendored

## Prior Ghoti Milestones Referenced

| Milestone | Role |
|-----------|------|
| N+6.12A   | Primary static inspection record for all five repos |
| N+6.13A   | Sandbox action planner/runner pattern |
| N+6.14A   | Confined browser sandbox + CDP isolation pattern |
| N+5.0A    | UI-TARS observation-only adapter baseline |
| N+6.27A   | Repo-backed manifest format (branch unmerged; files not modified) |
| N+6.28A   | Rust policy checker bridge target (branch unmerged; files not modified) |

## What Was NOT Done

- No repos cloned in this milestone (N+6.12A inspection record is authoritative)
- No third-party code installed or executed
- No third-party repo contents committed
- No secrets, tokens, or real paths committed
- N+6.27A and N+6.28A files untouched (dependency documented, branches unmerged)

## Rust Policy Bridge Plan

Once N+6.28A (`rust/ghoti_policy_checker/`) is merged, the adapter's `--plan --dry-run`
flow should be extended to pipe the validated plan JSON to:

```
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- <plan.json>
```

The Rust checker applies a second-pass, memory-safe policy denial layer. Until then,
`rust_policy_bridge_ready: false` is reported in every adapter result.
