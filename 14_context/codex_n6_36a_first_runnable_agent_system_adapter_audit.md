# N+6.36A First Runnable Agent System Adapter Audit

## Verdict

**PASS / MERGE READY AFTER AUDIT HARDENING**

The Ghoti-native adapter, metadata smoke, and dual-policy validation are safe
and runnable. The external `claude-swarm` CLI was not installed or executed
and remains blocked pending a separate provider/API audit.

## Git Truth

- Starting `origin/main`: `59b70ca42e9533681498650429fb5b4b56ff0084`
- Target branch: `origin/feat/ghoti-agent-claude-n6-36a-first-runnable-agent-system-adapter`
- Target commit: `d0599f5b6f83a2e764ea4126c124a56f3ede1640`
- Audit branch: `audit/ghoti-agent-codex-n6-36a-first-runnable-agent-system-adapter`
- Audit merge/hardening commit: `3532ab3666bd20836698a707e5185fdb0d7a8e38`
- Target scope: seven additive N+6.36A adapter/docs/tests/context files
- Target and audit author/committer identity: `IvanFuentesB <IvanFuentesB@users.noreply.github.com>`
- Prohibited attribution trailers: none
- Main pushed: no; this handoff requested the audit branch

## Safe Repo Intake

- Source: `https://github.com/affaan-m/claude-swarm`
- Pinned revision: `9b1c5561157abd2d0d043758b7bfcb0319267d9f`
- License: MIT
- Classification: `sandbox-required / metadata-read-only`
- Clone location: `21_repos/third_party_runtime_sandbox/claude_swarm`
- Clone contents: gitignored and untracked
- Third-party code installed, imported, or executed: no

Static source inspection confirmed:

- `--dry-run` avoids worker-agent execution.
- It still requires `ANTHROPIC_API_KEY`.
- It calls the decomposition model.
- It writes a session record.

Therefore, the external command is not an approved safe command. The only
approved runnable path in this milestone is Ghoti's local metadata-only smoke.

## Audit Hardening

1. Changed missing/import-failed N+6.33A policy bridge behavior from allow to
   fail closed.
2. Required explicit bridge readiness and an allowing Rust-policy decision.
3. Fixed UTF-8 metadata reads so real cloned-source smoke works on Windows.
4. Restricted public check/smoke sandbox paths to the approved runtime sandbox.
5. Refused detected targets resolving outside that sandbox.
6. Replaced machine-specific output paths with repo-relative paths.
7. Fixed the PowerShell checker to fail when smoke validation fails.
8. Reclassified external `claude-swarm --dry-run` as blocked pending
   provider/API audit.
9. Added regression tests for fail-closed, containment, privacy, external
   command truth, and dual-gate evidence.

## Runtime Truth

- Ghoti adapter check: pass
- Ghoti metadata smoke: pass
- Selected target: `claude_swarm`
- Source metadata: version `0.2.0`, MIT, Python `>=3.11`
- Local adapter `simulation`: true
- Local adapter `live_execution`: false
- Live agent launch: false
- Human approval required: true
- Rust-policy bridge ready: true
- Rust-policy decision: allow for the local synthetic no-op plan
- External candidate command approved: false
- Hooks, MCP, Docker, browser/computer-use, accounts, auto-submit, secrets,
  telemetry, VM launch, and live launch: blocked

## Validation

- `git diff --check`: pass
- `git show --check --stat`: pass
- N+6.36A tests: **56 passed**
- N+6.35A tests: **56 passed**
- N+6.33A tests: **23 passed**
- N+6.29A tests: **56 passed**
- Rust workspace: **19 passed**
- Rust policy checker default-deny check: pass
- PowerShell adapter checker: pass
- Public repo security audit: **150 checks / 0 blockers / 9 warnings**
- Product launcher status: pass; localhost-only; no external/live account action
- Context pack: pass
- Repo map: pass
- GitHub contributors API: only `IvanFuentesB`
- PR #11: draft; no CI checks, reviews, or comments

## Skills Effect

- Codex Merge Gate enforced the isolated no-commit merge, attribution checks,
  validation, and audit-only push boundary.
- Safe Repo Intake caused the pinned static clone and exposed that the external
  dry-run performs a provider call and session write.
- Agent Swarm Simulator kept the approved path synthetic, empty-agent,
  human-approved, and `live_execution=false`.

## Cleanup

- Generated context-pack and repo-map residue restored.
- Third-party source remains ignored/untracked.
- No third-party code or generated validation residue committed.

## Next Safest Milestone

**N+6.37A — Provider-Free Agent-System Fixture Replay + External CLI Safety Plan**

Replay a committed synthetic plan through the adapter and policy gates. Specify
the provider/key/session-write controls required before considering any
external `claude-swarm --dry-run` invocation. Do not install or invoke the
external CLI without a separate explicit approval and audit.
