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
- Desktop bridge actions now exist for allowlisted window listing, active-window detection, focusing allowed windows, opening allowed local apps, and capturing repo-local desktop screenshots
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
- Safe repo-local executor now exists for an allowlisted set of actions only
- Runtime can now queue and execute in-scope read_file, write_file, append_file, create_artifact, list_directory, git_status, git_diff, and run_checker actions without exposing arbitrary shell execution
- Write actions and checker runs stay approval-aware, and executor results now persist with status, summary, and artifact-path visibility in task history
- Dashboard now shows executor tasks, lets the operator queue allowlisted repo-local actions, and lets approved in-scope executor tasks run manually from the console
- Dashboard now shows desktop bridge tasks, lets the operator queue allowlisted desktop actions, and shows persisted desktop execution results and screenshot artifacts
- Desktop bridge now includes narrow clipboard, hotkey, wait, and mouse actions for explicit local operator control
- Dashboard now exposes clipboard, hotkey, wait, mouse, and interrupted-task visibility for the desktop hand layer
- Ctrl+8 now acts as a local desktop failsafe that interrupts the current desktop macro task, persists the interruption, and requires operator review before re-queueing
- Focus-first terminal reuse is now enforced more clearly, reducing duplicate terminal-window spawning when an allowed terminal window is already open
- First reusable operator recipes now exist on top of the desktop hand primitives
- Dashboard now shows recipe tasks, per-step recipe history, and recipe interruption state
- The first narrow supervised Codex-to-ChatGPT handoff MVP now exists as an operator recipe with explicit source and target metadata, clipboard classification, and paste-only default behavior
- Dashboard task views now include recent and visibility filters so the operator can reduce task-history noise without deleting old tasks
- Codex-to-ChatGPT handoff now rejects terminal and PowerShell fallback targets at queue time and only allows explicit `codex` to `chatgpt` matching for that recipe
- Codex-to-ChatGPT handoff now blocks safely with manual target resolution required when the intended Codex or ChatGPT window cannot be resolved confidently
- Repeated identical blocked handoff payloads are now counted, reported clearly, and stopped after the second explicit operator-approved retry path instead of looping
- The dashboard handoff UI now exposes only Codex and ChatGPT targets for the handoff recipe and keeps paste-only as the default behavior
- Real-window Codex and ChatGPT handoff targeting now exists with deterministic candidate discovery and manual candidate selection for the current run
- The dashboard now exposes handoff target candidates, manual source and destination candidate selectors, and richer handoff detail for automatic vs manual matching
- Runtime, dashboard, and desktop checkers now cover real-window handoff target matching, safe ambiguity blocking, and manual target-selection metadata
- Compact chat handoff memory now exists at 14_context\chat_handoff_latest.md for new-thread continuity
- Repo integration classification now exists at 08_research\repo_integration_map.md
- Blueprint.am is now explicitly classified as external inspiration only, with a narrow internal hardware-builder-assist note under 08_research
- Ghoti now has a visible dashboard state cue for idle, active, waiting, approval-needed, interrupted, and resource-guard-triggered states
- Resource/process guardrails now exist for duplicate terminal and process pressure
- Desktop and recipe steps now stop after two failed attempts instead of retrying indefinitely
- Checker and recipe label text is now blocked from being pasted into terminals by the clipboard guard
- Desktop checker behavior is now safe-by-default and non-disruptive in sessions where Windows foreground control or screenshot capture cannot be verified
- Recent task evidence now shows bad terminal payloads being blocked while valid paste and allowlisted hotkey actions can succeed
- No task deletion flow exists, and task cleanup should continue to prefer filtering, archive-style visibility, and history retention
- No task should be deleted without the user's explicit approval
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
- Refresh Ghoti handoff memory first when chats get long, then use the new cue, resource guard, retry ceiling, and no-terminal-fallback handoff path as the base for the next real cross-window loop
- Real-window handoff targeting is now implemented for the current MVP
- Manual target resolution exists, but it is still current-run only and not yet remembered across runs
- The next practical step is live manual-assisted Codex and ChatGPT handoff testing with the new candidate picker, then deciding whether safe remembered target preferences are justified
- Improve operator-facing task filtering and recent views instead of adding any task deletion path
- Keep the operator stack swappable from the provider brain so later model changes do not require a rewrite
- Decide the next narrow desktop-control implementation path only if it directly supports the real handoff loop
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
- The safe repo executor is intentionally narrow and repo-bound; it is not a generic shell runner, desktop controller, or autonomy layer
- The desktop bridge is intentionally narrow and allowlisted; it is not arbitrary desktop control, click or type automation, clipboard orchestration, or a background daemon
- The new desktop hand layer is useful but still narrow; it only supports explicit allowlisted clipboard, hotkey, wait, and mouse actions, and it still has no freeform typing, drag-and-drop, or arbitrary UI-state inference
- The first operator recipe layer is intentionally small and still prototype-grade; the current handoff recipe is an MVP and is still being hardened for safe real-world use
- Window matching still depends on visible titles and allowed aliases, so some cross-window flows can remain brittle until the target set is tightened
- Terminal or PowerShell must not be used as a substitute target for Codex-to-ChatGPT handoff
- The handoff bugfix now blocks bad fallback paths safely, but real Codex and ChatGPT window resolution is still title-dependent and can still stop at manual target resolution
- Real Codex and ChatGPT window targeting is better, but remembered preferred target selection still does not exist
- Some focus-sensitive desktop actions still depend on what the current Windows session allows; in non-interactive checker sessions they may stop safely with manual-focus-required instead of pretending success
- Desktop screenshot capture can still be unavailable in some Windows sessions, so manual capture remains the honest fallback there
- Task history is large and noisy even after the first filter pass, and the operator console still needs better operator-facing filtering so stale failures do not crowd current work
- Third-party intake repos are valuable comparison material, but most of their surface area is still too heavy to adopt directly
