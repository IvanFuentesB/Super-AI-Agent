# N+3.45B Course / Certificate Assistant Safety

Status: future lane safety spec.
Date: 2026-05-05

## Future Lane

```text
future_course_certificate_assistant
```

This lane is legitimate learning support only. It is not an impersonation, cheating, proctoring-bypass, or credential-fabrication system.

## Allowed

- course discovery
- study plans
- lesson summaries
- quiz generation
- progress tracking
- deadlines
- certificate checklist
- portfolio proof organization
- reminder drafts
- local notes

## Forbidden

- impersonation
- cheating
- proctoring bypass
- fake certificates
- fake credentials
- submitting assessments without user work and approval
- misrepresenting completion
- account creation/enrollment/payment without human approval
- submitting projects, exams, or quizzes as the user

## Source-Checked Boundary

Coursera terms explicitly treat contract cheating and impersonation as unauthorized. edX terms also flag impersonation/false identity and incorporate honor-code rules. MIT xPRO support pages describe consequences for cheating such as certificate denial/revocation. The safe Ghoti version must therefore support the learner, not replace the learner.

Source links:

- Coursera terms: https://www.coursera.org/about/terms
- edX terms: https://www.edx.org/edx-terms-service
- MIT xPRO honor code support: https://xpro.zendesk.com/hc/en-us/articles/360030200811-What-is-the-MIT-xPRO-Honor-Code

## Ethical Utility

Ghoti can be genuinely useful by:

- finding courses that match Mechatronics, robotics, automation, software, and AI goals
- comparing cost, duration, prerequisites, and certificate value
- turning syllabi into weekly plans
- turning lessons into notes
- creating practice quizzes that the user answers
- tracking deadlines
- organizing evidence of real work into a portfolio
- preparing checklist reminders before the user manually claims or shares credentials

## First MVP Idea

Local artifact generator:

```text
03_scripts/course_study_plan_intake.py
```

Future only; do not implement in this lane.

Inputs:

- course title/link pasted by user
- start/end date
- user goal
- weekly time budget
- modules/lessons pasted by user

Outputs:

- `05_logs/study_plans/<run_id>/study_plan.md`
- `05_logs/study_plans/<run_id>/quiz_bank.md`
- `05_logs/study_plans/<run_id>/certificate_checklist.md`
- `05_logs/study_plans/<run_id>/portfolio_evidence_plan.md`

All outputs are local. No login, no enrollment, no payment, no submission.

## Future Dashboard Card

Read-only card:

```text
Ghoti Learning - Study Plans
```

Shows:

- active study plans
- next lesson
- deadlines
- quiz practice count
- certificate checklist status
- portfolio artifacts
- warnings for approval-required actions

No submit/enroll/pay/claim-certificate buttons.

## Verdict

Safe as a future local-only support lane. Not approved for account actions, course submissions, proctored activity, credential claims, or anything that represents the user externally.
