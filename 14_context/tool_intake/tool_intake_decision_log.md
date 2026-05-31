# Tool Intake Decision Log

Append-only record of intake decisions. Each row records the resting decision for
a candidate as of this milestone. The decisions here are all **planning-only**:
no candidate is installed or wired in, no external repo is cloned or run, and the
registry installs nothing. A decision can be revisited in a later, approved
milestone after static review (and, where needed, an approved sandbox + Codex
audit).

Decision vocabulary:

- **document (candidate_only)** - keep in the registry as a documented candidate;
  **not installed**, not wired. Default safe resting state.
- **defer** - revisit later; heavier or more sensitive; static review first.
- **blocked** - not evaluated through normal intake; needs its own dedicated,
  human-approved safety milestone before it is even cloned.

## Decisions (2026-05-31, N+6.7A)

| Candidate | Tier | Risk | Decision | Reason |
|-----------|------|------|----------|--------|
| Understand-Anything | high | low | document (candidate_only) | Repo triage; static README/license review only. |
| MarkItDown | high | low | document (candidate_only) | Doc->Markdown for memory; sandbox convert of one local fixture only, later. |
| Graphify | high | low | document (candidate_only) | Repo graph for navigation; read-only output. |
| UI-TARS Observation | high | medium | document (candidate_only) | Screenshot observation only; no click/type; gated, separate milestone. |
| Browser Harness | high | medium | document (candidate_only) | Local fixture tests only; no live browser. |
| 21st.dev Design Skills | high | low | document (candidate_only) | UI quality references; guidance-only. |
| Graph MCP | high | medium | document (candidate_only) | Read-only repo-graph via MCP; deferred, MCP stays disabled now. |
| Security Checklists | high | low | document (candidate_only) | Public-repo / safety review checklists; guidance-only. |
| Vercel agent-browser | medium | high | defer | Live browser control; wait for the approved browser track. |
| FigMirror | medium | medium | defer | Design import; static review first. |
| OpenVid | medium | medium | defer | Video generation; heavy dependency. |
| YOLOv12 | medium | medium | defer | Object detection; heavy model, sandbox only if ever needed. |
| Meta SAM | medium | medium | defer | Segmentation; heavy model. |
| Frigate | medium | medium | defer | Local NVR / camera; out of current scope. |
| Pi-hole | medium | medium | defer | Network-level DNS; infra change, needs separate review. |
| OpenWA | medium | high | defer | WhatsApp automation; account action, blocked-adjacent. |
| Postiz | medium | high | defer | Social scheduling; posting, blocked-adjacent. |
| Social Posting Tools | blocked | blocked | blocked | Posts to social media / messages on someone's behalf. |
| Live Browser/Desktop Control Tools | blocked | blocked | blocked | Controls a live browser or the desktop (click/type/screen). |
| Money/Payment/Trading Tools | blocked | blocked | blocked | Handles money or payment credentials. |
| Account Login Tools | blocked | blocked | blocked | Logs into accounts or stores session tokens. |
| Unknown Binary Tools | blocked | blocked | blocked | Unknown binary or runs code on install. |
| OSINT/Kali Offensive Tools | blocked | blocked | blocked | Offensive tooling outside an authorized, scoped engagement. |

## Stop conditions (any halts intake and records "blocked")

Unknown binary, network-on-import, credential handling, license incompatibility,
or a missing human approval at a gate step.
