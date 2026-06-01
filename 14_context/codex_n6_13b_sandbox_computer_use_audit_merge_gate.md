# N+6.13B Sandbox Computer-Use Action Harness Audit Merge Gate

Date: 2026-06-01

Verdict: PASS / MERGE READY

## Scope

- Worktree: `.claude/worktrees/n6_13b_sandbox_computer_use_audit_merge_gate`
- Starting main: `f386cd7831e38e5b6e63b365424825f83c1e8c3e`
- Target branch: `origin/feat/ghoti-agent-claude-n6-13a-sandbox-computer-use-action-harness`
- Target commit audited: `e775efb967da31157a3bebb5743bbba21ead79c9`
- Merge-gate commit before this report: `43ee009297d39373ab4029ab7a57e0cb246ac7bb`
- Repository visibility: PUBLIC
- PUBLIC_REPO_WARNING: GitHub reports this repository as public. The gate continued because no secrets/private auth files were introduced and the public security audit passed with zero blockers. Recommended future posture: keep the full Ghoti workspace private and publish a separate sanitized public showcase repo.

## Attribution Check

Inspected target commit message:

```text
feat(ghoti): add sandbox computer-use action harness
```

Result: PASS.

No prohibited attribution trailer or GitHub-visible AI attribution text was present in the target commit message. The merge commit message was also verified clean:

```text
merge(ghoti): land sandbox computer-use action harness
```

## File Scope

The merge introduced the intended N+6.13A sandbox harness files:

- `docs/GHOTI_N6_13A_SANDBOX_COMPUTER_USE_ACTION_HARNESS.md`
- `14_context/computer_use/sandbox/SANDBOX_COMPUTER_USE_RULES.md`
- `14_context/computer_use/sandbox/sandbox_target.html`
- `14_context/computer_use/sandbox/sandbox_observation_fixture.json`
- `14_context/computer_use/sandbox/sandbox_expected_action_plan.json`
- `14_context/computer_use/sandbox/feature_flags_sandbox_computer_use.json`
- `03_scripts/computer_use_sandbox/sandbox_action_planner.py`
- `03_scripts/computer_use_sandbox/sandbox_action_runner.py`
- `03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1`
- `03_scripts/computer_use_sandbox/README.md`
- `01_projects/runtime_mvp/tests/test_n6_13a_sandbox_computer_use_action_harness.py`
- `14_context/claude_n6_13a_sandbox_computer_use_action_harness.md`
- `23_configs/ghoti_feature_flags.example.json`

The N+6.12B merge report already on main was preserved by the merge.

## Safety Checks

PASS:

- Sandbox target HTML has no external resources.
- Observation fixture is `local_only=true` and `live_website=false`.
- Planner emits JSON and only plans against `sandbox_only`.
- Runner emits JSON.
- Runner dry-run reports `action_performed=false`.
- `--allow-sandbox-action` remains in-memory simulation only and reports `action_performed=false`.
- Human approval is required.
- Global kill switch is engaged in the sandbox feature flags.
- Risky flags default false.
- `live_browser_computer_use_enabled=false`.
- `account_login_automation_enabled=false`.
- `captcha_bypass_enabled=false`.
- Real click/type flags are false.
- No real OS input is performed.
- No live browser, live website, account login, Telegram, MCP, provider setup, external API, install, Docker/QEMU/KASM, or third-party repo execution is enabled.
- No secrets, tokens, cookies, auth files, or `.env` files were introduced.

## Dry-Run Result

Command:

```text
python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json
```

Result: PASS.

Key facts:

- `mode= dry_run`
- `action_performed=false`
- `real_click_performed=false`
- `real_type_performed=false`
- `os_input_used=false`
- `requires_human_approval=true`

## Simulation Result

Command:

```text
python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --allow-sandbox-action --json
```

Result: PASS.

Key facts:

- `mode= allow_sandbox_action`
- `action_performed=false`
- `simulated_action_performed=true`
- `strict_sandbox_confinement_guaranteed=false`
- `sandbox_action_not_performed_reason= strict confinement not yet guaranteed`
- In-memory simulation reached the expected local state: `status-output` text became `GHOTI_OK`.

## Validation Results

Pre-commit merge rehearsal:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: PASS, 181 tests OK
- `python 03_scripts/computer_use_sandbox/sandbox_action_planner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json`: PASS
- `python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json`: PASS
- `python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --allow-sandbox-action --json`: PASS
- `powershell -ExecutionPolicy Bypass -File 03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 failed, 7 baseline warnings
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS

Post-merge validation:

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: PASS, 181 tests OK
- `python 03_scripts/computer_use_sandbox/sandbox_action_planner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json`: PASS
- `python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --json`: PASS
- `python 03_scripts/computer_use_sandbox/sandbox_action_runner.py --fixture 14_context/computer_use/sandbox/sandbox_observation_fixture.json --allow-sandbox-action --json`: PASS
- `powershell -ExecutionPolicy Bypass -File 03_scripts/computer_use_sandbox/check_sandbox_computer_use.ps1`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 failed, 7 baseline warnings
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS

Generated validation residue from context-pack and repo-map commands was restored before this report was written.

## Blockers

None.

## Safety Verdict

PASS. The sandbox harness is not live computer-use. It is local-only planning, dry-run, and in-memory simulation. No real browser, website, account, OS input, external API, third-party execution, or install path is enabled.

## Exact Next Milestone

N+6.14A Gemma local worker queue is the safer next milestone after this audit because strict sandbox confinement is still not guaranteed. A confined local GUI/HTML action runner should remain a later, separately audited step unless it can prove owned-renderer confinement before any real action.
