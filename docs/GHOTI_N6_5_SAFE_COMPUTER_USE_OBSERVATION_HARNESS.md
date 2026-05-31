# Ghoti N+6.5 Safe Computer-Use Observation Harness

## Purpose

N+6.5A adds a tiny local fixture harness for future computer-use planning. It
lets Ghoti read a mocked observation packet, summarize it, identify local
entities, and propose next steps that require human approval.

## Scope

- Reads a repo-local JSON fixture.
- Validates fixture shape.
- Emits deterministic JSON.
- Reports that the run is observation-only.
- Marks human approval as required.

## Non-Goals

- No live browser control now.
- No Chrome launch now.
- No Apple live visit now.
- No click/type.
- No live website scraping.
- No accounts, login, cart, purchase, payment, or credential handling.
- No CAPTCHA, cookie, bot, or cloak bypass.
- No external telemetry.

## Local Fixture Mode

Run:

```powershell
python 03_scripts/safe_computer_use_observation_harness.py --fixture 14_context/computer_use/fixtures/apple_mac_compare_fixture.json --json
```

The current fixture is a mock Apple Mac comparison. It is not product truth and
must not be used as a live buying recommendation.

## Approval Gate

The only allowed loop is:

1. Observe local fixture.
2. Interpret the local fixture.
3. Propose next actions.
4. Require human approval before any real-world step.

The forbidden loop is:

1. Observe.
2. Click, type, or control a browser automatically.

## Safety Boundaries

The harness output must report:

- `browser_opened: false`
- `live_network_used: false`
- `clicked_or_typed: false`
- `requires_human_approval: true`

## Future Roadmap

- N+6.6: Hermes wrappers for safe local fixture routing only.
- N+6.7: tool intake for observation harness candidates.
- Later audited milestones: browser/computer-use observation only after
  explicit approval, local logging, rollback, and strict per-action consent.
