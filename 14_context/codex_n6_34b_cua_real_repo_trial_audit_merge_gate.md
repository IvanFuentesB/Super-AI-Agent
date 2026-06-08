# N+6.34B CUA Real Repo Trial Audit Merge Gate

## Verdict

**PASS / MERGE READY**

The N+6.34A CUA isolated real-repo trial was audited in a clean repo-contained
worktree and merged into the local main candidate. The implementation remains
metadata-only, observation-only, dry-run only, and default-deny. No CUA code was
committed, imported, or executed.

## Merge Record

- Starting `origin/main`: `d074566a51048fc9ddc159534b2023cd1365a3cb`
- Target branch: `origin/feat/ghoti-agent-claude-n6-34a-cua-real-repo-trial`
- Target commit audited: `817aa8032c05e1ab168148db38ec0860abcd07c1`
- Local merge commit: `dc2d694c0618a14095605e46ea6b59c044b3bafe`
- Merge message: `merge(ghoti): land cua isolated trial adapter`
- Merge author/committer: `IvanFuentesB <IvanFuentesB@users.noreply.github.com>`
- Target and main author/committer scans: no Claude or `noreply@anthropic.com`
- Target and merge commit messages: no AI attribution trailers
- Old bad author commit `3a10177cc3595c9ae435fb807c2c0bbd0d214f89`:
  not reachable from the candidate main

## CUA Repo Intake Status

- Source: `https://github.com/trycua/cua`
- Reported inspected revision:
  `2925b491c20595ae850e3e4a05d6fea188e8f40a`
- GitHub API verified that revision exists.
- GitHub API reports `trycua/cua` as public, active, and MIT licensed.
- Fresh audit worktree clone status: absent, as expected for gitignored runtime
  sandbox content.
- Required sandbox location:
  `21_repos/third_party_runtime_sandbox/cua`
- Gitignore rule verified.
- Tracked third-party CUA files: none.
- CUA imports/execution: none.
- CUA shell scripts executed: none.
- Docker, QEMU, Lume, KASM, and VM launch: disabled and denied.
- PostHog telemetry: descriptive risk note only; not imported or triggered.

## Safety Review

- Adapter mode: `dry_run`
- Observation plan: local sandbox only
- Human approval: required
- Rust policy bridge: active for plan validation
- Agent Arena-shaped bridge status: `simulation: true`,
  `live_execution: false`
- Live OS click/type/hotkey: disabled and denied
- Live browser/external website action: disabled and denied
- Account login/session: disabled and denied
- Auto-submit: disabled and denied
- MCP: disabled and denied
- Secrets/tokens/cookies/auth files: disabled and denied
- CUA package code and third-party scripts: not executed

The audit gate fixed two narrow issues before the merge commit:

1. Temporary JSON bridge plans are now deleted after validation, preventing
   rejected secret-bearing plans from remaining in the temp directory.
2. The PowerShell checker was made ASCII-safe so Windows PowerShell 5 parses and
   runs it correctly.

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- Rust workspace tests: 19 passed, 0 failed
- Rust policy checker `--check`: PASS; unsafe built-in plan denied by default
- N+6.34A tests: 45 discovered, 36 passed, 9 metadata-smoke tests skipped
  because the gitignored CUA clone is absent in the fresh gate worktree
- N+6.33A tests: 23 passed, 0 failed
- N+6.32A attribution tests: 9 passed, 0 failed
- CUA Python adapter `--check --json`: PASS; all live flags false
- CUA PowerShell checker: PASS
- Public repo security audit: 150 checks, 0 blockers, 8 warnings for human review
- Product launcher status: PASS; localhost-only and external API disabled
- Context pack: PASS
- Repo map: PASS
- GitHub contributors API: only `IvanFuentesB`
- PR #9: open, no reviews, no comments
- Generated context-pack/repo-map residue: restored
- Worktree before report: clean

## Skills Applied

- Codex Merge Gate: isolated no-commit merge rehearsal, metadata checks,
  validation, and remote push gate.
- Safe Repo Intake: source/revision/license verification, static-only CUA
  boundary, and no-vendored-code check.
- Agent Swarm Simulator: verified simulation-only bridge status and no live
  execution path.
- Token Saving Audit: kept validation focused on the affected CUA, Rust,
  attribution, security, and product-status lanes.

## Next Milestone

**N+6.35A - CUA Isolated VM Trial Readiness + Human Approval Gate**

That milestone should review isolation, telemetry suppression, disposable test
data, kill switch, and approval steps before any separately approved live VM
trial. It must not grant CUA access to the Ghoti repo, real accounts, secrets, or
external production systems.
