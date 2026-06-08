# GHOTI N+6.29A — Computer-Use Repo-Backed Adapter Dry-Run

## Overview

N+6.29A introduces a dry-run computer-use adapter contract for the Ghoti
supervised operator system. The adapter reads a proposed computer-use action plan,
validates every field against a strict safety policy, and emits a structured
dry-run status payload suitable for Agent Arena visualization.

**No real OS control is performed.** The adapter does not click, type, navigate a
browser, login to accounts, access secrets, run Docker, setup MCP, or execute any
real action. All `real_*_performed` fields in the result are always `false`.

## Milestone

- **Milestone:** N+6.29A
- **Branch:** `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter`
- **Base main:** `1bedd9e` (N+6.26B Claude swarm deep intake — confirmed on main)

## Dependency State

| Branch | Merged to main | Action |
|--------|---------------|--------|
| N+6.27B (swarm launcher) | **Yes — merged** | `03_scripts/swarm_launcher/` present on main; this branch leaves it untouched |
| N+6.28B (Rust policy checker) | **Yes — merged** | `rust/ghoti_policy_checker/` present on main; `rust_policy_bridge_ready: false` until bridge is wired |

N+6.27B and N+6.28B are both on main. The Rust bridge wiring is the next step post N+6.29B merge.

## Repo-Backed Design

The adapter is re-expressed from scratch using design patterns from five
computer-use repos statically inspected in N+6.12A. No code is copied. No repos
are cloned in this milestone.

| Repo | License | Patterns Adapted |
|------|---------|-----------------|
| TryCUA / CUA Driver | MIT | action-intent payload, sandbox isolation, capability declaration, approval gate, dry-run status |
| UI-TARS | Apache-2.0 | observation-only mode, typed action contract, blocked-action manifest, arena status block |
| Browser Harness | MIT | local fixture pattern, CDP isolation, blocked-URL guard |
| Vercel agent-browser | Apache-2.0 | capability declaration contract, approval_token shape, refused_live_actions list |
| Ruflo | MIT | coordinator/worker + declared-skill pattern, dry-run-first invariant |

Full attribution: `14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json`

## Files Added

| File | Purpose |
|------|---------|
| `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py` | Dry-run adapter (stdlib-only Python) |
| `03_scripts/computer_use_adapter/check_computer_use_adapter.ps1` | PowerShell system check |
| `14_context/computer_use_adapter/README.md` | Context folder README |
| `14_context/computer_use_adapter/action_plan_schema.json` | JSON Schema for action plans |
| `14_context/computer_use_adapter/adapter_result_schema.json` | JSON Schema for adapter results |
| `14_context/computer_use_adapter/examples/dry_run_local_fixture_action.json` | Example: passes |
| `14_context/computer_use_adapter/examples/blocked_external_website_action.json` | Example: blocked |
| `14_context/computer_use_adapter/examples/blocked_secret_input_action.json` | Example: blocked |
| `14_context/computer_use_adapter/repo_inspiration_manifest_n6_29a.json` | Attribution manifest |
| `14_context/computer_use_adapter/repo_inspiration_report_n6_29a.md` | Attribution report |
| `01_projects/runtime_mvp/tests/test_n6_29a_computer_use_repo_backed_adapter.py` | 46 unit tests |
| `14_context/claude_n6_29a_computer_use_repo_backed_adapter.md` | Context snapshot |
| `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_COMPUTER_USE_ADAPTER_TASK.md` | Handoff |
| `docs/GHOTI_N6_29A_COMPUTER_USE_REPO_BACKED_ADAPTER.md` | This document |

## Adapter Contract

### Input: Action Plan

```json
{
  "plan_id": "my_plan",
  "milestone": "N+6.29A",
  "target": "local_sandbox",
  "target_url": "file://sandbox/page.html",
  "auto_submit": false,
  "requires_human_approval": true,
  "capabilities_required": [],
  "actions": [
    { "action_id": "a1", "type": "read_fixture", "target_element": null }
  ]
}
```

### Output: Dry-Run Result

```json
{
  "ok": true,
  "milestone": "N+6.29A",
  "mode": "dry_run",
  "status": "allowed",
  "real_action_performed": false,
  "real_click_performed": false,
  "real_type_performed": false,
  "os_input_used": false,
  "secrets_accessed": false,
  "auto_submit_performed": false,
  "approval_token": null,
  "rust_policy_bridge_ready": false,
  "arena_status": { "simulation": true, "live_execution": false, ... },
  "refused_live_actions": [...],
  "safety": { "dry_run_only": true, ... }
}
```

## Validation Rules

A plan is **blocked** if any of the following are true:

- `target` is not `local_sandbox` or `approved_window`
- `target_url` has a non-empty authority (e.g. `file://hostname/...` — only `file:///` hostless local URLs are allowed)
- `target_url` uses `http/https` with a non-local hostname (allowed: `localhost`, `127.0.0.1`, `::1`)
- `auto_submit` is `true`
- `requires_human_approval` is `false` or missing
- Any `capabilities_required` entry is in the blocked set
- Any action `type` is in the blocked set (e.g. `real_click`, `login`, `navigate_url`, ...)
- Any action `value` matches a secret keyword pattern
- Any action has a secret field name (e.g. `password`, `token`, `api_key`, ...)

## Blocked Action Types

`real_click`, `real_type`, `real_key_press`, `real_mouse_move`,
`real_screenshot_upload`, `login`, `submit_form`, `auto_submit`,
`purchase`, `transfer_money`, `open_browser`, `launch_docker`,
`mcp_setup`, `install_package`, `run_shell_command`, `write_env_file`,
`access_keychain`, `copy_token`, `read_secret_file`, `navigate_url`,
`execute_script`

## Blocked Capabilities

`live_browser`, `real_os_input`, `account_login`, `external_web`, `docker`,
`mcp`, `shell`, `secrets`, `auto_submit`, `purchase`, `money_transfer`,
`mass_messaging`, `file_system_write_outside_sandbox`

## CLI Usage

```bash
# System check
python 03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py --check --json

# Allowed plan
python 03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py \
    --plan 14_context/computer_use_adapter/examples/dry_run_local_fixture_action.json \
    --dry-run --json

# Blocked plan
python 03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py \
    --plan 14_context/computer_use_adapter/examples/blocked_external_website_action.json \
    --dry-run --json

# Run tests
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_29a_*.py" -v
```

## Rust Policy Bridge (Post-N+6.29B)

N+6.28B (`rust/ghoti_policy_checker/`) is merged on main. Once this branch
(N+6.29B) is merged, the adapter should be extended to pipe validated plans to
the Rust policy checker for a second-pass memory-safe denial layer:

```bash
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- <plan.json>
```

Until the bridge is wired, `rust_policy_bridge_ready: false` is reported in every result.

## Safety Invariants

- `real_action_performed` is always `false`
- `mode` is always `dry_run`
- `live_computer_use_enabled` is always `false`
- `live_browser_enabled` is always `false`
- `approval_token` is always `null` (no real execution without human approval)
- No subprocess, shell, Docker, MCP, or network calls
- No secrets, tokens, or credentials read or written
- Pure Python standard library; no third-party dependencies

## Next Steps for Codex

1. ~~Audit N+6.27B (swarm launcher) → merge~~ — **done**
2. ~~Audit N+6.28B (Rust policy checker) → merge~~ — **done**
3. Audit this branch (N+6.29B) → merge → wire Rust policy bridge
3. Then wire N+6.29A's Rust bridge (post both merges)
4. N+6.30A: Real confined DOM action in local browser (extending N+6.14A pattern)
