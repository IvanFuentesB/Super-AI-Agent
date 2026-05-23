/ultraplan
/goal

Continue N+4.5A Seed implementation now.

You are Claude Code. Codex is already auditing/polling in parallel, but the
implementation branch is missing because Claude has not pushed it yet. Your job
is to create, implement, validate, commit, push, and verify the feature branch.

Target branch:
feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

Current main:
origin/main — confirm with: git ls-remote origin refs/heads/main

PLANNING: Use /ultraplan for deep planning mode. Maximum planning effort.
Use the strongest available reasoning. Produce a complete, risk-checked plan
before writing any code.

EXECUTION: Use /goal for long-horizon execution. Claude Sonnet 4.6, high effort.
Work until IMPLEMENTED_AND_PUSHED or a real, confirmed blocker.

MISSION: Parallel Agent Relay Seed Pair

REQUIRED STEPS:
1. Create isolated worktree from origin/main.
   Use a path inside the repo root — never C:\w\.
   If CLAUDE.md demands stricter containment, use:
   ..\AI_Managed_Only\.claude\worktrees\<branch-slug>
2. Implement all milestone deliverables (see milestone spec above).
3. Run all validations:
   - git diff --check
   - node --check (dashboard JS files if changed)
   - python -m unittest (all test modules)
   - python 03_scripts/... --validate / --status / --json
   - pwsh 03_scripts/check_runtime_mvp.ps1
   - pwsh 03_scripts/check_dashboard_mvp.ps1
4. Write milestone report to:
   14_context/claude_n4_5a_seed_*.md
5. Commit: feat(ghoti): parallel agent relay seed pair
6. Push:   git push origin feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center
7. Verify: git ls-remote origin refs/heads/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

SAFETY RULES:
- Do not push main. Do not force-push. Never rewrite history.
- No live account actions. No cap bypass.
- No external repo clone/install/run.
- No autonomous Claude/Codex launch.
- No secrets or API keys committed.
- Stage only intentional milestone files — never git add -A.
- All writes must stay inside repo root.

CODEX AUDIT BRANCH (do NOT push — Codex handles it):
audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3

FINAL RESPONSE PACKET must include:
- Branch
- New commit hash
- Pushed yes/no
- ls-remote verification hash
- Test totals (pass/fail/error)
- Runtime check result
- Dashboard check result
- Safety summary
- Final verdict: IMPLEMENTED_AND_PUSHED or real blocker with exact error
