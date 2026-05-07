# Claude N+3.61A — LLM Council Scaffold + Clean Merge Readiness

Branch: `feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness`
Base: `origin/feat/ghoti-agent-claude-n3-58-fix-obsidian-dashboard-whitespace` @ `ffc9cc0`
Agent: `claude_code_n3_61a`
Date: 2026-05-07

## Mission Summary

N+3.61A delivers two things:

1. **Clean merge readiness** — fixes the 3 inherited documentation files that were
   blocking a clean `git diff --check` pass due to CRLF line endings.

2. **Local-first LLM Council scaffold** — adds a Karpathy-style 3-stage council
   (individual opinions, anonymous peer review, chairman synthesis) as a stdlib-only
   Python script with no external API calls by default.

## Whitespace Fixes

Files fixed (CRLF -> LF, trailing whitespace stripped):
- `14_context/tooling/merge_assistant_n3_58.md`
- `14_context/tooling/repo_language_inventory_n3_58.md`
- `14_context/tooling/rust_readiness_n3_58.md`

Files verified clean (already LF, no trailing whitespace):
- `14_context/ghoti_dashboard_card.md`

## LLM Council Scaffold

### Files Added

| File | Purpose |
|------|---------|
| `03_scripts/llm_council_runner.py` | Main runner: 3-stage council flow, CLI, stdlib-only |
| `23_configs/llm_council.example.json` | Example config: council members, ranking criteria, safety flags |
| `14_context/tooling/llm_council_n3_61.md` | Tooling reference: flow, customization guide |
| `14_context/tooling/karpathy_llm_council_source_note_n3_61.md` | Source note: what we did/did not do |

### Files Modified

| File | Change |
|------|--------|
| `03_scripts/local_worker_router.py` | Added llm_council_worker route (7 trigger keywords) |
| `03_scripts/ghoti_dashboard.py` | Added llm_council status section |

### Karpathy-Style 3-Stage Flow

1. **Stage 1 — First Opinions**: Each council member answers independently from their role
2. **Stage 2 — Anonymous Peer Review**: Responses labeled A/B/C, scored against criteria, ranked
3. **Stage 3 — Chairman Synthesis**: Chairman reads anonymous ranking, produces final answer

### Provider Modes

| Mode | Default | Requires | External calls |
|------|---------|----------|----------------|
| local_demo | YES | nothing | NO |
| ollama_local | no | Ollama installed | NO (local only) |
| openrouter_external | DISABLED | config flag + env var | stub only (TODO) |

### Safety Invariants (Always Present in Output)

- `LOCAL_ONLY_BY_DEFAULT`
- `NO_AUTONOMOUS_ACTIONS`
- `HUMAN_REVIEW_REQUIRED`
- `EXTERNAL_CALLS_DISABLED_BY_DEFAULT`

## Safety Gate Confirmation

- External API calls enabled: NO
- OpenRouter key stored: NO
- Ollama required: NO (local_demo works without it)
- CC/Codex automatic: NO
- Ruflo runtime wired: NO
- Autonomous actions: NO
- Live account actions: NO
- Secret reads: NO
- Package installs: NO
- venv/node_modules: NO

## Validation Results

(See lane_status.jsonl for full validation record)

## How to Use

```bash
# Status
python 03_scripts/llm_council_runner.py --status

# Demo (no model required)
python 03_scripts/llm_council_runner.py --demo --dry-run

# Ask a question (dry run)
python 03_scripts/llm_council_runner.py --ask "How should Ghoti use an LLM council safely?" --dry-run

# Ask a question (write session log)
python 03_scripts/llm_council_runner.py --ask "How should Ghoti use an LLM council safely?" --apply

# List past sessions
python 03_scripts/llm_council_runner.py --list-sessions
```

## Next Steps for Codex Audit (N+3.62)

1. Verify `git diff --check` passes on this branch
2. Confirm LLM Council runner AST-parses and passes --status / --demo --dry-run
3. Verify router and dashboard changes do not break existing routes/sections
4. Confirm no external API calls, no secrets, no autonomous actions
5. Recommend merge to main branch after clean audit pass
