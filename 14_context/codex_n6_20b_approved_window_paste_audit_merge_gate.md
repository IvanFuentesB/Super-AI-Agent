# N+6.20B Approved-Window Paste Audit Merge Gate

## Verdict

PASS / MERGE READY.

N+6.20A was audited in an isolated merge-gate worktree and merged cleanly into the local main merge gate. The approved-window paste lane remains conservative: dry-run by default, no auto-submit, no Enter key, no mouse click, no account/login action, no browser/chat/app control, and live paste execution remains disabled behind feature flags.

## Branches and Commits

- Merge-gate worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_20b_approved_window_paste_audit_merge_gate`
- Starting main: `733bd8e094eb39198a6a418af187b94c5e44241c`
- Target branch: `origin/feat/ghoti-agent-claude-n6-20a-approved-window-copy-paste-harness`
- Target commit audited: `662126cfc4c574c4e12f475711b3638acf1f4767`
- Target commit message: `feat(ghoti): add approved-window copy paste harness`
- Local merge commit: `35c07bc8e39f1a3e5684d716bf00ef413480e8cd`
- Merge commit message: `merge(ghoti): land approved-window copy paste harness`

## Repo Visibility

GitHub CLI reports the repository is `PUBLIC`, so this gate records `PUBLIC_REPO_WARNING`.

The merge remains acceptable because the public audit passed with zero blockers, no secrets/private runtime artifacts were introduced, no real Telegram token or chat id was committed, and no third-party repo contents were committed.

## Skills

Requested skills used:

- `codex-merge-gate`: used for target/base/ref verification, attribution check, no-commit merge rehearsal, validation, report, and push gate.
- `safe-repo-intake`: used for the ECC/GBrain/ECC-inspired-workflow safety lens; N+6.20A adapts inspected ideas only and does not install plugins, hooks, or Node scripts.

Available local skill directories observed:

- `.agents`: `agent-swarm-simulator`, `codex-merge-gate`, `safe-repo-intake`, `token-saving-audit`
- `.codex`: `.system`, `agent-swarm-simulator`, `chatgpt-apps`, `cloudflare-deploy`, `codex-merge-gate`, `codex-primary-runtime`, `doc`, `figma*`, `gh-address-comments`, `gh-fix-ci`, `jupyter-notebook`, `notion-*`, `pdf`, `playwright`, `playwright-interactive`, `safe-repo-intake`, `screenshot`, `security-ownership-map`, `sora`, `speech`, `token-saving-audit`, `transcribe`, `vercel-deploy`

Only the requested audit/intake skills were used; UI/browser/design skills were not used because this was a merge gate, not a UI implementation task.

## Scope Check

PASS.

Expected N+6.20A files are present:

- `AGENTS.md`
- `docs/GHOTI_N6_20A_APPROVED_WINDOW_COPY_PASTE_HARNESS.md`
- `docs/GHOTI_ECC_AGENT_WORKFLOW_UPGRADE_PLAN.md`
- `docs/GHOTI_GBRAIN_MEMORY_UPGRADE_PLAN.md`
- `docs/GHOTI_ECC_INTENDED_USE_VS_GHOTI_ADAPTATION.md`
- `docs/GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md`
- `14_context/approved_window_paste/README.md`
- `14_context/approved_window_paste/approved_windows.example.json`
- `14_context/approved_window_paste/paste_status_schema.json`
- `14_context/approved_window_paste/manual_output_drop/README.md`
- `03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1`
- `03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1`
- `03_scripts/approved_window_paste/ghoti_paste_status.py`
- `03_scripts/approved_window_paste/check_approved_window_paste.ps1`
- `03_scripts/approved_window_paste/write_manual_output_summary.py`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_APPROVED_WINDOW_PASTE_TASK.md`
- `01_projects/runtime_mvp/tests/test_n6_20a_approved_window_copy_paste_harness.py`
- `14_context/claude_n6_20a_approved_window_copy_paste_harness.md`

`.gitignore` was updated only for N+6.20A manual-output/runtime residue. `23_configs/ghoti_feature_flags.example.json` was updated with new risky flags defaulting false.

## Attribution Check

PASS.

The target commit message and merge commit message contain no prohibited AI attribution trailer and no AI/Claude/Anthropic co-author metadata.

## Safety Checks

PASS.

- Project `AGENTS.md` exists, is concise, and contains no secrets/private memory.
- Approved window allowlist uses conservative examples only.
- Detector is read-only and does not focus windows, click, type, or submit.
- Clipboard/paste harness defaults to dry-run.
- `CopyOnly` copies only when explicitly requested.
- `PasteApproved` requires an allowlist match and still defers live keystroke paste.
- No Enter key, no submit key, no mouse click, and no uncontrolled browser/computer-use.
- Input file must be under `14_context/overnight_operator/outbox`.
- Secret-shaped input is rejected.
- Kill switch/feature flags exist; risky flags default false.
- Only `telegram_status_commands_enabled` is true globally.
- Manual output drop exists.
- ECC docs state ECC is not a Hermes app, not live in Hermes, not installed, and not running hooks or Node scripts.
- GBrain memory upgrade plan is concrete and planning-only.
- Agent Arena plan is simulation-first, not a live swarm.
- No ECC plugin install, no ECC hooks, no ECC Node scripts, no MCP setup, no Telegram `/run`, no live app control, no account/login/email/WhatsApp/payment/trading action.

## Validation Results

Validation was run against exact merge commit `35c07bc8e39f1a3e5684d716bf00ef413480e8cd` from a temporary local clone outside `Documents` to avoid the known local Python write issue under the repo path.

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_20a_*.py" -v`: PASS, 19 tests OK
- `powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1`: PASS
- `powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1 -InputFile 14_context/overnight_operator/outbox/latest_prompt_packet.md -DryRun`: PASS
- `python 03_scripts/approved_window_paste/ghoti_paste_status.py --json`: PASS
- `powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/check_approved_window_paste.ps1`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: PASS, 150 checks, 0 blockers, 9 warnings requiring human review
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS
- Full N+6 suite: PASS, 336 tests OK

The paste dry-run result showed `copied=false`, `pasted=false`, `submitted=false`, `presses_enter=false`, `clicks_coordinates=false`, and `controls_chat_or_browser_apps=false`.

## Paste Harness Result

PASS.

The detector returned JSON and found no approved match among active app windows. The dry-run paste wrapper accepted the generated local prompt packet, detected no secret pattern, and performed no copy/paste/submit action. The check script confirms non-matching paste-approved targets are refused.

## AGENTS.md Status

PASS.

`AGENTS.md` is concise and repo-scoped. It records worktree/branch rules, no-secret rules, no live app/control rules, feature flag expectations, explicit staging expectations, and commit attribution policy. It does not contain private memory or credentials.

## ECC/GBrain Status

PASS.

The ECC intended-use/adaptation doc correctly states that ECC is not installed, is not a Hermes app, is not live in Hermes, and that Ghoti adapts ideas only. The ECC workflow upgrade and GBrain memory upgrade docs are concrete future plans, not runtime wiring.

## Agent Arena Status

PASS.

The Agent Arena plan is simulation-first and explicitly blocks live unattended swarms, automatic agent launch, and auto merge/push. The exact next milestone is `N+6.21A Agent Arena visual simulator`.

## Cleanup

Generated outbox packets, context-pack/repo-map outputs, status bridge handoff logs, and Python caches from validation were confined to the temporary validation clone or restored/ignored. No generated residue is staged in the merge-gate worktree.

## Final Verdict

PASS / MERGE READY.

If the final report commit validates and `origin/main` remains at the recorded starting hash, push this merge-gate HEAD to `origin/main`.

Exact next milestone: `N+6.21A Agent Arena visual simulator`.
