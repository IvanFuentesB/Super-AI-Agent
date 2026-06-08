# NEXT COMPUTER-USE ADAPTER TASK

## Current state (as of N+6.29A)

**Branch:** `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter`
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

The N+6.29A dry-run adapter contract is complete. The adapter:
- reads a proposed computer-use action plan
- validates target (local_sandbox / approved_window only)
- rejects real OS input, external URLs, secrets, auto-submit, blocked capabilities
- emits a dry-run status payload for Agent Arena
- records repo inspiration / attribution
- prepares a bridge field for the N+6.28A Rust policy checker (currently: `rust_policy_bridge_ready: false`)

## Pending merges (Codex sequence)

| Order | Branch | Audit target |
|-------|--------|-------------|
| 1st | `feat/ghoti-agent-claude-n6-27a-repo-backed-controlled-swarm-launcher` | `audit/ghoti-agent-codex-n6-27a-repo-backed-controlled-swarm-launcher` |
| 2nd | `feat/ghoti-agent-claude-n6-28a-rust-policy-checker` | `audit/ghoti-agent-codex-n6-28a-rust-policy-checker` |
| 3rd | `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter` | `audit/ghoti-agent-codex-n6-29a-computer-use-repo-backed-adapter` |

## Post N+6.28A merge: wire Rust bridge

After N+6.28A is merged, extend the adapter to pipe validated plans to the Rust policy checker:

```python
# In ghoti_computer_use_adapter.py, after _validate_plan():
import subprocess
rust_result = subprocess.run(
    ["cargo", "run", "--manifest-path", "rust/ghoti_policy_checker/Cargo.toml",
     "--", plan_path],
    capture_output=True, text=True, timeout=30
)
rust_ok = json.loads(rust_result.stdout).get("allowed", False)
```

Update `rust_policy_bridge_ready` to `True` once the bridge is wired and tested.

## Post N+6.29B merge: N+6.30A

**Mission:** Real confined DOM action in local browser sandbox (extending N+6.14A pattern).

- Target: local `file://` sandbox page
- Action: real DOM interaction in headless Chromium (127.0.0.1 only)
- Gate: approval token required before any real DOM action
- Safety: no external URL, no account, no secret, no real OS input
- Use: `03_scripts/computer_use_sandbox/confined_browser_sandbox_runner.py` (N+6.14A) as reference

## Files to check for context

| File | Purpose |
|------|---------|
| `14_context/claude_n6_29a_computer_use_repo_backed_adapter.md` | This milestone's full report |
| `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py` | Main adapter |
| `14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json` | Attribution |
| `14_context/claude_n6_14a_confined_browser_sandbox_runner.md` | N+6.14A reference for N+6.30A |
| `14_context/claude_n6_12a_ruflo_computer_use_repo_intake.md` | Original static inspection record |
