# Codex N+3.17 Gemma Compression Completion Audit

Status: codex_audit_only / implementation_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 77bfb74

## Purpose

Audit the local Gemma context-compression route so the next Claude Code milestone can finish or repair it safely. This audit does not edit runtime code and does not run Ollama, Docker, CUA, browser automation, or any external workflow.

## Current `local_brain_router.py` Truth

Observed file: `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`

Current local dirty-file truth:

- The file is modified in the working tree and was not staged by this Codex lane.
- It contains the original `--preview` draft-checklist path.
- It also contains a `compress_context` route:
  - `_DEFAULT_MAX_CHARS = 12000`
  - `_ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".py", ".js", ".ps1"}`
  - `_COMPRESS_PROMPT_TEMPLATE`
  - `_resolve_input_path`
  - `_read_excerpt`
  - `run_compress_context`
  - `_parse_args`
  - CLI handling for `--task compress_context --input <path> --max-chars <number>`
- The route writes artifacts under `05_logs/local_brain_runs/<run_id>/`.
- The route records `request.json`, `source_excerpt.*`, `response.txt`, and `run_summary.json`.
- The route records `api_usage: none`, `external_calls: none`, `model_output_executed: false`, and `repo_edits_from_model: false`.

## Policy Truth

Observed file: `23_configs/local_brain_router_policy.example.json`

The policy is also modified in the working tree and was not staged by this Codex lane. It currently includes:

- `routing_mode: preview_only`
- `enabled: false`
- `autonomous_execution_enabled: false`
- `default_local_model: gemma3:4b`
- `local_provider: ollama`
- `local_task_classes` includes `compress_context`
- `compress_context_defaults.max_input_chars: 12000`
- safety gates for repo-root-only, no external API, no model output execution, artifact-only outputs, and allowed extensions

## What Claude Code Must Complete or Repair

Claude Code should inspect the dirty implementation and decide whether it is already correct enough to commit. Minimum expected completion:

1. Confirm `compress_context` exists and is reachable from CLI.
2. Confirm all input paths are resolved under repo root.
3. Confirm disallowed file extensions are rejected.
4. Confirm binary-looking content is rejected.
5. Confirm `--max-chars` clips source excerpts and records clipping truth.
6. Confirm artifacts are written under `05_logs/local_brain_runs/`.
7. Confirm model output is never executed and never written back into source files.
8. Confirm failures still create a useful `run_summary.json`.
9. Confirm the policy file documents `compress_context`.
10. Commit the runtime/policy/log docs only if validation passes and the user scope permits it.

## Exact Validation Commands Claude Should Run

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -c "import json; json.load(open('23_configs/local_brain_router_policy.example.json', encoding='utf-8')); print('policy json ok')"
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/codex_n3_16_numbers_game_money_os.md --max-chars 12000
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/ghoti_current_prompt_N1_6.md --max-chars 12000
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input ..\outside_repo_test.md --max-chars 12000
git diff --check
git diff --cached --check
```

The outside-repo rejection command should be adjusted to a harmless existing outside path only if Claude can do so without reading private or unrelated data. The expected result is rejection, not success.

## Safety Gates

- Repo-root-only input files.
- Allowed extensions only: `.md`, `.txt`, `.json`, `.py`, `.js`, `.ps1`.
- Default max input chars: 12000.
- Artifact-only outputs.
- No model-output execution.
- No repo edits from model output.
- No external API.
- No live accounts.
- No posting, sending, scraping, selling, or account actions.
- No Docker, CUA, Paperclip, OpenClaw, or n8n involvement.

## PASS Criteria

PASS means:

- Python syntax check passes.
- Policy JSON parses.
- `compress_context` successfully creates a run folder for an allowed repo-local text file.
- `request.json`, source excerpt, `response.txt`, and `run_summary.json` exist.
- `run_summary.json` says `task_type: compress_context`.
- Rejected inputs fail safely.
- No source file is edited by model output.
- No external service is called beyond local Ollama inference.

## Blockers

Block and repair before commit if:

- `compress_context` cannot be invoked.
- Path traversal or outside-repo file input is possible.
- Disallowed binary or private files can be summarized.
- Artifacts are missing or written outside `05_logs/local_brain_runs/`.
- Model output is executed, imported, appended, or staged automatically.
- The policy claims runtime/autonomous routing while `enabled=false`.
- The route requires external APIs or network services.

## API-Saving Truth

This saves credits by moving easy local summarization and context compression to Gemma/Ollama. This is legal context management, not provider cap bypass, quota evasion, fake accounts, or safety bypass. Hard implementation, risky decisions, and final edits still belong to Claude Code, Codex, ChatGPT, and the human operator.
