# Codex N+3.50 - Orchestrator And Prompt Bus Audit

Milestone: N+3.50B - Audit Claude N+3.49A and prepare merge safety verdict

Date: 2026-05-06

## ghoti_local_orchestrator.py

File audited from Claude commit `c053fc6b3e1fca9ad90d39569f797a43272b2df7`.

### CLI Surface

The script exposes:

- `--status`
- `--plan-next`
- `--write-next-prompts`
- `--obsidian-check`
- `--ruflo-check`
- `--gemma-check`
- `--dry-run`
- `--apply`

### Behavior Summary

- `--status` prints Git, prompt bus, worker config, Obsidian, compact memory, lane, Ruflo, Ollama, and Gemma status.
- `--plan-next` prints a dry-run plan and rough capability percentages.
- `--write-next-prompts --dry-run` previews a Claude prompt and Codex prompt without writing.
- `--write-next-prompts --apply` writes:
  - `14_context/ghoti_current_prompt.md`
  - one Codex prompt under `14_context/prompt_bus/outbox/`
- `--obsidian-check` reads expected Obsidian vault and compact memory files.
- `--ruflo-check` reads Ruflo directory/package metadata if present.
- `--gemma-check` runs local `ollama --version` and `ollama list`.

### Dry-Run Review

`--write-next-prompts --dry-run` returned before any `write_text()` call. Smoke test left the validation worktree clean.

`--status`, `--plan-next`, `--obsidian-check`, `--ruflo-check`, and `--gemma-check` are read-only from the repo perspective.

### Subprocess Review

The script uses `subprocess.run()` with list arguments through `_run()`. No `shell=True` use was found.

Commands invoked are limited to:

- `git branch --show-current`
- `git rev-parse --short HEAD`
- `git rev-parse origin/feat/ghoti-visible-operator-stack`
- `git rev-parse --short HEAD` inside Ruflo dir, if present
- `ollama --version`
- `ollama list`

No email, posting, payment, scraping, browser automation, account login, npm install, or secrets access was found.

### External Tool Touches

- Ruflo: read-check only; no install or runtime wiring.
- Ollama/Gemma: read-check only; no model pull or model generation.
- Obsidian: file existence checks only.

### Issues

- The generated N+3.50A Claude prompt says "Current: ~65% | After N+3.50A: ~72%" while N+3.48 estimated current at 68% and next at 74%. This is a stale percentage, not a safety issue.
- In a detached validation worktree, branch name is blank/unknown and `ghoti_current_prompt.md` is missing. The script handles this gracefully.

## prompt_bus.py

### Added Behavior

N+3.49A adds:

- `--write-chatgpt`
- `--status-json`

### Behavior Summary

- `--status-json` prints JSON to stdout and writes nothing.
- `--write-chatgpt --dry-run` previews the target outbox file and writes nothing.
- `--write-chatgpt --apply` writes a timestamped handoff file under `14_context/prompt_bus/outbox/`.

### Safety Verdict

PASS.

No clipboard write, external API call, email send, posting, account action, payment, or scraping was found.

All prompt writes remain local file writes and require `--apply`.

## local_worker_router.py

### Added Routes

N+3.49A adds or expands routes for:

- Python automation worker
- course/certificate assistant
- Ruflo orchestrator candidate
- Obsidian memory worker
- prompt bus worker
- human approval required

### Smoke Results

- `write a small Python automation to organize local prompt files` routes to `python_automation_worker`.
- `use Ruflo to coordinate local agents` routes to `ruflo_orchestrator_candidate`.
- `help me complete a course and get a certificate ethically` routes to `claude_code_impl`.

### Safety Verdict

CONDITIONAL PASS.

The router correctly gates Ruflo as an isolated candidate and human-live actions as `human_approval_required`. However, the course/certificate route needs keyword tuning so plain ethical certificate language routes to `course_certificate_assistant`, not default Claude implementation.

## open_obsidian_vault.ps1

### Behavior

- `-Check` verifies required Obsidian vault files exist.
- `-Open` constructs an `obsidian://open?path=...` URI and calls `Start-Process`.

### Safety Verdict

PASS with local-app caveat.

The helper does not modify vault contents, connect accounts, install plugins, or call network APIs. `-Open` launches the local Obsidian app if present. This is acceptable as a manual local helper, but should not be called automatically by dashboard/server routes.

## Ruflo Check Behavior

`ghoti_local_orchestrator.py --ruflo-check`:

- checks whether `21_repos/third_party/evals/ruflo` exists
- optionally runs `git rev-parse --short HEAD` inside the Ruflo directory
- parses `package.json`
- detects lifecycle scripts named `preinstall`, `postinstall`, or `prepare`
- checks whether `node_modules` exists
- recommends `npm ci --ignore-scripts` if `package-lock.json` exists

It does not:

- run npm install
- run Ruflo
- start an MCP server
- read credentials
- connect accounts
- create background processes
- write repo files

## Command Write Matrix

| Command | Writes during dry-run? | Writes with apply? | External/live actions? |
|---|---:|---:|---:|
| `ghoti_local_orchestrator.py --status` | No | N/A | Local git/ollama read checks only |
| `ghoti_local_orchestrator.py --plan-next` | No | N/A | No |
| `ghoti_local_orchestrator.py --write-next-prompts --dry-run` | No | N/A | No |
| `ghoti_local_orchestrator.py --write-next-prompts --apply` | N/A | Yes, local prompt files | No |
| `ghoti_local_orchestrator.py --obsidian-check` | No | N/A | No |
| `ghoti_local_orchestrator.py --ruflo-check` | No | N/A | Local read-check only |
| `ghoti_local_orchestrator.py --gemma-check` | No | N/A | Local `ollama` read-check only |
| `prompt_bus.py --status-json` | No | N/A | No |
| `prompt_bus.py --write-chatgpt --dry-run` | No | N/A | No |
| `prompt_bus.py --write-chatgpt --apply` | N/A | Yes, local outbox file | No |

## Overall Verdict

The orchestrator and prompt bus remain local, dry-run-first, and supervised. They are safe to merge with follow-up improvements for course/certificate routing and environment truth around Gemma/Ruflo.
