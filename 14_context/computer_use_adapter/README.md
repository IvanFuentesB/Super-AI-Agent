# Computer-Use Adapter Context — N+6.29A

This folder stores schemas, examples, and attribution records for the
N+6.29A computer-use repo-backed adapter dry-run.

## Contents

| File / Folder | Purpose |
|---------------|---------|
| `action_plan_schema.json` | JSON Schema for a proposed computer-use action plan |
| `adapter_result_schema.json` | JSON Schema for the adapter's dry-run result payload |
| `repo_inspiration_manifest_n6_29a.json` | Attribution manifest: which repos were referenced and what patterns were adapted |
| `repo_inspiration_report_n6_29a.md` | Human-readable repo inspection and pattern report |
| `examples/dry_run_local_fixture_action.json` | Example plan: local sandbox fixture — expected to pass |
| `examples/blocked_external_website_action.json` | Example plan: external URL + live_browser — expected to be blocked |
| `examples/blocked_secret_input_action.json` | Example plan: secret value in type action — expected to be blocked |

## Safety invariants

- Every adapter result has `real_action_performed: false`
- `mode` is always `dry_run`
- `live_computer_use_enabled` is always `false`
- `requires_human_approval` must be `true` in every accepted plan
- `auto_submit` must be `false` in every accepted plan

## Main script

`03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py`

```
python 03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py --check --json
python 03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py \
    --plan 14_context/computer_use_adapter/examples/dry_run_local_fixture_action.json \
    --dry-run --json
```

## Dependencies (unmerged)

| Branch | Status | Impact on this folder |
|--------|--------|----------------------|
| N+6.27A (swarm_launcher) | unmerged | No files here touched |
| N+6.28A (rust policy checker) | unmerged | `rust_policy_bridge_ready: false` in all results |

The Rust policy bridge will be wired post-merge of N+6.28A.
