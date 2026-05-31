# N+6.8 — Fast Command-Center Dashboard + Local Analytics (SPEC ONLY)

Status: PLAN / SPEC ONLY. No dashboard view, endpoint, or analytics store is
built or enabled by this document. It defines the quality bar and the local-first
analytics contract a future N+6.8A milestone implements. Writing this spec takes
no live action.

Author lane: systems architect (planning lane)
Date: 2026-05-31

Existing surface this would extend (not modified here):
`01_projects/dashboard_mvp/server.js`, `01_projects/dashboard_mvp/public/index.html`,
`01_projects/dashboard_mvp/public/app.js`. This builds on the backlog direction in
`14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md`.

## Part A — Dashboard quality bar (how it should feel)

The command center is a utility, not a flashy web app. The target feel is
industrial-grade: instant, predictable, boring in the best way.

- **Fast.** View/page transitions feel instant; common actions have low
  input-to-response latency. Speed and reliability are the product.
- **Predictable.** The same action behaves the same way every time; no surprising
  slow paths under repeated use.
- **Low-friction.** Minimal visual noise; utility over decoration; the current
  task, last run, and last audit are visible at a glance.
- **Honest.** The UI shows real status from the vault/notes; it never displays a
  capability as "on" when it is not enabled.

Acceptance ideas for N+6.8A (to be made concrete then): a "command center" view
that reads the vault's CURRENT_TASK / CLAUDE_LAST_RUN / CODEX_LAST_AUDIT and the
wrapper run log, and renders them quickly with no external calls.

## Part B — Local analytics contract (local-first)

Analytics, if/when added, is **local-first** and privacy-preserving by
construction. This is the hard contract for any analytics work in the command
center.

### Hard constraints

- **Local-only by default.** No external telemetry, no third-party analytics, no
  network beacon. Nothing leaves the machine without explicit human approval.
- **no secrets, no PII.** Never store tokens, credentials, cookies, file
  contents, prompts, or personal data. Metrics are counts and durations, not
  content.
- **Inspectable + reversible.** The store is a plain local file a human can read.
  Deletion and export are **human-approved** manual actions.
- **Opt-in for anything outbound.** Export off the machine is a deliberate,
  manual, approved step — never automatic.

### Metrics to track locally (counts/durations only)

| Metric | What it measures | Why |
|--------|------------------|-----|
| page/view transitions | navigation events + timing | dashboard speed |
| command usage counts | which CLI/launcher commands ran | what's used |
| feature usage counts | which dashboard features are opened | what's used |
| wrapper runs | which Hermes wrappers ran, run vs dry-run | coordination visibility |
| validation durations | how long test/validation passes take | regressions in speed |
| error counts | how often actions error | reliability |
| task completion / task failure | pass vs fail counts per task | throughput |
| blocked reasons | why a task was blocked (category, not content) | recurring friction |
| model routing | which model handled which class of task | routing sanity |
| manual token/cost notes | human-entered cost notes | budget awareness |

All of these are non-sensitive aggregates. None requires storing user content.

### Storage

- **Phase 1:** append-only local **JSONL** at a proposed path
  `01_projects/dashboard_mvp/runtime_data/analytics/<date>.jsonl` (gitignored
  runtime data; not committed). One event per line.
- **Phase 2 (optional, later):** a local **SQLite** file for queries, only if the
  JSONL volume warrants it — still local-only, still human-deletable.

### Event record (schema)

```json
{
  "ts": "2026-05-31T00:00:00Z",
  "kind": "view | command | wrapper | validation | error | task | routing | note",
  "name": "string",
  "ms": 0,
  "ok": true,
  "count": 1,
  "local_only": true
}
```

`local_only: true` is required on every event. The writer refuses to emit an
event that would carry content, a secret, or PII.

## Audit checklist for N+6.8A (what Codex verifies)

1. Analytics writer is **local-first**: writes only to the local runtime-data
   path; makes no network call.
2. **no secrets, no PII**, no content — only counts/durations/names from a fixed
   allow-list of event kinds.
3. The store is gitignored runtime data, not committed; deletion/export are manual
   and human-approved.
4. The dashboard view renders from local sources only; no external telemetry.
5. UI shows honest status (nothing claimed "on" that is not enabled).
6. Reversible: a view + a local writer + tests; trivially revertable.
