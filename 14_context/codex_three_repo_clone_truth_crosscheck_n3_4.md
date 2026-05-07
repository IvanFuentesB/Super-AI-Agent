# Codex Three-Repo Clone Truth Crosscheck - N+3.4

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ad022a0
Status label: parallel_audit_only / clone_truth_crosscheck / not_runtime_wired

## Scope

This Codex lane checked local clone truth for RUFLO, AutoBrowser, and Obscura without installing, building, running, staging, or modifying any third-party repo contents.

Normal `git -C` inspection of the nested eval repos is blocked by Git dubious-ownership protection because the nested repos are owned by `Ivan-G14/Navif` while this process runs as `Ivan-G14/ai_sandbox`. Codex did not modify global `safe.directory`. HEAD and remote URL were crosschecked by reading each nested repo's `.git/HEAD`, ref file, and `.git/config` directly.

## Repo Truth Table

| Repo | Path exists | Git repo | HEAD hash | Remote URL | Used how | Runtime wired | Audit doc present | Committed or untracked |
|---|---:|---:|---|---|---|---:|---:|---|
| RUFLO | YES | YES | `01070ed` | `https://github.com/ruvnet/ruflo.git` | Isolated source/read-only audit only | NO | YES | `14_context/ruflo_isolated_clone_audit.md` is untracked; `14_context/ruflo_read_only_evaluation.md` is tracked |
| AutoBrowser | YES | YES | `e646a48` | `https://github.com/LvcidPsyche/auto-browser.git` | Isolated source/read-only audit only | NO | YES | `14_context/autobrowser_isolated_clone_audit.md` is untracked; `14_context/external_operator_candidates_audit.md` is tracked |
| Obscura | YES | YES | `99e75f1` | `https://github.com/h4ckf0r0day/obscura.git` | Isolated source/read-only audit plus separate Obscura runtime verification recorded by Claude | NO | YES | `14_context/obscura_isolated_clone_audit.md` is untracked; `14_context/obscura_runtime_verification.md` is tracked |

## Used Or Only Audited

- RUFLO: only audited. No install, no MCP server start, no provider key configuration, no runtime wiring.
- AutoBrowser: only audited. No Docker start, no browser session, no auth profile, no runtime wiring.
- Obscura: source audited and a separate tracked verification doc says Obscura was built outside the repo at `C:\tmp\obscura_build` and smoke-tested against safe targets. It is still not wired into Ghoti runtime.

## Untracked Audit Docs

These untracked docs look intentional and likely should be committed by the Claude lane or a later reconciliation lane if their contents are still accurate:

- `14_context/ruflo_isolated_clone_audit.md`
- `14_context/autobrowser_isolated_clone_audit.md`
- `14_context/obscura_isolated_clone_audit.md`

Codex did not stage them because this task explicitly allowed only the four N+3.4 Codex crosscheck docs.

## Third-Party Staging Rule

Do not stage:

- `21_repos/third_party/evals/ruflo/**`
- `21_repos/third_party/evals/auto-browser/**`
- `21_repos/third_party/evals/obscura/**`
- `21_repos/third_party/.gitkeep`

The cloned repos remain reference/evaluation material, not Ghoti source code.

## Verdict

Clone truth is consistent with prior reports:

- RUFLO, AutoBrowser, and Obscura are cloned under `21_repos/third_party/evals/`.
- They are nested Git repos with the expected HEAD hashes and remotes.
- None is runtime-wired into Ghoti.
- Untracked isolated audit docs appear useful, but were intentionally not staged by this Codex lane.
