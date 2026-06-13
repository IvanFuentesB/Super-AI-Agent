# Agent OS Approval Queue

This folder is the inspectible state machine for supervised local artifact
writes. Runtime queue items are JSON files under `pending/`, `approved/`,
`rejected/`, `executed/`, or `failed/`; those generated files are ignored.

The Rust Agent OS guard validates requests before they enter the queue, again
before approval, and again before execution. The executor can only write
declared text/JSON artifacts under the approved repo-local output roots. It
cannot run commands, open a browser, touch accounts, send messages, or make
external writes.

Transitions use append/copy records rather than destructive deletes. An older
state copy remains useful audit history but is inactive when its embedded
`approval_state` no longer matches its folder. On restricted Windows
worktrees, storage may use the command center's fixed data-only writer
fallback; that fallback accepts encoded bytes and no command surface.
