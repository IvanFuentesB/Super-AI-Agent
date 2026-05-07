# Supervised Content MVP — Tooling Notes (N+3.65)

**Milestone:** N+3.65
**Script:** `03_scripts/supervised_content_mvp_runner.py`

---

## Purpose

Implements a local, fully auditable content artifact packet generator. Turns the
OpenFang + MoneyPrinter + LLM Council + content runway ideas into a Ghoti-native,
local, auditable workflow.

Produces one complete content artifact packet from:
idea → review → script → shot list → rights/TOS/brand-safety →
human approval packet → manual publish checklist → Obsidian memory snapshot →
readiness score.

---

## Safety Invariants

All invariants are encoded in SAFETY_FLAGS at the top of the script and in the
manifest of every proof packet written:

| Flag | Value |
|------|-------|
| live_posting | false |
| upload | false |
| account_login | false |
| fake_engagement | false |
| external_api_calls | false |
| clone_install_run_external_repos | false |
| human_approval_required | true |

---

## CLI

```
python 03_scripts/supervised_content_mvp_runner.py --status
python 03_scripts/supervised_content_mvp_runner.py --list-runs

python 03_scripts/supervised_content_mvp_runner.py --run \
  --niche "..." --idea "..." --audience "..." --platform "..." --goal "..." \
  --dry-run

python 03_scripts/supervised_content_mvp_runner.py --run \
  --niche "..." --idea "..." --audience "..." --platform "..." --goal "..." \
  --apply

python 03_scripts/supervised_content_mvp_runner.py --show-latest
python 03_scripts/supervised_content_mvp_runner.py --validate-latest
```

---

## LLM Council Integration

If `03_scripts/llm_council_runner.py` exists, the runner uses its local/demo logic
by mirroring the 3-stage pattern:
- Stage 1: independent opinions (pragmatist, critic, synthesizer)
- Stage 2: anonymous peer review
- Stage 3: chairman synthesis

If it cannot be called safely (script missing), a deterministic fallback is used.
The packet records which path was taken in `02_llm_council_review.md`.

No external API is called in either path.

---

## Proof Packet

Written under `14_context/content_workflows/runs/<timestamp_slug>/` with `--apply`.

Contains 12 files — see `14_context/tooling/content_artifact_packet_n3_65.md`
for the full packet spec.

---

## Validation

`--validate-latest` checks:
- All 12 files exist
- manifest.live_posting = false
- manifest.external_api_calls = false
- manifest.human_approval_required = true
- All 5 gates = pending_human_review
- supervised_mvp_slice_score = 100
- production_public_release_ready = false
- No file claims published/uploaded/revenue
