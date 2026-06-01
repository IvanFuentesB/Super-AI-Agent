# Ghoti N+6.12A Ruflo + Computer-Use Repo Intake

## Purpose

N+6.12A is the first milestone where Ghoti uses external repos as **source
material** instead of only planning around them. The workflow is: clone for
read-only static inspection, check the license, document useful patterns and risks,
and - only where allowed and safe - re-express **one** pattern from scratch with
attribution. Repos are **static-inspected, not blindly run**.

## Scope

- Clone candidate repos into `21_repos/third_party_static/` for **read-only**
  inspection. Clones are git-ignored, never staged, never installed, never executed.
- Inspect each clone with a standard-library-only inspector that reads files and
  runs nothing: `03_scripts/external_repo_static_intake.py`.
- Record per-candidate intake fields in a manifest and one report each.
- Produce **disabled** adapter contracts that capture patterns behind feature flags.

## Non-Goals (nothing here is enabled)

- No live browser control. No desktop control. No click/type/hotkeys.
- No execution of third-party code. No `npm` / `pip` / `pnpm` / `uv` installs.
- No imports of cloned-repo modules. No Docker/QEMU/KASM runtime.
- No model-provider/network calls. No credential/token/cookie/auth reads.
- No MCP server enablement. No account login. No stealth/captcha/proxy bypass.
- No `main` push. No AI-attribution in commit metadata.

## The rule: inspect -> classify -> sandbox -> integrate

1. **Inspect** the project's own README, license, and file tree **without running it**.
2. **Classify** the risk and record stop conditions (done in each report).
3. **Sandbox** only if behaviour must be observed - isolated, no secrets, no network,
   and only after explicit human approval. (Not done this milestone.)
4. **Integrate** only after tests prove safe behaviour and a Codex audit passes.
   "Documented + statically reviewed" is the default resting state.

## What was inspected

| Candidate | License | Cloned | Commit | Decision |
|-----------|---------|--------|--------|----------|
| Ruflo (`ruvnet/ruflo`) | MIT | yes | `f57b698` | Pattern re-expressed with attribution (no code copied) |
| TryCUA / CUA Driver (`trycua/cua`) | MIT | yes | `4c54f43` | Patterns documented, no code copied |
| Browser Harness (`browser-use/browser-harness`) | MIT | yes | `6d20866` | Patterns documented, no code copied |
| Vercel agent-browser (`vercel-labs/agent-browser`) | Apache-2.0 | yes | `b4f2f37` | Patterns documented, no code copied |
| UI-TARS | unknown | no | - | Source-needed (do not guess) |
| Browser-use (`browser-use/browser-use`) | MIT | no | - | Deferred (blocked priority) |

Full details: `14_context/tool_intake/repo_intake_reports/` and the manifest at
`14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json`.

## Reuse with attribution and license awareness

Where a pattern is reused, the source project, URL, and license are named, and we
record that **no code was copied** (patterns are re-expressed from scratch):

- **Ruflo (MIT)** - reuse is permitted by the license, but Ruflo has a documented
  supply-chain history (an obfuscated malicious npm pre-install script, an MCP
  prompt-injection issue #1375, and a remediated SQL-injection history). Ghoti
  therefore **re-expresses** the coordinator/worker + local-memory hand-off pattern
  from scratch in `03_scripts/external_adapters/ruflo_adapter_contract.py` and never
  installs, imports, or runs Ruflo.
- **agent-browser (Apache-2.0)** - reuse would require preserving `NOTICE`/attribution.
  No code is reused, so no `NOTICE` applies this milestone.

## Feature flags and kill switches

Every capability is disabled by default and overridden by a global kill switch:

- `ruflo_adapter_contract.py`: `RUFLO_SWARM_ENABLED = False`, global kill switch engaged.
- `computer_use_adapter_contract.py`: `COMPUTER_USE_ENABLED = False`; every
  sub-capability flag (`live_browser_enabled`, `desktop_control_enabled`,
  `click_enabled`, `type_enabled`, `hotkeys_enabled`, `network_enabled`,
  `container_sandbox_enabled`, `self_writing_code_enabled`, `stealth_enabled`,
  `live_api_enabled`) defaults `False`; stealth/captcha/proxy are **permanently refused**.

See `docs/GHOTI_FEATURE_FLAGS_AND_KILL_SWITCHES.md` for the broader flag model.

## Safety boundaries (verified by the inspector on every run)

```
executed_third_party_code: false
imported_third_party_modules: false
installed_dependencies: false
network_used: false
only_standard_library: true
read_only: true
```

Every manifest candidate is `safe_to_run: false` and `runtime_wired: false`.

## How to run (read-only)

```bash
python 03_scripts/external_repo_static_intake.py \
  --manifest 14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json --json

python 03_scripts/external_repo_static_intake.py \
  --manifest 14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json \
  --candidate Ruflo --json

python 03_scripts/external_adapters/ruflo_adapter_contract.py --status --json
python 03_scripts/external_adapters/computer_use_adapter_contract.py --status --json
```

## Future roadmap

- UI-TARS: operator supplies the exact source URL, then static clone + license/README
  review only.
- Browser-use: if needed later, static-clone only the local open-source parts
  read-only after approval; never use stealth/captcha/proxy features.
- Any runtime wiring (Ruflo swarm or computer-use action) is a separate, approved
  milestone behind a human approval gate and a Codex audit. Until then, the contracts
  stay disabled.
