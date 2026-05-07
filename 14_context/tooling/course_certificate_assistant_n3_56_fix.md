# Course/Certificate Assistant — N+3.56-FIX

**Script**: `03_scripts/course_certificate_assistant.py`

## What changed in N+3.56-FIX

- Added optional `--goal` argument to `--plan` mode.
- Goal appears in generated plan as personal learning objective.
- `--policy` updated to document `--goal`.
- All existing safety rules unchanged.

## --goal behavior
- Optional. Default: none.
- If provided, appears in plan output under "Goal:" with a clarification note.
- The note states: goal is for planning purposes only; does not imply fake certification, assessment submission, or any shortcut.
- Policy still says NO to: fake certs, cheating, assessment submission, impersonation, proctoring bypass.

## Validation commands
```bash
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Audit Smoke Course" --provider "Local Test" --goal "Create legitimate study plan only" --dry-run
python 03_scripts/course_certificate_assistant.py --tracker --course-name "Audit Smoke Course" --dry-run
python 03_scripts/course_certificate_assistant.py --certificate-log --course-name "Audit Smoke Course" --provider "Local Test" --dry-run
python 03_scripts/course_certificate_assistant.py --status
```

## Safety (unchanged)
- NO fake certificates
- NO assessment submission
- NO cheating
- NO impersonation
- Human does all assessments
