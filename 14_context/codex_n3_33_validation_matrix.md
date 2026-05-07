# Codex N+3.33 Validation Matrix

Status: codex_audit_only / validation_matrix / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Provide Claude Code with a compact validation matrix for finishing or pausing N+3.18. Commands are PowerShell-friendly where possible.

Codex did not run these validators in this milestone because Codex did not change JS/Python/JSON implementation files and the user requested documentation-only recovery.

## local_brain_router.py Validators

File:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
```

Static compile:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
```

Help/no-action smoke:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
```

Existing compress context smoke, local model required:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/money_workflows/video_to_money_intake_template.md --max-chars 12000
```

New video-to-money smoke, local model required:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Expected success symptoms:

- returns exit code 0
- creates `05_logs/money_runs/<run_id>/`
- writes required artifacts
- run summary has no external/live actions
- no tracker mutation
- no model output execution

Failure symptoms:

- syntax error from `py_compile`
- `ollama not found on PATH`
- model timeout
- input path rejected
- `.md` sample missing
- output missing expected artifacts
- candidate JSONL collapsed into one malformed record

Likely fixes Claude should try:

- fix syntax/import errors first
- ensure sample input path is repo-relative and exists
- keep `.md`/`.txt` restriction
- harden candidate parser around repeated keys and blank-line assumptions
- force `approval_required` to boolean true
- add parse warnings to artifacts instead of silently losing candidates

## money_workflow_new_experiment.py Validators

File:

```text
03_scripts/money_workflow_new_experiment.py
```

Static compile:

```powershell
python -m py_compile 03_scripts/money_workflow_new_experiment.py
```

Help smoke:

```powershell
python 03_scripts/money_workflow_new_experiment.py --help
```

Unscored dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "Prompt pack smoke" --target-customer "solo AI builders" --pain-point "starting from blank prompts wastes time" --offer "local prompt pack draft" --next-action "draft local outline only" --risk-level low --channel manual_review_first
```

Scored dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "AI operator prompt pack" --target-customer "solo AI builders" --pain-point "They waste time rebuilding prompts" --offer "Prompt pack draft artifact" --next-action "Draft local product outline only" --risk-level low --channel manual_review_first --speed-to-ship 5 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Partial scoring should fail:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "bad partial score" --target-customer "test" --pain-point "test" --offer "test" --next-action "test" --speed-to-ship 5
```

Out-of-range scoring should fail:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "bad score" --target-customer "test" --pain-point "test" --offer "test" --next-action "test" --speed-to-ship 6 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Expected success symptoms:

- dry-run does not append to tracker
- scored dry-run prints `total_score` and `priority_bucket`
- lower-is-better fields are inverted in `adjusted_scores`
- medium/high/live-action wording sets `approval_required` true

Failure symptoms:

- typo in CLI args silently ignored
- partial scoring accepted unexpectedly
- score outside 1-5 accepted
- scoring object missing in dry-run
- dry-run accidentally writes to JSONL

Likely fixes Claude should try:

- fail on unknown args if feasible
- keep all-ten-or-none scoring rule
- keep dry-run write-free
- add validation docs showing expected bucket math

## experiment_tracker.schema.json Validators

File:

```text
14_context/money_workflows/experiment_tracker.schema.json
```

JSON parse:

```powershell
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > $null
```

Schema shape review:

```powershell
Select-String -Path 14_context/money_workflows/experiment_tracker.schema.json -Pattern '"scoring"|"raw_scores"|"adjusted_scores"|"priority_bucket"'
```

Expected success symptoms:

- JSON parses
- `scoring` object exists
- `priority_bucket` enum includes `A`, `B`, `C`, `D`
- schema matches the record emitted by the script

Failure symptoms:

- JSON parse error
- produced record has keys missing from schema
- schema allows partial raw scores despite script requiring all ten

Likely fixes Claude should try:

- add inner `required` lists for the ten score fields
- keep optional `scoring` at top level
- add adjusted score min/max if desired

## experiment_tracker.jsonl Validators

File:

```text
14_context/money_workflows/experiment_tracker.jsonl
```

Line-by-line JSON parse:

```powershell
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/experiment_tracker.jsonl'); rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print(f'experiment tracker jsonl ok: {len(rows)} rows')"
```

Optional score presence check:

```powershell
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/experiment_tracker.jsonl'); rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print(sum(1 for r in rows if 'scoring' in r), 'scored rows')"
```

Expected success symptoms:

- all lines parse
- sample rows remain local/planning-only
- no live-action fields imply execution

Failure symptoms:

- malformed JSONL line
- appended smoke record unintentionally committed
- revenue or proof fields imply real results without manual metrics

Likely fixes Claude should try:

- do not rewrite tracker unless intentionally appending a reviewed record
- keep smoke commands in dry-run mode unless append is explicitly desired
- preserve sample-only notes

## Global Git Validators

Whitespace:

```powershell
git diff --check
```

Staged whitespace:

```powershell
git diff --cached --check
```

Staged file review:

```powershell
git diff --cached --name-status
```

Expected success symptoms:

- only intentional N+3.18 files staged
- no `.claude/skills/`, CV docs, `output/`, third-party dirt, prompt scratch files, or unrelated local logs staged
- no unrelated external repo intake docs staged

## Safe Smoke Policy

Safe:

- local py_compile
- local JSON parse
- local JSONL parse
- dry-run helper commands
- local Gemma smoke only when operator allows and no live actions occur

Not safe for N+3.18:

- YouTube fetch/download
- scraping
- posting
- selling/listing products
- email/outreach sending
- payments
- account login
- model-output execution
- Docker/CUA/browser actions unrelated to the local runner

## Final Validation Gate

Before commit, Claude should have evidence for:

- router compile pass
- money helper compile pass
- schema parse pass
- tracker JSONL parse pass
- video-to-money smoke pass or documented blocked reason
- scoring dry-run pass
- `git diff --check` pass
- staged file list reviewed

If any of these are missing, do not call N+3.18 finished.
