# Status Board

## Foundation
- [x] Workspace initialized
- [x] Git repository initialized
- [x] GitHub private repo connected
- [x] Continue local config working
- [x] Continue workspace rules active
- [x] Handoff files exist
- [x] Approval-system skeleton exists
- [x] Memory architecture skeleton exists
- [x] Runtime MVP sandbox exists
- [x] Runtime MVP checker passed
- [x] Council, workflow, and report scaffolding exist
- [x] Truth-council scaffolding exists
- [x] Publishability and access-control foundation exists
- [x] Curated repo intake layer exists
- [x] Provider adapter roadmap exists
- [x] Personal-ops scaffolding exists
- [x] Integration adapter foundation exists
- [x] GitHub write-action layer exists
- [x] Environment hardening and capability detection exist
- [x] GitHub remote smoke-test layer exists
- [x] Internship ops and career-ops intake layer exists
- [x] Showcase scaffolding and final reference repo intake exist
- [x] Browser control playground exists
- [x] Browser visible demo exists
- [x] Local dashboard MVP exists
- [x] Operator console v2 exists
- [x] Operator console v3 polish exists
- [x] Artifact UX and desktop bridge foundation exist
- [x] Supervisor and approval inbox foundation exist
- [x] Workspace boundary enforcement exists
- [x] Manual supervisor loop and task state controls exist
- [x] Safe repo-local executor exists
- [x] Safe local desktop bridge actions exist
- [x] Safe local desktop input, mouse actions, and Ctrl+8 failsafe exist
- [x] Operator recipes, repo integration map, and compact chat handoff memory exist
- [x] Ghoti visual cue, resource guard, retry limits, and clipboard guard exist
- [x] First supervised Codex-to-ChatGPT handoff MVP exists
- [x] Operator task-history filtering exists
- [x] Ghoti dashboard and CLI control center now exist
- [x] Ghoti visible operator stack with overlay, watchdog, and target marker now exists

## Current Control Layer
- Continue for local context/rules
- Codex for execution and Git workflow

## Current Branch
- feat/ghoti-visible-operator-stack

## Current Phase
- Real-window handoff targeting, wrong-active-window input blocking, the browser-local remembered candidate toggle, the Ghoti control center, and the visible operator stack are complete; the next step is manual validation and operator use of the clearer surface without widening the safety boundary

## Next Milestones
- manually validate real Codex and ChatGPT handoff with the new candidate picker
- manually validate that a foreground terminal or other wrong active window blocks Codex-to-ChatGPT handoff before any input
- manually validate that explicit terminal-targeted actions still work as intentional terminal actions
- use the dashboard control center, floating overlay, Operator Watchdog, and `ghoti-*` CLI commands as the first operator view during manual validation
- validate the new browser-local remembered candidate option for repeated Codex and ChatGPT handoff runs
- decide later whether anything broader than browser-local remembered candidates is justified
- tighten real Codex and ChatGPT target matching only if it reduces manual picks without unsafe guessing
- keep repeated junk payload retry handling capped at two attempts and visible to the operator
- validate the overlay/target-marker state transitions for idle, active, waiting, approval-needed, interrupted, and blocked work during real operator use
- decide later whether the watchdog should surface a cleaner usage-exhaustion handoff hint without becoming a daemon
- capture the OpenClaw patterns that fit later Ghoti channel, browser-assist, and long-running operator work without making it a hard dependency now
- improve operator-facing task-history filtering further only if stale failures still crowd current work
- test the safe repo executor manually from the operator console
- test the desktop bridge hand layer manually from the operator console
- test the workspace-boundary flow manually from the operator console
- test the manual supervisor loop from the operator console
- test the first reusable operator recipes from the operator console
- manually verify the new Ghoti cue, resource/process guard warnings, retry ceiling, and interrupted-task messaging
- design an explicit allowlist-expansion or workspace-override path later
- add a real notification channel later
- choose the real desktop-control implementation path
- evaluate Windows-Use and Windows-MCP
- optionally use the Playwright skill in Codex
- prepare one internship-facing live demo
- plan the live Notion adapter carefully
- keep browser and app execution for a later implementation step
- strengthen auth and access control

## Known Constraints
- Continue context fills quickly
- memory must stay compact
- avoid bloated or messy setup
- no live provider integrations yet
- no real browser or app execution yet
- no remote auth layer yet
- third-party repos are intake material only, not core project code
- no live mail or LinkedIn adapters yet
- no live Notion writes yet
- live remote GitHub mutation is possible in this environment, so approval discipline remains critical
- browser visible demo, artifact UX, desktop bridge foundation, supervisor inbox, and manual task-control loop now exist, but browser and app execution beyond the local playground are still research-only
- the safe repo executor is intentionally narrow and repo-bound, and it still is not a generic shell runner or full executor
- the desktop bridge is intentionally narrow and allowlisted, and it still is not arbitrary desktop control, freeform typing, drag-and-drop, or autonomous computer use
- some focus-sensitive desktop actions still depend on what the active Windows session allows, so manual-focus-required remains the honest fallback in some checker sessions
- desktop screenshot capture can still be unavailable in some Windows sessions, so manual capture remains the honest fallback there
- no task deletion flow exists, and old task noise should be handled through filtering, recent views, or archive-style visibility instead
- Codex-to-ChatGPT handoff is not allowed to fall back to terminal or PowerShell targets, although explicit terminal-targeted actions elsewhere remain valid
- if the same action or payload fails twice, Ghoti should stop retrying it and clearly report the problem
- the operator stack should stay separable from the provider brain so future model changes do not require a rewrite
- OpenClaw is now a major strategic reference, so new operator-core decisions should stay compatible with later OpenClaw-style channel and control-surface integration

## Last Reviewed
- 2026-04-11
