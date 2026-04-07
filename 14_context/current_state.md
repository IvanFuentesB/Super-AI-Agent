# Current State

## Project
Super AI Agent

## Goal
Build an execution-first AI control system for legitimate business, documentation, research, and owned-account workflows, using approval gates, durable memory, handoff files, and future multi-model orchestration.

## Canonical Workspace Root
C:\Users\ai_sandbox\Documents\AI_Managed_Only

## Current Status
- Base Windows toolchain mostly working
- Local Git repo is initialized and pushed to the private GitHub repo Super-AI-Agent
- Continue local config is working and workspace rules are being picked up
- Durable handoff files exist in 14_context
- Runtime MVP exists with approval-aware lifecycle support
- Council, workflow, and report scaffolding now exist
- Truth-council scaffolding and publishability/access-control docs now exist
- Runtime includes planning-only truth and publishability utilities
- Curated repo intake area exists under 21_repos/third_party
- First-wave third-party repos are cloned locally for evaluation only
- Career-ops and related reference repos are now cloned locally for evaluation
- Official Claude Code and OpenClaw are now cloned locally for evaluation and reference
- Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, and official Playwright are now cloned locally for evaluation and reference
- Provider adapter roadmap now exists
- Integration adapter foundation now exists
- GitHub live read-only adapter now exists
- GitHub draft generation now exists
- Approval-gated local branch, remote issue, and remote PR actions now exist
- Environment detection now exists
- Capability summary now exists
- gh is available on PATH and authenticated in the current runtime environment
- Remote GitHub smoke-test capability now exists
- Explicit approval is still required before any live remote GitHub mutation
- Default checker behavior remains non-mutating even though remote smoke actions are possible
- Mail and Notion planning adapters now exist
- Scoped core publishability scan now exists
- Remote access and auth plan now exists
- Public repo split strategy now exists
- Owned-account personal-ops scaffolding now exists
- Mail, LinkedIn, CV, and outreach workflow packs now exist as scaffolds
- Internship application pack scaffolding now exists
- Showcase case-study and portfolio page scaffolding now exist
- Browser executor research docs now exist
- Browser control playground now exists
- Playwright-based local smoke test now exists
- Browser playground now has a visible headed demo mode
- Local operator-console-style dashboard now exists
- Dashboard now has a cleaner Operator Console V3 UX with clearer action feedback, less clutter, and less visually dominant raw details
- Dashboard can trigger safe local scaffold generation
- Dashboard can trigger local browser demos
- GitHub status and scaffold generation are accessible through the dashboard
- Artifact UX is improved and the dashboard can preview, open, and reveal generated artifacts
- Desktop bridge foundation now exists with safe local status and checker support
- Always-on supervisor foundation now exists
- Approval inbox foundation now exists
- Local-only notification abstraction now exists
- Dashboard now exposes supervisor status, pending approvals, and human-needed task state
- Allowed-root workspace policy now exists with C:\Users\ai_sandbox\Documents\AI_Managed_Only as the default allowed root
- Runtime now classifies task targets as in-scope, out-of-scope, or no-path-detected
- Out-of-scope targets are blocked by workspace policy and surfaced clearly in approval and human-needed views
- Dashboard now shows workspace scope, workspace policy, and readable workspace-block reasons for approval items
- Manual supervisor loop now exists for queued, pending_approval, blocked_human_needed, waiting, ready_to_resume, and completed task states
- Dashboard now lets the operator inspect stopped tasks, review human-needed work, resume waiting tasks, and re-queue ready-to-resume tasks manually
- Task history is now persisted and visible for key events such as created, escalated, approved or denied, deferred, blocked, resumed, and completed
- No live external provider APIs yet
- No real browser or app executor beyond the local playground yet
- No remote auth layer yet
- Remote GitHub issue and PR execution still depends on gh presence and auth
- No live mail sending adapter yet
- No live LinkedIn posting or edit adapter yet
- No live Notion writes yet
- No real external notification channels yet
- Future outbound actions still require approval
- Third-party repos remain reference-only, not core project code
- Leak or extraction repos remain excluded from the core foundation
- Claw Code remains temporary reference, not foundation

## Immediate Focus
- Test the workspace-boundary flow manually from the dashboard
- Test the manual supervisor loop from the dashboard
- Decide the real desktop-control implementation path
- Keep GitHub remote actions explicit and approval-gated
- Prepare one internship-facing live demo from the current runtime outputs
- Keep browser and app execution beyond the local playground in research until the control boundary is clearer

## Current Risk / Constraint
- Continue session context still fills quickly
- Runtime behavior still depends on the actual shell seeing the expected tool/auth state
- Live remote GitHub mutation is now possible, so approval discipline matters more than before
- Browser and app execution are still mostly research-only, even though the operator console and visible demo now make the current step easier to inspect
- Browser and app execution are still mostly research-only, even though the operator console now makes artifacts more usable and exposes the desktop bridge foundation
- The supervisor, approval inbox, and manual task-control loop are still local-only foundations, not a full autonomous executor yet
- Workspace policy blocks out-of-scope targets cleanly now, but there is still no explicit allowlist expansion flow yet
- Third-party intake repos are valuable comparison material, but most of their surface area is still too heavy to adopt directly
