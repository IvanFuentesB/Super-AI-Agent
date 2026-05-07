# Codex N+3.14 Next Claude Implementation Prompt Review

Status: codex_parallel_audit / prompt_review_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Recommended Claude Code Options

### Option A — N+3.14 Claude: Local Gemma Brain Router Preview

Rank: 1

Goal:

- Add config/policy docs and one CLI preview that routes safe local task descriptions to recommended brains.
- Use Gemma only for a tiny approved/local summary smoke if needed.
- Do not add broad runtime automation.
- Do not trigger CUA/browser/live actions.

Why this is best:

- Gemma3:4b is now pulled and smoke-passed in the Claude lane.
- This immediately reduces API-credit usage for easy work.
- It does not require another big install.
- It creates the policy bridge toward many agents.

Suggested files:

- `23_configs/local_brain_task_policy.example.json`
- `23_configs/brain_routing_policy.example.json`
- `20_agents/worker_card_registry.example.json`
- maybe `01_projects/runtime_mvp/src/super_ai_agent/brain_route_preview.py` if Claude is explicitly in implementation lane
- docs under `14_context/`

Constraints:

- Preview-only.
- No autonomous dispatch.
- No CUA execution.
- No external API.
- No git push without validation.

### Option B — N+3.14 Claude: Paperclip Isolated Install Plan

Rank: 2

Goal:

- Read cloned Paperclip source.
- Create install checklist.
- Map Paperclip concepts onto Ghoti worker cards.
- Do not install yet unless user approves.

Why not first:

- Paperclip is large and will introduce a second control plane.
- Ghoti should first define what it wants Paperclip to control.

### Option C — N+3.14 Claude: Persistent Dashboard Launcher Test

Rank: 3

Goal:

- Test `03_scripts/run_dashboard.ps1`.
- Add desktop shortcut instructions.
- No Windows service.
- No Electron/Tauri app.
- No autostart.

Why useful:

- Improves daily usability.
- Lower risk than Paperclip install.

Why not first:

- API-saving local-brain routing is more strategically urgent.

### Option D — N+3.14 Claude: CUA Second Smoke With Actual Screenshot Capture

Rank: 4

Goal:

- Only if approved.
- Still no click/type/login/live accounts.
- Capture a real screenshot artifact if allowed.

Why not first:

- CUA is higher risk than local-brain routing.
- First smoke already proved KasmVNC reachability and safe container constraints.

## Final Recommended Next Milestone

N+3.14 — Local Gemma Brain Router Preview + Worker Card Registry.

Reason:

This gets Ghoti closer to API-free use immediately and does not depend on installing another big system. It also creates the small control vocabulary needed before Paperclip, OpenClaw, or n8n should be allowed to coordinate work.

## Exact Claude Code Focus

Claude Code should:

1. Confirm local Gemma ready truth from existing smoke docs.
2. Add preview-only brain routing policy/config.
3. Add worker-card registry example.
4. Add a dry-run CLI if scoped and safe.
5. Run validation.
6. Document that no autonomous routing exists yet.

Claude Code should avoid:

- Paperclip install.
- OpenClaw install.
- n8n install.
- CUA execution.
- browser actions.
- live account actions.
- auto-dispatch.
- model/provider cap bypass.
- editing prompt files.
- staging third-party clone contents.

## Acceptance Criteria

- Preview command or config can recommend `gemma_local`, `codex`, `claude_code`, or `human_approval`.
- Local Gemma recommendations require `brain_inference_ready: true`.
- Risky/external/destructive tasks recommend human approval.
- No task is executed automatically.
- No external tool is installed.
- No runtime action is performed by Paperclip/OpenClaw/n8n.
