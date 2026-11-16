# NOVA Command Center browser implementation

This draft publishes the actual browser assets and local tests. It does not publish
the unrelated historical development branch, an installed runtime, or live memory.

## Provenance and review

- Clean publication base: `9e6a5987f617da443f0f802cb82d3a4a291117a3`.
- Original UI parent: `e108378c6aea726a4160b70e1549f5f06ab70e52` (scoped independent source/GET-preview PASS).
- Published source snapshot: `9ad5a3938d4762e28a8e684b2637d8eae2b6fb7f` (independent CHANGES_REQUESTED).
- Static assets and existing tests are exact Git blobs from that snapshot.
- The retained independent regression file changes only its project import path.

Implemented: seven-view navigation, local chat and bounded Computer UI clients,
status/approval/verification presentation, keyboard focus, responsive layout,
runtime observation views and unavailable/stale fallbacks. These clients require
the separately reviewed local runtime contract. Current main does not yet contain
those runtime producers; this component must not be presented as a complete
installed app or as a backend deployment.

## Known defects: do not merge or deploy this draft

1. A pending Stop and a running poll after a failed Stop can lose unresolved
   cancellation visibility in navigation/progress. A running poll is not an acknowledgment.
2. A top-level free-text reason can override the structured unverified-success
   warning and claim verified completion without SUCCESS evidence.
3. Identical Paperclip refresh writes the same state attribute (minor DOM churn).

The independent review executed 99 affected existing tests successfully and four
additional regressions with one PASS and three expected RED failures. The owner
separately reported 103 Node/6 markup passes and 14 failing old-snapshot reproductions;
those are not additional independent passes. The publication rerun is recorded in
the PR; do not infer a green result from test collection or a completed process.

## Local checks (no provider, installation or account action)

From `01_projects/ghoti_os_app`:

```sh
node --test tests/test_computer_client.js tests/test_computer_render.js tests/test_daily_chat.js tests/test_daily_journeys.js tests/test_daily_shell.js tests/test_local_session.js tests/test_runtime_observations.js tests/test_runtime_service_worker.js tests/test_state_honesty.js
python -B -m unittest discover -s tests -p test_daily_markup.py
node --test tests/test_review_state_regressions.js
```

The last command deliberately retains the unresolved product assertions; at this
snapshot it fails three of four cases. Do not weaken them to make this draft green.
The optional browser-form test requires an already-installed Playwright module
(`GHOTI_BROWSER_TEST_MODULE`) and Edge; no dependency or model is downloaded by
these commands. Browser fixtures are not installed/native execution evidence.

## Safety and installation boundary

No backend/serverless routes, provider credentials, connectors, hooks, MCPs,
computer-use executor, runtime data or service startup are enabled by publication.
The UI defines local API requests but cannot supply their authentication/authority.
Do not expose a local command API publicly or deploy this as a public action UI.
The current runtime's optional Paperclip status contract remains a separate adoption
step; missing status is unknown, not a stopped or zero-approval board.

Project artwork provenance is in `dashboard_app/static/assets/GHOTI_FISH_ASSET_ORIGIN.md`.
The original source commits are provenance identifiers, not promises that their
unrelated histories are published or approved. No change to the installed release
is authorized by this draft.
