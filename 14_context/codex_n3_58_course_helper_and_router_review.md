# Codex N+3.58 - Course Helper And Router Review

## Verdict

PASS.

The N+3.56-FIX branch resolves the prior `--goal` and bridge-routing gaps.

## Course Helper Commands

```powershell
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --status
python 03_scripts/course_certificate_assistant.py --plan --course-name "Audit Smoke Course" --provider "Local Test" --goal "Create legitimate study plan only" --dry-run
```

Observed:

- `--goal` is supported.
- `--goal` is described as a personal learning objective for planning only.
- Dry-run writes nothing.
- Policy forbids fake certificates, cheating, assessment submission, impersonation, claiming completion without proof, proctoring bypass, and answer keys for graded work.
- Human does all assessments.

Direct answer: Course helper supports `--goal` safely? Yes.

## Router Commands

```powershell
python 03_scripts/local_worker_router.py --recommend --task "create bridge handoff for Claude Code and Codex"
python 03_scripts/local_worker_router.py --recommend --task "course certificate study plan with goal"
python 03_scripts/local_worker_router.py --recommend --task "use ruflo orchestrator candidate for local agent coordination"
python 03_scripts/local_worker_router.py --recommend --task "compress memory with local gemma"
python 03_scripts/local_worker_router.py --recommend --task "open obsidian vault and check memory"
```

Observed routes:

- Bridge handoff -> `cc_codex_bridge_worker`.
- Course certificate -> `course_certificate_assistant`.
- Ruflo orchestration candidate -> `ruflo_orchestrator_candidate`.
- Gemma compression -> `gemma_local_worker`.
- Obsidian memory -> `obsidian_memory_worker`.

## Safety Result

No course/helper behavior enables fake certificates, cheating, assessment submission, impersonation, or credential fraud. Router outputs preserve local/safe boundaries.
