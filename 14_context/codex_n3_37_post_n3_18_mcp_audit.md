# Codex N+3.37 Post N+3.18 MCP Audit

Status: codex_audit_only / no_runtime_edits / no_tool_connections

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Current HEAD: e25a24c
Origin HEAD observed: e25a24c

## Executive Verdict

N+3.18 is finished and pushed.

`e25a24c feat(ghoti): finish N+3.18 video money runner` is both local HEAD and `origin/feat/ghoti-visible-operator-stack`.

Ghoti MCP source safety looks good from repo inspection: `01_projects/mcp_server/server.py` exposes read-only JSON-RPC tools and does not contain shell, write, delete, env, or network primitives.

Claude Code MCP connection status is unverified from this Codex shell because the `claude` command is not available on PATH. The expected N+3.36 connection report was not found at `14_context/n3_36_claude_mcp_connection_report.md`.

## Repo Truth

Commands inspected:

```powershell
git status --short
git branch --show-current
git log --oneline --graph --decorate --all -15
git remote -v
git show --stat --oneline HEAD
git show --name-only --oneline HEAD
```

Observed:

```text
branch: feat/ghoti-visible-operator-stack
HEAD: e25a24c
origin/feat/ghoti-visible-operator-stack: e25a24c
remote: https://github.com/IvanFuentesB/Super-AI-Agent.git
```

Latest commit:

```text
e25a24c feat(ghoti): finish N+3.18 video money runner
```

## N+3.18 Final Status

Status: finished / pushed.

Files in `e25a24c`:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
03_scripts/money_workflow_new_experiment.py
14_context/current_state.md
14_context/distribution_exposure_system_n3_18.md
14_context/gemma_video_to_money_runner_n3_18.md
14_context/ghoti_finish_line_log.md
14_context/money_experiment_scoring_n3_18.md
14_context/money_runner_safety_review_n3_18.md
14_context/money_workflows/experiment_tracker.schema.json
14_context/money_workflows/sample_video_notes_n3_18.md
14_context/next_actions.md
23_configs/local_brain_router_policy.example.json
```

N+3.18 implementation docs state:

- `video_to_money` accepts `.md` and `.txt` local inputs only.
- Gemma/Ollama is used locally through `ollama run`.
- Artifacts are written under `05_logs/money_runs/<run_id>/`.
- Outputs are drafts only.
- No posting, selling, emailing, scraping, live accounts, payments, or model-output execution.
- Experiment scoring is optional but all-or-nothing when used.
- Lower-is-better scoring fields are inverted.
- Schema includes required lists for scoring fields.

## N+3.18 Validation Evidence

Evidence in `14_context/ghoti_finish_line_log.md` and N+3.18 docs reports:

- local router AST: PASS
- money script AST: PASS
- schema JSON parse: PASS
- policy JSON parse: PASS
- tracker JSONL parse: PASS
- `git diff --check`: PASS
- router help includes `--task video_to_money`: PASS
- money script help includes scoring args and buckets: PASS
- scored dry-run total_score=41, bucket=A: PASS
- partial scoring error exits 1: PASS
- `video_to_money` smoke using gemma3:4b: PASS
- `approval_required` is bool `True`: PASS
- 9 artifacts written under `05_logs/money_runs/<run_id>/`: PASS

Codex also ran safe local validation in this audit:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m py_compile 01_projects/mcp_server/server.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > $null
python -c "... parse experiment_tracker.jsonl ..."
```

Observed result: all passed; tracker JSONL parsed with 3 rows.

## MCP Connection Status

Commands attempted:

```powershell
claude mcp list
claude mcp get ghoti-local
```

Observed:

```text
claude: The term 'claude' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

Therefore Codex cannot directly confirm that Claude Code currently has `ghoti-local` connected.

No `.mcp.json` file was found in the repo root during this audit.

Expected report file:

```text
14_context/n3_36_claude_mcp_connection_report.md
```

Observed: missing.

Conclusion: MCP server source is present and safe-looking; Claude Code connection remains unverified from this Codex environment.

## MCP Server Source Audit

File inspected:

```text
01_projects/mcp_server/server.py
```

Server description says:

```text
Safety: no shell, no writes, no network, no env access. Read-only within repo.
```

Imports observed:

```text
sys
json
datetime
pathlib.Path
```

No matches were found for:

```text
subprocess
socket
requests
urllib
httpx
aiohttp
openai
anthropic
write_text
unlink
remove
rmdir
mkdir
rename
replace
shutil
Popen
os.system
environ
```

The only file helper is `_safe_read(path)`, which calls `path.read_text()`.

## MCP Tools Exposed

Codex ran a local JSON-RPC `initialize` and `tools/list` smoke against `server.py`.

Tools exposed:

```text
ghoti_status
read_repo_summary
read_current_state
read_latest_operator_state
read_manual_execution_queue
read_audit_trace
read_control_center_state
read_pipeline_items_overview
read_approval_inbox
read_approval_item
read_manual_queue_item
```

All advertised tools are status/read tools.

No shell/write/delete/network/live-account tool was exposed in `tools/list`.

## MCP Safety Verdict

Source-level verdict: safe to keep as a local read-only bridge.

Connection-level verdict: unverified until Claude Code itself can run:

```powershell
claude mcp list
claude mcp get ghoti-local
```

Recommended next MCP step:

Create or recover `14_context/n3_36_claude_mcp_connection_report.md` with:

- exact `claude mcp list` output
- exact `claude mcp get ghoti-local` output
- command path used for the MCP server
- tool list
- read-only safety confirmation

## Remaining Dirty Files

Remaining local dirt after N+3.18 push:

```text
M  14_context/ghoti_external_repo_tool_intake.md
M  21_repos/third_party/.gitkeep
?? .claude/skills/
?? 01_projects/mcp_server/test.txt
?? 05_logs/local_brain_runs/
?? 05_logs/money_runs/
?? 14_context/ghoti_current_prompt_N1_6.md
?? CV_*.docx
?? output/
```

Known previous N+3.18 dirty runtime files are no longer dirty after `e25a24c`.

## Later Milestone Check

No evidence was found that Claude implemented later planned milestones:

- N+3.29 weekly money review artifact generator
- N+3.30 weekly review dashboard card
- N+3.31 manual queue draft intake helper
- N+3.32 manual queue read view and operator work session planner
- N+3.34 Obsidian compact memory scaffolding

The next Money OS sequence remains valid.

## Unknowns

Codex could not verify:

- actual Claude Code MCP config because `claude` is not on PATH in this shell
- whether the user has a global/user-scope Claude MCP config outside the repo
- whether N+3.36 was completed in an uncommitted external Claude environment
- whether the N+3.18 smoke artifacts under `05_logs/money_runs/` should be committed or remain local-only

## Audit Conclusion

N+3.18 is now finished and pushed at `e25a24c`.

The local Ghoti MCP server source appears read-only and safe, but Claude Code connection must be treated as unverified until a Claude-side MCP report is created.
