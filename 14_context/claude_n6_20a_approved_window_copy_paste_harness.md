# Ghoti N+6.20A — Approved-Window Copy/Paste Harness (Report)

## Summary

N+6.20A adds the **approved-window** safety layer on top of the N+6.19A overnight
operator, plus the project `AGENTS.md` and four planning docs (ECC agent-workflow
upgrade, GBrain memory upgrade, ECC-intended-use-vs-Ghoti-adaptation, and the
simulation-first Agent Arena swarm simulator). The harness can list visible windows,
copy an outbox packet to the clipboard on explicit command, validate a paste target
against a conservative allowlist, and summarize manually dropped agent outputs - **and
it never pastes into apps, presses Enter, submits, or clicks.**

## Verdict

IMPLEMENTED_AND_PUSHED.

## Branch / worktree / base

- Branch: `feat/ghoti-agent-claude-n6-20a-approved-window-copy-paste-harness`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_20a_approved_window_copy_paste`
- Commit message: `feat(ghoti): add approved-window copy paste harness`
- Base `origin/main`: `733bd8e` ("docs(ghoti): record n6.19b validation environment note")

### Dependency

N+6.19B (the overnight operator MVP) is merged to `origin/main` (`384b2d7` feat ->
`0a1c43e` merge -> `429f18a` merge-gate -> `733bd8e`), so this branch was created
cleanly from `origin/main`. The harness reuses the N+6.19A outbox
(`14_context/overnight_operator/outbox/`) as the only allowed paste-input location.

## Skills and plugins

I inspected the installed Claude Code skills/plugins.

- **Detected (Claude Code):** project skills `ghoti-status`, `goal`, `prompt-bus`,
  `ultraplan`; plugin skills `anthropic-skills:*` (karpathy-guidelines, doc-coauthoring,
  docx/pptx/pdf/xlsx, mcp-builder, skill-creator, theme-factory, web-artifacts-builder,
  consolidate-memory); built-ins (`verify`, `code-review`, `security-review`,
  `simplify`, `run`, `init`, `loop`, `schedule`, `claude-api`, ...).
- **ECC / everything-claude-code:** **not installed** as a Claude Code skill/plugin in
  this session (a filesystem check under the user's `.claude` found no
  `everything-claude-code` plugin). The mission's global Codex `AGENTS.md` and Codex
  skills (`safe-repo-intake`, `codex-merge-gate`, `agent-swarm-simulator`,
  `token-saving-audit`) live **outside** this repo and outside Claude Code's plugin
  view. Per the mission I did **not** rely on any ECC live hook, and the repo installs
  no ECC plugin and runs no ECC Node script - only inspected ideas are adapted (see the
  ECC docs).
- **Used, and why relevant:** `ghoti-status` (git state, lane locks, prompt bus before
  editing - confirmed no N6 lane-lock conflict) and `anthropic-skills:karpathy-guidelines`
  (surgical, minimal, goal-driven guardrails). They match the task: repo inspection,
  local PowerShell/Python automation, computer-use safety, and documentation.
- **Ignored, and why:** UI/UX-framework and document-format skills
  (`web-artifacts-builder`, `theme-factory`, `docx/pptx/pdf/xlsx`, `doc-coauthoring`),
  `mcp-builder`, and every live-action connector (computer-use, Claude-in-Chrome,
  Figma, Gmail, Calendar). They are irrelevant to a local, gated paste harness and
  would breach this lane's no-live-action rules.
- **Did skill instructions change the implementation?** Yes. `karpathy-guidelines`
  drove the decision to **defer live keystroke paste** (smallest safe surface),
  keep every script free of OS-input primitives, treat "hooks" only as read-only
  validators, and make surgical additive changes. `ghoti-status` cleared the path.

## Files

New files (18) + one config edit:

- `AGENTS.md` - concise, auto-loaded project rules.
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
- `14_context/claude_n6_20a_approved_window_copy_paste_harness.md` (this report)
- **edited:** `23_configs/ghoti_feature_flags.example.json` (added the 6 missing flags,
  all `false`; invariant preserved) and `.gitignore` (manual_output_drop runtime).

## Useful commands

```
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1 -InputFile 14_context/overnight_operator/outbox/latest_prompt_packet.md -DryRun
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1 -InputFile 14_context/overnight_operator/outbox/latest_prompt_packet.md -CopyOnly
python 03_scripts/approved_window_paste/ghoti_paste_status.py --json
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/check_approved_window_paste.ps1
```

## AGENTS.md status

Created at the repo root, concise and auto-loadable: project rules, one-agent-per-task,
branch/worktree rules, main-is-protected (no merge without a separate gate), no
secrets, no AI attribution, argument-list-only subprocess, validation commands, and
pointers to the ECC-inspired workflow docs (adapt only; do not install).

## Agent Arena plan status

`docs/GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md` is written and **simulation-first**:
agent nodes/cards, queue/timeline, branch+worktree per agent, per-card token/cost
estimate, simulate swarms before live swarms, inspiration candidates
(`generative_agents`, AgentPrism-style traces, SwarmClaw-style dashboard), an N+6.21A
scope (reuse the N+6.18A loopback dashboard pattern), and no live unattended swarm
until approval gates exist.

## ECC / GBrain upgrade summary

- **ECC:** adapt inspected ideas only - agent roles, skill layout, command templates,
  hooks **as read-only validators**, security-scanner and token-optimization ideas.
  Do not install the plugin, enable hooks, or run Node scripts (see
  `GHOTI_ECC_AGENT_WORKFLOW_UPGRADE_PLAN.md` and
  `GHOTI_ECC_INTENDED_USE_VS_GHOTI_ADAPTATION.md`).
- **GBrain:** a local, file-based memory graph index over milestones/reports/handoffs,
  offline and read-only, behind `gbrain_memory_upgrade_enabled` (see
  `GHOTI_GBRAIN_MEMORY_UPGRADE_PLAN.md`).

## Validation

- `python ... test_n6_20a_...py` → **19 tests, 19 pass**.
- Full n6 suite (`unittest discover -p "test_n6_*.py"`) → **336 tests, 1 failure + 1
  error**, both pre-existing/environmental in files this lane did not touch: (a) the
  known `test_n6_14a_...test_check_emits_json_disabled_posture` (broken PATH `python`
  shim), and (b) an `test_n6_15a` `--use-gemma-if-available` status-brain call that ran
  real local gemma/ollama inference and exceeded its 200s timeout. Neither is an
  N+6.20A regression; the N+6.20A tests are 19/19.
- Detector → emits JSON `ok: true`. Paste wrapper `-DryRun` → `pasted: false`,
  `copied: false`, `submitted: false` (on the real `latest_prompt_packet.md`,
  `input_under_outbox: true`, 2149 chars). `-PasteApproved` with a non-allowlisted
  window → refused (`ok: false`, `approved_match: null`). `ghoti_paste_status.py
  --json` → `ok: true`. `check_approved_window_paste.ps1` → `ok: true`
  (detector_works, paste_dry_run_works, paste_approved_refuses_without_match all true).
- `public_repo_security_audit.py --run --json` → `failed_checks: 0`,
  `safe_to_make_public: true`, no blocking findings.
- `ghoti_product_launcher.py --status / --context-pack / --repo-map --json` → all
  `ok: true`.
- `git diff --check` → clean.
- Generated residue restored (the generated outbox packet is git-ignored; the
  context-pack / repo-map generated files and the N+6.16A status-bridge log produced
  during the suite were restored; only the 18 new files + `.gitignore` + the flags
  config remain).

## What remains disabled

Live keystroke paste, Enter/submit keystrokes, mouse clicks, app/window control,
auto-submit, account login, email/WhatsApp, Docker, MCP, live browser, and any
unattended live agent loop are all disabled. Every example-config risky flag is
`false`; only `telegram_status_commands_enabled` is true. Fully unattended overnight
operation remains blocked until approved-window detection, a clipboard guard, a kill
switch, no overlapping worktrees, auto-stop on errors, logs, and no auto merge/push are
all in place.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-20a-approved-window-copy-paste-harness`
