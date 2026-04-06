# Runtime Environment

## Purpose

The runtime should detect and use the tools that actually exist in this Windows execution environment before assuming deeper integrations will work.

## Expected Tools

- `python`
- `git`
- `gh`

## PATH vs Fallback Detection

- PATH-visible tools are preferred first
- If a tool is not on PATH, the runtime may use a known fallback path for that process only
- Fallback resolution should stay explicit and reversible

## Why Shells Differ

Codex, the runtime checker, and an interactive terminal may not see the same PATH or session state. A tool can be installed and still be invisible to one shell.

## Current Approach

- detect first
- use per-process fallback paths if needed
- avoid global machine mutation
- keep readable diagnostics in the CLI and checker

## Practical Rule

Environment consistency matters before deeper live integrations. If `python`, `git`, or `gh` are inconsistently resolved, the runtime should report that clearly instead of pretending the tool layer is stable.
