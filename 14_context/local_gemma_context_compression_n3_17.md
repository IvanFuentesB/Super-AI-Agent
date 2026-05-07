# Local Gemma Context Compression — N+3.17

Date: 2026-04-28
Milestone: N+3.17
Branch: feat/ghoti-visible-operator-stack
Status: implemented / route_verified / no_external_api

---

## Agent Role Summary

Ghoti uses a four-agent split for different task types:

| Agent | Role | Cost |
|---|---|---|
| **Gemma / Ollama** | Easy local text work: compression, checklists, risk labels, first drafts | Free (local compute) |
| **Claude Code** | Hard multi-file implementation, debugging, validation, commits, push | Paid API |
| **Codex** | Audits, reviews, planning docs, second opinions | Paid / copy-paste |
| **ChatGPT** | High-level planning, strategy, new milestone prompts | Paid / human-operated |

This is NOT cap bypass or quota evasion. It is legitimate local compute using an already-installed model (gemma3:4b via Ollama) for tasks that do not require cloud-level reasoning.

---

## What Changed in N+3.17

The `compress_context` task class was already implemented in N+3.15 and is confirmed working.
N+3.17 adds:
- N+3.17 docs confirming compression route health
- Two new smoke test runs (Test A and Test B) PASS
- Money workflow foundation ready to use Gemma for first-draft intake

---

## Smoke Tests (N+3.17)

Test A: `14_context/current_state.md`
- Command: `python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md --max-chars 12000`
- Result: PASS — artifacts at `05_logs/local_brain_runs/compress_20260428_203025_9cef4f/`

Test B: `14_context/agent_registry/agent_routing_policy_n3_14.md`
- Command: `python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/agent_registry/agent_routing_policy_n3_14.md --max-chars 12000`
- Result: PASS — artifacts at `05_logs/local_brain_runs/compress_20260428_203107_a0b523/`

---

## CLI Reference

```
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --preview
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md --max-chars 12000
```

---

## Safety Boundaries (unchanged from N+3.15)

- `repo_root_only: true` — rejects any path outside repo root
- `no_external_api: true` — Ollama is local only; no cloud round-trip
- `no_model_output_execution: true` — response saved and displayed only; never run as code
- `artifact_only_outputs: true` — writes only to `05_logs/local_brain_runs/<run_id>/`
- Model output is NEVER auto-committed, NEVER auto-executed, NEVER used to edit repo files

---

## Money Handoff Ready

The compression route is ready to summarize video notes, intake docs, and context files before feeding them into money workflow templates. Operator reviews Gemma output before any use.

Next step: use Gemma to compress raw video/transcript notes → paste summary into `video_to_money_intake_template.md` → generate experiment tracker entries.
