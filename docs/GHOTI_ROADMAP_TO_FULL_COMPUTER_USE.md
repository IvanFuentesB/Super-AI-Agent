# Ghoti Roadmap -- From Suggestion-Only to Supervised Computer-Use

**Status:** Roadmap. Only Stage 0 is implemented today; Stage 1 exists as a
mechanism but ships with no approvals granted. Everything later is not built
or not wired, and is labeled accordingly.

---

## Summary

This is the honest big picture: how the current suggestion-only Agent OS
grows into a full local agent OS without ever skipping a gate. The rule is
constant across all stages: capability is unlocked only by an explicit,
inspectable approval artifact plus proof that the previous stage holds.
Nothing here changes the standing prohibitions - no usage-cap bypass, no
fake engagement, no unattended autonomy. Content, business, and email
workflows stay draft-only until their own gates, independent of how far the
execution stages advance.

## Stage table

| # | Stage | Honesty label today | Gate to unlock |
|---|-------|---------------------|----------------|
| 0 | Suggestion-only worker + copy-paste handoffs | working now (`suggestion_only`) | none - this is the floor |
| 1 | Approved repo-local writes via `APPROVED_ACTIONS.json` | mechanism built, no approvals granted | human edits the approval file; repo-local dirs only |
| 2 | Supervised single-agent execution behind the approval queue | not wired | per-action approval through `super_ai_agent.queue`; evidence trail per run |
| 3 | Local model routing (Ollama/Gemma) for cheap drafts | probe only today | model verified by `local-model-check`; output guard rules applied |
| 4 | Telegram status, read-only | runtime doc exists, not enabled | notification-only token setup; no inbound commands |
| 5 | Observation-only computer-use | adapter exists, observation only | dry-run evidence from the adapter; zero control paths |
| 6 | Approved supervised computer-use behind kill-switch | not built | Rust runtime vocabulary live (`KillSwitchState`, `PolicyVerdict`); per-session approval; kill-switch tested |
| 7 | Multi-agent waves with file-ownership locks | planning preview only | ownership checker green on real waves; lane locks enforced |

## Stage detail and gates

### Stage 0 (current): suggestion-only worker + copy-paste handoffs

What exists: `03_scripts/agent_os/ghoti_agent_os.py` and
`03_scripts/agent_os/local_worker.py`. The worker reads verified memory,
writes proposals under `14_context/agent_os/`, and contains no execution
primitive (a self-check enforces this). All handoffs are
`relay_mode: copy_paste_only`.

Gate to stay here: none. This is the permanent safe floor the system can
always fall back to.

### Stage 1: approved repo-local writes

What exists: `14_context/agent_os/APPROVED_ACTIONS.json` can extend the
worker's allowed output directories. Only a human edits this file; entries
outside the repo are ignored by design (never approvable).

Gate: the approval file itself, reviewed in git. Proof required: the
`--check` suite still passes, including "writes outside agent_os refused"
for unapproved paths.

### Stage 2: supervised single-agent execution

Plan: one agent executes one bounded, pre-declared action behind the
existing approval queue in the runtime
(`01_projects/runtime_mvp/src/super_ai_agent/queue.py`). Every action is
proposed first, approved explicitly, executed once, and logged.

Gate: per-action human approval through the queue; an evidence file per run
under `14_context/agent_os/evidence/`. No batch approvals.

### Stage 3: local model routing for cheap drafts

Plan: route draft generation (scripts, titles, checklists) to local
Ollama/Gemma models so iteration is free and offline. Today only the
read-only probe exists (`ollama_endpoint_up`, model list, `auto_pull:
false`).

Gate: `local-model-check` recipe green for the chosen model, plus the local
model output guard rules (`docs/LOCAL_MODEL_OUTPUT_GUARD.md`). Drafts remain
drafts: routing changes who writes the text, not what may be done with it.

### Stage 4: Telegram status, read-only

Plan: outbound status notifications only, per
`docs/GHOTI_N6_10C_TELEGRAM_STATUS_BOT_RUNTIME.md`. No inbound commands, no
remote control.

Gate: explicit token setup by the human; the policy manifest keeps
`telegram` in `blocked_capabilities` for recipes, so only the dedicated
notification path may send, and only status text.

### Stage 5: observation-only computer-use

Plan: use the existing adapter (`03_scripts/ui_tars_observation_adapter.py`)
to observe screen state without any control path. The `computer-use-prep`
workflow checklist verifies preconditions.

Gate: adapter dry-run evidence showing observation only, plus an auditor
pass confirming every live-action path is still blocked.

### Stage 6: approved supervised computer-use behind kill-switch

Plan: bounded mouse/keyboard actions, each behind a per-session approval and
a tested kill-switch. The Rust runtime core already defines the vocabulary
(`rust/ghoti_runtime_core`: `KillSwitchState`, `PolicyVerdict`); the runtime
that enforces it during live actions is not built yet.

Gate: kill-switch demonstrated to halt mid-action; `PolicyVerdict::Deny`
proven to block; per-session human approval with explicit scope; instant
fallback to Stage 5 on any failure.

### Stage 7: multi-agent waves with file-ownership locks

Plan: multiple supervised agents work one wave at a time, with file
ownership enforced by the lane lock system
(`14_context/agent_lanes/active_locks.jsonl`) and verified by the ownership
checker (`ghoti_policy_checker --ownership-input`).

Gate: ownership check green on the real wave before it starts; locks taken
before any write; every agent individually subject to Stages 2-6 gates.

## Workflows that stay draft-only regardless

Content, business-research, and email workflows do not inherit execution
capability from any stage above. Each has its own future gate (for example,
"human approved this specific send") and until then their deliverables are
drafts and checklists a human acts on manually.

## Standing prohibitions (never unlocked by any stage)

- No usage-cap bypass of any provider or tool.
- No fake engagement, impersonation, or fabricated credentials.
- No unattended autonomy: a human is present and approving at every stage.
- No weakening of the deny-by-default policy to make a stage easier.
