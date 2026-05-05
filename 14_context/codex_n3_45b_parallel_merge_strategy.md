# N+3.45B Parallel Merge Strategy

Status: controlled pilot merge plan.
Date: 2026-05-05

## Parallel Branches

Claude implementation branch:

```text
feat/ghoti-agent-claude-n3-45-tooling-prompt-bus
```

Codex audit branch:

```text
audit/ghoti-agent-codex-n3-45-tool-routing
```

## Separation Rule

Codex docs should not touch Claude-owned files. Claude implementation should not touch Codex docs.

Codex owns:

- `14_context/codex_n3_45b_*.md`

Claude owns, if scoped by the user:

- `03_scripts/`
- `01_projects/`
- `14_context/prompt_bus/`
- `14_context/tooling/`
- `14_context/local_workers/`
- `23_configs/`

State docs are not owned by either lane unless a state-doc owner is explicitly designated.

## Active Lock / Status Inspection

Before merge:

```powershell
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
git fetch origin
git status --short
```

Manual inspection:

- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- each branch's staged/committed files

## Merge Order

Preferred:

1. Merge Claude implementation branch if validation passes and no Codex-file overlap.
2. Merge Codex audit branch if doc checks pass and no Claude-file overlap.
3. Run a small follow-up state-owner update if needed.

Alternative:

- If Claude is blocked, merge Codex docs first because they are isolated docs-only.

## Conflict Handling

Stop if:

- both branches edit the same file
- either branch edits `current_state.md` or `next_actions.md` without being state owner
- Claude touches `14_context/codex_n3_45b_*.md`
- Codex touches implementation/runtime paths
- either branch stages recurring unrelated dirty files

Resolution:

- no reset
- no force merge
- inspect branch diffs
- decide one writer
- replay only the intended changes manually or via a new recovery branch

## Lock Release / Archive

Current N+3.43 lock system is append-only and status-based. Do not delete lock records.

To release later:

- append a `released` status record
- mention merged/abandoned branch
- keep historical lock lines for audit

Future hardening can add a convenience `--release-lock` action, but deletion should remain forbidden.

## Shared-State Conflict Avoidance

- Use one state-doc owner after both branches finish.
- Keep Codex lane docs-only.
- Keep Claude lane implementation-only.
- Do not update compact memory or Obsidian from parallel lanes.
- Merge one branch at a time.
- Re-run validation after each merge.

## Pilot Success Criteria

- Both branches push independently.
- No overlapping write sets.
- No live actions.
- No external installs/connectors.
- Merge history remains understandable.
- State docs updated once, after merge, by a designated owner.
