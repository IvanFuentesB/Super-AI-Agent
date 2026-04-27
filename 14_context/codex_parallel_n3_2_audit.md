# Codex Parallel N+3.2 Audit

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD observed by Codex lane: 87357f1
Status label: parallel_audit_only / no_runtime_changes / not_runtime_wired

## Scope

This is a parallel Codex audit lane for N+3.2. It intentionally avoids runtime Python, dashboard server code, current state docs, next-action docs, finish-line log, token-saving plan, computer-use strategy note, and prompt files because Claude Code may be implementing runtime work in parallel.

Files intentionally edited by this lane are limited to:

- `14_context/codex_parallel_n3_2_audit.md`
- `14_context/tool_intake_new_candidates_n3_2_codex.md`
- `14_context/loc_count_crosscheck_n3_2_codex.md`
- `14_context/computer_use_candidate_ranking_n3_2_codex.md`

## Repo Truth Observed

- Branch: `feat/ghoti-visible-operator-stack`
- Current HEAD during this lane: `87357f1 docs/verification milestone N+3.2-obscura - record source build and CDP smoke`
- No staged files were present when checked by Codex.
- Dirty or untracked files existed before this Codex lane and were left untouched, including dashboard/runtime work and local-only artifacts.
- `14_context/ghoti_code_line_count_report.md` exists and reports the Claude N+3.2 LOC count.

## Current Known Ghoti Status

- N+3.0 added a native multi-agent MVP and compact memory artifacts.
- N+3.1 added ActionIntent, CapabilityAdapter-style contracts, action audit logging, and an action demo.
- External operator candidates are still research/reference unless explicitly wired later.
- RUFLO, AutoBrowser, and Obscura have been evaluated or partially verified as external candidates, but none is approved as a Ghoti runtime dependency.
- Gemma/Ollama remains diagnostic/status unless explicitly wired under future gates.
- Browser overlay remains browser-based, not native always-on-top.
- Capture gallery means local screenshots, not automatic AI screen sharing.

## What Claude Code N+3.2 Should Implement

Minimum expected runtime slice:

- A local wait/resume JSON state file exists.
- Default waits are seeded with useful blockers such as approval needed, credits/auth needed, external install approval needed, model missing, and manual review needed.
- A direct local script can print pending, ready, and blocked waits without dashboard dependency.
- Dashboard read route exists, or dashboard integration is explicitly deferred with a reason.
- LOC report exists and states tracked-file counting rules.
- Tool intake includes computer-use and tool candidates such as CUA/TryCUA, LTX, Shannon, Proxima, LibreChat, ComfyUI, AnythingLLM, Perplexica, and Open WebUI.
- No external runtime wiring occurs in N+3.2.
- No autonomous external actions occur in N+3.2.

## Wait/Resume Supervisor Acceptance Criteria

The design is sufficient only if all of these are true:

- Wait items are durable across process exits.
- Each wait item has an id, title, status, blocker type, created time, last updated time, owner, resume condition, and next operator action.
- Statuses are explicit and finite, for example `pending`, `ready`, `blocked`, `resolved`, and `cancelled`.
- The system can show waits without executing them.
- The system never marks a wait ready because of time passing alone unless the readiness condition is actually checked.
- Runtime output distinguishes "blocked by user approval" from "blocked by auth/credits" from "blocked by missing tool/model".
- Resuming a wait does not bypass ActionIntent approval or manual gates.
- Read-only dashboards and scripts do not silently create execution side effects.
- State writes are local, bounded, and gitignored if they are runtime data.

## Risks In Wait/Resume Supervisor

- False-ready states could make the operator think a task is safe when the blocker is unresolved.
- Hidden retries could turn "wait" into background automation.
- Stale waits could accumulate and create misleading operator pressure.
- Dashboard and CLI/script read models could drift if they parse different state shapes.
- A future resume action could accidentally bypass ActionIntent approval if not bound to action type and payload.
- Runtime JSON files could be accidentally staged if git hygiene is not enforced.
- Credit/auth waits can become ethically risky if framed as cap bypass instead of normal user-side availability.

## How This Reduces User Babysitting

A good wait/resume supervisor lets the user stop sitting in the loop while a tool waits for a human-only condition. The key is that Ghoti should record why work paused, what evidence is needed to resume, and what should happen next. It should not poll paid services aggressively, work around account limits, or take actions while the user is absent.

Useful wait categories:

- `operator_approval_required`
- `auth_required`
- `credits_or_quota_unavailable`
- `tool_install_approval_required`
- `model_missing`
- `external_service_review_required`
- `manual_review_required`
- `unsafe_or_out_of_scope`

## What It Must Not Do

- No autonomous outreach, posting, messaging, purchases, trades, filings, or external account actions.
- No provider cap, quota, subscription, or credit bypass.
- No hidden browser, desktop, or shell workers.
- No external service connection without explicit approval.
- No computer-use adapter execution outside ActionIntent and CapabilityAdapter gates.
- No staging of runtime data, screenshots, Playwright traces, output folders, CV documents, or third-party repo artifacts.

## Support For Many Agents Working In Parallel

The wait/resume model should help multiple local agents coordinate without creating chaos:

- Each agent should publish a small wait item instead of blocking the whole run.
- Shared memory should store compact summaries, not pasted transcripts.
- Supervisor summaries should report which agents are ready, blocked, or complete.
- Every agent should have a narrow role and one next action.
- A wait item should point to exact files/artifacts instead of embedding large context.

## Support For Future Computer-Use Adapters

Wait/resume is a prerequisite for safer computer use because it gives Ghoti a place to stop before consequential actions.

Future computer-use adapter waits should include:

- screenshot consent missing
- target app/domain not allowlisted
- sensitive app blocked
- ActionIntent approval missing
- payload hash mismatch
- operator kill switch triggered
- adapter health unavailable
- sandbox not ready

## Legal Token Saving

Allowed token/context-saving patterns:

- compact memory
- resumable handoffs
- short role-specific artifacts
- bounded summaries
- file references instead of pasted blobs
- fresh-session checkpoints
- local diagnostic summaries

Forbidden patterns:

- provider quota or cap bypass
- fake accounts
- hidden manipulation of provider limit state
- credential/session abuse
- using local models to evade safety or law

## Recommended N+3.3 After Claude Finishes

Recommended: implement a local-only wait/resume dashboard read panel and a safe local "resume candidate" report that produces proposed next steps without executing them.

Reason: it converts wait/resume from backend state into a visible operator workflow while preserving manual approval gates. If Claude already lands dashboard read support in N+3.2, then N+3.3 should instead build the first sandbox-only CapabilityAdapter demo that writes a local artifact and proves ActionIntent approval binding end to end.
