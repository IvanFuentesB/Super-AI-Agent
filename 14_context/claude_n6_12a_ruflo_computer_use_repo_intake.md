# N+6.12A - Ruflo + Computer-Use Repo Static Clone/Inspect/Extract

**Verdict:** IMPLEMENTED_AND_PUSHED (see push verification at end)
**Branch:** `feat/ghoti-agent-claude-n6-12a-ruflo-computer-use-repo-intake`
**Worktree:** `.claude/worktrees/n6_12a_ruflo_computer_use_repo_intake`
**Base main:** `0edba03`
**Codex audit target branch:** `audit/ghoti-agent-codex-n6-12a-ruflo-computer-use-repo-intake`

## Mission

First milestone where Ghoti uses external repos as **source material**: clone for
read-only static inspection, check the license, document useful patterns/risks, and
- only where allowed and safe - re-express one pattern with attribution. Nothing is
installed, executed, imported, or wired into the runtime.

## Repos cloned (static, git-ignored, never installed/run)

Clones live under `21_repos/third_party_static/` and are git-ignored (only a
`.gitkeep` is tracked). Commit SHAs recorded for reproducibility.

| Repo | Source | License | Commit | Files scanned |
|------|--------|---------|--------|---------------|
| Ruflo | `github.com/ruvnet/ruflo` | MIT | `f57b69876ba1c4e6bf4e317d0d1529a5481692c4` | 4336 |
| TryCUA / CUA Driver | `github.com/trycua/cua` | MIT | `4c54f43ffd9a46cf9c96b06f477a986316d19260` | 2185 |
| Browser Harness | `github.com/browser-use/browser-harness` | MIT | `6d20866664ea3d9691b27bbf64f42ae097437dc3` | 150 |
| Vercel agent-browser | `github.com/vercel-labs/agent-browser` | Apache-2.0 | `b4f2f37d7b4f954022bc77f8d6dce70e07072b00` | 275 |

`cua` is a partial Windows checkout (a few CI YAMLs with invalid-on-Windows names
did not materialize); all key files (README, LICENSE, package.json, pyproject.toml,
Dockerfile) are present, so the inspection is sound.

## Ruflo result

Cloned and statically inspected. License **MIT** (reuse permitted). The inspector
confirmed the documented risk surface: install scripts (`scripts/install.sh`,
`.claude-plugin/scripts/install.sh`) and `postinstall` lifecycle hooks
(`v3/@claude-flow/browser`, `v3/@claude-flow/cli`). Combined with the repo's
documented supply-chain history (obfuscated malicious npm pre-install across
v3.1.0-alpha.55..v3.5.2; MCP prompt-injection #1375; remediated SQL-injection),
the decision is to **re-express one pattern from scratch with attribution and NOT
vendor any Ruflo code**.

## Computer-use result

| Member | Outcome |
|--------|---------|
| TryCUA / CUA Driver | Cloned + documented; no code copied. Live desktop control, Docker/QEMU/KASM, 189 shell scripts noted. |
| Browser Harness | Cloned + documented; no code copied. Thin CDP harness + self-writing-code risk noted. |
| Vercel agent-browser | Cloned + documented; no code copied. Apache-2.0 (NOTICE needed only if code reused; none reused). |
| UI-TARS | **Source-needed** - no URL recorded, ambiguous upstream; not cloned (do not guess). |
| Browser-use | **Deferred** - blocked priority; stealth/cloud positioning; not cloned. |
| Computer-use stack | Umbrella; members tracked individually. `computer_use_enabled` stays false. |

## Extracted / adapted component

One safe, non-runtime extraction: **Ruflo's coordinator/worker + shared-local-memory
hand-off + declared-skill pattern**, re-expressed from scratch (no code copied) as an
inert, default-disabled contract:

- `03_scripts/external_adapters/ruflo_adapter_contract.py` - `RUFLO_SWARM_ENABLED = False`,
  global kill switch engaged, `code_copied_from_source: false`.
- `03_scripts/external_adapters/computer_use_adapter_contract.py` - documents the
  observe -> plan -> action loop as disabled capability flags
  (`live_browser_enabled` / `desktop_control_enabled` / `click_enabled` /
  `type_enabled` / `hotkeys_enabled` / `network_enabled` / `container_sandbox_enabled`
  / `self_writing_code_enabled` / `stealth_enabled` / `live_api_enabled`, all false);
  stealth/captcha/proxy permanently refused.
- `03_scripts/external_adapters/README.md` - attribution, license, and disabled posture.

## Files added (this lane writes only its own files)

- `03_scripts/external_repo_static_intake.py` (stdlib-only, read-only inspector)
- `03_scripts/external_adapters/{ruflo_adapter_contract.py,computer_use_adapter_contract.py,README.md}`
- `14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json`
- `14_context/tool_intake/repo_intake_reports/{n6_12a_overview,ruflo_n6_12a,computer_use_stack_n6_12a,ui_tars_n6_12a,browser_harness_n6_12a,vercel_agent_browser_n6_12a,trycua_cua_driver_n6_12a}.md`
- `docs/GHOTI_N6_12A_RUFLO_COMPUTER_USE_REPO_INTAKE.md`
- `01_projects/runtime_mvp/tests/test_n6_12a_ruflo_computer_use_repo_intake.py`
- `.gitignore` (added the `21_repos/third_party_static/*` rule) and
  `21_repos/third_party_static/.gitkeep`

## Inspector safety block (reported on every run)

```
executed_third_party_code: false
imported_third_party_modules: false
installed_dependencies: false
network_used: false
only_standard_library: true
read_only: true
```

## Manifest field verification

Every candidate carries `safe_to_run: false` and `runtime_wired: false`. Ruflo:
MIT, `license_allows_reuse: true`, `extraction_status: pattern_re_expressed_with_attribution`.
Computer-use members all present (UI-TARS, Browser Harness, Vercel agent-browser,
TryCUA/CUA, Browser-use) plus the umbrella.

## Validation

| Check | Result |
|-------|--------|
| `unittest discover -p test_n6_*.py` | **163 tests, OK** (my module adds 17; 0 failures, 0 errors) |
| `external_repo_static_intake.py --manifest ... --json` | ok; 7 candidates; safety block all-safe |
| `external_repo_static_intake.py ... --candidate Ruflo --json` | ok; 1 candidate |
| `ruflo_adapter_contract.py --status --json` | disabled; kill switch engaged; no code copied |
| `computer_use_adapter_contract.py --status --json` | every capability false; stealth/captcha/proxy refused |
| `public_repo_security_audit.py --run --json` | 150 checks / 143 passed / **0 failed** / 7 warnings / blocking_findings `[]` / safe_to_make_public `true` |
| `ghoti_product_launcher.py --status --json` | ok; dashboard not running; localhost_only true; no external/live actions |
| `git diff --check` / `git show --check --stat HEAD` | clean (see commit) |

The 7 security warnings and 143 passes are identical to the prior baseline - the new
files added zero failures and zero new warnings.

## What remains disabled

Live browser control, desktop control, click/type/hotkeys, container runtimes
(Docker/QEMU/KASM), model-provider/network calls, MCP enablement, dependency
installs, and any execution of third-party code. Both adapter contracts are inert
and default-disabled behind feature flags and the global kill switch. UI-TARS stays
source-needed; Browser-use stays deferred.

## Direct answers

- **Were the repos cloned for static inspection only?** Yes - 4 cloned (Ruflo, cua,
  browser-harness, agent-browser), git-ignored, never installed, never executed.
- **Did Ghoti install anything?** No.
- **Did Ghoti execute any third-party repo code?** No.
- **Did Ghoti import any cloned module?** No.
- **Was any Ruflo code vendored/copied?** No - one pattern re-expressed from scratch
  with MIT attribution and a security note.
- **Did Ghoti make network calls on a repo's behalf, or use a live browser /
  desktop / computer-use?** No.
- **Are the adapter contracts disabled by default?** Yes - feature flags false,
  global kill switch engaged.
- **Were any secrets, tokens, or `.env`/auth files read or committed?** No.
- **Was main pushed?** No - feature branch only.
- **Are approval/safety gates intact?** Yes - unchanged.

## Push verification

`git ls-remote origin refs/heads/feat/ghoti-agent-claude-n6-12a-ruflo-computer-use-repo-intake`
returns the pushed commit (recorded in the session log).

**Final verdict: IMPLEMENTED_AND_PUSHED.**
