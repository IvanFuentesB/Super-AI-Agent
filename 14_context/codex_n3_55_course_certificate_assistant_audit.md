# Codex N+3.55 - Course Certificate Assistant Audit

## Verdict

AUDIT STATUS: PENDING TARGET BRANCH

The course/certificate assistant cannot be audited because the real N+3.51 implementation branch is missing.

## Required Ethical Boundary

Allowed:

- Course discovery.
- Study plans.
- Lesson summaries.
- Flashcards and notes.
- Progress tracking.
- Deadline reminders.
- Certificate checklists.
- Portfolio proof organization.

Forbidden:

- Impersonating the user.
- Taking quizzes, tests, exams, or assessments for the user.
- Submitting assessments or coursework.
- Bypassing proctoring.
- Creating fake certificates.
- Misrepresenting credentials.
- Violating course terms of service.

## What Must Be Proven On The Real Branch

- `03_scripts/course_certificate_assistant.py` exists.
- `--policy` clearly states the ethical boundary.
- `--plan`, `--tracker`, `--certificate-log`, and `--status` work.
- Dry-run writes nothing.
- Apply mode, if present, writes only local study/tracker/checklist artifacts.
- No credentials, browser automation, account actions, submissions, or external course-site actions occur.
- Local worker routing sends legitimate study tasks to this helper.

## Required Commands Once Target Exists

```powershell
python 03_scripts/course_certificate_assistant.py --help
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Python Automation Foundations" --provider "Local/Online" --hours 10 --deadline "2026-06-01" --dry-run
python 03_scripts/course_certificate_assistant.py --tracker --course-name "Python Automation Foundations" --dry-run
python 03_scripts/course_certificate_assistant.py --certificate-log --course-name "Python Automation Foundations" --provider "Local/Online" --dry-run
python 03_scripts/course_certificate_assistant.py --status
```

## Direct Answer

Are course/cert workflows ethical and useful? The intended workflow is ethical if it stays study/tracker/checklist-only. It is not proven implemented until the branch is pushed.
