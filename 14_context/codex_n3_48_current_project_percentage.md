# Codex N+3.48 - Current Project Percentage

Milestone: N+3.48 - Post-Merge Audit + 80 Percent Roadmap Lock

Date: 2026-05-06

## Blunt Estimate

Current project capability estimate: **68%**.

This is not a product-completion score. It is a practical Ghoti-operator-system score: how close the repo is to being a durable, low-copy-paste, multi-agent local operating system that can safely coordinate Claude Code, Codex, ChatGPT, Gemma/local workers, Obsidian memory, prompt bus, lane locks, and controlled parallel work.

## Why 68%, Not 80%

The repo now has important local rails:

- Money OS local workflows exist.
- Weekly review and manual decision queue pieces exist.
- Agent lane locks exist and validate.
- Obsidian vault and compact memory exist.
- Prompt bus exists and can stage prompts locally.
- Local worker router exists and recommends worker lanes.
- Claude slash commands exist.
- Controlled parallel pilot happened and was merged.
- Safety gates remain strong.

But the work is still too manual to call 80%:

- The operator still pastes most prompts manually.
- `ghoti_current_prompt.md` can be overwritten by prompt bus, but no higher-level context pack generator builds the prompt automatically from state, locks, and current goal.
- Codex outbox generation exists only as a low-level command, not a workflow.
- Lane status and active locks are valid files, but not automatically updated by scripts at task start/finish.
- There is no dashboard card for prompt bus, lane locks, local workers, or merge readiness.
- Gemma/local worker routing is recommendation-only; no workflow calls Gemma for context compression.
- Obsidian/compact memory refresh is not scripted.
- There is no merge assistant script that checks branch ancestry, locks, validation, and safe merge order.
- Ruflo/OpenClaw/Paperclip/n8n/CUA remain research/intake only, correctly not wired.

## Score Breakdown

| Capability area | Current score | Notes |
|---|---:|---|
| Repo audit discipline and safety gates | 85% | Strong docs, validation habits, no live-action creep. |
| Money OS local artifact loop | 75% | Many local artifacts and read views exist; still manual and not fully dashboard-unified. |
| Agent lane locks and branch separation | 78% | Lock/status JSONL and helper exist; updates are not automatic enough yet. |
| Prompt bus | 62% | Real CLI exists; still low-level and manual. |
| Local worker routing | 58% | Recommendation layer exists; no generalized worker execution or Gemma compression pipeline. |
| Obsidian/compact memory | 65% | Vault exists and is useful; refresh/promotion workflow is still manual. |
| Dashboard visibility | 55% | Money OS cards exist from prior milestones, but prompt bus/lane/local-worker views are missing. |
| Controlled parallel operation | 60% | Proven small pilot, but merge/state ownership still needs tooling. |
| External orchestration readiness | 35% | Correctly gated; no runtime integration yet. |
| End-to-end operator autonomy | 55% | Much safer and more organized, but still too much copy-paste and manual status tracking. |

Weighted practical estimate: **68%**.

## What 80% Means

80% should mean:

- A user can start a milestone from a compact prompt pack rather than a giant pasted prompt.
- Prompt bus can generate Claude/Codex/ChatGPT prompt artifacts from templates, current goal, branch, locks, allowed paths, forbidden paths, and validation commands.
- Dashboard exposes prompt bus status, lane locks, local worker recommendations, and next manual action.
- Lane status beacons are updated by helper scripts, not manually edited.
- Gemma/local worker can produce context compression drafts into `05_logs/` without becoming canonical truth.
- Obsidian/compact memory refresh has a safe dry-run/apply path.
- Merge assistant can say whether branches are ready to merge and what validations to run.
- All public/live/account/money actions remain human-approved and manual.

## What 99% Would Mean

99% is a much higher bar:

- Reliable multi-agent orchestration with recoverable state.
- Automatic context compression and promotion workflow.
- Dashboard-led operation.
- Sandbox-tested external worker/orchestrator integrations.
- Strong secret handling and connector inventory.
- Safe browser/operator lanes.
- Repeatable merge/release workflow.
- Production-grade observability and rollback.
- Very little copy-paste.

The repo is not close to 99% yet. It has the right bones, but the nervous system is still being wired.

## Expected Gain From Next Claude Implementation

Recommended next Claude implementation should target:

```text
N+3.49 - Prompt Bus Dashboard + Context Pack Generator + Lane Status Beacon Helper
```

Expected score after that implementation if done well: **74%**.

Why not 80 immediately:

- One milestone can make prompt/lane work visible and reduce copy-paste, but Gemma compression, Obsidian refresh, and merge-assistant automation likely need a second implementation milestone.

Expected path to 80:

- Current: 68%.
- After N+3.49 prompt bus/dashboard/beacon implementation: 74%.
- After N+3.50 Gemma context compression + Obsidian compact memory refresh + merge assistant: 80-83%.
