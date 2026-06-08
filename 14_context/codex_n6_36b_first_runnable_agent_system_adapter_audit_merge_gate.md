# N+6.36B First Runnable Agent System Adapter Merge Gate

## Verdict

**PASS / MERGED LOCALLY / READY TO PUSH MAIN**

## Git Truth

- Starting `origin/main`: `59b70ca42e9533681498650429fb5b4b56ff0084`
- Hardened source branch: `origin/audit/ghoti-agent-codex-n6-36a-first-runnable-agent-system-adapter`
- Hardened source tip: `7702ababb4cba1d10479c0b21cee02a75a6a517b`
- Required hardening commit included: `3532ab3666bd20836698a707e5185fdb0d7a8e38`
- Context-pack writer fix: `0c7d2da5f1a2f1abf846e325a4b04eec2f3726f4`
- N+6.36B merge commit: `b4646cd4c0029d580ae354613c96ca0849076758`
- Author and committer: `IvanFuentesB <IvanFuentesB@users.noreply.github.com>`
- Prohibited attribution trailers: none

## Context-Pack Fix

The active Hermes Python 3.11 interpreter could read the repo but could not
create repo-local files on this Windows host. The launcher now selects an
already-installed local Python only after a fixed-argv, self-cleaning,
repo-local write probe. This is used for context-pack and repo-map writes.

- No shell command string
- No install or download
- No network or provider call
- No machine-specific path committed
- Regression tests: 2 passed
- Launcher context-pack: passed
- Launcher repo-map: passed

## Adapter Safety

- Fail-closed policy bridge: enabled
- Sandbox containment and path privacy: enabled
- PowerShell checker failure propagation: enabled
- `claude-swarm` code imported or executed: no
- External candidate command approved: no
- Provider key/API used: no
- Agents launched: no
- Third-party code committed: no
- Live launch, hooks, MCP, browser/computer-use, account actions, secrets, and
  auto-submit: blocked
- Agent Arena-shaped output: `simulation=true`, `live_execution=false`

## Validation

- N+6.36A: 56 passed, 14 clone-dependent metadata tests skipped in fresh worktree
- N+6.36B context-pack regression: 2 passed
- N+6.35A: 56 passed
- N+6.33A: 23 passed
- N+6.29A: 56 passed
- Rust workspace: 19 passed
- Rust policy checker default-deny check: passed
- Adapter PowerShell checker: passed
- Launcher status/context-pack/repo-map: passed
- Public security audit: 150 checks, 0 blockers
- `git diff --check` and `git show --check`: passed

## Cleanup

- Generated context-pack and repo-map residue restored.
- No third-party sandbox contents tracked.
- Worktree clean before report commit.

## Next Gate

Audit N+6.37A isolated dry-run wrapper. Do not execute the external
`claude-swarm` CLI; its nominal dry-run requires provider/API work before the
dry-run skip.
