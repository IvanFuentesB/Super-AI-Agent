# Codex N+3.52 - Next Claude Implementation Brief

## Recommended Milestone

`N+3.51A - Safe Write Fallback + Ruflo Isolated Install + Gemma Draft Compression + Course Helper + Prompt Bus Apply Hardening`

If the N+3.50A branch cannot be pushed or recovered, rename this to `N+3.50A-Recovery` and rebuild from main cleanly.

## Branch

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git status --short
git push origin feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git switch -c feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
```

If dirty N+3.51A work already exists, inspect it before committing. Do not reset or discard it without explicit human approval.

## Goal

Move Ghoti from local bridge scaffolding toward a usable supervised bridge by fixing the hard gaps from Codex N+3.52.

## Allowed Files

Expected files to touch:

- `03_scripts/ruflo_install_gate.py`
- `03_scripts/gemma_compact_memory_worker.py`
- `03_scripts/prompt_bus.py`
- `03_scripts/local_worker_router.py`
- `03_scripts/ghoti_dashboard.py`
- `03_scripts/open_obsidian_vault.ps1`
- `03_scripts/course_certificate_assistant.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/index.html`
- `14_context/tooling/ruflo_install_gate_n3_51a.md`
- `14_context/tooling/gemma_compact_memory_worker_n3_51a.md`
- `14_context/prompt_bus_n3_51a_context_pack_hardening.md`
- `14_context/ghoti_dashboard_n3_51a.md`
- `14_context/course_certificate_assistant_n3_51a.md`
- `14_context/claude_n3_51a_ruflo_gemma_bridge_hardening.md`
- `23_configs/ruflo_install_gate.example.json`
- `23_configs/gemma_compact_memory_worker.example.json`

Do not touch unrelated docs, CVs, logs, `.env`, credentials, browser cookies, external accounts, or external repos except read-only Ruflo package metadata.

## Required Implementation

### Ruflo Install Gate

- Keep Python stdlib-only.
- Add an explicit confirmation flag such as `--confirm-local-ruflo-install`.
- `--install --apply` without confirmation must fail safely.
- Locate npm safely or document that npm is missing.
- Only approved install command:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

- No global install.
- No `npx`.
- No swarm launch.
- No MCP launch.
- No credentials.
- No live accounts.
- No hidden background processes.
- Log install/smoke results locally only when apply is explicit.

### Gemma Draft Compression

- Do not pull models automatically.
- Add `--model` override.
- If no Gemma model exists, create a safe draft/fallback artifact explaining what is missing.
- If a Gemma model exists, call local Ollama only.
- Write only to `05_logs/gemma_compact_runs/<run_id>/` and optionally `14_context/prompt_bus/outbox/`.
- Never overwrite `14_context/compact_memory/*.md` directly.
- Label every output `DRAFT_ONLY`, `NOT_CANONICAL`, and `HUMAN_REVIEW_REQUIRED`.

### Prompt Bus Hardening

- Default context packs should be dry-run or outbox-first.
- Overwriting `14_context/ghoti_current_prompt.md` must require explicit confirmation.
- Add a `--review` or equivalent mode that lists exact writes before apply.
- Fix local worker routing for prompt-bus/context-pack tasks.
- Add status JSON fields for latest context packs.

### Dashboard Truth

Render explicit fields:

- `bridge_auto_control = false`
- `manual_copy_paste_required = true`
- `ruflo_runtime_wired = false`
- `gemma_token_saving_ready = true/false based on model plus successful draft write`
- `obsidian_app_accessible = true/false based on helper check`

No approve, execute, install, send, post, pay, scrape, account, or job buttons.

### Obsidian Helper

- Keep `-Check` read-only.
- Add optional `-ExePath` support if safe.
- Explain the profile mismatch between `C:\Users\Navif\...` and `C:\Users\ai_sandbox\...`.
- Do not open by default unless `-Open` is explicit.

### Course/Certificate Helper

Create `03_scripts/course_certificate_assistant.py` if feasible.

Allowed local outputs:

- study plan
- notes template
- flashcards template
- progress tracker
- certificate checklist
- portfolio proof organizer

Forbidden:

- impersonation
- cheating
- proctoring bypass
- fake certificates
- fake credentials
- submitting assessments for the user
- violating course ToS

## Validation Suite

```powershell
python -c "import ast, pathlib; files=['03_scripts/ghoti_dashboard.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py','03_scripts/course_certificate_assistant.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files if pathlib.Path(f).exists()]; print('AST OK')"
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/ghoti_dashboard.py --card --dry-run
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/ruflo_install_gate.py --install --apply
python 03_scripts/ruflo_install_gate.py --install --apply --confirm-local-ruflo-install
python 03_scripts/ruflo_install_gate.py --smoke
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --max-chars 2500 --dry-run
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-context-pack --target all --title "n3-51a-smoke" --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/local_worker_router.py --recommend --task "create prompt bus context pack for claude and codex"
python 03_scripts/local_worker_router.py --recommend --task "course certificate study plan for a legitimate online course"
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
git diff --check
```

The Ruflo install command without confirmation should fail safely. The confirmed install may run only if the operator explicitly approves isolated install.

## Commit Message

```text
feat(ghoti): harden N+3.51 local bridge gates
```

## Final Report Requirements

Include branch, starting HEAD, new commit hash, pushed yes/no, validation pass/fail table, Ruflo install readiness, Gemma token-saving readiness, prompt bus context-pack readiness, dashboard bridge truth, course/certificate helper status, dirty files left unstaged, and exact next Codex audit recommendation.

## Safety Gate

No live accounts, email, posting, payments, scraping, job applications, giveaways, secrets, external swarms, hidden agents, cap bypass, fake certificates, impersonation, or assessment submission.
