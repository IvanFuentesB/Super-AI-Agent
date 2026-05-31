# Tool / Repo Intake (`14_context/tool_intake/`)

This folder is a **static, planning-only** registry of external tools Ghoti may
one day evaluate. Listing a tool here is **not** adoption. **No blind installs:**
a candidate is inspected before any of its code runs, and nothing here is
installed, cloned, downloaded, executed, or wired into the runtime by this
milestone (N+6.7A).

## Files

| File | Purpose |
|------|---------|
| `tool_candidate_registry.json` | The machine-readable registry of candidates and their intake fields. |
| `tool_intake_decision_log.md` | Human-readable decision record for each candidate (append-only). |
| `README_TOOL_INTAKE.md` | This guide. |

The CLI that reads the registry is `03_scripts/tool_intake_static_registry.py`.
It is read-only: it loads the JSON, validates it, and prints a summary. It adds,
downloads, fetches, and runs nothing, and makes no outbound network calls.

## The rule: inspect -> classify -> sandbox -> integrate

1. **Inspect** the project's own README, license, and file tree **without running it**.
2. **Classify** the risk (low / medium / high / blocked) and record stop conditions.
3. **Sandbox** only if behavior must be observed - isolated, no secrets, no network
   beyond the test, and only after explicit human approval.
4. **Integrate** only after the tool has tests proving safe behavior and a Codex
   audit passes. "Documented + statically reviewed" is the default resting state.

A candidate may sit at `candidate_only` (documented, **not installed**) indefinitely.
That is a valid, safe end state.

## What is allowed now vs forbidden now

**Allowed now (per candidate):** read the project's own docs, inspect its file
tree statically, and record intake + risk notes.

**Forbidden now (per candidate):** install or download the tool, run any of its
code, wire it into the Ghoti runtime/dashboard/wrappers, or make network calls on
its behalf. No executable third-party script is run before inspection. No secrets,
no live accounts, no external telemetry.

## Tiers

- **HIGH** - near-term, mostly static/read-only (Understand-Anything, MarkItDown,
  Graphify, UI-TARS observation-only, Browser Harness local fixture, 21st.dev /
  design skills, Graph MCP read-only later, Security Checklists).
- **MEDIUM** - useful but heavier or more sensitive; revisit after the HIGH set.
- **BLOCKED** - not evaluated through normal intake; each needs its own dedicated,
  human-approved safety milestone before it is even cloned (social posting, live
  browser/desktop control, money/payment, account login, unknown binaries,
  OSINT/Kali offensive tooling).

## Not enabled by this milestone

MCP, browser-use, computer-use, and Telegram are **not enabled**. No candidate is
installed or wired in. No external repo is cloned or run. The registry installs
nothing. Adding or wiring any tool is a separate, approved milestone.

## Usage

```bash
python 03_scripts/tool_intake_static_registry.py --json
python 03_scripts/tool_intake_static_registry.py --list
python 03_scripts/tool_intake_static_registry.py --candidate "MarkItDown" --json
```
