# Implementation Planner Agent (implementation-planner-agent)

- Status: done
- Task: Create the next coding milestone plan for ActionIntent and CapabilityAdapter.
- Proposed next milestone: native ActionIntent state, approval binding, payload binding, audit trace.
- No external adapter execution yet.
- Supporting notes:
  - Ghoti should own the safety contract. External tools can become adapters only after they fit Ghoti's approval, audit, and local-control model.
  - - `ActionIntent` schema with action type, target, payload hash, risk level, source observation, and expiry.
  - - `CapabilityAdapter` interface for future browser, desktop, repo, content, inventory, and research adapters.
  - - Approval creation path that binds approval to action type + payload hash.
  - - Approval consumption path that rejects replay, mismatched payloads, expired approvals, and wrong adapter IDs.
  - - Audit trace entry for every observation, proposal, approval, rejection, consumption, adapter call, and result.
  - - Required approvals:
  - - navigation/click/type/submit require explicit approval.
  - - login/auth profile save/reuse require high-risk approval.
