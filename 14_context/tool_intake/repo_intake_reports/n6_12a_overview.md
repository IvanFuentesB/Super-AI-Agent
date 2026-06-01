# N+6.12A Repo Intake Overview - Ruflo + Computer-Use

**Milestone:** N+6.12A - Ruflo + Computer-Use Repo Static Clone/Inspect/Extract
**Base main:** `0edba03`
**Mode:** `static_inspection_only / not_runtime_wired / no_execution / no_install`

This is the first milestone where Ghoti treats external repos as **source material**:
clone for read-only inspection, check the license, document useful patterns, and -
only where allowed and safe - re-express one pattern with attribution. Nothing is
installed, executed, imported, or wired into the runtime.

## What was cloned and inspected

Clones live under `21_repos/third_party_static/` and are **git-ignored** (never
staged, never installed, never executed). Commit SHAs are recorded for
reproducibility. The static inspector is
`03_scripts/external_repo_static_intake.py` (standard library only; reads files,
runs nothing).

| Candidate | License | Cloned | Commit | Files scanned | Decision |
|-----------|---------|--------|--------|---------------|----------|
| Ruflo (`ruvnet/ruflo`) | MIT | yes | `f57b698` | 4336 | Pattern re-expressed with attribution (no code copied) |
| TryCUA / CUA Driver (`trycua/cua`) | MIT | yes (partial Win checkout) | `4c54f43` | 2185 | Patterns documented, no code copied |
| Browser Harness (`browser-use/browser-harness`) | MIT | yes | `6d20866` | 150 | Patterns documented, no code copied |
| Vercel agent-browser (`vercel-labs/agent-browser`) | Apache-2.0 | yes | `b4f2f37` | 275 | Patterns documented, no code copied |
| UI-TARS | unknown | no | - | - | Source-needed (do not guess the URL) |
| Computer-use stack | n/a | n/a | - | - | Umbrella; members tracked separately |
| Browser-use (`browser-use/browser-use`) | MIT | no | - | - | Deferred (blocked priority; stealth/cloud positioning) |

## Safety posture (verified by the inspector on every run)

```
executed_third_party_code: false
imported_third_party_modules: false
installed_dependencies: false
network_used: false
only_standard_library: true
read_only: true
```

Every candidate in the manifest is `safe_to_run: false` and `runtime_wired: false`.

## What this milestone produced

- **Manifest:** `14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json`
- **Static inspector:** `03_scripts/external_repo_static_intake.py`
- **Adapter contracts (disabled stubs):** `03_scripts/external_adapters/ruflo_adapter_contract.py`,
  `03_scripts/external_adapters/computer_use_adapter_contract.py`, and their README.
- **Per-repo reports:** this folder (`14_context/tool_intake/repo_intake_reports/`).
- **Doc:** `docs/GHOTI_N6_12A_RUFLO_COMPUTER_USE_REPO_INTAKE.md`.
- **Test:** `01_projects/runtime_mvp/tests/test_n6_12a_ruflo_computer_use_repo_intake.py`.

## What stays disabled

Live browser control, desktop control, click/type/hotkeys, container runtimes
(Docker/QEMU/KASM), model-provider/network calls, MCP enablement, installs, and any
execution of third-party code. The one extraction (Ruflo's coordinator/worker +
local-memory hand-off pattern) is an inert, default-disabled contract behind a
feature flag and the global kill switch. Turning anything on is a future, separately
approved milestone with its own Codex audit gate.
