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
- Provider adapter roadmap now exists
- Integration adapter foundation now exists
- GitHub live read-only adapter now exists
- GitHub draft generation now exists
- Approval-gated local branch, remote issue, and remote PR actions now exist
- Mail and Notion planning adapters now exist
- Scoped core publishability scan now exists
- Remote access and auth plan now exists
- Public repo split strategy now exists
- Owned-account personal-ops scaffolding now exists
- Mail, LinkedIn, CV, and outreach workflow packs now exist as scaffolds
- No live external provider APIs yet
- No real browser or app execution yet
- No remote auth layer yet
- Remote GitHub issue and PR execution still depends on gh, which is unavailable in this shell today
- No live mail sending adapter yet
- No live LinkedIn posting or edit adapter yet
- No live Notion writes yet
- Future outbound actions still require approval
- Claw Code remains temporary reference, not foundation

## Immediate Focus
- Standardize gh availability for explicit GitHub remote actions
- Refine safe GitHub write behavior without adding destructive actions
- Deepen mail and Notion planning without enabling unsafe actions
- Keep LinkedIn planning-only until approval and adapter boundaries are clearer
- Strengthen auth, access control, and publishability without bloating the core

## Current Risk / Constraint
- Continue session context still fills quickly
- Python works through a resolved local interpreter, but not via a clean python PATH yet
- gh is not currently available on PATH in this execution environment
