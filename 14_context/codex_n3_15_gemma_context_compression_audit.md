# Codex N+3.15 Gemma Context Compression Audit

Status: codex_parallel_audit / implementation_spec_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 925387f

## Current Truth

N+3.14 added a preview-only local brain router at:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`

The router currently:

- loads `23_configs/local_brain_router_policy.example.json`
- keeps `enabled=false`
- runs one safe `draft_checklist` preview via `ollama run gemma3:4b`
- writes local artifacts under `05_logs/local_brain_runs/<run_id>/`
- does not execute model output
- does not edit repo files from model output
- does not call any external API

The policy already lists `compress_context` as a local task class, but there is no dedicated compression route yet.

## What Claude Should Implement

Add a `compress_context` task path to `local_brain_router.py`.

Recommended invocation shape:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md
```

Optional aliases are acceptable if documented, but the behavior must remain explicit. Avoid automatic compression loops.

## Required Safety Boundaries

### Repo-Root-Only Inputs

The input path must be resolved and validated before reading:

- must be inside `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- must exist
- must be a regular file
- must not be inside forbidden roots such as third-party clone contents, runtime data, screenshots, CV docs, or output artifacts unless explicitly approved
- must not follow a path traversal outside the repo root

If validation fails, the router should write a failed `run_summary.json` and exit non-zero without calling Ollama.

### Max Input Chars

Add a hard maximum input length. Recommended initial value:

```text
max_input_chars = 12000
```

If the source file is larger, write only the first `max_input_chars` characters to the prompt and record:

- source byte/char length
- excerpt char length
- truncation status
- source path

The full source file must not be copied into artifacts when too large.

### Artifact-Only Outputs

Gemma output must be written only as artifacts. It must not modify the source file, current state files, prompt files, runtime code, dashboard code, or any config directly.

Required artifact directory:

```text
05_logs/local_brain_runs/<run_id>/
```

Required artifacts:

- `request.json`
- `source_excerpt.md` or `source_excerpt.txt`
- `response.txt`
- `run_summary.json`

Optional artifact:

- `summary.md`, if it only summarizes the run and points to the required artifacts

### No Model Output Execution

Gemma output must never be executed as code, shell commands, PowerShell, Python, Docker, Git, browser automation, CUA, n8n, Paperclip, or OpenClaw instructions.

The router should write explicit fields:

```json
{
  "model_output_executed": false,
  "repo_edits_from_model_output": false,
  "external_actions_triggered": false
}
```

### No Repo Edits From Gemma Output

The compress route may produce a suggested compact summary, but a human/Claude/Codex must decide whether to copy or apply it later. This is what makes the route safe and cheap without turning Gemma into an autonomous editor.

## Required Prompt Constraints

The compression prompt should tell Gemma:

- summarize only the supplied excerpt
- do not invent missing facts
- preserve concrete file paths, commit hashes, approval states, and blockers
- keep output compact
- label uncertainty
- do not propose executing commands
- do not claim runtime wiring that is not present

Recommended output style:

```text
Return a compact handoff summary with:
- current truth
- active blockers
- relevant files
- next safe step
- explicit unknowns
```

## Required Run Summary Fields

`run_summary.json` should include:

- `run_id`
- `task_type`
- `status`
- `provider`
- `model`
- `input_path`
- `input_inside_repo_root`
- `source_chars`
- `excerpt_chars`
- `truncated`
- `max_input_chars`
- `request_path`
- `source_excerpt_path`
- `response_path`
- `api_usage`
- `cloud_inference`
- `model_output_executed`
- `repo_edits_from_model_output`
- `external_actions_triggered`
- `started_at_utc`
- `finished_at_utc`
- `error`, if any

## Required Smoke Tests

Claude should run two smoke tests:

1. Compress `14_context/current_state.md`.
2. Compress `14_context/agent_registry/agent_routing_policy_n3_14.md`.

Pass criteria:

- both runs exit 0
- each run writes the four required artifacts
- output is text-only
- source files remain unchanged
- no runtime/dashboard/prompt files are modified by model output
- no external APIs are called
- `run_summary.json` says `api_usage: none` and `cloud_inference: false`

## Validation Commands Claude Should Run

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/agent_registry/agent_routing_policy_n3_14.md
python -m json.tool 23_configs/local_brain_router_policy.example.json
git diff --check
git status --short
```

## Verdict

The N+3.15 implementation should add a single explicit `compress_context` route, not a general autonomous router. It should prove that Gemma can cheaply compress local context into artifacts while preserving the rule that model output is reviewed, not executed.
