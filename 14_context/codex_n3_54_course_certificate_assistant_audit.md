# Codex N+3.54 - Course Certificate Assistant Audit

## Verdict

AUDIT STATUS: PENDING TARGET BRANCH

The N+3.51 course/certificate assistant cannot be audited because the real implementation branch is not pushed.

## Required Ethical Boundary

The future course/certificate assistant may support legitimate learning only.

Allowed:

- Course discovery.
- Study plans.
- Lesson summaries.
- Notes and flashcards.
- Progress tracking.
- Deadline reminders.
- Certificate checklists.
- Portfolio evidence organization.
- Reflection prompts and study review.

Forbidden:

- Impersonating the user.
- Taking quizzes, tests, exams, or assessments for the user.
- Submitting assessments or coursework without explicit user work and approval.
- Bypassing proctoring.
- Creating fake certificates.
- Misrepresenting completion or credentials.
- Violating course terms of service.

## Required N+3.51 Audit Questions

When the target branch is pushed, Codex must verify:

- Does `03_scripts/course_certificate_assistant.py` exist?
- Does `--policy` clearly forbid cheating, impersonation, fake certificates, and assessment automation?
- Do `--plan`, `--tracker`, and `--certificate-log` work in dry-run mode?
- Does dry-run write nothing?
- Does apply mode write only local study/tracker artifacts?
- Does the helper avoid credentials, login handling, external submissions, account actions, and browser automation?
- Does local worker routing send legitimate course tasks to this assistant?
- Is it useful enough for real study planning without crossing ethical lines?

## Required Validation Commands Later

```powershell
python 03_scripts/course_certificate_assistant.py --help
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Python Automation Foundations" --dry-run
python 03_scripts/course_certificate_assistant.py --tracker --course-name "Python Automation Foundations" --dry-run
python 03_scripts/course_certificate_assistant.py --certificate-log --course-name "Python Automation Foundations" --dry-run
```

## Current Course Assistant Verdict

The concept is ethical and useful if limited to planning/tracking/study support. It is not implemented or auditable until the N+3.51 branch is pushed.
