# Ghoti N+6.29A — Computer-Use Repo-Backed Adapter Dry-Run (Report)

## Verdict

IMPLEMENTED_AND_PUSHED

## Lane

- **Branch:** `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter`
- **Worktree:** `<repo>/.claude/worktrees/n6_29a_computer_use_repo_backed_adapter` (remote execution; created as branch from origin/main)
- **Base main:** `1bedd9e` (docs: finalize n6.26b merge gate — N+6.26B Claude swarm deep intake confirmed)
- **Commit:** `feat(ghoti): add computer-use repo-backed adapter dry run`
- **Codex audit target branch:** `audit/ghoti-agent-codex-n6-29a-computer-use-repo-backed-adapter`

## Start Condition Verification

- `git fetch origin --prune` completed.
- `origin/main` = `1bedd9e` (N+6.26B confirmed: Claude swarm deep intake).
- N+6.27A (`feat/ghoti-agent-claude-n6-27a-repo-backed-controlled-swarm-launcher`) **not merged** →
  `03_scripts/swarm_launcher/` and `14_context/swarm_launcher/` left completely untouched.
- N+6.28A (`feat/ghoti-agent-claude-n6-28a-rust-policy-checker`) **not merged** →
  `rust/ghoti_policy_checker/` left completely untouched; `rust_policy_bridge_ready: false` in all results.
- Clean branch created from `origin/main`; no dirty primary worktree edits.

## Mission

Build a dry-run computer-use adapter contract using the five computer-use repos
statically inspected in N+6.12A as design reference. No repos are re-cloned.
No third-party code is copied. The adapter validates proposed action plans and
emits a dry-run status payload; it performs no real OS action.

## Inspected Repos (N+6.12A static record; no new clones in N+6.29A)

| Repo | License | Commit at Inspection | Patterns Adapted |
|------|---------|---------------------|-----------------|
| TryCUA / CUA Driver | MIT | 4c54f43 | action-intent payload, sandbox isolation, capability declaration, approval gate, dry-run status |
| UI-TARS | Apache-2.0 | source-needed (N+5.0A context used) | observation-only mode, typed action contract, blocked-action manifest, arena status block |
| Browser Harness | MIT | 6d20866 | local fixture, CDP isolation, blocked-URL guard |
| Vercel agent-browser | Apache-2.0 | b4f2f37 | capability declaration contract, approval_token, refused_live_actions list |
| Ruflo | MIT | f57b698 | coordinator/worker + declared-skill, dry-run-first invariant |

No code copied. No repos installed or executed. Attribution:
`14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json`.

## Files Added

- `docs/GHOTI_N6_29A_COMPUTER_USE_REPO_BACKED_ADAPTER.md`
- `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py` (stdlib-only Python)
- `03_scripts/computer_use_adapter/check_computer_use_adapter.ps1`
- `14_context/computer_use_adapter/README.md`
- `14_context/computer_use_adapter/action_plan_schema.json`
- `14_context/computer_use_adapter/adapter_result_schema.json`
- `14_context/computer_use_adapter/examples/dry_run_local_fixture_action.json`
- `14_context/computer_use_adapter/examples/blocked_external_website_action.json`
- `14_context/computer_use_adapter/examples/blocked_secret_input_action.json`
- `14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json`
- `14_context/computer_use_adapter/repo_inspiration_report_n6_29a.md`
- `01_projects/runtime_mvp/tests/test_n6_29a_computer_use_repo_backed_adapter.py`
- `14_context/claude_n6_29a_computer_use_repo_backed_adapter.md` (this report)
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_COMPUTER_USE_ADAPTER_TASK.md`

## Files NOT Modified (dependency isolation)

- `03_scripts/swarm_launcher/` — untouched (N+6.27A unmerged)
- `14_context/swarm_launcher/` — untouched (N+6.27A unmerged)
- `rust/ghoti_policy_checker/` — untouched (N+6.28A unmerged)
- All other pre-existing files — untouched

## Adapter Summary

`ghoti_computer_use_adapter.py` (stdlib-only):

- **`--check --json`** → system readiness check: all live/real/secret flags false,
  Rust bridge not yet ready, N+6.27A/28A dependencies documented.
- **`--plan <file> --dry-run --json`** → validates plan:
  - target must be `local_sandbox` or `approved_window`
  - target_url must be `file://` or `localhost`/`127.0.0.1`
  - `auto_submit` must be `false`; `requires_human_approval` must be `true`
  - capabilities_required must not contain blocked capabilities
  - action types must be from the allowed set
  - action values must not contain secret/token keywords
  - action fields must not use secret field names
  - emits `status: allowed` or `status: blocked` with full reasons list
  - `real_action_performed`, `real_click_performed`, `real_type_performed`,
    `os_input_used` are always `false`
  - includes `arena_status` block (`simulation: true`, `live_execution: false`)
  - includes `refused_live_actions` canonical list (17 entries)
  - includes `safety` block with all invariants

## Validation Results

| Test | Result |
|------|--------|
| `python -m unittest discover -p "test_n6_29a_*.py" -v` | 46 passed, 0 failed |
| `--check --json` | ok: true, all live/real flags false |
| `--plan dry_run_local_fixture_action.json --dry-run --json` | status: allowed, 4 dry_run_actions |
| `--plan blocked_external_website_action.json --dry-run --json` | status: blocked, 5 blocked_reasons |
| `git diff --check` | clean |

## Refused Live Actions (enforced)

- real OS click or mouse move
- real OS keyboard input
- live web browser launch or control
- account login or session management
- external website navigation
- secrets / tokens / cookies / auth files
- auto-submit / auto-post / auto-paste
- purchase / payment / money transfer
- Docker container launch
- MCP server setup or activation
- package installation
- shell command execution
- keychain or credential store access
- remote API call
- screenshot upload to external service
- mass messaging
- file system writes outside sandbox

## Rust Policy Bridge (deferred)

`rust_policy_bridge_ready: false` in all results. Post-merge of N+6.28A, the
adapter's `--plan --dry-run` should pipe the validated plan JSON to:
```
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- <plan.json>
```

## Next Steps for Codex

1. Audit N+6.27A → merge as N+6.27B
2. Audit N+6.28A → merge as N+6.28B
3. Audit N+6.29A → merge as N+6.29B (target: `audit/ghoti-agent-codex-n6-29a-computer-use-repo-backed-adapter`)
4. Post both merges: wire Rust bridge in adapter
5. N+6.30A: Real confined DOM action extending N+6.14A pattern
