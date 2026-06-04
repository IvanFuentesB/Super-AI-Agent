# Ghoti N+6.19A Overnight Operator MVP

N+6.19A moves Ghoti from status-only planning into safe repo-local operator work. It creates a prompt packet builder, a dry-run clipboard relay, a local operator queue, and an external repo execution sandbox.

## What Works

- Prompt packets can be generated from local JSON tasks.
- Prompt packets can be written into a local outbox.
- Clipboard relay can dry-run safely and copy only when explicitly requested.
- ECC, GBrain, and MarkItDown can be cloned into the ignored runtime sandbox.
- The repo execution sandbox can static-scan cloned repos and run read-only git metadata commands.
- ECC patterns can be inspected without executing ECC code.

## What Stays Disabled

- live app paste
- auto-submit
- OS-level click/type
- live browser automation
- Telegram `/run`
- MCP setup
- live agent launch
- provider token setup
- Docker
- arbitrary command execution
- third-party package install
- pushing or merging main from the operator

## External Repo Priority

ECC is first priority because it contains a broad agentic coding setup: agent profiles, skills, rules, commands, hooks, MCP configuration surfaces, prompt rules, and security scanning ideas.

GBrain is second priority because it maps to Ghoti's personal brain and memory architecture. It includes skills, docs, MCP material, brain-oriented operations, and examples that can inform Obsidian/status-brain handoffs.

MarkItDown remains the preferred document-ingestion target for future PDF/doc-to-Markdown work, but its install/run path remains blocked until a separate sandbox install milestone passes.

## Next Milestone

N+6.20A should implement an approved-window copy/paste harness using the ECC/GBrain-informed workflow. It should remain human-approved, local-only, and no auto-submit.
