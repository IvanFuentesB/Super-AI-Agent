# Codex N+3.51 - Next Claude Implementation Brief

Milestone to give Claude Code:

```text
N+3.51A - Bridge Dashboard + Prompt Bus Apply + Gemma Compression + Ruflo Isolated Install Gate
```

Recommended branch:

```text
feat/ghoti-agent-claude-n3-51-bridge-dashboard-gemma-ruflo
```

## Claude Copy-Paste Prompt

```text
You are Claude Code working in:

C:\Users\ai_sandbox\Documents\AI_Managed_Only

Branch:
feat/ghoti-agent-claude-n3-51-bridge-dashboard-gemma-ruflo

Base branch:
feat/ghoti-visible-operator-stack

Recommended mode:
high or max available

Milestone:
N+3.51A - Bridge Dashboard + Prompt Bus Apply + Gemma Compression + Ruflo Isolated Install Gate

Goal:
Move Ghoti from local bridge scaffolding toward a real supervised operator bridge between Claude Code, Codex, ChatGPT, Python local workers, Gemma/Ollama, Obsidian memory, prompt bus, lane locks, and Ruflo/claude-flow.

This milestone should make the system feel meaningfully more connected and less manual, while staying local-only and approval-gated.

Hard safety rules:
- Do NOT connect live accounts.
- Do NOT touch credentials, .env, secrets, tokens, or browser profiles.
- Do NOT send emails.
- Do NOT post to social media.
- Do NOT sell/list products.
- Do NOT pay, subscribe, buy credits, or enter payment details.
- Do NOT scrape or use OSINT tools.
- Do NOT apply to jobs.
- Do NOT enter giveaways.
- Do NOT run Ruflo swarms.
- Do NOT launch Ruflo MCP.
- Do NOT globally install Ruflo or claude-flow.
- Do NOT run OpenClaw, Paperclip, n8n, CUA, Chrome DevTools MCP, Firecrawl, Glif, JobSpy, browser tools, or account connectors.
- Do NOT execute model output.
- Do NOT make Gemma output canonical memory automatically.
- Do NOT create mutation buttons in the dashboard.
- Do NOT stage unrelated dirty files.
- Do NOT delete logs, tasks, history, or memory.

Allowed:
- local stdlib Python helper scripts,
- read-only dashboard route/card,
- dry-run/apply local file writes under approved repo paths,
- isolated Ruflo install gate command generation,
- optional isolated Ruflo install only if explicit --install-apply is passed,
- local Ollama/Gemma compression only if the model exists and command is explicit,
- Obsidian vault open/check helper improvements,
- docs and validation.

First sync and inspect:
1. cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
2. git fetch origin
3. git switch feat/ghoti-visible-operator-stack
4. git pull --ff-only origin feat/ghoti-visible-operator-stack
5. git switch -c feat/ghoti-agent-claude-n3-51-bridge-dashboard-gemma-ruflo
   - If branch exists, switch to it and pull fast-forward if it already tracks origin.
   - Do not reset.
6. git status --short
7. git log --oneline --decorate -12
8. python 03_scripts/ghoti_local_orchestrator.py --status
9. python 03_scripts/agent_lane_status.py --check
10. python 03_scripts/prompt_bus.py --status-json

Expected current truth from Codex N+3.51:
- base main HEAD is e7e946a or newer.
- N+3.49A is merged.
- prompt bus and local orchestrator exist.
- Ruflo exists at 21_repos/third_party/evals/ruflo.
- Ruflo package is claude-flow 3.5.80.
- Ruflo node_modules are not installed.
- Ruflo top-level package.json has no preinstall/install/postinstall/prepare lifecycle scripts.
- Nested Ruflo git HEAD may be blocked by Git dubious ownership; do not change global git config unless explicitly approved.
- Obsidian vault files exist.
- Obsidian app is not verified as installed/visible in this sandbox.
- Ollama is found, but current `ollama list` may show no Gemma model.
- Course/certificate route exists but needs broader safe keyword matching.

Implementation Part A - Dashboard local bridge read card:

Add a read-only dashboard route and card that summarize local bridge status.

Files likely touched:
- 01_projects/dashboard_mvp/server.js
- 01_projects/dashboard_mvp/public/app.js
- 01_projects/dashboard_mvp/public/index.html only if needed
- optional CSS only if existing patterns require it
- 14_context/ghoti_dashboard_n3_51a.md

Route proposal:
GET /api/ghoti/local-bridge/status

The route must read local files only:
- 14_context/prompt_bus/current_status.md
- 14_context/prompt_bus/outbox/
- 14_context/agent_lanes/active_locks.jsonl
- 14_context/agent_lanes/lane_status.jsonl
- 14_context/compact_memory/
- 14_context/obsidian_vault/
- 23_configs/local_worker_routing.example.json
- 21_repos/third_party/evals/ruflo/package.json

Response should include:
- status
- generated_at
- branch if easy/read-only
- prompt_bus:
  - canonical_prompt_exists
  - canonical_prompt_path
  - outbox_count
  - latest_outbox_files
- agent_lanes:
  - active_lock_count
  - latest_lock
  - latest_status
  - warnings
- local_workers:
  - routing_config_present
  - routing_config_valid
  - recommended_worker_summary if simple
- obsidian:
  - vault_present
  - required_files_present
  - app_install_verified false/unknown unless checked by helper output
- gemma:
  - ollama_detected if safe
  - model_detected if safe
  - no model pull
- ruflo:
  - dir_present
  - package_name
  - package_version
  - node_modules_installed
  - lifecycle_scripts_found
  - install_gate_required
- warnings
- source_files

Dashboard card title:
Ghoti Bridge - Local Operator Status

Card should show:
- prompt bus outbox count
- lane locks/status count
- Ruflo installed/not installed
- Ollama/Gemma available/not available/unknown
- Obsidian vault present/app unknown
- next manual action
- warnings

Allowed UI actions:
- refresh
- copy path text if existing UI pattern supports copy

Forbidden UI actions:
- approve
- execute
- install
- run Ruflo
- run Gemma
- open accounts
- send/post/pay/scrape
- mutate files

Implementation Part B - Prompt bus apply/context packs:

Improve `03_scripts/prompt_bus.py` or add `03_scripts/prompt_context_pack.py`.

Preferred if small:
- extend `prompt_bus.py` with a `--context-pack` command.

If cleaner:
- add `03_scripts/prompt_context_pack.py`.

Required behavior:
- stdlib only,
- dry-run default,
- `--apply` required to write,
- reads current state, next actions, compact memory, agent lanes, prompt bus status,
- generates local artifacts:
  - `claude_prompt.md`
  - `codex_prompt.md`
  - `chatgpt_handoff.md`
  - `context_pack.md`
  - `context_pack.json`
  - `run_summary.json`
- recommended output:
  `05_logs/prompt_context_packs/<run_id>/`
- optionally copies selected prompts to `14_context/prompt_bus/outbox/` only with `--apply`.
- never auto-sends.
- never touches clipboard unless a later explicit approval milestone adds it.

Suggested commands:
python 03_scripts/prompt_context_pack.py --help
python 03_scripts/prompt_context_pack.py --goal "N+3.51A bridge dashboard" --dry-run
python 03_scripts/prompt_context_pack.py --goal "N+3.51A bridge dashboard" --apply

Implementation Part C - Gemma compact memory draft worker:

Create:
03_scripts/gemma_compact_memory_worker.py

Requirements:
- Python stdlib only.
- dry-run default.
- no external APIs.
- repo-local only.
- read input markdown via `--input`.
- optional `--model gemma3:4b` default.
- `--check` verifies Ollama and model availability.
- `--compress --dry-run` prints planned command and output path but does not call Ollama.
- `--compress --apply` may call `ollama run <model>` only if model is present.
- If model is missing, do not pull automatically. Write a warning and optional prompt outbox draft.
- Never execute model output.
- Never overwrite canonical compact memory.
- Write drafts under:
  `05_logs/gemma_compact_memory_drafts/<run_id>/`
- Draft artifacts:
  - `draft_summary.md`
  - `source_map.json`
  - `promotion_checklist.md`
  - `run_summary.json`

Suggested commands:
python 03_scripts/gemma_compact_memory_worker.py --help
python 03_scripts/gemma_compact_memory_worker.py --check
python 03_scripts/gemma_compact_memory_worker.py --input 14_context/compact_memory/project_state.md --compress --dry-run
python 03_scripts/gemma_compact_memory_worker.py --input 14_context/compact_memory/project_state.md --compress --apply

The apply command must fail safely if no Gemma model is available.

Implementation Part D - Ruflo isolated install gate runner:

Create:
03_scripts/ruflo_install_gate.py

Requirements:
- Python stdlib only.
- repo-local only.
- no global install.
- no shell=True.
- no swarm/MCP/runtime wiring.
- no secrets.
- no live actions.
- no account actions.
- no browser automation.
- no hidden background process.
- never stage node_modules.

CLI:
python 03_scripts/ruflo_install_gate.py --help
python 03_scripts/ruflo_install_gate.py --check
python 03_scripts/ruflo_install_gate.py --install-dry-run
python 03_scripts/ruflo_install_gate.py --install-apply --confirm "INSTALL RUFLO ISOLATED DEPS ONLY"

Check behavior:
- verify path exists,
- parse package.json,
- print package name/version,
- verify package-lock.json exists,
- detect lifecycle scripts among preinstall/install/postinstall/prepare,
- report node_modules status,
- report nested git HEAD if possible,
- if dubious ownership blocks git, report it but do not fix global config.

Dry-run behavior:
- print exact command,
- no writes,
- no npm invocation.

Apply behavior:
- require exact confirm string,
- run:
  npm ci --ignore-scripts
  inside `21_repos/third_party/evals/ruflo`
- do not run any Ruflo command automatically after install,
- write `05_logs/ruflo_install_gate/<run_id>/run_summary.json`,
- write command output logs,
- never stage node_modules.

After install, only a future audited milestone may run local help/version.

Implementation Part E - Obsidian open helper polish:

Improve:
03_scripts/open_obsidian_vault.ps1

Add or improve:
- `-CheckInstall`,
- PATH check,
- common user install path check,
- winget list check if safe and non-mutating,
- clear output when app is not found,
- `-Open` remains explicit only,
- no dashboard auto-open,
- no vault writes.

If Obsidian app cannot be found, print manual guidance:
- install/open Obsidian manually,
- choose "Open folder as vault",
- select `C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\obsidian_vault`.

Implementation Part F - local_worker_router route improvements:

Improve `03_scripts/local_worker_router.py`:
- add natural course/certificate keywords:
  - complete a course
  - get a certificate
  - certificate ethically
  - study for certificate
  - course progress
  - course deadline
  - lesson summary
  - flashcards
- ensure those route to `course_certificate_assistant`.
- do not add unsafe keywords that imply cheating.

Add tests via CLI smoke:
python 03_scripts/local_worker_router.py --recommend --task "help me complete a course and get a certificate ethically"
python 03_scripts/local_worker_router.py --recommend --task "course certificate tracker and study plan"

Both should route to `course_certificate_assistant`.

Implementation Part G - docs and lane status:

Create docs:
- 14_context/claude_n3_51a_bridge_dashboard_gemma_ruflo.md
- 14_context/tooling/ruflo_install_gate_n3_51a.md
- 14_context/tooling/gemma_compact_memory_worker_n3_51a.md
- 14_context/prompt_bus_n3_51a_context_packs.md
- 14_context/ghoti_dashboard_n3_51a.md

Update lane status only if safe:
- 14_context/agent_lanes/lane_status.jsonl
- 14_context/agent_lanes/active_locks.jsonl if a lock was intentionally created/closed according to lane policy

Do not update broad state docs unless explicitly designated state owner.

Validation commands:
git status --short
python -c "import ast, pathlib; files=['03_scripts/ghoti_local_orchestrator.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files if pathlib.Path(f).exists()]; print('AST OK')"
python 03_scripts/ghoti_local_orchestrator.py --status
python 03_scripts/ghoti_local_orchestrator.py --obsidian-check
python 03_scripts/ghoti_local_orchestrator.py --ruflo-check
python 03_scripts/ghoti_local_orchestrator.py --gemma-check
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/agent_lane_status.py --check
python 03_scripts/ruflo_install_gate.py --check
python 03_scripts/ruflo_install_gate.py --install-dry-run
python 03_scripts/gemma_compact_memory_worker.py --check
python 03_scripts/gemma_compact_memory_worker.py --input 14_context/compact_memory/project_state.md --compress --dry-run
python 03_scripts/local_worker_router.py --recommend --task "help me complete a course and get a certificate ethically"
python -c "import json, pathlib; json.loads(pathlib.Path('23_configs/local_worker_routing.example.json').read_text(encoding='utf-8')); print('routing config JSON OK')"
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
if (Test-Path 01_projects/dashboard_mvp/public/overlay.js) { node --check 01_projects/dashboard_mvp/public/overlay.js }
git diff --check

Optional if dashboard route was added:
- run server only if already part of repo workflow and safe,
- do not open browser/live accounts,
- no external connections.

Staging:
Stage only intentional N+3.51A files.
Do not stage:
- unrelated logs,
- CV docs,
- output/,
- .claude/skills/,
- test temp files,
- `node_modules`,
- external repo changes,
- credentials or .env.

Commit:
feat(ghoti): add N+3.51 bridge dashboard Gemma and Ruflo gates

Push:
git push origin feat/ghoti-agent-claude-n3-51-bridge-dashboard-gemma-ruflo

Final report must include:
- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- bridge dashboard truth
- prompt bus/context pack truth
- Ruflo install gate truth
- Gemma worker truth
- Obsidian helper truth
- course/certificate router truth
- safety gates preserved yes/no
- whether any installs were actually run
- whether Gemma model was available
- dirty files intentionally left unstaged
- exact next Codex audit recommendation
```

## Why This Prompt Is Stronger

This prompt gives Claude:

- exact branch,
- exact safety boundaries,
- exact files,
- exact commands,
- exact CLI designs,
- exact dashboard route/card design,
- exact output locations,
- exact validation,
- exact staging,
- exact final report.

It also prevents the common failure modes:

- "Ruflo was cloned but not used" becomes "Ruflo gets a real isolated install gate."
- "Gemma exists but does not save tokens" becomes "Gemma gets a draft compression worker."
- "Prompt bus is still manual" becomes "Prompt bus gets context packs and handoffs."
- "Obsidian exists but user cannot see it" becomes "helper reports install/open truth."
- "Course assistant could drift into cheating" becomes "router and policy reinforce ethical boundaries."
