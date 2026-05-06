# Codex N+3.56 - Dashboard And Prompt Bus Audit

## Verdict

CONDITIONAL PASS.

Dashboard and prompt bus behavior is local-first, truthful, and dry-run safe. The remaining issues are capability/polish gaps rather than unsafe execution.

## Dashboard CLI

Commands run:

- `python 03_scripts/ghoti_dashboard.py --help`
- `python 03_scripts/ghoti_dashboard.py --status`
- `python 03_scripts/ghoti_dashboard.py --json`
- `python 03_scripts/ghoti_dashboard.py --card --dry-run`

Observed:

- Dashboard says `CC/Codex auto: NO`.
- Dashboard says Ruflo runtime wiring is NO.
- Dashboard says human approval is required.
- Card dry-run writes nothing.
- Card includes prompt bus, agent lanes, Obsidian, compact memory, Ruflo, Gemma/Ollama, course helper, and safety flags.
- It correctly reports Gemma model not found.
- It reports Ruflo path missing and node_modules not installed.

## Dashboard API/UI

Commands run:

- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`

Observed:

- Node syntax checks pass.
- `/api/ghoti/local-orchestrator/status` exists.
- The route is GET-only and read-only.
- It reads local JSONL/files and uses `ollama list` plus `git branch --show-current`.
- It does not trigger Ruflo install, Gemma compression, prompt-bus apply, Obsidian open, live accounts, or external actions.
- UI card says it is read-only and has no live actions, no approve/execute/install buttons.

Safety note:

- The broader dashboard app contains older executor/clipboard/task features elsewhere, but the audited local-orchestrator card added here is read-only.

## Prompt Bus

Commands run:

- `python 03_scripts/prompt_bus.py --help`
- `python 03_scripts/prompt_bus.py --status-json`
- `python 03_scripts/prompt_bus.py --write-context-pack --target all --title codex-audit-smoke --include-status --include-memory --include-next-actions --dry-run`

Observed:

- Status JSON works.
- Context-pack dry-run writes nothing.
- Context pack includes branch, HEAD, dirty state, lane/memory/next-action context.
- It previews Claude, Codex, and ChatGPT outputs.
- Source inspection shows canonical Claude prompt overwrite protection:
  - If `14_context/ghoti_current_prompt.md` exists and `--allow-canonical-overwrite` is not provided, apply refuses.
  - The same guard exists for context packs targeting Claude.

## Gaps

- The clean merged audit worktree does not contain `14_context/ghoti_current_prompt.md`, so refusal behavior was verified by source inspection rather than direct runtime overwrite attempt.
- The context-pack dry-run says Claude "would overwrite" the canonical prompt, which is accurate but emotionally sharp. The apply guard appears safe.
- Router sends "create bridge handoff for Claude Code and Codex" to `codex_audit`, not the new `cc_codex_bridge` helper. That is not unsafe, but it misses a routing opportunity.
