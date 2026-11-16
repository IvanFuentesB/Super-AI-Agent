# NOVA Command Center browser implementation

This component publishes browser assets and local tests, not an installed
runtime, private memory or an unrelated historical branch. It integrates the
accepted correction through existing PR #24, IvanCX/nova-ui-publication.

## Source identity and independent review

- Original scoped UI source: e108378c6aea726a4160b70e1549f5f06ab70e52.
- Earlier successor: 9ad5a3938d4762e28a8e684b2637d8eae2b6fb7f; its original
  CHANGES_REQUESTED verdict and failing evidence remain historical facts.
- Corrected successor: 6541093494d223e6c8f587116b1ba70af8cb63f6, parent 9ad5a39.
- Five selected correction files are exact raw Git blobs from 6541093. The
  owner's duplicate four-case regression file is omitted: the existing public
  test_review_state_regressions.js keeps the same assertions without duplication.
- Independent technical/source and targeted synthetic browser verdict: APPROVED
  for this correction and five-file port. No installed/native acceptance implied.

Stop intent becomes unresolved before transport and remains bound to task and
generation through failed requests and running/stopping/terminal polls. Only
same-task stopped plus cancellation_confirmed:true clears it. Succeeded wording
uses structured verification SUCCESS; other prose is labelled Reported. Identical
Paperclip state no longer rewrites its attribute, including the failure path.

## Executed checks

Independent reviewer: 68 affected/retained Node checks plus two additional
negative cases, all PASS. Isolated browser checks passed pending/failed Stop,
structured verification, identical polling/focus, stale HTTP503 and Chat/Computer
at 320/1280 without overflow or page/console errors. Only frozen assets and
synthetic responses were used; real account/runtime requests were blocked.

The main-based public port separately passed 120 Node tests, six markup tests
and changed-JS syntax checks. These scopes are not added together. Original
retained assertions remain unchanged. The one owner expectation that displayed
Running after failed Stop was strengthened to Stop unconfirmed, matching the
reported defect rather than weakening the contract.

From this directory, with already-installed Node/Python:

```sh
node --test tests/test_computer_client.js tests/test_computer_render.js tests/test_state_honesty.js tests/test_review_state_regressions.js tests/test_paperclip_state_churn.js tests/test_daily_journeys.js tests/test_daily_shell.js tests/test_daily_chat.js tests/test_local_session.js tests/test_runtime_observations.js tests/test_runtime_service_worker.js
python -B -m unittest discover -s tests -p test_daily_markup.py
```

Optional browser-form checks require an existing Playwright module and Edge;
no model, package or browser is downloaded by these commands.

## Runtime and adoption boundary

These clients require separately adopted local authentication, authority and
runtime producers. Main does not yet supply the complete ghoti_os_app server or
the private Paperclip observation producer. Missing API/status must remain
unavailable/unknown, never proof of stopped or zero approvals. Actual installed
producer source was inspected; synthetic positive states are not live evidence.

No computer-use executor, backend/serverless route, provider credential,
connector, hook, MCP, service startup or host adoption is enabled here. Do not
expose local command APIs publicly or deploy this as a public action interface.
The original source commits are provenance, not published historical Git ancestry.
Installed release 9613e877 is unchanged by this source integration; Hermes owns
adoption and any authenticated/native acceptance. Existing artwork provenance
remains in dashboard_app/static/assets/GHOTI_FISH_ASSET_ORIGIN.md.
