# N+6.7A - Tool/Repo Intake Static Registry

Status: IMPLEMENTED (safe foundation). This milestone builds a local, static,
planning-only registry that tracks external tool candidates and classifies their
intake status **without installing them**. It does **not** enable autonomy and
adds no external capability.

Author lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Date: 2026-05-31

## 1. What this milestone is

A safe foundation for evaluating useful tools (Understand-Anything, MarkItDown,
Graphify, UI-TARS observation-only, Browser Harness, 21st.dev / design skills,
Graph MCP, security checklists, and more). It gives Ghoti:

- a machine-readable registry (`14_context/tool_intake/tool_candidate_registry.json`),
- a human-readable decision log (`14_context/tool_intake/tool_intake_decision_log.md`),
- an intake guide (`14_context/tool_intake/README_TOOL_INTAKE.md`),
- a read-only CLI (`03_scripts/tool_intake_static_registry.py`), and
- tests that lock the safety behavior so it cannot silently regress.

**No blind installs.** A candidate is inspected before any of its code runs.
Every candidate stays at status `candidate_only` or `blocked`; nothing is
installed, cloned, downloaded, executed, or wired into the runtime here.

## 2. The intake rule: inspect -> classify -> sandbox -> integrate

1. **Inspect** the project's own README, license, and file tree without running it.
2. **Classify** the risk (low / medium / high / blocked) and record stop conditions.
3. **Sandbox** only if behavior must be observed - isolated, no secrets, no network
   beyond the test, and only after explicit human approval.
4. **Integrate** only after the tool has tests proving safe behavior and a Codex
   audit passes.

"Documented + statically reviewed" is the default resting state, and a candidate
may remain `candidate_only` (documented, **not installed**) indefinitely.

## 3. Registry contents

23 candidates across three tiers:

- **HIGH (8)** - Understand-Anything, MarkItDown, Graphify, UI-TARS observation-only,
  Browser Harness (local fixture), 21st.dev / design skills, Graph MCP (read-only,
  later), Security Checklists. Mostly static/read-only and low/medium risk.
- **MEDIUM (9)** - Vercel agent-browser, FigMirror, OpenVid, YOLOv12, Meta SAM,
  Frigate, Pi-hole, OpenWA, Postiz. Useful but heavier or more sensitive; deferred.
- **BLOCKED (6)** - social posting, live browser/desktop control, money/payment,
  account login, unknown binaries, OSINT/Kali offensive tooling. Each needs its
  own dedicated, human-approved safety milestone before it is even cloned.

Each candidate carries: `name`, `category`, `priority`, `status`, `installed`,
`runtime_wired`, `intended_value`, `risk_level`, `safe_intake_method`,
`first_safe_test`, `integration_target`, `stop_conditions`, `allowed_now`, and
`forbidden_now`. The registry validator enforces `installed: false` and
`runtime_wired: false` on every candidate.

## 4. The CLI

`03_scripts/tool_intake_static_registry.py` is stdlib-only and read-only. It adds,
downloads, fetches, and runs nothing, and makes no outbound network calls.

| Command | Result |
|---------|--------|
| `--json` | JSON summary with counts by priority / risk / status. |
| `--list` | One candidate per line, by tier. |
| `--candidate "MarkItDown" --json` | The single candidate's record. |
| `--registry <path> --json` | Validate + summarize a specific registry file. |

It exits non-zero on an invalid registry (bad JSON, missing field, or a candidate
that claims `installed: true` / `runtime_wired: true`) and on a missing candidate.

## 5. What is explicitly NOT enabled

- **No blind installs.** No candidate is installed or wired in; the registry
  installs nothing.
- **No external repo is cloned or run.** No external code is executed.
- **MCP, browser-use, computer-use, and Telegram are not enabled.**
- No autonomous agent launch. No live account/API/posting/money action. No secrets,
  no external telemetry.
- `main` is not touched by this milestone.

## 6. What Codex should audit next

1. The registry lists only documented candidates; every candidate is
   `candidate_only` or `blocked`, with `installed: false` and `runtime_wired: false`.
2. The CLI installs, clones, fetches, and runs nothing, and makes no network call.
3. The blocked tier names the dangerous boundaries (social posting, live
   browser/desktop, money, account login, unknown binary, OSINT/Kali).
4. No doc claims MCP, browser-use, computer-use, Telegram, or autonomy is enabled.
5. The change is registry + decision log + README + CLI + doc + test only, and is
   trivially revertable.
