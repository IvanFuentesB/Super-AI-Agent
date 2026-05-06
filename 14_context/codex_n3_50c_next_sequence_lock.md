# Codex N+3.50C - Next Sequence Lock

Milestone: N+3.50C - Dashboard/Ruflo/Gemma parallel audit lane

Date: 2026-05-06

## Current Verdict

Verdict: CONDITIONAL SAFE PLAN.

The N+3.50 direction is correct if Claude preserves these boundaries:

- dashboard is read-only
- prompt/context packs are dry-run-first
- Gemma worker writes draft artifacts only
- Ruflo install gate does not run install without explicit `--apply`
- no runtime Ruflo wiring
- no live account actions
- no external browser/operator automation
- no secrets

## Exact Next Claude Recommendation

Claude should finish and push:

```text
feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
```

Expected implementation focus:

- `03_scripts/ghoti_dashboard.py`
- `03_scripts/ruflo_install_gate.py`
- `03_scripts/gemma_compact_memory_worker.py`
- dashboard read-only route/card
- prompt bus context packs
- Obsidian open/check polish
- configs under `23_configs/`
- docs under `14_context/`

Do not broaden into live tool execution.

## Exact Next Codex Recommendation

After Claude branch exists on origin:

```text
N+3.50D - Audit actual Claude N+3.50 implementation
```

Codex should run the validation commands from `14_context/codex_n3_50c_merge_plan.md`, inspect every changed file, and only then decide PASS / CONDITIONAL PASS / FAIL.

## Exact Next ChatGPT / Operator Recommendation

ChatGPT/operator should:

1. Wait for Claude to push `feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma`.
2. Ask Codex to run the actual implementation audit.
3. Merge Claude only if Codex passes or conditional-passes it.
4. Merge Codex audit docs after Claude merge.
5. Do not run Ruflo install until the install gate is reviewed.

## Next Milestone Toward 90%+

If N+3.50 lands cleanly, next milestone should be:

```text
N+3.51 - Supervised Local Orchestrator Retrospective + Merge Assistant + First Ruflo Install Gate Execution
```

Scope:

- run Ruflo install gate only if approved
- add merge readiness assistant
- improve lane status beacons
- improve prompt/context pack dashboard
- audit generated Gemma drafts and compact memory promotion

Still not allowed:

- Ruflo swarm launch
- MCP launch
- live accounts
- browser/desktop operator control
- email/social/payment/job/giveaway actions

## Hard Stop Conditions

Stop if Claude branch:

- adds account connectors
- reads `.env` or credentials
- runs npm install automatically without approval
- starts Ruflo/MCP/swarm processes
- makes dashboard mutation buttons
- makes Gemma output canonical automatically
- stages `node_modules`
- deletes source memory files
- touches unrelated local dirt
