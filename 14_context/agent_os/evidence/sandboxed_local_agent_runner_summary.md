# Sandboxed Local Agent Runner Summary

Ghoti can now launch one real, fixed local worker process after explicit human
approval and a positive Rust guard verdict.

## Real capability

- Allowlisted workers: `repo-summary-worker` and
  `local-model-summary-classification-worker`
- Process protocol: fixed Python entrypoint plus `--json`, stdin/stdout data
- Inputs: declared repo-local files only
- Outputs: declared repo-local Agent OS artifacts only
- Runtime: bounded to 30 seconds or less
- Kill paths: timeout and request-specific cancellation marker
- Log safety: capped stdout/stderr; oversized output fails closed
- Evidence: run record, evidence note, handoff, artifact, and runner state
- Command center: existing Agent OS panel, not a new dashboard

## Guardrails

- Exactly one of the two local workers can hold the active-worker lock.
- Rust validates action, capability, worker identity, task, paths, ownership,
  approval, runtime, and fingerprint.
- Dynamic executable, command, argument, shell, environment, script, and code
  fields are denied.
- The worker cannot launch processes, use network, or write files.
- Worker output is data only and is never interpreted as a command.

## Still blocked

Browser/computer-use, mouse/keyboard, accounts, sending/posting, purchases,
payments, trading, external writes, arbitrary commands, live swarms, and
multiple concurrent workers remain blocked.
