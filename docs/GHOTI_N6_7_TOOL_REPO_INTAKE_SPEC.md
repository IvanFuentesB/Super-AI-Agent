# N+6.7 — Tool / Repo Intake Pipeline (SPEC ONLY)

Status: PLAN / SPEC ONLY. No repo is cloned, installed, executed, or wired by
this document. It defines the gated process a future N+6.7A milestone follows to
evaluate an external tool or repository. Writing this spec takes no live action.

Author lane: systems architect (planning lane)
Date: 2026-05-31

## Principle: no blind installs

The intake pipeline exists so a candidate tool is **inspected before any of its
code runs**. The rule is **no blind installs**: documentation review and static
inspection come first; cloning is static-only and approval-gated; nothing is
runtime-wired until it has tests and a passing audit. A candidate may sit at
"documented, not installed" indefinitely — that is a valid, safe end state.

Where intake artifacts live (proposed, not created here):

- Per-candidate intake note: `14_context/repo_intake/<candidate>/INTAKE.md`.
- Decision record: appended to `14_context/agent_handoff_vault/03_Decisions/`
  (folder is part of the target vault contract; created only when first used).

## The 10-step intake pipeline

Each step has an output and a stop condition. A candidate advances only if the
prior step passed and a human approved the gate steps (marked **[GATE]**).

1. **Backlog entry.** Add the candidate to the intake backlog with a one-line
   reason and the problem it would solve. Output: backlog row. No code touched.
2. **README / docs review.** Read the project's own README and docs. Record what
   it claims to do, its maturity, and its maintenance status. Output: summary.
3. **License + security scan.** Record the license (and whether it permits our
   use) and scan for obvious red flags (telemetry, network calls on import,
   credential handling, obfuscated blobs). Output: license + risk notes.
4. **File-tree inspection.** Inspect the repository tree *without executing it*
   (read-only browse / static listing). Note entry points, scripts, and any
   bundled binaries. Output: annotated tree.
5. **Detect install scripts / hooks / binaries.** Explicitly look for
   `postinstall`/setup hooks, build scripts, git hooks, and prebuilt binaries —
   the things that would run code on install. Output: a list of "runs-on-install"
   items. Any unknown binary → escalate to Blocked.
6. **Risk classification.** Classify the candidate low / medium / high / blocked
   (see the risk table in `docs/GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md`).
   Output: a risk verdict with justification.
7. **[GATE] Static clone only if approved.** With human approval, clone into a
   read-only reference area (`21_repos/third_party`, which CLAUDE.md marks
   read-only). Static clone means: fetch the files, run nothing. Output: a pinned
   commit reference.
8. **[GATE] Sandbox only if needed.** If behavior must be observed, run it in an
   isolated sandbox with no repo write access, no secrets, and no network beyond
   what the test needs — only after explicit approval. Many candidates never need
   this step. Output: sandbox observation notes.
9. **No runtime wiring until test + audit.** The tool is **not** imported into the
   Ghoti runtime, dashboard, or wrappers until it has tests proving safe behavior
   and a Codex audit passes. "Documented + statically reviewed" is the default
   resting state. Output: pending wiring decision.
10. **Record the decision.** Write a decision record: adopt (guidance-only),
    adopt (sandboxed), defer, or reject — with the reason. Output: decision note
    in `03_Decisions/`. This closes the intake.

Stop conditions (any of these halts intake and records "blocked"): unknown
binary, network-on-import, credential handling, license incompatibility, or a
missing human approval at a **[GATE]** step.

## Candidate priority — HIGH (near-term, mostly static/read-only)

These solve real command-center problems and are low-risk under the pipeline
above. Listing them here is **not** adoption.

| Candidate | What it would help with | Intended posture |
|-----------|-------------------------|------------------|
| Understand-Anything | Explain a repo/codebase quickly for triage | static review; guidance-only |
| MarkItDown | Convert docs/PDF/office files to Markdown for memory | static review; sandbox convert only |
| Graphify | Build a repo/structure graph for navigation | static review; read-only output |
| UI-TARS (observation only) | Screenshot observation harness — **no click/type** | observation-only; gated |
| Browser harness (local fixture) | Local test fixture for future browser work | local fixture tests only |
| 21st.dev / design skills | Dashboard UI quality references | guidance-only |
| Graph MCP (read-only, later) | Read-only repo-graph via MCP | deferred; read-only MCP only |
| Security checklists | Public-repo / safety review checklists | guidance-only |

## Candidate priority — MEDIUM (later, needs more review)

Useful but heavier or more sensitive; revisit after the HIGH set is settled.

| Candidate | Note |
|-----------|------|
| Vercel agent-browser | live browser control — defer until the browser track is approved |
| FigMirror | design import — medium; static review first |
| OpenVid | video generation — heavy; defer |
| YOLOv12 | object detection — heavy model; sandbox only if ever needed |
| Meta SAM | segmentation — heavy model; defer |
| Frigate | local NVR / camera — out of current scope; defer |
| Pi-hole | network-level DNS — infra change; defer, needs separate review |
| OpenWA | WhatsApp automation — account action; **blocked-adjacent**, defer |
| Postiz | social scheduling — posting; **blocked-adjacent**, defer |

## Candidate priority — BLOCKED (until a separate, dedicated review)

Not evaluated through normal intake. Each needs its own safety milestone with
explicit human approval before it is even cloned.

- Anything that **posts to social media** or messages on someone's behalf.
- Anything that **controls a live browser** or the desktop (click/type/screen).
- Anything that **handles money** or payment credentials.
- Anything that **logs into accounts** or stores session tokens.
- **Unknown binaries** or tools that run code on install.
- **OSINT / Kali-style** offensive tooling outside an explicitly authorized,
  scoped engagement.

## Audit checklist for N+6.7A (what Codex verifies)

1. Only the approved HIGH candidates were processed, and only through the static
   steps (1–6, plus any **[GATE]** step that has a recorded human approval).
2. **no blind installs** — no install script, hook, or binary was executed; no
   `npm install` / `pip install` of a candidate was run.
3. Nothing was runtime-wired into the Ghoti runtime, dashboard, or wrappers.
4. Each processed candidate has an INTAKE note and a decision record.
5. No secrets touched; no network beyond an approved, sandboxed step; no live API.
6. Reversible: intake notes + decision records only.
