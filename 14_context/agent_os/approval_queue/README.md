# Agent OS Approval Queue

This folder is the inspectible state machine for supervised local artifact
writes. Runtime queue items are JSON files under `pending/`, `approved/`,
`rejected/`, `executed/`, or `failed/`; those generated files are ignored.

The Rust Agent OS guard validates requests before they enter the queue, again
before approval, and again before execution. The executor can only write
declared text/JSON artifacts under the approved repo-local output roots. It
cannot run commands, open a browser, touch accounts, send messages, or make
external writes.
