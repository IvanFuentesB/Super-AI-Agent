# Ghoti Codex Productivity Setup

Codex is Ghoti's audit, verification, safe-continuation, and merge-gate lane.
Its source-of-truth config is
`23_configs/assistant_productivity/codex_productivity.example.json`; ready
prompts live in `14_context/assistant_productivity/codex_ready_prompts.md`.

## Use now

- Activate `karpathy-guidelines`, `context-engineering`, `verification-loop`,
  `parallel-execution-optimizer`, `codex-merge-gate`, `safe-repo-intake`, and
  `token-saving-audit` when their task matches.
- Treat `security-review`, `rust-validator-audit`, `merge-gate`, and
  `repo-intake-audit` as capability names mapped to existing repo checks or
  available skills; do not pretend missing skills are installed.
- Work in isolated worktrees and reproduce builder claims before merging.
- Use the "finish incomplete Claude branch" prompt when credits interrupt a
  builder lane.

Codex must not bypass approval gates, write secrets, perform live account
actions, or push main outside an explicit clean merge gate.
