# 14_context/cua_trial — N+6.34A CUA Isolated Trial Context

**Milestone:** N+6.34A
**Status:** metadata smoke only — no live CUA execution

## What this folder contains

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `cua_trial_status_schema.json` | JSON schema for the trial adapter's status output |

## What is real in N+6.34A

- TryCUA/CUA cloned (depth=1, no hooks) into the gitignored sandbox
  `21_repos/third_party_runtime_sandbox/cua` (commit `2925b491`, June 2025).
- LICENSE.md confirmed MIT. Package name: `cua-workspace`. 175 shell scripts.
- Runtime requirements inspected: Docker/QEMU/Lume VM + Python >=3.12 + live OS
  websocket connections + posthog telemetry on import.
- A dry-run observation plan generated and validated through the N+6.33A dual gate
  (Python adapter + Rust policy checker). Plan: accepted.

## What is NOT live

- No CUA code imported or executed.
- No Docker / QEMU / Lume VM.
- No MCP server.
- No real OS click/type/hotkey.
- No browser control.
- No account login.
- No secrets/tokens/cookies.
- No auto-submit.
- Telemetry NOT triggered (cua-core posthog fires on package import; we never import).

## Sandbox path

`21_repos/third_party_runtime_sandbox/cua` — gitignored via `.gitignore:149`.

To refresh:
```
git -C 21_repos/third_party_runtime_sandbox/cua pull --ff-only
```

To initial clone:
```
git clone --depth=1 --no-tags --template="" \
  https://github.com/trycua/cua \
  21_repos/third_party_runtime_sandbox/cua
```

## Why CUA is first

- It directly matches the computer-use domain (N+6.29A adapter contract was
  designed with CUA patterns in mind).
- The Ghoti adapter's action-intent contract, capability declaration, sandbox
  isolation, and approval gate all map to CUA's own design.
- CUA has the clearest isolation boundary (Docker/Lume VMs) that can be
  progressively enabled behind the approval gate.

## Relation to other repos (none executed here)

| Repo | Role | Status |
|------|------|--------|
| TryCUA/CUA | First engine trial | sandbox cloned; metadata only |
| UI-TARS | Observation-only mode patterns | static inspection (N+5.0A, N+6.12A) |
| Browser Harness | Local fixture / CDP isolation | static inspection (N+6.12A) |
| Vercel agent-browser | Capability gate patterns | static inspection (N+6.12A) |
| Ruflo | Coordinator/worker contract | static inspection; trial planned post-CUA |

## Next step

An actual CUA sandbox execution trial:
- Requires a separate audited milestone.
- Requires human approval.
- Must use an isolated OS profile / VM with no Ghoti repo access, no real accounts,
  no secrets, and no environment other than a scratch repo.
- Must still pass the N+6.33A dual gate.
