# Codex N+3.51 - Course / Certificate Assistant Policy

Milestone: N+3.51

Date: 2026-05-06

## Current Router Truth

File audited:

```text
03_scripts/local_worker_router.py
```

The router includes a `course_certificate_assistant` route with keywords including:

- `course certificate`
- `certificate tracker`
- `study plan`
- `study tracker`
- `coursera`
- `udemy`
- `linkedin learning`
- `badge`
- `learning path`
- `course cert`

Positive test:

```powershell
python 03_scripts/local_worker_router.py --recommend --task "course certificate tracker and study plan"
```

Result:

```text
Route: course_certificate_assistant
Description: Course/cert tracker. Templates + study plans. Human does all assessments.
```

Template test:

```powershell
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
```

Result:

- prints a local course/certificate backlog template,
- includes a safety note,
- dry-run does not write unless `--apply` is used.

Gap found:

```powershell
python 03_scripts/local_worker_router.py --recommend --task "help me complete a course and get a certificate ethically"
```

Result:

```text
Route: claude_code_impl
Reason: No clear rule match - defaulting to Claude Code for human judgment.
```

The route exists, but the natural phrase "course and get a certificate" did not match. Next Claude should expand course/certificate keywords to catch natural user wording without broadening into unsafe credential automation.

## Allowed Behavior

The future course/certificate assistant may:

- find legitimate courses,
- compare course options,
- create study plans,
- create schedules,
- summarize lessons provided by the user,
- generate flashcards,
- generate practice quizzes,
- track progress,
- remind the user what to study,
- prepare certificate checklists,
- organize portfolio evidence,
- draft notes for the user to review,
- help write honest resume/portfolio descriptions after real completion.

## Forbidden Behavior

The assistant must never:

- impersonate the user,
- take exams for the user,
- answer graded quizzes for the user,
- submit assessments,
- bypass proctoring,
- bypass course platform rules,
- fabricate certificates,
- fabricate completion,
- misrepresent credentials,
- falsify portfolio artifacts,
- use private course content outside allowed use,
- create fake proof of study,
- automate credential-seeking actions without explicit user work and approval.

## Approval Gates

Human approval is required before:

- enrolling in a paid course,
- entering payment details,
- submitting any coursework,
- taking a graded assessment,
- sharing a certificate publicly,
- adding credentials to CV/LinkedIn/portfolio,
- contacting course instructors or institutions.

## Ethical MVP

First safe MVP:

- `03_scripts/course_certificate_tracker.py`
- stdlib only,
- dry-run default,
- reads/writes local JSON or JSONL under `14_context/learning/` or `05_logs/study_artifacts/`,
- generates:
  - course backlog,
  - weekly study plan,
  - flashcard draft,
  - progress summary,
  - certificate checklist,
  - portfolio evidence checklist.

No platform login, no browser automation, no submissions.

## Router Improvement Recommendation

Add safe keywords:

- `complete a course`
- `get a certificate`
- `certificate ethically`
- `study for certificate`
- `course progress`
- `course deadline`
- `learning reminder`
- `course notes`
- `lesson summary`
- `flashcards`

Do not add keywords like:

- `pass exam for me`
- `take quiz`
- `submit assignment`
- `fake certificate`
- `bypass proctor`

Those should route to a refusal/safety explanation if a future safety classifier is added.
