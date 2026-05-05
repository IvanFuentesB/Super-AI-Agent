# Codex N+3.46 - Claude N+3.45A Branch Audit

Milestone: N+3.46 - Audit N+3.45A Claude Tooling/Prompt Bus Branch And Prepare Safe Merge

Date: 2026-05-05

## Branch Truth

- Base branch: `feat/ghoti-visible-operator-stack`
- Base HEAD before N+3.45 merge: `46941c8a0e68a8f67fe6ceb00e1be40032c8629b`
- Claude implementation branch: `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`
- Claude branch HEAD: `13266eaf663bc0a6b7d205d57d869263b1af6e38`
- Claude expected commit: `13266ea feat(ghoti): add N+3.45A tooling and prompt bus`
- Codex audit branch: `origin/audit/ghoti-agent-codex-n3-45-tool-routing`
- Codex branch HEAD: `c79940106f85ceffa30fba2e6de32225bec4c6fe`

## Claude Branch Diff Scope

Claude branch changed only the expected N+3.45A implementation/tooling files:

- `.claude/commands/ghoti-status.md`
- `.claude/commands/goal.md`
- `.claude/commands/prompt-bus.md`
- `.claude/commands/ultraplan.md`
- `03_scripts/local_worker_router.py`
- `03_scripts/prompt_bus.py`
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `14_context/claude_commands_n3_45a.md`
- `14_context/local_worker_routing_n3_45a.md`
- `14_context/local_workers/`
- `14_context/prompt_bus/`
- `14_context/prompt_bus_n3_45a.md`
- `14_context/tooling/`
- `23_configs/local_worker_routing.example.json`

No Codex `codex_n3_45b_*.md` files were present in the Claude branch diff against base.

## Validation Evidence

Validated from branch `feat/ghoti-agent-claude-n3-45-tooling-prompt-bus` after `git pull --ff-only` confirmed the branch was up to date.

Commands run:

```powershell
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK prompt_bus.py local_worker_router.py')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --init --dry-run
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --list-outbox
python 03_scripts/local_worker_router.py --help
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/local_worker_router.py --study-template --dry-run
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
```

Results:

- Python AST validation: PASS.
- Prompt bus help/status/list/write dry-run smokes: PASS.
- Local worker router help/recommend/template dry-run smokes: PASS.
- Agent lane status check/list: PASS.
- `23_configs/local_worker_routing.example.json`: JSON PASS.
- `14_context/agent_lanes/active_locks.jsonl`: JSONL PASS, 1 record.
- `14_context/agent_lanes/lane_status.jsonl`: JSONL PASS, 2 records.
- `git diff --check`: PASS, with only an LF-to-CRLF warning on pre-existing dirty `14_context/ghoti_external_repo_tool_intake.md`.

## Safety Review

### prompt_bus.py

Verdict: mostly safe, with one dry-run purity issue.

Positive findings:

- Python stdlib only.
- No external API calls.
- No clipboard writes.
- No email, posting, payment, browser automation, or live-account actions.
- `--write-claude` and `--write-codex` require `--apply` before writing.
- `--status` and `--list-outbox` are read-only.

Finding:

- `cmd_init()` calls `_ensure_dirs()` before checking `--dry-run`, so `python 03_scripts/prompt_bus.py --init --dry-run` may create prompt bus directories even while reporting dry-run. In the committed branch those directories already exist, so this did not dirty the tree during smoke testing. It is still a real dry-run contract bug and should be fixed before merge if strict dry-run purity is required.

Recommended fix:

Move `_ensure_dirs()` inside the `args.apply` path, or check dry-run before creating directories.

### local_worker_router.py

Verdict: safe for local routing recommendations and dry-run templates.

Positive findings:

- Python stdlib only.
- No network calls during tested commands.
- No account actions.
- No live sends/posts/payments.
- Deterministic work routes to `python_automation_worker`.
- Compression/draft work routes to `gemma_local_worker`.
- Dashboard/code edits route to `claude_code_impl`.
- JSONL validation routes to `python_automation_worker`.
- Live/account/public/money keywords route to `human_approval_required`.

Note:

- `_check_ollama_available()` exists and would call `ollama list`, but it is not exposed through the current CLI path and was not run during this audit. The file comments say this check is disabled by default.

### Claude Slash Commands

Verdict: safe enough for merge if the user accepts local command helpers.

Positive findings:

- Slash commands are local Claude Code prompt helpers.
- Commands include safety reminders: no live accounts, no cap bypass, no destructive git ops without confirmation, stage only intentional milestone files.
- `/ultraplan` is planning-only and explicitly says not to implement.
- `/prompt-bus` documents manual copy-paste workflow and no clipboard write by default.

Potential risk:

- `.claude/commands/goal.md` allows Bash, Read, Write, Edit, Glob, Grep and instructs Claude to execute the current prompt. This is consistent with Claude implementation lanes, but should not be used as a bypass around lane locks, file ownership, or human approval gates.

### Obsidian

Verdict: documented as local-only and no account/cloud sync.

Evidence:

- `14_context/tooling/obsidian_install_and_vault_link_n3_45a.md` states Obsidian 1.12.7 was installed via `winget`.
- The doc instructs: no Obsidian Sync, no plugins, no account login.
- Vault path remains repo-local: `14_context/obsidian_vault`.

Audit note:

- Codex did not install Obsidian in this audit. This audit only reviewed Claude's documentation of the install.

### Ruflo

Verdict: not wired into Ghoti runtime.

Evidence:

- Claude branch tracks only docs for Ruflo intake, not the Ruflo repository itself.
- `git ls-files 21_repos/third_party/evals/ruflo` returned no tracked files.
- A local nested Git checkout exists at `21_repos/third_party/evals/ruflo`, but it is not staged/tracked in the main repo.
- Docs say no npm install, no MCP launch, no API key, no runtime wiring.

Risk note:

- Because the local Ruflo eval repo exists outside the main Git index, it remains a local cleanup/research concern and should not be staged into `feat/ghoti-visible-operator-stack`.

## Lane Records

`active_locks.jsonl` has one Claude lock:

- agent: `claude_code_n3_45a`
- branch: `feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`
- task: `tooling-prompt-bus`
- locked files include `03_scripts/prompt_bus.py`, `03_scripts/local_worker_router.py`, `14_context/prompt_bus/README.md`, and `14_context/tooling/tooling_bootstrap_n3_45a.md`

`lane_status.jsonl` has two records:

- implementation started
- implementation complete validation passed

Both JSONL files parse.

## Merge Verdict

Claude branch audit verdict: CONDITIONAL PASS.

Reason:

- No live-account, posting, sending, payment, scraping, job application, giveaway, browser-operator, or external orchestrator wiring risk was found.
- Branch changed the expected Claude-owned implementation/tooling files.
- Validation and smoke tests passed.
- The branch is merge-safe from a file separation perspective.
- The only material issue is local and fixable: `prompt_bus.py --init --dry-run` is not a pure dry-run.

Recommended action:

- Best path: have Claude patch the dry-run purity bug on the Claude branch, validate, then merge.
- Acceptable path: merge now if the user explicitly accepts the local-only dry-run issue as non-blocking, then fix it in the next small maintenance milestone.
