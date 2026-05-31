# HERMES_CURRENT_STATUS.md — Current State of the System

Status: living status note. Hermes updates this; it is not a secret store.
Date: 2026-05-31

## Branch / merge truth

- **N+6.4B is on `main`.** This is the current verified baseline.
- **N+6.5A** exists as a **safe computer-use observation harness** branch. If that
  branch is detected, treat it as observation-only. **Do not claim N+6.5A is merged
  unless `main` actually contains it.**
- **N+6.6A** is the current milestone: it **implements the wrapper foundation**
  (Hermes soul + router policy + dry-run PowerShell wrappers + tests). No autonomy
  is enabled by N+6.6A.

## Capabilities truth (today)

| Capability | State |
|------------|-------|
| Telegram | **not enabled** |
| Browser / computer-use | **not enabled** |
| MCP | **not installed** |
| Autonomous agent launch | **not enabled** (dry-run designs only) |
| External repos | **not mass-installed**; intake is gated and inspected first |
| Arbitrary command execution by Hermes | **not enabled** |

## Local models

- Hermes uses **`llama3.1:8b`** as its **local coordinator brain**.
- **Gemma (`gemma3:4b`)** is the **cheap summary / compression worker** only.
- Models are reached on **loopback only** (`http://127.0.0.1:11434`); wrappers in
  this milestone do **not** call them — they only describe what they would do.

## What N+6.6A does NOT change

- Telegram, browser/computer-use, and MCP remain disabled.
- No external repo is cloned, installed, or executed.
- No agent is launched; no live account/API/posting/money action is taken.
- `main` is not touched by this milestone.
