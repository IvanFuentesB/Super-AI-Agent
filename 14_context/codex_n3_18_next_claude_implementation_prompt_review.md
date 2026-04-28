# Codex N+3.18 Next Claude Implementation Prompt Review

Status: codex_audit_only / next_claude_scope_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 6be07a5

## Recommended Claude Code Milestone

N+3.18 Claude - Gemma Video-to-Money Intake Runner + Money Experiment Scoring

## What Claude Code Should Implement

Create a local, repo-root-bound runner that turns a local markdown/text transcript or notes file into artifact-only money workflow outputs.

Suggested files:

- `03_scripts/money_video_to_money_runner.py`
- `14_context/money_workflows/video_to_money_runner_readme.md`
- optional update to `14_context/money_workflows/experiment_tracker.schema.json` to include scoring fields
- optional sample input under `14_context/money_workflows/video_intake/` only if synthetic and clearly marked sample
- optional run artifacts under `05_logs/money_workflow_runs/<run_id>/`

Do not modify dashboard or runtime code in the first implementation unless the user explicitly expands scope.

## Required Runner Behavior

- Accept `--input <repo-local .md/.txt path>`.
- Accept `--max-chars`, default 12000.
- Accept `--dry-run`.
- Reject URLs and outside-repo paths.
- Reject unsupported extensions.
- Use local Gemma/Ollama only if available.
- Write artifacts under `05_logs/money_workflow_runs/<run_id>/`.
- Write request/source/prompt/response/summary artifacts.
- Generate business summary, product candidates, content angles, distribution plan, risk review.
- Generate experiment candidates as local run artifacts only.
- Do not auto-append to canonical tracker.

## Files Claude Should Avoid

- `14_context/ghoti_current_prompt.md`
- `14_context/ghoti_current_prompt_N1_6.md`
- third-party repo contents
- `.claude/skills/`
- CV docs
- `output/`
- live account configs
- dashboard files unless explicitly requested
- runtime files unless explicitly required

## Validation Commands

Minimum:

```powershell
python -m py_compile 03_scripts/money_video_to_money_runner.py
python -c "import json; json.load(open('14_context/money_workflows/experiment_tracker.schema.json', encoding='utf-8')); print('schema json ok')"
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/experiment_tracker.jsonl', encoding='utf-8') if line.strip()]; print('tracker jsonl ok')"
git diff --check
git diff --cached --check
```

Dry-run smoke:

```powershell
python 03_scripts/money_video_to_money_runner.py --input 14_context/money_workflows/video_to_money_intake_template.md --max-chars 12000 --dry-run
```

Optional real local smoke if Gemma/Ollama is available and user scope permits:

```powershell
python 03_scripts/money_video_to_money_runner.py --input 14_context/money_workflows/video_to_money_intake_template.md --max-chars 12000
```

The smoke must create artifacts only. It must not append to the canonical tracker and must not perform live actions.

## Stage / Commit / Push Plan

Before staging:

```powershell
git status --short
git diff --cached --name-status
```

Stage only N+3.18 implementation files.

Suggested commit:

```text
feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring
```

Push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Format

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- runner smoke result
- artifact path
- whether canonical tracker was changed
- runtime wiring truth
- install/run truth
- live account truth
- dirty files intentionally left unstaged
- next milestone

## Explicit No-Go List

Claude must not:

- fetch URLs
- scrape YouTube or comments
- download videos
- post content
- send outreach
- sell/list/upload products
- use payment or app-store workflows
- run Docker/CUA
- install Paperclip/OpenClaw/n8n/Unity-MCP/Mythos/Dolphin/CUDA/Manus
- clone leaked/proprietary code
- execute model output
- weaken approval gates

## Exact Next Milestone After Implementation

N+3.19 - Money Workflow Dashboard Read View + Shot Counter

Goal:

- Add read-only dashboard visibility for experiment count, top priority candidates, approval-needed items, and weekly shot counter.
- No posting, selling, outreach, payment, app-store, or live-account action.
