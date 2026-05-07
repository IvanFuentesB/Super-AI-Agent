# N+3.43 Agent Lane Implementation Brief

Status: future Claude implementation brief.
Date: 2026-05-05

## Target Milestone

```text
N+3.43 Claude - Agent Lane Locks And Parallel Execution Scaffolding
```

## Preconditions

- N+3.34 must be pushed first.
- Start with `git fetch origin`.
- Confirm branch and origin state.
- Do not begin from a stale clone.
- Do not install external agents.
- Do not connect live tools.
- Do not enable parallel execution yet.

## Implementation Goal

Create local scaffolding so future Claude, Codex, ChatGPT, Gemma, and other approved workers can coordinate safely.

This milestone should create templates and helper checks only. It should not launch or connect agents.

## Files To Create

Create folder:

```text
14_context/agent_lanes/
```

Suggested files:

```text
14_context/agent_lanes/README.md
14_context/agent_lanes/agent_lane_contract.md
14_context/agent_lanes/active_locks_index.md
14_context/agent_lanes/status_beacon_template.md
14_context/agent_lanes/active_lock_template.md
14_context/agent_lanes/merge_protocol.md
14_context/agent_lanes/stop_conditions.md
14_context/agent_lanes/shared_file_lock_list.md
```

Optional helper script:

```text
03_scripts/agent_lane_status.py
```

Helper script constraints:

- Python standard library only.
- No network.
- No installs.
- No model calls.
- No account actions.
- No git mutation by default.
- Read-only check mode first.
- If it writes, it should write only lane status/lock markdown files after explicit command.

## Required Template Fields

Active lock template should include:

- `agent_id`
- `model_or_tool`
- `machine_id`
- `branch`
- `current_task`
- `milestone`
- `locked_files`
- `started_at`
- `heartbeat_at`
- `expected_outputs`
- `safe_to_interrupt`
- `do_not_touch`
- `operator_approval_scope`
- `status`

Status beacon template should include:

- branch
- local HEAD
- origin HEAD
- dirty files observed
- staged files
- write scope
- files edited
- validation commands run
- blockers
- next intended step
- final report status

## Shared Files Requiring Locks

Include these in `shared_file_lock_list.md`:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/*`
- `14_context/obsidian_vault/00_Index.md`
- `14_context/obsidian_vault/01_Current_State.md`
- `14_context/obsidian_vault/02_Next_Actions.md`
- `14_context/obsidian_vault/03_Decisions.md`
- `14_context/obsidian_vault/08_Dirty_State.md`

## Safety Rules

N+3.43 must not:

- install external agents
- clone external repos
- connect MCP servers
- create accounts
- read/send real emails
- post to social media
- submit job applications
- run scraping workflows
- pay/subscribe/buy credits
- run guardrail-removal tools
- enable autonomous real-money actions
- enable actual parallel execution

## Validation Commands

Run:

```powershell
git status --short
git branch --show-current
git fetch origin
git rev-parse HEAD
git rev-parse origin/feat/ghoti-visible-operator-stack
git diff --check
git diff --cached --check
```

If Python helper is added:

```powershell
python -m py_compile 03_scripts/agent_lane_status.py
python 03_scripts/agent_lane_status.py --help
python 03_scripts/agent_lane_status.py --check
```

If JSON config is added:

```powershell
python -m json.tool <path-to-json>
```

## Staging Rules

Stage only intentional N+3.43 files:

- `14_context/agent_lanes/*`
- `03_scripts/agent_lane_status.py` if created
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md` if updated
- N+3.43 implementation doc

Do not stage:

- unrelated dirty files
- generated local brain logs
- generated money logs
- CV documents
- prompt scratch files
- `.claude/skills/`
- third-party placeholder dirt unless intentionally scoped

## Commit Message Suggestion

```text
feat(ghoti): add agent lane lock scaffolding
```

## Final Report Fields

Claude final report should include:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validations run
- lane scaffold truth
- helper script truth
- lock/status template truth
- runtime wiring truth
- install/connect truth
- live action truth
- dirty files intentionally left unstaged
- exact next Codex recommendation
- exact next future milestone recommendation

## Next After N+3.43

After lane scaffolding is implemented and audited, controlled parallel lanes can begin in limited form. External tool integrations should still wait until lane locks and connector/account safety are stable.
