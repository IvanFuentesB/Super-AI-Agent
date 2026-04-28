# Local Gemma Context Compression — N+3.15

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.15
Status: implemented / preview_only / no_external_api

---

## What Was Added

Added `compress_context` task class to `local_brain_router.py`.

New CLI usage:
```
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py \
  --task compress_context \
  --input 14_context/current_state.md \
  --max-chars 12000
```

Existing preview behavior unchanged:
```
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --preview
```

---

## Exact Behavior

1. Validates input path is inside repo root — rejects any outside path.
2. Checks file extension against allowlist: `.md`, `.txt`, `.json`, `.py`, `.js`, `.ps1`.
3. Reads file text, clips to `--max-chars` (default 12000) if larger.
4. Rejects binary-looking files (>10% non-printable chars in first 2000 bytes).
5. Builds a structured compression prompt asking Gemma for:
   - Up to 10 bullet summary
   - Active blockers
   - Next actions
   - Decisions/memory worth preserving
   - Files cited by path
6. Calls `ollama run gemma3:4b <prompt>` locally — no external API.
7. Saves all artifacts to `05_logs/local_brain_runs/<run_id>/`.

---

## Artifacts Written Per Run

| File | Contents |
|---|---|
| `request.json` | Run metadata: input file, chars read, clipped flag, model, timestamp |
| `source_excerpt.md` / `.txt` | Exact excerpt sent to Gemma (clipped if needed) |
| `response.txt` | Raw Gemma output |
| `run_summary.json` | Status, artifacts list, safety confirmations |

---

## Safety Boundaries

- `repo_root_only: true` — rejects any path outside `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- `no_external_api: true` — Ollama is local-only; no cloud round-trip
- `no_model_output_execution: true` — response is saved and displayed only; never run as code
- `artifact_only_outputs: true` — writes only to `05_logs/local_brain_runs/<run_id>/`
- Model output is NEVER auto-committed, NEVER auto-executed, NEVER used to edit repo files
- Operator reviews output manually before any use

---

## What Gemma Is Allowed to Do

- Summarize a local markdown or text file
- Identify blockers, next actions, and decisions from that file
- Cite file paths mentioned in the text
- Draft checklists for local task validation
- Classify a task as easy/medium/hard/risky

---

## What Gemma Is NOT Allowed to Do

- Edit repo files (no auto-commit path exists)
- Access external APIs, cloud services, or remote endpoints
- Read secrets, `.env`, CV files, or credential stores
- Execute shell commands or code
- Make decisions about live accounts, payments, or legal matters
- Access files outside repo root

---

## Compression Smoke Tests (Phase 7)

Test A input: `14_context/current_state.md`
Test B input: `14_context/agent_registry/agent_routing_policy_n3_14.md`

Results: see `05_logs/local_brain_runs/compress_*/run_summary.json`
