# N+6.13A - Sandboxed Computer-Use Action Harness

**Verdict:** IMPLEMENTED_AND_PUSHED (see push verification at end)
**Branch:** `feat/ghoti-agent-claude-n6-13a-sandbox-computer-use-action-harness`
**Worktree:** `.claude/worktrees/n6_13a_sandbox_computer_use_action_harness`
**Base main:** `0edba03`
**Built on (dependency):** N+6.12A feature branch
`feat/ghoti-agent-claude-n6-12a-ruflo-computer-use-repo-intake` @ `4e81610` (unmerged)
**Codex audit target branch:** `audit/ghoti-agent-codex-n6-13a-sandbox-computer-use-action-harness`

## Mission

First milestone where Ghoti moves beyond observation-only toward a **local sandbox
computer-use action harness** - a local sandbox target, an action planner, a dry-run
runner, and an optional in-memory sandbox simulation - without becoming unsafe. It is
**sandbox only**: no live web control, no account control, no arbitrary desktop
control, and no full autonomy. It reuses the N+6.12A statically inspected patterns
and disabled adapter contracts as design inspiration, with attribution and no code
copied.

## Dependency on N+6.12A

`origin/main` is `0edba03`; the N+6.12A work (`4e81610`) is on its feature branch and
not yet merged. Per the start condition, this branch was created **from the N+6.12A
feature branch** and depends on it landing first. The N+6.12A static intake,
`computer_use_adapter_contract.py` disabled flags, and per-repo reports are the
source material reused here.

## Files added (this lane writes only its own files)

- `14_context/computer_use/sandbox/sandbox_target.html` (offline; no external resources)
- `14_context/computer_use/sandbox/sandbox_observation_fixture.json` (`local_only: true`)
- `14_context/computer_use/sandbox/sandbox_expected_action_plan.json`
- `14_context/computer_use/sandbox/feature_flags_sandbox_computer_use.json`
- `14_context/computer_use/sandbox/SANDBOX_COMPUTER_USE_RULES.md`
- `03_scripts/computer_use_sandbox/sandbox_action_planner.py` (stdlib-only planner)
- `03_scripts/computer_use_sandbox/sandbox_action_runner.py` (stdlib-only runner)
- `03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1` (JSON check)
- `03_scripts/computer_use_sandbox/README.md`
- `docs/GHOTI_N6_13A_SANDBOX_COMPUTER_USE_ACTION_HARNESS.md`
- `01_projects/runtime_mvp/tests/test_n6_13a_sandbox_computer_use_action_harness.py`
- `14_context/claude_n6_13a_sandbox_computer_use_action_harness.md` (this report)

## Files updated (surgical)

- `23_configs/ghoti_feature_flags.example.json` - appended the 7 sandbox flag keys
  in their safe all-off baseline (every sandbox flag `false`, preserving that
  file's "only status-commands true" default convention). The dedicated
  `feature_flags_sandbox_computer_use.json` carries `dry_run` `true`.

## Was any action performed?

No real action. The runner is dry-run by default (`action_performed: false`). The
optional `--allow-sandbox-action` mode does **not** control the real OS: with the
standard library alone, real input cannot be strictly confined to the local sandbox
target, so the action stays a pure in-memory **simulation** and reports
`action_performed: false` with
`sandbox_action_not_performed_reason: strict confinement not yet guaranteed`. The
simulation parses the local sandbox HTML and confirms the goal locally
(`status-output` becomes `GHOTI_OK`, `goal_satisfied_in_simulation: true`), with a
clear N+6.13B next step.

## Dry-run / simulation result

- Dry-run: `mode: dry_run`, `action_performed: false`, lists the two `would_perform`
  actions (type `GHOTI_OK` into `note-input`, click `status-button`).
- Simulation (`--allow-sandbox-action`): `simulated_action_performed: true`,
  `action_performed: false`, parsed ids `[note-input, status-button, status-output]`,
  `final_state.status-output.text == "GHOTI_OK"`, `goal_satisfied_in_simulation: true`.

## Manifest / safety field verification

| Field | Planner | Runner (dry-run) | Runner (simulate) |
|-------|---------|------------------|-------------------|
| `target` | `sandbox_only` | `sandbox_only` | `sandbox_only` |
| `requires_human_approval` | true | true | true |
| `action_performed` | n/a | false | false |
| `real_click_performed` | n/a | false | false |
| `real_type_performed` | n/a | false | false |
| `os_input_used` | n/a | false | false |
| `live_website` (safety) | false | false | false |
| `desktop_control_enabled` (safety) | false | false | false |
| `external_repo_code_executed` (safety) | false | false | false |
| `installs_performed` (safety) | false | false | false |
| `network_used` (safety) | false | false | false |
| `global_kill_switch_engaged` | true | true | true |

## Validation

| Check | Result |
|-------|--------|
| `unittest discover -p test_n6_*.py` | **181 tests, OK** (my module adds 18; 0 failures, 0 errors) |
| `sandbox_action_planner.py --fixture ... --json` | ok; target sandbox_only; safety all-safe |
| `sandbox_action_runner.py --fixture ... --json` | ok; dry-run; action_performed false |
| `sandbox_action_runner.py ... --allow-sandbox-action --json` | simulated only; action_performed false; goal satisfied in simulation |
| `check_sandbox_computer_use.ps1` | JSON; ok true; every risky flag false; kill switch true |
| `public_repo_security_audit.py --run --json` | 150 checks / 143 passed / **0 failed** / 7 warnings / blocking_findings `[]` / safe_to_make_public `true` |
| `ghoti_product_launcher.py --status --json` | ok; localhost-only; no external/live actions |
| `git diff --check` / `git show --check --stat HEAD` | clean (see commit) |

The 7 security warnings and 143 passes are identical to the prior baseline - the new
files added zero failures and zero new warnings.

## What remains disabled

Live browser / live website control, account login automation, CAPTCHA/bot/proxy/
stealth bypass, arbitrary desktop or window control, real click/type/hotkeys,
arbitrary shell execution, dependency installs, third-party repo code execution,
Docker/QEMU/KASM runtime, and external APIs/accounts. Every risky feature flag
defaults `false`; the global kill switch is engaged. Human approval is required
before any future real action. N+6.13B remains the gate for strictly confined real
sandbox action.

## Direct answers

- **Was any (real) action performed?** No - dry-run by default; `--allow-sandbox-action`
  is an in-memory simulation only (`action_performed: false`).
- **Did Ghoti run a live browser or computer-use against a real website?** No.
- **Did Ghoti control / click / type the desktop?** No.
- **Did Ghoti install anything?** No.
- **Did Ghoti execute external repo code?** No.
- **Did Ghoti start a UI-TARS or any third-party runtime?** No.
- **Did Ghoti make network calls / use live APIs or accounts?** No.
- **Were any captcha/stealth/proxy bypasses used?** No - permanently refused.
- **Is the harness sandbox-only and default-disabled?** Yes - feature flags false,
  dry-run default, global kill switch engaged.
- **Were any secrets/tokens/`.env`/auth files read or committed?** No.
- **Were approval/safety gates weakened?** No - intact and unchanged.
- **Was main pushed?** No - feature branch only.

## Push verification

`git ls-remote origin refs/heads/feat/ghoti-agent-claude-n6-13a-sandbox-computer-use-action-harness`
returns the pushed commit (recorded in the session log).

**Final verdict: IMPLEMENTED_AND_PUSHED.**
