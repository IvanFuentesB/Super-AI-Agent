# Native developer harness and optional local evaluation

This is the accepted first-party source subset from local commit
`890b48c2380f5d43b3c89a7ecec3381ca6b2116d`, published without its private run
receipts, transcripts, graphs, upstream checkout, dependency trees or Git history.
It does not replace Hermes, canonical memory, approvals, Paperclip or the running host.

## Included behavior

- Five reusable project-scoped native roles and a concurrency cap of three.
- Read-only readiness validation of project roles plus a caller-supplied filtered
  native configuration/model receipt. Configured is a snapshot; automatic role
  selection remains unproved and is never reported true by this validator.
- A bounded OpenJarvis evaluation adapter whose public live-inference path stays
  disabled, including when `--enable` is supplied. Recording tests reject foreign
  endpoints, cloud aliases, redirects, credentials and oversized/budget-exceeding work.
- Bounded arithmetic tool source, synthetic transport tests and native-protocol
  receipt tests. No background service, canonical-memory writer or model pull.

## Setup and validation

Python3.11+ is required. Use an existing reviewed environment rather than installing
anything globally. Optional dependency source: official
https://github.com/open-jarvis/OpenJarvis at
`e97088f199cf86ea5f78de921772357d1f0d2cec` (OpenJarvis1.0.0, Apache-2.0).
The tested pilot used its separate reviewed environment with httpx and MCP support.
No third-party implementation is vendored here. No fresh installation or live
inference is authorized by publishing these files.

From this `harness` directory, using that environment:

```text
python -B -m unittest discover -s tests -v
python -B openjarvis_adapter.py
python -B scripts/native_role_readiness.py --project-root PROJECT --receipt FILTERED_RECEIPT.json --json
```

The default adapter must report disabled. The readiness command reports pending
when real matching metadata is absent; do not publish private host receipts to
make it configured. Native-protocol flags were tested with retained client
0.167.0-alpha.4.1; confirm compatibility before using a different installed client.
If a config probe is separately authorized, give it an explicit new `--output`
outside source/config directories in the approved runtime evidence area.

Review role files before copying them into an ordinary project. Preserve existing
roles, model/sandbox/approval settings and user-owned project trust. The nested
`.codex` directory applies only to this component when opened and trusted; it does
not enable the repository root or change global defaults. Existing MCP/hook and
memory ownership is unchanged. Do not create a second orchestration controller.

## Acceptance and adoption boundary

Prior source acceptance recorded70 offline tests and independent review of the
readiness fixes. Publication tests and candidate-bound integration review are
recorded in the PR, separately from prior receipts. No comparative performance
advantage or NOVA host adoption is inferred from those results. Hermes must
separately establish cloud-disabled local inference and review adoption before
any live path can be introduced. Local source publication does not approve that step.

Rollback: revert the containing source-publication commit. For a manually copied
project role set, restore only that project's recorded preimage; never reset
global configuration or remove another owner's roles. No installed service is
changed by this source subset.
