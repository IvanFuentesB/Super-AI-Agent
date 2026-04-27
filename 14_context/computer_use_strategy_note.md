# Computer Use Strategy Note

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: strategy_note / not_runtime_wired / N+3.1

## Current Status

- Claude computer use exists as a current capability in the Claude ecosystem.
- Ghoti is NOT using it yet.
- No external browser or desktop adapter is wired or executing in this milestone.
- This note defines the evaluation and safety gate framework for future adoption.

## Why ActionIntent First

Computer use is a powerful but inherently risky capability class. Before wiring any
computer-use adapter, Ghoti must have:
1. A native ActionIntent contract that models proposed actions.
2. A CapabilityAdapterDescriptor for each candidate adapter.
3. An audit trail that records every proposed and consumed action.
4. An approval gate that requires explicit operator consent for non-local actions.

N+3.1 delivers items 1–4. Only after these are validated should adapter integration begin.

## Required Safety Gates for Any Future Computer-Use Adapter

Before ANY computer-use adapter may be enabled in Ghoti:

- **Screenshot consent**: Operator must explicitly enable screen capture per session.
- **Allowed app/domain list**: Only pre-approved apps and domains may be targeted.
- **No sensitive apps**: Banking, email, password managers, system admin tools are blocked.
- **Pause/kill switch**: Operator must be able to halt execution immediately (Ctrl+8 or equivalent).
- **Approval before click/type on external systems**: Every external action requires an ActionIntent with approval.
- **Audit trace**: All proposed and consumed computer-use actions must be logged.
- **Visible overlay/state**: The overlay must show the current adapter, target, and action in real time.
- **No credentials without explicit approval**: No credential entry, form fill, or auth token use without per-intent approval.
- **Payload-hash binding**: The approved payload must match the consumed payload exactly.

## Candidate Adapters

| Adapter | Status | Notes |
|---------|--------|-------|
| Claude computer use (Anthropic) | `descriptor_only` | Native Claude capability; appropriate for supervised, approval-gated UI control. Evaluate after ActionIntent gate is validated. |
| AutoBrowser | `best_next_external_browser_candidate` | Strong alignment with supervised browser control; good sandboxing posture. Best candidate for first external browser adapter. |
| Browser Use | `research_only` | Promising architecture but needs isolated review before runtime wiring. |
| Playwright | `local_playground_only` | Already in local browser playground. Deterministic. Current safe fallback for local browser tests. |
| OS-level desktop bridge | `local_prototype` | Narrow allowlist desktop bridge exists. Not a computer-use adapter yet; suitable only for explicit clipboard/hotkey/window actions. |

## Evaluation Order

1. Validate ActionIntent + CapabilityAdapter contracts (N+3.1, this milestone).
2. Run the local demo to confirm gating logic works.
3. Design the CapabilityAdapterDescriptor and ActionIntent policy for the first external adapter.
4. Propose adapter integration as a separate milestone with explicit user approval.
5. Evaluate AutoBrowser first (best safety/capability tradeoff of the candidates).
6. Claude computer use is a future step after at least one external adapter is validated.

## Adapter Preference Rationale

Prefer more precise tools first:
1. MCP/server APIs (most precise, narrowest blast radius)
2. Shell / repo-local actions (already implemented)
3. Browser-specific tools like AutoBrowser or Playwright (narrow, observable)
4. Broad computer use / OS-level desktop control (widest blast radius — last resort)

## What Is NOT Allowed Without Full Safety Gate

- Running AutoBrowser, Browser Use, Claude computer use, Playwright, or OS-level desktop control outside of approved ActionIntent flow.
- Clicking, typing, or submitting forms on external services without per-intent approval.
- Capturing screenshots autonomously without operator-enabled session.
- Storing or forwarding credentials without explicit per-intent approval.
- Taking automated actions on owned accounts (social, email, banking) without approval.

---

## N+3.2 Update — TryCUA/CUA Driver + External Claude Computer Use

Date: 2026-04-27
Status label: strategy_note / not_runtime_wired / N+3.2

### Claude Computer Use (External)

Claude computer use exists as a live Anthropic capability (e.g., via the Anthropic API's
`computer_use` tool type). Ghoti has NOT wired it. No computer-use tool calls have been
made. This note exists to track the decision path.

### TryCUA / CUA Driver

TryCUA and its companion CUA Driver are candidate frameworks for structured
computer-use/operator capability. Key properties:

- Execute UI actions (click, type, screenshot) via a controlled agent loop.
- API-style action dispatch: fits naturally with Ghoti's ActionIntent gate pattern.
- Must be evaluated in a fully sandboxed environment before any live use.

**Ghoti gate before any TryCUA/CUA Driver wiring:**

1. Propose an ActionIntent for each UI action.
2. Wait for explicit operator approval per intent.
3. Consume exactly the approved payload — no payload mutation.
4. Write a full audit trace entry per action.
5. Expose status via dashboard read route.
6. Stop immediately on mismatch, replay attempt, or risk escalation.
7. Run only in a local sandbox / controlled VM until explicitly promoted by operator.

**Never:**
- Live account access before sandbox gate is passed.
- Full desktop autonomy without per-intent approval.
- Stealth operation or background autonomous loops.

### Browser-Specific Adapters First

Browser-specific adapters (AutoBrowser, Obscura CDP) remain lower blast-radius
than full desktop control. They are still pending approval — but they are the safer
path to test the ActionIntent gate before escalating to full TryCUA/CUA Driver.

### Runtime Status (N+3.2)

No computer-use adapter is runtime-wired. TryCUA/CUA Driver is in the wait/resume
queue (see `14_context/tool_intake_new_candidates_n3_2.md`) pending operator approval
and sandboxed evaluation.
