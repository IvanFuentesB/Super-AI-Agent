# ActionIntent Demo Run Summary

Run id: `20260426_204756`
Status label: `contract_created / local_demo_only / not_external_adapter_wired`
Timestamp: `2026-04-26T20:47:58Z`

## Stats

- Proposed: 5
- Approved: 4
- Blocked: 1
- Consumed: 4

## Intent Outcomes

- `memory-agent` -> `update_compact_memory` -> **CONSUMED** (risk: low)
- `token-saver-agent` -> `write_local_artifact` -> **CONSUMED** (risk: low)
- `browser-candidate-agent` -> `external_adapter_execution_without_approval` -> **BLOCKED** (risk: blocked)
- `ruflo-review-agent` -> `propose_next_step` -> **CONSUMED** (risk: low)
- `implementation-planner-agent` -> `summarize_local_file` -> **CONSUMED** (risk: low)

## Approval Gate Truth

- Low-risk local actions auto-approved by `local-demo-auto-approver`.
- Forbidden action `external_adapter_execution_without_approval` blocked by policy gate.
- Blocked intents are never consumed or executed.
- Execution performed: NO (all consumed intents get result_status=local_demo_no_execution).
- External adapters: NOT wired. `browser-candidate-agent` action blocked by classify_action.

## Adapter Descriptors

- `native-demo-adapter` — status: `contract_ready_disabled` — external: False
- `autobrowser-reference` — status: `research_only` — external: True
- `ruflo-reference` — status: `research_only_security_blocked` — external: True
- `obscura-reference` — status: `research_only_tos_risk` — external: True

## Shared Memory Current Priorities

- Prove native multi-agent coordination with compact memory.
- Build ActionIntent and CapabilityAdapter before external adapters.
- Implement ActionIntent and CapabilityAdapter before external tool integration.
- Use compact file-based memory instead of repeating giant context.
- Keep each agent job narrow and artifact-backed.

## Audit Log

- Path: `05_logs\action_audit.jsonl`

## Run Artifacts

- Intents JSON: `05_logs\action_intent_runs\20260426_204756\action_intents.json`
- Run dir: `05_logs\action_intent_runs\20260426_204756`
