# Money Workflow Helper Script — N+3.17

Date: 2026-04-28
Milestone: N+3.17
Branch: feat/ghoti-visible-operator-stack
Status: implemented / tested / no_external_api

---

## What Was Built

`03_scripts/money_workflow_new_experiment.py`

A Python standard-library-only CLI script that appends one JSON object to `14_context/money_workflows/experiment_tracker.jsonl`.

---

## Usage

```
python 03_scripts/money_workflow_new_experiment.py \
  --workflow-type digital_product \
  --source "YouTube: 'How to make money with AI templates'" \
  --product-idea "AI operator starter kit for solo builders" \
  --target-customer "solo AI builders and engineering students" \
  --pain-point "setup is confusing and there is no simple safe starter system" \
  --offer "$17 markdown template bundle with safety checklists" \
  --next-action "draft MVP outline and review before any pricing" \
  --risk-level low \
  --channel email_list \
  --channel tiktok
```

Add `--dry-run` to print without writing.

---

## Required Arguments

| Flag | Description |
|---|---|
| `--workflow-type` | Category (digital_product, prompt_pack, video_to_business_system, etc.) |
| `--source` | Origin of the idea |
| `--product-idea` | One-sentence description |
| `--target-customer` | Who the buyer is |
| `--pain-point` | The problem being solved |
| `--offer` | What is offered and how |
| `--next-action` | Most important next step |

## Optional Arguments

| Flag | Default | Description |
|---|---|---|
| `--risk-level` | low | low / medium / high |
| `--channel` | (none) | Repeatable; comma-separated ok |
| `--dry-run` | false | Print JSON without writing |

---

## Automatic approval_required Logic

- `true` if risk_level is medium or high
- `true` if any required field contains live-action words (post, publish, send, email, sell, buy, etc.)
- `false` for low-risk records with no live-action words

---

## Experiment ID Format

`exp_YYYYMMDD_HHMMSS_<6-char-hash>` — generated from UTC timestamp, deterministic from run time.

---

## Safety Properties

- Standard library only — no external API, no network calls
- No posting, selling, emailing, scraping, or account actions
- Writes only to `14_context/money_workflows/experiment_tracker.jsonl`
- Does not modify any other repo file
- `approval_required` defaults to true for medium/high risk

---

## Smoke Tests (N+3.17)

Test 1 (dry-run):
```
python 03_scripts/money_workflow_new_experiment.py \
  --dry-run \
  --workflow-type digital_product \
  --source "test" \
  --product-idea "Test prompt pack" \
  --target-customer "solo creator" \
  --pain-point "too many ideas, no execution system" \
  --offer "simple workflow templates" \
  --next-action "review"
```

Expected: prints JSON to stdout, no file write.

Test 2 (real append): one safe sample appended to `experiment_tracker.jsonl`.

---

## Output File

`14_context/money_workflows/experiment_tracker.jsonl` — JSONL format, one record per line, append-only.
