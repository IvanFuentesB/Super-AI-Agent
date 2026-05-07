# Codex N+3.34 Claude Implementation Checklist

Status: codex_planning_only / claude_implementation_checklist / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Recommended Claude Milestone

```text
N+3.34 Claude - Obsidian Local Memory And Gemma Compression Scaffolding
```

## First Rule

FIRST resolve or consciously pause dirty N+3.18 before runtime implementation.

This memory milestone can later be implemented as docs/file scaffolding safely after N+3.18 is resolved or explicitly parked. Do not mix memory scaffolding with dirty video-to-money runtime changes unless the operator explicitly scopes that combined milestone.

## Scope

Allowed future implementation:

- create missing Obsidian vault files
- create missing compact memory files
- append or merge timestamped sections into existing memory files
- add a local stdlib-only helper only if needed
- write local draft artifacts only

Forbidden:

- overwrite existing user memory blindly
- delete source records
- install Obsidian or plugins
- run live account actions
- run external APIs
- scrape
- post/send/sell/pay
- execute model output
- broad runtime refactor

## Repo Truth Step

Run first:

```powershell
git status --short
git branch --show-current
git log --oneline --graph --decorate --all -8
git diff --cached --name-status
```

Confirm N+3.18 dirty files are not staged unless the operator explicitly resumes N+3.18.

## File Scaffolding Steps

1. Read `14_context/codex_n3_34_obsidian_vault_structure_spec.md`.
2. Read `14_context/codex_n3_34_compact_memory_contract.md`.
3. List existing files under `14_context/obsidian_vault/`.
4. List existing files under `14_context/compact_memory/`.
5. Create only missing target files.
6. If a file exists, append a dated migration/update section instead of replacing it.
7. Include metadata headers for compact memory files.
8. Include source references in every new or updated note.
9. Mark Gemma-generated content as draft until reviewed.
10. Keep all content repo-local and no-live-action.

## Future Obsidian Files

Create if missing:

```text
14_context/obsidian_vault/00_Index.md
14_context/obsidian_vault/01_Current_State.md
14_context/obsidian_vault/02_Next_Actions.md
14_context/obsidian_vault/03_Decisions.md
14_context/obsidian_vault/04_Tools_And_Repos.md
14_context/obsidian_vault/05_Money_OS.md
14_context/obsidian_vault/06_Safety_Gates.md
14_context/obsidian_vault/07_Agent_Routing.md
14_context/obsidian_vault/08_Dirty_State.md
14_context/obsidian_vault/09_Migration_Handoff.md
```

Note: existing N+3.7 files include `04_Tools.md` and `05_Safety_Gates.md`. Claude should preserve them and decide whether to create `04_Tools_And_Repos.md` as a new canonical note or migrate via append.

## Future Compact Memory Files

Create if missing:

```text
14_context/compact_memory/project_state.md
14_context/compact_memory/repo_and_tool_index.md
14_context/compact_memory/money_os_memory.md
14_context/compact_memory/agent_routing_memory.md
14_context/compact_memory/safety_rules.md
14_context/compact_memory/dirty_state_warning.md
```

Do not delete older compact memory files. They can be referenced from the new index or migration note.

## Optional Helper Script

Only if needed:

```text
03_scripts/memory_compress_draft.py
```

Rules:

- Python standard library only
- repo-root-only file reads
- dry-run first
- artifact-only output by default
- no canonical overwrite unless explicit reviewed promotion mode
- no model-output execution

## Validation Commands

Always:

```powershell
git diff --check
git diff --cached --check
```

Markdown file existence checks:

```powershell
Test-Path 14_context/obsidian_vault/00_Index.md
Test-Path 14_context/compact_memory/project_state.md
```

If a helper script is added:

```powershell
python -m py_compile 03_scripts/memory_compress_draft.py
```

If config JSON is added:

```powershell
python -m json.tool <path-to-config-json>
```

If compact memory metadata is added, inspect headers:

```powershell
Get-Content -TotalCount 20 14_context/compact_memory/project_state.md
```

## Staging Rules

Stage only intentional N+3.34 files.

Do not stage:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`
- `.claude/skills/`
- `05_logs/local_brain_runs/`
- CV docs
- `output/`
- `21_repos/third_party/.gitkeep`
- prompt scratch files
- `01_projects/mcp_server/test.txt`
- unrelated external repo intake docs

Before commit:

```powershell
git diff --cached --name-status
git diff --cached --check
```

## Future Commit Message

```text
docs(ghoti): add Obsidian and compact memory scaffolding
```

If a helper script is included:

```text
feat(ghoti): add local memory compression draft helper
```

## Verdict

Claude should implement memory scaffolding as conservative file creation and reviewed append/merge only. No installs, no live actions, no broad refactor, no runtime changes while N+3.18 is dirty.
