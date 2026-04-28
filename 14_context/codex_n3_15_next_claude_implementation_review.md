# Codex N+3.15 Next Claude Implementation Review

Status: codex_parallel_audit / implementation_spec_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Recommended Claude Code Milestone

N+3.15 — Local Gemma Context Compression Route.

Goal:

Add an explicit `compress_context` task to the existing local brain router so Gemma can compress repo-local markdown/text files into artifacts. Do not let Gemma edit the repo or execute output.

## Files Claude Should Likely Touch

Allowed for Claude implementation lane:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `23_configs/local_brain_router_policy.example.json`
- `14_context/local_gemma_context_compression_n3_15.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- generated artifacts under `05_logs/local_brain_runs/<run_id>/` if intentionally committed and small

Claude should not touch:

- Paperclip/OpenClaw/n8n runtime files
- third-party repo contents
- dashboard code unless explicitly required
- prompt files
- `.claude/skills/`
- CV docs
- `output/`
- unrelated dirty files

## Implementation Requirements

### Add `compress_context`

Recommended command:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md
```

Required behavior:

- validate input path is inside repo root
- reject missing/non-file/out-of-root paths
- reject or skip forbidden areas unless explicitly approved
- enforce max input chars
- write artifacts only
- never execute model output
- never edit source or repo files from model output

### Required Artifacts

Each compression run must write:

- `request.json`
- `source_excerpt.md` or `source_excerpt.txt`
- `response.txt`
- `run_summary.json`

Recommended path:

```text
05_logs/local_brain_runs/<run_id>/
```

### Required Policy Update

Update `23_configs/local_brain_router_policy.example.json` with:

- `compress_context.max_input_chars`
- `compress_context.allowed_extensions`
- `compress_context.output_artifacts`
- `compress_context.model_output_executed=false`
- `compress_context.repo_edits_from_model_output=false`
- `compress_context.preview_only=true`

## Required Smoke Tests

Run two smoke tests:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/agent_registry/agent_routing_policy_n3_14.md
```

Pass conditions:

- both commands exit 0
- required artifacts exist for each run
- `run_summary.json` parses
- source files unchanged
- output is not executed
- no external API
- no repo edits from Gemma output

## Required State Updates

Claude should update:

- `14_context/local_gemma_context_compression_n3_15.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- wait/resume seeds to show context compression route validated

Finish-line log should include:

- previous HEAD
- new commit hash
- pushed yes/no
- commands run
- artifact paths
- source files compressed
- model/version truth
- API usage none
- runtime wiring truth
- dirty files left unstaged

## Required Validation

Run:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
python -m json.tool 23_configs/local_brain_router_policy.example.json
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
git diff --check
git status --short
git diff --cached --name-status
```

If generated artifacts are committed, verify they are small and do not contain secrets, screenshots, credentials, or private data.

## Commit and Push

Recommended commit:

```text
feat/ghoti milestone N+3.15 — add Gemma context compression route
```

Push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Stop Conditions

Stop and report if:

- Gemma output suggests running commands or editing files directly
- input path validation fails unexpectedly
- `run_summary.json` cannot be parsed
- compression output contains secrets or private data
- Docker/CUA/browser actions are requested
- any third-party repo files become staged
- unrelated dirty files are accidentally staged

## Verdict

Claude should implement `compress_context` next. This is the fastest safe way to turn the successful Gemma smoke into useful API-saving work while preserving Ghoti's approval-gated operator philosophy.
