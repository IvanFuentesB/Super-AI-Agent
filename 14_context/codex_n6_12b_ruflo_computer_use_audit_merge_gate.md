# N+6.12B Ruflo + Computer-Use Repo Intake Audit Merge Gate

Date: 2026-06-01

Verdict: PASS / MERGE READY

## Scope

- Worktree: `.claude/worktrees/n6_12b_ruflo_computer_use_audit_merge_gate`
- Starting main: `0edba034c6ecdb83fd4a1106a8ef475bd5fa39e1`
- Target branch: `origin/feat/ghoti-agent-claude-n6-12a-ruflo-computer-use-repo-intake`
- Target commit audited: `4e816108cc351d4555f4450bfbad862a7d19eae8`
- Merge-gate commit before this report: `e3f81ec5243df8dcf62df9d22fc63e8d2afabd93`
- Repository visibility: PUBLIC
- PUBLIC_REPO_WARNING: GitHub reports the repository as public. This gate continued because no secrets/private auth files were introduced and the public security audit passed with zero blockers.

## Attribution Check

Inspected target commit message:

```text
feat(ghoti): add Ruflo and computer-use repo intake
```

Result: PASS.

No prohibited attribution trailer or GitHub-visible AI attribution text was present in the target commit message. The merge commit message was also verified clean:

```text
merge(ghoti): land Ruflo and computer-use repo intake
```

## File Scope

The merge introduced only the intended N+6.12A files:

- `.gitignore`
- `21_repos/third_party_static/.gitkeep`
- `03_scripts/external_repo_static_intake.py`
- `03_scripts/external_adapters/ruflo_adapter_contract.py`
- `03_scripts/external_adapters/computer_use_adapter_contract.py`
- `03_scripts/external_adapters/README.md`
- `14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json`
- `14_context/tool_intake/repo_intake_reports/*.md`
- `docs/GHOTI_N6_12A_RUFLO_COMPUTER_USE_REPO_INTAKE.md`
- `01_projects/runtime_mvp/tests/test_n6_12a_ruflo_computer_use_repo_intake.py`
- `14_context/claude_n6_12a_ruflo_computer_use_repo_intake.md`

Only `.gitkeep` is tracked under `21_repos/third_party_static`. Static clone contents remain ignored and are not committed.

## Repos Audited

Recorded static-intake targets:

- Ruflo / `ruvnet/ruflo`, MIT, commit `f57b69876ba1c4e6bf4e317d0d1529a5481692c4`
- TryCUA / CUA Driver, MIT, commit `4c54f43ffd9a46cf9c96b06f477a986316d19260`
- Browser Harness, MIT, commit `6d20866664ea3d9691b27bbf64f42ae097437dc3`
- Vercel agent-browser, Apache-2.0, commit `b4f2f37d7b4f954022bc77f8d6dce70e07072b00`
- UI-TARS, source needed / not guessed
- Browser-use, candidate recorded but deferred
- Computer-use stack, umbrella candidate only

The clean merge worktree does not contain the ignored static clone directories, which is expected. The static-intake CLI reported those local paths absent while preserving the recorded source/commit/license facts in the manifest.

## Safety Checks

PASS:

- Branch is static-intake only.
- No third-party repo source was committed.
- No external repo was cloned, installed, imported, executed, built, or run in this Codex gate.
- Ruflo pattern is re-expressed with attribution; no Ruflo source is vendored.
- Computer-use adapter contract is inert and default-disabled.
- `safe_to_run=false` and `runtime_wired=false` for every manifest candidate.
- Adapter flags remain disabled and the global kill switch is engaged.
- UI-TARS remains source-needed / observation-planning only.
- Browser-use remains deferred because anti-abuse evasion features conflict with Ghoti policy.
- No Telegram, MCP, provider auth, live browser, desktop control, account action, or live API is enabled.
- No secrets, tokens, cookies, auth files, or `.env` files were introduced.

## Validation Results

Pre-commit merge rehearsal:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: PASS, 163 tests OK
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 failed, 7 baseline warnings

Post-merge validation:

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: PASS, 163 tests OK
- `python 03_scripts/external_repo_static_intake.py --manifest 14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json --json`: PASS
- `python 03_scripts/external_repo_static_intake.py --manifest 14_context/tool_intake/repo_intake_manifests/n6_12a_ruflo_computer_use_manifest.json --candidate Ruflo --json`: PASS
- `python 03_scripts/external_adapters/ruflo_adapter_contract.py`: PASS, disabled non-runtime contract
- `python 03_scripts/external_adapters/computer_use_adapter_contract.py`: PASS, disabled non-runtime contract
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 failed, 7 baseline warnings
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS

Generated validation residue from context-pack and repo-map commands was restored before this report was written.

## Blockers

None.

## Safety Verdict

PASS. The branch is safe to merge to main. It records static repo intake and inert contracts only. No runtime capability, third-party execution, external install, live computer-use, account action, credential flow, or networked provider action is enabled.

## Exact Next Action

Push the clean merge-gate HEAD to `main` after committing this report with a clean human-readable message and verifying the latest commit message contains no prohibited attribution trailers.

Next milestone: N+6.13A sandboxed computer-use action harness.
