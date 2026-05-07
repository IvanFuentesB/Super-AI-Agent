# Codex N+3.62 Next Sequence Lock

## Current Lock

Do not merge.

N+3.62 is PENDING TARGET BRANCH because:

`origin/feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness`

does not exist after fetch and eight polling attempts.

## Exact Next Claude Recommendation

Next Claude task:

`N+3.61A Recovery - Push LLM Council Clean Merge Readiness Branch`

Claude should create or push:

`feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness`

Required scope:

- Clean inherited N+3.58 documentation whitespace blockers.
- Add `03_scripts/llm_council_runner.py`.
- Add `23_configs/llm_council.example.json`.
- Add local-only LLM Council docs.
- Update dashboard and router truthfully.
- Preserve all existing safety gates.

Required validation before Claude reports done:

```powershell
git fetch origin
git rev-parse origin/feat/ghoti-agent-claude-n3-58-fix-obsidian-dashboard-whitespace
python -c "import ast, pathlib; files=['03_scripts/llm_council_runner.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/obsidian_probe.py','03_scripts/ghoti_merge_assistant.py','03_scripts/repo_language_inventory.py','03_scripts/rust_readiness_probe.py','03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/prompt_bus.py','03_scripts/agent_lane_status.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/llm_council_runner.py --status
python 03_scripts/llm_council_runner.py --demo --dry-run
python 03_scripts/llm_council_runner.py --ask "How should Ghoti use an LLM council safely?" --dry-run
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/local_worker_router.py --recommend --task "use Karpathy LLM Council to compare model answers"
git diff --check
git diff --cached --check
git push origin feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness
```

## Exact Next Codex Recommendation

After the remote target exists, rerun:

`N+3.62 - LLM Council Clean Merge Readiness Audit`

Do not audit unrelated branches such as:

- `feat/council-control-foundation`
- `feat/security-publishability-truth-council`

unless the operator explicitly changes the target branch.

## Direct Truth Lock

- Inherited whitespace blocker fixed? Unknown on N+3.61A; target missing.
- LLM Council implemented? Unknown; target missing.
- Karpathy-style three-stage flow present? Unknown; target missing.
- External API calls enabled? Unknown on target; must be NO by default.
- OpenRouter key stored? Unknown on target; must be NO.
- Ollama required? Unknown on target; local demo should be able to report availability truthfully.
- CC/Codex automatic? NO on the known Ghoti design; target must not claim otherwise.
- Ruflo runtime wired? NO on the known Ghoti design; target must preserve this.
- Java tracked? No evidence from known prior audits; target must preserve language truth.
- Rust tracked? No evidence from known prior audits; target must preserve language truth.
- Rust rewrite now? NO.

## Operator Command Now

Do not merge. First verify or push the exact target:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git fetch origin
git rev-parse origin/feat/ghoti-agent-claude-n3-61-llm-council-clean-merge-readiness
```

If that fails, Claude/operator must push the N+3.61A branch before Codex can audit it.
