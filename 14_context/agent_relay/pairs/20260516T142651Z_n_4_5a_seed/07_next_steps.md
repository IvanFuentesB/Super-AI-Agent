# Next Steps — N+4.5A Seed: Parallel Agent Relay Seed Pair

## After Claude pushes feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

1. Codex poll detects branch (git ls-remote returns hash).
2. Codex proceeds to audit: fetch, merge --no-commit, verify deliverables.
3. Codex runs full regression suite (python -m unittest, node --check, pwsh checks).
4. Codex writes audit report to 14_context/.
5. Codex pushes audit to audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3 (fresh -3 if -2 exists — never force-push).

## After Codex audit is complete

1. Human reviews both reports on GitHub.
2. If both CLEAN PASS:
   - Approve main merge gate.
   - Run final main merge (separate merge gate process).
3. If either BLOCKED:
   - Investigate root cause.
   - Fix on the implementation branch.
   - Re-run the failing lane.

## Future: Agent Exchange / AEX

When AEX becomes available, this relay workflow will be enhanced via:
- Claude Cowork for automated implementation coordination
- The Agency for audit orchestration
- agent-skills-eval for skill benchmarking

Currently: copy-paste only. Human approval required at every step.

## Codex effort: extra-high
## Claude planning: /ultraplan max
## Claude execution: /goal Sonnet high
