# Rust runtime lane (N+6.22A)

Static, planning-only. **Do not introduce Rust now.**

## Decision

- Rust is not needed for the current docs/planning lanes (these are Python +
  Markdown + small PowerShell wrappers).
- No Rust toolchain, crate, or build is added in this milestone or the near-term lanes.

## When a future Rust lane becomes worth it

Reserve a future Rust lane only when a **concrete** high-performance or time-sensitive
use case appears, such as:

- a high-performance / time-sensitive agent runtime,
- file watchers,
- tracing / high-volume structured logging,
- local IPC between components,
- long-running background services.

## Rule

Until such a concrete use case is approved, **do not introduce Rust now**. Some
candidate tools (AppFlowy, Qdrant) happen to be written in Rust; studying their ideas
does not require a Rust toolchain here, and none is added.
