# Codex N+3.53 - Course Certificate Assistant Audit

## Implementation Truth

`03_scripts/course_certificate_assistant.py` is missing from the pushed N+3.50A branch.

The existing `local_worker_router.py` does include course/certificate routing and template helpers:

- `course_certificate_assistant` route exists.
- `--study-template` exists.
- `--course-cert-template` exists.
- Safety language says human completes assessments.

## Validation Truth

The route test passed:

```powershell
python 03_scripts/local_worker_router.py --recommend --task "course certificate study plan for a legitimate online course"
```

It correctly routed to `course_certificate_assistant` and described it as template generation and study tracking only.

## Ethical Boundary

Allowed future behavior:

- Find legitimate courses.
- Create study plans.
- Summarize lessons after the user provides material.
- Generate flashcards and practice questions.
- Track progress.
- Remind deadlines.
- Prepare certificate checklists.
- Organize portfolio proof.

Forbidden behavior:

- Impersonating the user.
- Taking quizzes, exams, or assessments for the user.
- Submitting coursework for the user.
- Bypassing proctoring.
- Fabricating certificates.
- Misrepresenting credentials.
- Handling course credentials or account login.
- Violating course Terms of Service.

## Usefulness Verdict

`USEFUL POLICY, MISSING HELPER`

The routing and policy are ethical and useful as planning scaffolding, but there is no dedicated assistant script yet. It is not doing courses; it can only help the human organize learning.

## Next Required Implementation

N+3.51 or N+3.53 should add a local-only `03_scripts/course_certificate_assistant.py` that can generate:

- study plan markdown
- tracker JSON/JSONL draft
- certificate checklist
- portfolio proof checklist
- reminder draft

Every output must state that the human does learning and assessments.
