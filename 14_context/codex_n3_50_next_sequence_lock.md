# Codex N+3.50 - Next Sequence Lock

Milestone: N+3.50B - Audit Claude N+3.49A and prepare merge safety verdict

Date: 2026-05-06

## If N+3.49A Is Merged

Next Claude should implement:

```text
N+3.50A - Dashboard / Local Orchestrator Card + Ruflo Install Gate Runner
```

Scope:

- Add a read-only dashboard card for the local orchestrator, prompt bus, lane locks, Obsidian status, local worker routes, and Ruflo/Gemma readiness.
- Add a Ruflo install gate runner that is dry-run by default and only runs `npm ci --ignore-scripts` in the approved eval directory after explicit `--apply`.
- Fix local worker router course/certificate keyword coverage.
- Re-check Ollama/Gemma model truth and avoid pulling models without explicit user approval.
- Keep Ruflo runtime unwired.

## If N+3.49A Fails Merge Or Validation

Next Claude should fix only the specific failing issue.

Do not broaden the branch. Do not add external tools. Do not install npm dependencies until the install gate is explicitly approved.

## Next Future Milestone

Recommended sequence:

1. Merge N+3.49A if operator accepts conditional pass.
2. Claude N+3.50A - dashboard/local orchestrator card + Ruflo install gate runner.
3. Codex N+3.50C - audit dashboard/install gate implementation.
4. Claude N+3.51 - Ruflo isolated install + local help smoke + no runtime wiring, unless N+3.50A already includes the install gate execution.

## Ruflo Position

Ruflo should advance from ignored/research-only to isolated install-gated evaluation.

Allowed next:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

Only after explicit approval and only with logs.

Still forbidden:

- global install
- runtime wiring
- swarm execution
- MCP server launch
- Claude API keys
- live accounts
- browser/desktop control
- hidden background processes

## Current Capability Estimate

If N+3.49A lands:

- current practical capability moves from about 68% to about 71-72%
- N+3.50A dashboard plus install gate can move it toward 74-75%
- actual 80% still requires Gemma compression, Obsidian refresh, merge assistant, and safer deterministic automation runner

## Exact Next ChatGPT / Operator Action

Prepare the merge prompt with:

- merge branch: `origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke`
- validation commands from `14_context/codex_n3_50_merge_plan.md`
- acceptance of conditional pass caveats
- no npm install during merge
- no live actions
