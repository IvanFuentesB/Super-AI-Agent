# Codex Audit + Merge Gate -- N+6.38B Claude-Swarm Fixture Replay

**Milestone:** N+6.38B (merge gate for N+6.38A)
**Date:** 2026-06-09
**Verdict:** PASS -- merged to main
**Audited target:** `feat/ghoti-agent-claude-n6-38a-claude-swarm-fixture-replay`
**Target SHA:** `0c0fc9e26e5add2bf1d049c2f22da1bcee6f4a81`
**Merge commit:** `51b59d3cfe4df4246c4c83557a802114077c5278`

---

## Background

N+6.38A delivered a provider-free claude-swarm fixture replay subsystem.
N+6.38B was BLOCKED across prior audits by:

1. `/etc/passwd.json` not rejected on Windows (substring match against the
   raw path string failed when `Path()` produced backslash form).
2. PowerShell StrictMode failure: `$presentKeys.Count` was unsafe when the
   `Where-Object` pipeline returned `$null` or a scalar.
3. Stale start-condition text claiming N+6.36B / N+6.37B were not merged.

The latest hardening pass on the target branch addresses all three. This
gate audited the remote branch and merged after full validation.

---

## Old blocked-commit comparison

| SHA | Relationship to target |
|-----|------------------------|
| `e7258bc` (original impl) | ancestor of target -- superseded |
| `611a7a9` (prior ascii fix) | ancestor of target -- superseded |
| `0c0fc9e` (target) | newest -- includes path + StrictMode hardening |

Target verified to contain `_BLOCKED_PATH_NORMS`, forward-slash
normalisation, UNC guard, and parent-traversal guard before proceeding.

---

## Path rejection audit (portable, host-OS independent)

Validation normalises the path to forward slashes and lowercases it before
matching, so Unix-style dangerous paths are rejected on every platform.

| Path | Result |
|------|--------|
| `/etc/passwd` | REJECTED |
| `/etc/passwd.json` | REJECTED (`/etc/`, `/passwd`) |
| `/root/.ssh/id_rsa` | REJECTED |
| `/root/.ssh/id_rsa.json` | REJECTED |
| `/home/user/.ssh/id_rsa.json` | REJECTED |
| `C:\Users\Name\.ssh\id_rsa.json` | REJECTED |
| `C:\Windows\System32\config\SAM.json` | REJECTED |
| `\\server\share\secret.json` | REJECTED (UNC) |
| `../../etc/passwd.json` | REJECTED (traversal) |
| `../secret.json` | REJECTED (traversal) |
| temp-dir `fixture.json` | ALLOWED |
| default sample fixture | ALLOWED |

Covering unit tests:
- `TestBlockedPaths.test_etc_path_blocked` -- `/etc/passwd.json`
- `TestBlockedPaths.test_etc_passwd_no_ext_blocked` -- `/etc/passwd`
- `TestBlockedPaths.test_root_ssh_blocked`
- `TestBlockedPaths.test_home_ssh_blocked`
- `TestBlockedPaths.test_windows_system32_blocked` -- Windows absolute path
- `TestBlockedPaths.test_windows_ssh_blocked`
- `TestBlockedPaths.test_unc_path_blocked` -- UNC path
- `TestBlockedPaths.test_parent_traversal_blocked` -- parent traversal
- `TestBlockedPaths.test_valid_json_path_allowed` -- safe path passes

---

## PowerShell StrictMode + ASCII audit

- `Set-StrictMode -Version Latest` remains enabled.
- `$taskCount = if ($fixtureJson.tasks) { @($fixtureJson.tasks).Count } else { 0 }`
  -- pipeline output wrapped with `@(...)` before `.Count`.
- `$presentKeys = @($apiKeyVars | Where-Object { ... })`
  -- safe under StrictMode for null / scalar / single-item / many-item.
- No `Invoke-Expression`. No `Start-Process`. No external CLI call.
- Checker non-ASCII byte count: **0**.
- ASCII regression: `TestAsciiSafe` (4 tests) including
  `test_all_milestone_files_ascii_only` sweeping all 8 milestone files.

PowerShell is not present in this Linux gate environment, so the checker was
not executed; StrictMode correctness is verified by source inspection and
ASCII safety by byte scan + regression test.

---

## Execution-primitive safety scan

`TestSourceSafety` proves the fixture replay path contains no execution
primitives (needles assembled dynamically to avoid self-trigger):

- `test_no_subprocess_launch` -- AST: no `subprocess.run/call/Popen`
- `test_no_exec_primitives_in_wrapper` -- no `os.system(`, `os.popen(`,
  `import subprocess`, `subprocess.run(`, `subprocess.Popen(`, `docker run`
- `test_no_exec_primitives_in_ps1` -- no `Invoke-Expression`, `Start-Process`
- `test_wrapper_does_not_import_claude_swarm`
- `test_no_third_party_code_committed`

The N+6.37B safety conclusion is preserved: `external_cli_execution` and
`provider_api_calls` remain documented as BLOCKED; the wrapper never executes
claude-swarm and never imports subprocess.

---

## Stale status correction

`_run_check()` `start_conditions` now reports:

| Key | Value |
|-----|-------|
| `n6_35b_on_main` | true |
| `n6_36b_on_main` | true |
| `n6_37b_on_main` | true |
| `n6_38b_on_main` | false (pending at audit time) |

Covered by `TestCheckMode.test_check_start_conditions_accurate`. Docs and
context snapshot updated to the same gate status.

---

## Fixture replay behavior (preserved)

| Property | Value |
|----------|-------|
| accepted | true |
| task_count | 5 |
| parallel_groups | 3 |
| overlap_count | 0 |
| simulation | true |
| live_execution | false |
| external_cli_executed | false |
| provider_called | false |
| api_key_used | false |
| live_agent_launch | false |

---

## Validation results (merged tree)

| Check | Result |
|-------|--------|
| `test_n6_38a_*` | 61 tests OK |
| `test_n6_37a_*` | 51 tests OK |
| `test_n6_36a_*` | 56 tests OK |
| `public_repo_security_audit.py --run` | `blocking_findings: []`, ok |
| launcher `--status` | ok |
| launcher `--context-pack` | ok |
| launcher `--repo-map` | ok |
| `/etc/passwd.json` rejection | REJECTED |
| ASCII scan (3 core files) | 0 non-ASCII, exit 0 |
| `git diff --check` | clean |
| `git show --check HEAD` | clean |

Merge added exactly 8 new files; no existing main file modified; no
generated-file pollution committed.

---

## Contributor / authorship

All target commits and the merge commit authored and committed by
IvanFuentesB <IvanFuentesB@users.noreply.github.com>. No
`noreply@anthropic.com`, no Claude/GPT co-author or contributor wording, no
AI attribution trailers on main or the target branch. (GitHub contributors
API not queried this run -- `gh`/MCP unavailable; git log is authoritative
for landed history.)

---

## Safety verdict

SAFE. No external CLI executed. No provider/API key used. No provider/model
calls. No agents launched. No account login. No browser/computer-use. No MCP.
No hooks. No auto-submit. No secrets. No third-party code committed. No real
local paths in committed files. PowerShell checker ASCII-clean.

---

## Next milestone

N+6.39A -- Obsidian Memory Bridge. Now unblocked (N+6.36B, N+6.37B, N+6.38B
all on main). NOT started in this run.
